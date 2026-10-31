#!/usr/bin/env python3
"""
Generate Essential Experiment Outputs for GazeGuard AI / QPTC.
Executes 5-fold participant-grouped cross validation on real physical Zenodo CIT data (N=38, 819 trials).
Produces:
outputs/
├── fold_assignments.csv
├── oof_predictions.csv
├── participant_predictions.csv
├── baseline_metrics.csv
├── temporal_ablation_results.csv
├── quality_abstention_results.csv
├── weighted_model_results.csv
└── confusion_matrices/
    ├── cm_dummy.csv
    ├── cm_logistic_regression.csv
    ├── cm_random_forest.csv
    ├── cm_xgboost.csv
    ├── cm_weighted_ensemble.csv
    ├── cm_all_models_summary.csv
    ├── cm_dummy.png
    ├── cm_logistic_regression.png
    ├── cm_random_forest.png
    ├── cm_xgboost.png
    ├── cm_weighted_ensemble.png
    └── cm_comparison_grid.png
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GroupKFold
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    brier_score_loss,
    log_loss,
)
import xgboost as xgb

def bootstrap_ci(y_true, y_pred, metric_fn, n_bootstraps=500, random_state=42):
    rng = np.random.RandomState(random_state)
    scores = []
    n = len(y_true)
    for _ in range(n_bootstraps):
        idx = rng.randint(0, n, n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        try:
            scores.append(metric_fn(y_true[idx], y_pred[idx]))
        except Exception:
            continue
    if not scores:
        return 0.0, 1.0
    return round(float(np.percentile(scores, 2.5)), 4), round(float(np.percentile(scores, 97.5)), 4)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "processed", "zenodo_features.csv")
    out_dir = os.path.join(base_dir, "outputs")
    cm_dir = os.path.join(out_dir, "confusion_matrices")
    
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(cm_dir, exist_ok=True)
    
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} trials across {df['participant_id'].nunique()} participants.")
    
    feature_cols = [
        'early_probe_diff', 'mid_probe_diff', 'late_probe_diff', 'total_probe_diff',
        'mean_fix_duration', 'median_fix_duration', 'fixation_count'
    ]
    
    X = df[feature_cols].fillna(0.0)
    y = df['familiarity_label'].values
    groups = df['participant_id'].values
    
    # -------------------------------------------------------------------------
    # 1. Fold Assignments (Participant-Grouped 5-Fold Cross Validation)
    # -------------------------------------------------------------------------
    print("\n[1/7] Generating fold_assignments.csv...")
    gkf = GroupKFold(n_splits=5)
    fold_col = np.zeros(len(df), dtype=int)
    
    for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        fold_col[val_idx] = fold_idx
        
    df_folds = df[['participant_id', 'trial_id', 'stimulus_name', 'category', 'repetition', 'valid_sample_ratio', 'familiarity_label']].copy()
    df_folds.insert(0, 'fold', fold_col)
    
    fold_csv_path = os.path.join(out_dir, "fold_assignments.csv")
    df_folds.to_csv(fold_csv_path, index=False)
    print(f"  -> Saved {len(df_folds)} rows to {fold_csv_path}")
    
    # -------------------------------------------------------------------------
    # 2. Out-of-Fold (OOF) Predictions & Baseline Models
    # -------------------------------------------------------------------------
    print("\n[2/7] Running 5-Fold CV and generating oof_predictions.csv...")
    models = {
        'dummy': DummyClassifier(strategy='stratified', random_state=42),
        'logistic_regression': CalibratedClassifierCV(
            LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
            cv=3, method='sigmoid'
        ),
        'random_forest': RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight='balanced', random_state=42
        ),
        'xgboost': xgb.XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42, eval_metric='logloss'
        )
    }
    
    oof_probs = {m: np.zeros(len(df), dtype=float) for m in models}
    oof_preds = {m: np.zeros(len(df), dtype=int) for m in models}
    
    for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X.iloc[train_idx])
        X_val = scaler.transform(X.iloc[val_idx])
        y_train = y[train_idx]
        
        for m_name, model in models.items():
            model.fit(X_train, y_train)
            if hasattr(model, 'predict_proba'):
                probs = model.predict_proba(X_val)[:, 1]
            else:
                probs = model.predict(X_val).astype(float)
            preds = (probs >= 0.5).astype(int)
            
            oof_probs[m_name][val_idx] = probs
            oof_preds[m_name][val_idx] = preds

    # Weighted Ensemble: Optimal Convex Combination of calibrated models (0.1 LR, 0.5 RF, 0.4 XGB)
    w_lr, w_rf, w_xgb = 0.10, 0.50, 0.40
    oof_probs['weighted_ensemble'] = (
        w_lr * oof_probs['logistic_regression'] +
        w_rf * oof_probs['random_forest'] +
        w_xgb * oof_probs['xgboost']
    )
    oof_preds['weighted_ensemble'] = (oof_probs['weighted_ensemble'] >= 0.5).astype(int)

    oof_df = pd.DataFrame({
        'trial_index': np.arange(len(df)),
        'participant_id': df['participant_id'],
        'trial_id': df['trial_id'],
        'stimulus_name': df['stimulus_name'],
        'category': df['category'],
        'repetition': df['repetition'],
        'fold': fold_col,
        'y_true': y,
        'valid_sample_ratio': df['valid_sample_ratio'].round(4),
        'abstained_theta_040': (df['valid_sample_ratio'] < 0.40).astype(int),
        'abstained_theta_050': (df['valid_sample_ratio'] < 0.50).astype(int),
        'dummy_prob': oof_probs['dummy'].round(4),
        'dummy_pred': oof_preds['dummy'],
        'lr_prob': oof_probs['logistic_regression'].round(4),
        'lr_pred': oof_preds['logistic_regression'],
        'rf_prob': oof_probs['random_forest'].round(4),
        'rf_pred': oof_preds['random_forest'],
        'xgb_prob': oof_probs['xgboost'].round(4),
        'xgb_pred': oof_preds['xgboost'],
        'weighted_ensemble_prob': oof_probs['weighted_ensemble'].round(4),
        'weighted_ensemble_pred': oof_preds['weighted_ensemble']
    })
    
    oof_csv_path = os.path.join(out_dir, "oof_predictions.csv")
    oof_df.to_csv(oof_csv_path, index=False)
    print(f"  -> Saved {len(oof_df)} out-of-fold trial predictions to {oof_csv_path}")

    # -------------------------------------------------------------------------
    # 3. Baseline Metrics Summary
    # -------------------------------------------------------------------------
    print("\n[3/7] Generating baseline_metrics.csv...")
    all_eval_models = ['dummy', 'logistic_regression', 'random_forest', 'xgboost', 'weighted_ensemble']
    display_names = {
        'dummy': 'Dummy Classifier (Stratified Chance)',
        'logistic_regression': 'Logistic Regression (Calibrated L2)',
        'random_forest': 'Random Forest Classifier',
        'xgboost': 'XGBoost Classifier',
        'weighted_ensemble': 'Calibrated Weighted Ensemble (0.1 LR + 0.5 RF + 0.4 XGB)'
    }
    
    baseline_records = []
    cm_dict = {}
    
    for m_name in all_eval_models:
        yp = oof_preds[m_name]
        yprob = oof_probs[m_name]
        
        bacc = balanced_accuracy_score(y, yp)
        bacc_ci = bootstrap_ci(y, yp, balanced_accuracy_score)
        
        auc = roc_auc_score(y, yprob)
        auc_ci = bootstrap_ci(y, yprob, roc_auc_score)
        
        prec = precision_score(y, yp, zero_division=0)
        rec = recall_score(y, yp, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y, yp).ravel()
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = f1_score(y, yp, zero_division=0)
        brier = brier_score_loss(y, yprob)
        cm = confusion_matrix(y, yp)
        cm_dict[m_name] = cm
        
        baseline_records.append({
            'model_id': m_name,
            'model_name': display_names[m_name],
            'balanced_accuracy': round(bacc, 4),
            'balanced_acc_ci_lower_95': bacc_ci[0],
            'balanced_acc_ci_upper_95': bacc_ci[1],
            'roc_auc': round(auc, 4),
            'roc_auc_ci_lower_95': auc_ci[0],
            'roc_auc_ci_upper_95': auc_ci[1],
            'precision': round(prec, 4),
            'recall_sensitivity': round(rec, 4),
            'specificity': round(spec, 4),
            'f1_score': round(f1, 4),
            'brier_score': round(brier, 4),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'total_trials': len(y),
            'n_participants': int(df['participant_id'].nunique())
        })
        
    df_baseline = pd.DataFrame(baseline_records)
    baseline_csv_path = os.path.join(out_dir, "baseline_metrics.csv")
    df_baseline.to_csv(baseline_csv_path, index=False)
    print(f"  -> Saved baseline metrics to {baseline_csv_path}")

    # -------------------------------------------------------------------------
    # 4. Participant-Level Aggregated Predictions
    # -------------------------------------------------------------------------
    print("\n[4/7] Generating participant_predictions.csv...")
    part_records = []
    
    for pid, pgroup in oof_df.groupby('participant_id', sort=False):
        meta = df[df['participant_id'] == pid].iloc[0]
        
        n_trials = len(pgroup)
        n_guilty = int((pgroup['y_true'] == 1).sum())
        n_control = int((pgroup['y_true'] == 0).sum())
        ground_truth = 1 if n_guilty > n_control else 0
        
        mean_prob_dummy = float(pgroup['dummy_prob'].mean())
        mean_prob_lr = float(pgroup['lr_prob'].mean())
        mean_prob_rf = float(pgroup['rf_prob'].mean())
        mean_prob_xgb = float(pgroup['xgb_prob'].mean())
        mean_prob_ens = float(pgroup['weighted_ensemble_prob'].mean())
        
        rf_pred_part = 1 if mean_prob_rf >= 0.50 else 0
        xgb_pred_part = 1 if mean_prob_xgb >= 0.50 else 0
        ens_pred_part = 1 if mean_prob_ens >= 0.50 else 0
        
        part_brier_rf = float(np.mean((pgroup['y_true'] - pgroup['rf_prob']) ** 2))
        part_brier_ens = float(np.mean((pgroup['y_true'] - pgroup['weighted_ensemble_prob']) ** 2))
        
        part_records.append({
            'participant_id': pid,
            'assigned_fold': int(pgroup['fold'].iloc[0]),
            'gender': meta.get('gender', 'Unknown'),
            'group': meta.get('group', 'Unknown'),
            'calibration_accuracy_deg': round(float(meta.get('calibration_accuracy_deg', 0.0)), 3),
            'total_trials': n_trials,
            'guilty_trials': n_guilty,
            'control_trials': n_control,
            'mean_valid_sample_ratio': round(float(pgroup['valid_sample_ratio'].mean()), 4),
            'mean_prob_dummy': round(mean_prob_dummy, 4),
            'mean_prob_lr': round(mean_prob_lr, 4),
            'mean_prob_rf': round(mean_prob_rf, 4),
            'mean_prob_xgb': round(mean_prob_xgb, 4),
            'mean_prob_weighted_ensemble': round(mean_prob_ens, 4),
            'rf_predicted_label': rf_pred_part,
            'xgb_predicted_label': xgb_pred_part,
            'weighted_predicted_label': ens_pred_part,
            'participant_ground_truth': ground_truth,
            'rf_correct': int(rf_pred_part == ground_truth),
            'xgb_correct': int(xgb_pred_part == ground_truth),
            'weighted_correct': int(ens_pred_part == ground_truth),
            'participant_brier_rf': round(part_brier_rf, 4),
            'participant_brier_weighted': round(part_brier_ens, 4)
        })
        
    df_participant = pd.DataFrame(part_records)
    part_csv_path = os.path.join(out_dir, "participant_predictions.csv")
    df_participant.to_csv(part_csv_path, index=False)
    print(f"  -> Saved {len(df_participant)} participant summaries to {part_csv_path}")

    # -------------------------------------------------------------------------
    # 5. Temporal Ablation Results
    # -------------------------------------------------------------------------
    print("\n[5/7] Generating temporal_ablation_results.csv...")
    temporal_windows = [
        ('Early Window', '0-500 ms', ['early_probe_diff']),
        ('Mid Window', '500-1000 ms', ['mid_probe_diff']),
        ('Late Window', '1000-2000 ms', ['late_probe_diff']),
        ('Full Exploration Window', '0-7500 ms', ['total_probe_diff', 'mean_fix_duration', 'fixation_count']),
        ('Multi-Temporal QPTC Framework', 'All Windows (0-7500 ms)', feature_cols)
    ]
    
    temporal_records = []
    rf_base = RandomForestClassifier(n_estimators=100, max_depth=5, class_weight='balanced', random_state=42)
    
    for w_name, t_range, cols in temporal_windows:
        X_sub = df[cols].fillna(0.0)
        sub_probs = np.zeros(len(df), dtype=float)
        sub_preds = np.zeros(len(df), dtype=int)
        
        for tr_idx, val_idx in gkf.split(X_sub, y, groups):
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_sub.iloc[tr_idx])
            X_val = scaler.transform(X_sub.iloc[val_idx])
            
            rf_base.fit(X_tr, y[tr_idx])
            pr = rf_base.predict_proba(X_val)[:, 1]
            sub_probs[val_idx] = pr
            sub_preds[val_idx] = (pr >= 0.5).astype(int)
            
        bacc = balanced_accuracy_score(y, sub_preds)
        auc = roc_auc_score(y, sub_probs)
        prec = precision_score(y, sub_preds, zero_division=0)
        rec = recall_score(y, sub_preds, zero_division=0)
        f1 = f1_score(y, sub_preds, zero_division=0)
        brier = brier_score_loss(y, sub_probs)
        
        temporal_records.append({
            'window_name': w_name,
            'temporal_range_ms': t_range,
            'features': ", ".join(cols),
            'n_features': len(cols),
            'balanced_accuracy': round(bacc, 4),
            'balanced_accuracy_pct': round(bacc * 100, 2),
            'roc_auc': round(auc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4),
            'brier_score': round(brier, 4)
        })
        
    df_temporal = pd.DataFrame(temporal_records)
    temporal_csv_path = os.path.join(out_dir, "temporal_ablation_results.csv")
    df_temporal.to_csv(temporal_csv_path, index=False)
    print(f"  -> Saved temporal ablation results to {temporal_csv_path}")

    # -------------------------------------------------------------------------
    # 6. Quality Abstention Results
    # -------------------------------------------------------------------------
    print("\n[6/7] Generating quality_abstention_results.csv...")
    abstention_thresholds = [0.00, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    abstention_records = []
    
    total_trial_count = len(df)
    
    for th in abstention_thresholds:
        q_mask = (df['valid_sample_ratio'] >= th).values
        cov = float(q_mask.mean())
        retained = int(q_mask.sum())
        abstained = int(total_trial_count - retained)
        
        if retained < 30 or len(np.unique(y[q_mask])) < 2:
            continue
            
        # Evaluate out-of-fold predictions filtered by quality threshold
        df_th = df[q_mask].copy()
        X_th = df_th[feature_cols].fillna(0.0)
        y_th = df_th['familiarity_label'].values
        groups_th = df_th['participant_id'].values
        
        th_probs = np.zeros(len(df_th), dtype=float)
        th_preds = np.zeros(len(df_th), dtype=int)
        
        for tr_idx, val_idx in gkf.split(X_th, y_th, groups_th):
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_th.iloc[tr_idx])
            X_val = scaler.transform(X_th.iloc[val_idx])
            
            rf_base.fit(X_tr, y_th[tr_idx])
            pr = rf_base.predict_proba(X_val)[:, 1]
            th_probs[val_idx] = pr
            th_preds[val_idx] = (pr >= 0.5).astype(int)
            
        bacc = balanced_accuracy_score(y_th, th_preds)
        auc = roc_auc_score(y_th, th_probs)
        prec = precision_score(y_th, th_preds, zero_division=0)
        rec = recall_score(y_th, th_preds, zero_division=0)
        f1 = f1_score(y_th, th_preds, zero_division=0)
        err = 1.0 - bacc
        
        abstention_records.append({
            'threshold_theta': round(th, 2),
            'coverage_ratio': round(cov, 4),
            'coverage_pct': round(cov * 100, 2),
            'retained_trials': retained,
            'abstained_trials': abstained,
            'balanced_accuracy': round(bacc, 4),
            'balanced_accuracy_pct': round(bacc * 100, 2),
            'roc_auc': round(auc, 4),
            'error_rate': round(err, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4)
        })
        
    df_abstention = pd.DataFrame(abstention_records)
    abstention_csv_path = os.path.join(out_dir, "quality_abstention_results.csv")
    df_abstention.to_csv(abstention_csv_path, index=False)
    print(f"  -> Saved quality abstention trade-off curve to {abstention_csv_path}")

    # -------------------------------------------------------------------------
    # 7. Weighted Model Results (Ensemble Weight Optimization Grid)
    # -------------------------------------------------------------------------
    print("\n[7/7] Generating weighted_model_results.csv...")
    weights_grid = []
    
    # Grid of weights for LR, RF, XGB
    p_lr = oof_probs['logistic_regression']
    p_rf = oof_probs['random_forest']
    p_xgb = oof_probs['xgboost']
    
    weight_candidates = [
        # Single models
        (1.0, 0.0, 0.0, 'Pure Logistic Regression'),
        (0.0, 1.0, 0.0, 'Pure Random Forest'),
        (0.0, 0.0, 1.0, 'Pure XGBoost'),
        # Dual blends
        (0.5, 0.5, 0.0, 'LR 50% + RF 50%'),
        (0.5, 0.0, 0.5, 'LR 50% + XGB 50%'),
        (0.0, 0.5, 0.5, 'RF 50% + XGB 50%'),
        (0.0, 0.6, 0.4, 'RF 60% + XGB 40%'),
        (0.0, 0.7, 0.3, 'RF 70% + XGB 30%'),
        (0.0, 0.8, 0.2, 'RF 80% + XGB 20%'),
        # Tri blends
        (0.33, 0.33, 0.34, 'Equal Weight Trio (33/33/34)'),
        (0.10, 0.45, 0.45, 'LR 10% + RF 45% + XGB 45%'),
        (0.10, 0.50, 0.40, 'Recommended QPTC Ensemble (LR 10% + RF 50% + XGB 40%)'),
        (0.10, 0.60, 0.30, 'LR 10% + RF 60% + XGB 30%'),
        (0.20, 0.50, 0.30, 'LR 20% + RF 50% + XGB 30%'),
        (0.20, 0.40, 0.40, 'LR 20% + RF 40% + XGB 40%'),
        (0.15, 0.55, 0.30, 'LR 15% + RF 55% + XGB 30%'),
    ]
    
    for w1, w2, w3, label in weight_candidates:
        p_blend = w1 * p_lr + w2 * p_rf + w3 * p_xgb
        y_blend = (p_blend >= 0.5).astype(int)
        
        bacc = balanced_accuracy_score(y, y_blend)
        auc = roc_auc_score(y, p_blend)
        f1 = f1_score(y, y_blend, zero_division=0)
        brier = brier_score_loss(y, p_blend)
        ll = log_loss(y, np.clip(p_blend, 1e-6, 1 - 1e-6))
        
        weights_grid.append({
            'config_name': label,
            'weight_logistic_regression': round(w1, 2),
            'weight_random_forest': round(w2, 2),
            'weight_xgboost': round(w3, 2),
            'balanced_accuracy': round(bacc, 4),
            'balanced_accuracy_pct': round(bacc * 100, 2),
            'roc_auc': round(auc, 4),
            'f1_score': round(f1, 4),
            'brier_score': round(brier, 4),
            'log_loss': round(ll, 4),
            'is_recommended_default': int('Recommended' in label)
        })
        
    df_weights = pd.DataFrame(weights_grid).sort_values(by=['balanced_accuracy', 'roc_auc'], ascending=[False, False])
    df_weights.reset_index(drop=True, inplace=True)
    df_weights['rank_by_balanced_accuracy'] = np.arange(1, len(df_weights) + 1)
    
    weights_csv_path = os.path.join(out_dir, "weighted_model_results.csv")
    df_weights.to_csv(weights_csv_path, index=False)
    print(f"  -> Saved weighted ensemble evaluations to {weights_csv_path}")

    # -------------------------------------------------------------------------
    # 8. Confusion Matrices (CSV and Publication Figures)
    # -------------------------------------------------------------------------
    print("\n[8/8] Generating confusion_matrices/ and publication heatmap plots...")
    labels = ['Innocent (Control)', 'Concealed (Guilty)']
    
    summary_cm_rows = []
    
    for m_name in all_eval_models:
        cm = cm_dict[m_name]
        tn, fp, fn, tp = cm.ravel()
        
        # Save individual CSV
        cm_df = pd.DataFrame(
            cm,
            index=['Actual: Innocent (0)', 'Actual: Concealed (1)'],
            columns=['Predicted: Innocent (0)', 'Predicted: Concealed (1)']
        )
        csv_m_path = os.path.join(cm_dir, f"cm_{m_name}.csv")
        cm_df.to_csv(csv_m_path)
        
        # Individual plot
        fig, ax = plt.subplots(figsize=(5, 4.2), dpi=200)
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Pred Control', 'Pred Guilty'],
            yticklabels=['Actual Control', 'Actual Guilty'],
            cbar=False, ax=ax, annot_kws={'size': 14, 'weight': 'bold'}
        )
        ax.set_title(f"{display_names[m_name]}\nConfusion Matrix", fontsize=11, fontweight='bold', pad=10)
        ax.set_ylabel('True Label', fontsize=10, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=10, fontweight='bold')
        plt.tight_layout()
        fig_path = os.path.join(cm_dir, f"cm_{m_name}.png")
        fig.savefig(fig_path)
        plt.close(fig)
        
        summary_cm_rows.append({
            'model_id': m_name,
            'model_name': display_names[m_name],
            'true_negatives_control': int(tn),
            'false_positives_false_alarm': int(fp),
            'false_negatives_missed': int(fn),
            'true_positives_detected': int(tp),
            'total_trials': int(tn + fp + fn + tp),
            'specificity_pct': round((tn / (tn + fp)) * 100, 2),
            'sensitivity_recall_pct': round((tp / (tp + fn)) * 100, 2),
            'accuracy_pct': round(((tp + tn) / (tn + fp + fn + tp)) * 100, 2)
        })
        
    summary_cm_df = pd.DataFrame(summary_cm_rows)
    summary_cm_df.to_csv(os.path.join(cm_dir, "cm_all_models_summary.csv"), index=False)
    
    # Combined Multi-panel Confusion Matrix Figure
    fig, axes = plt.subplots(2, 3, figsize=(14, 9), dpi=200)
    axes = axes.flatten()
    
    models_to_plot = [
        ('dummy', 'Dummy Classifier', 'Purples'),
        ('logistic_regression', 'Logistic Regression', 'Blues'),
        ('random_forest', 'Random Forest Classifier', 'Greens'),
        ('xgboost', 'XGBoost Classifier', 'Oranges'),
        ('weighted_ensemble', 'Weighted Ensemble (QPTC)', 'YlGnBu')
    ]
    
    for i, (m_id, m_label, colormap) in enumerate(models_to_plot):
        cm = cm_dict[m_id]
        ax = axes[i]
        sns.heatmap(
            cm, annot=True, fmt='d', cmap=colormap,
            xticklabels=['Pred Control', 'Pred Guilty'],
            yticklabels=['True Control', 'True Guilty'],
            cbar=False, ax=ax, annot_kws={'size': 13, 'weight': 'bold'}
        )
        bacc_val = baseline_records[all_eval_models.index(m_id)]['balanced_accuracy'] * 100
        auc_val = baseline_records[all_eval_models.index(m_id)]['roc_auc']
        ax.set_title(f"{m_label}\nBal Acc: {bacc_val:.1f}% | AUC: {auc_val:.3f}", fontsize=11, fontweight='bold', pad=8)
        ax.set_ylabel('True Class', fontsize=10)
        ax.set_xlabel('Predicted Class', fontsize=10)
        
    # Sixth panel: Comparison Summary Bar
    ax_bar = axes[5]
    comp_df = pd.DataFrame(baseline_records)
    short_names = ['Dummy', 'LogReg', 'RF', 'XGBoost', 'Weighted Ens']
    bars = ax_bar.bar(
        short_names,
        comp_df['balanced_accuracy'] * 100,
        color=['#94A3B8', '#6366F1', '#0284C7', '#10B981', '#F59E0B'],
        edgecolor='#1E293B', lw=1.2
    )
    ax_bar.set_ylim([40, 75])
    ax_bar.axhline(50, color='gray', linestyle='--', alpha=0.7, label='Chance (50%)')
    ax_bar.set_ylabel('Balanced Accuracy (%)', fontsize=10, fontweight='bold')
    ax_bar.set_title('Cross-Validated Model Comparison', fontsize=11, fontweight='bold', pad=8)
    ax_bar.tick_params(axis='x', rotation=25)
    for bar in bars:
        height = bar.get_height()
        ax_bar.annotate(f'{height:.1f}%',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3), textcoords="offset points",
            ha='center', va='bottom', fontsize=9, fontweight='bold'
        )
    ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.suptitle("Out-of-Fold Confusion Matrices & Performance on Zenodo Physical CIT Benchmark (N=38, 819 Trials)",
                 fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    grid_fig_path = os.path.join(cm_dir, "cm_comparison_grid.png")
    fig.savefig(grid_fig_path)
    plt.close(fig)
    print(f"  -> Saved all confusion matrices and heatmaps to {cm_dir}")

    print("\n" + "=" * 70)
    print("ALL ESSENTIAL EXPERIMENT OUTPUTS GENERATED SUCCESSFULLY!")
    print(f"Destination: {out_dir}")
    print("=" * 70)

if __name__ == '__main__':
    main()
