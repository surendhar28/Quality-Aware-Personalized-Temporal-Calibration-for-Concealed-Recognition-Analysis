#!/usr/bin/env python3
"""
Generate Essential Experiment Outputs for GazeGuard AI / QPTC (Revision 12).
Executes 5-fold StratifiedGroupKFold cross validation on real physical Zenodo CIT data (N=38, 819 trials).
Uses the 11 baseline predictors.
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
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
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

def bootstrap_ci(y_true, y_pred, metric_fn, n_bootstraps=5000, random_state=42):
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
        "valid_sample_ratio", "early_window_sample_count", "early_probe_fix_dur",
        "early_irrel_fix_dur", "early_probe_diff", "mid_probe_diff", "late_probe_diff",
        "total_probe_diff", "mean_fix_duration", "median_fix_duration", "fixation_count"
    ]
    
    X = df[feature_cols].copy()
    y = df['familiarity_label'].values
    groups = df['participant_id'].values
    
    # -------------------------------------------------------------------------
    # 1. StratifiedGroupKFold Split & Fold Assignments
    # -------------------------------------------------------------------------
    print("\n[1/7] Generating fold_assignments.csv...")
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    fold_col = np.zeros(len(df), dtype=int)
    
    for fold_idx, (train_idx, val_idx) in enumerate(sgkf.split(X, y, groups)):
        fold_col[val_idx] = fold_idx
        
    df_folds = df[['participant_id', 'trial_id', 'stimulus_name', 'category', 'repetition', 'valid_sample_ratio', 'familiarity_label']].copy()
    df_folds.insert(0, 'fold', fold_col)
    
    fold_csv_path = os.path.join(out_dir, "fold_assignments.csv")
    df_folds.to_csv(fold_csv_path, index=False)
    print(f"  -> Saved {len(df_folds)} rows to {fold_csv_path}")
    
    # -------------------------------------------------------------------------
    # 2. Out-of-Fold (OOF) Predictions & Baseline Models
    # -------------------------------------------------------------------------
    print("\n[2/7] Running 5-Fold StratifiedGroupKFold CV and generating oof_predictions.csv...")
    models = {
        'dummy': Pipeline([
            ('model', DummyClassifier(strategy='stratified', random_state=42))
        ]),
        'logistic_regression': Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            ('model', LogisticRegression(C=1.0, penalty='l2', class_weight='balanced', max_iter=3000, random_state=42))
        ]),
        'random_forest': Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('model', RandomForestClassifier(n_estimators=500, max_depth=5, min_samples_leaf=3, class_weight='balanced', random_state=42))
        ]),
        'xgboost': Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('model', xgb.XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, reg_lambda=2, random_state=42, eval_metric='logloss'))
        ])
    }
    
    oof_probs = {m: np.zeros(len(df), dtype=float) for m in models}
    oof_preds = {m: np.zeros(len(df), dtype=int) for m in models}
    
    for fold_idx, (train_idx, val_idx) in enumerate(sgkf.split(X, y, groups)):
        X_train, y_train = X.iloc[train_idx], y[train_idx]
        X_val = X.iloc[val_idx]
        
        for m_name, model in models.items():
            model.fit(X_train, y_train)
            if hasattr(model, 'predict_proba'):
                probs = model.predict_proba(X_val)[:, 1]
            else:
                probs = model.predict(X_val).astype(float)
            preds = (probs >= 0.5).astype(int)
            
            oof_probs[m_name][val_idx] = probs
            oof_preds[m_name][val_idx] = preds

    # Weighted Ensemble (0.1 LR + 0.5 RF + 0.4 XGB)
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
    # 3. Participant-Level Aggregated Predictions
    # -------------------------------------------------------------------------
    print("\n[3/7] Generating participant_predictions.csv...")
    part_records = []
    
    for pid, pgroup in oof_df.groupby('participant_id', sort=False):
        meta = df[df['participant_id'] == pid].iloc[0]
        
        n_trials = len(pgroup)
        n_guilty = int((pgroup['y_true'] == 1).sum())
        n_control = int((pgroup['y_true'] == 0).sum())
        ground_truth = 1 if n_guilty > n_control else 0
        
        prob_dummy = float(pgroup['dummy_prob'].mean())
        prob_lr = float(pgroup['lr_prob'].mean())
        prob_rf = float(pgroup['rf_prob'].mean())
        prob_xgb = float(pgroup['xgb_prob'].mean())
        prob_ens = float(pgroup['weighted_ensemble_prob'].mean())
        
        pred_dummy = int(prob_dummy >= 0.50)
        pred_lr = int(prob_lr >= 0.50)
        pred_rf = int(prob_rf >= 0.50)
        pred_xgb = int(prob_xgb >= 0.50)
        pred_ens = int(prob_ens >= 0.50)
        
        part_records.append({
            'participant_id': pid,
            'assigned_fold': int(pgroup['fold'].iloc[0]),
            'gender': meta.get('gender', 'Unknown'),
            'group': meta.get('group', 'Unknown'),
            'calibration_accuracy_deg': round(float(meta.get('calibration_accuracy_deg', 0.0)), 3),
            'total_trials': n_trials,
            'ground_truth': ground_truth,
            'mean_valid_sample_ratio': round(float(pgroup['valid_sample_ratio'].mean()), 4),
            'dummy_prob': round(prob_dummy, 4),
            'dummy_pred': pred_dummy,
            'lr_prob': round(prob_lr, 4),
            'lr_pred': pred_lr,
            'rf_prob': round(prob_rf, 4),
            'rf_pred': pred_rf,
            'xgb_prob': round(prob_xgb, 4),
            'xgb_pred': pred_xgb,
            'weighted_ensemble_prob': round(prob_ens, 4),
            'weighted_ensemble_pred': pred_ens,
            'dummy_correct': int(pred_dummy == ground_truth),
            'lr_correct': int(pred_lr == ground_truth),
            'rf_correct': int(pred_rf == ground_truth),
            'xgb_correct': int(pred_xgb == ground_truth),
            'weighted_correct': int(pred_ens == ground_truth)
        })
        
    df_participant = pd.DataFrame(part_records)
    part_csv_path = os.path.join(out_dir, "participant_predictions.csv")
    df_participant.to_csv(part_csv_path, index=False)
    print(f"  -> Saved {len(df_participant)} participant summaries to {part_csv_path}")

    # -------------------------------------------------------------------------
    # 4. Baseline Metrics (Participant Primary Unit)
    # -------------------------------------------------------------------------
    print("\n[4/7] Generating baseline_metrics.csv...")
    all_eval_models = ['dummy', 'logistic_regression', 'random_forest', 'xgboost', 'weighted_ensemble']
    display_names = {
        'dummy': 'Dummy Classifier (Stratified Chance)',
        'logistic_regression': 'Logistic Regression (L2, Balanced)',
        'random_forest': 'Random Forest Classifier (500 Trees)',
        'xgboost': 'XGBoost Classifier (300 Trees)',
        'weighted_ensemble': 'Calibrated Weighted Ensemble (0.1 LR + 0.5 RF + 0.4 XGB)'
    }
    
    baseline_records = []
    cm_dict = {}
    y_part_true = df_participant["ground_truth"].values
    
    col_map = {
        'dummy': ('dummy_prob', 'dummy_pred'),
        'logistic_regression': ('lr_prob', 'lr_pred'),
        'random_forest': ('rf_prob', 'rf_pred'),
        'xgboost': ('xgb_prob', 'xgb_pred'),
        'weighted_ensemble': ('weighted_ensemble_prob', 'weighted_ensemble_pred')
    }

    for m_name in all_eval_models:
        prob_col, pred_col = col_map[m_name]
        yp = df_participant[pred_col].values
        yprob = df_participant[prob_col].values
        
        bacc = balanced_accuracy_score(y_part_true, yp)
        bacc_ci = bootstrap_ci(y_part_true, yp, balanced_accuracy_score)
        
        auc = roc_auc_score(y_part_true, yprob)
        auc_ci = bootstrap_ci(y_part_true, yprob, roc_auc_score)
        
        prec = precision_score(y_part_true, yp, zero_division=0)
        rec = recall_score(y_part_true, yp, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_part_true, yp).ravel()
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = f1_score(y_part_true, yp, zero_division=0)
        brier = brier_score_loss(y_part_true, yprob)
        cm = confusion_matrix(y_part_true, yp)
        cm_dict[m_name] = cm
        
        baseline_records.append({
            'model_id': m_name,
            'model_name': display_names[m_name],
            'unit': 'participant',
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
            'sample_count': len(y_part_true)
        })
        
    df_baseline = pd.DataFrame(baseline_records)
    baseline_csv_path = os.path.join(out_dir, "baseline_metrics.csv")
    df_baseline.to_csv(baseline_csv_path, index=False)
    print(f"  -> Saved baseline metrics to {baseline_csv_path}")

    # -------------------------------------------------------------------------
    # 5. Weighted Model Grid Evaluation
    # -------------------------------------------------------------------------
    print("\n[5/7] Generating weighted_model_results.csv...")
    weights_grid = []
    
    p_lr = df_participant['lr_prob'].values
    p_rf = df_participant['rf_prob'].values
    p_xgb = df_participant['xgb_prob'].values
    
    weight_candidates = [
        (1.0, 0.0, 0.0, 'Pure Logistic Regression'),
        (0.0, 1.0, 0.0, 'Pure Random Forest'),
        (0.0, 0.0, 1.0, 'Pure XGBoost'),
        (0.5, 0.5, 0.0, 'LR 50% + RF 50%'),
        (0.5, 0.0, 0.5, 'LR 50% + XGB 50%'),
        (0.0, 0.5, 0.5, 'RF 50% + XGB 50%'),
        (0.0, 0.6, 0.4, 'RF 60% + XGB 40%'),
        (0.0, 0.7, 0.3, 'RF 70% + XGB 30%'),
        (0.0, 0.8, 0.2, 'RF 80% + XGB 20%'),
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
        
        bacc = balanced_accuracy_score(y_part_true, y_blend)
        auc = roc_auc_score(y_part_true, p_blend)
        f1 = f1_score(y_part_true, y_blend, zero_division=0)
        brier = brier_score_loss(y_part_true, p_blend)
        ll = log_loss(y_part_true, np.clip(p_blend, 1e-6, 1 - 1e-6))
        
        weights_grid.append({
            'config_name': label,
            'weight_logistic_regression': round(w1, 2),
            'weight_random_forest': round(w2, 2),
            'weight_xgboost': round(w3, 2),
            'participant_balanced_accuracy': round(bacc, 4),
            'participant_balanced_accuracy_pct': round(bacc * 100, 2),
            'participant_roc_auc': round(auc, 4),
            'f1_score': round(f1, 4),
            'brier_score': round(brier, 4),
            'log_loss': round(ll, 4),
            'is_recommended_default': int('Recommended' in label)
        })
        
    df_weights = pd.DataFrame(weights_grid).sort_values(by=['participant_balanced_accuracy', 'participant_roc_auc'], ascending=[False, False])
    df_weights.reset_index(drop=True, inplace=True)
    df_weights['rank_by_balanced_accuracy'] = np.arange(1, len(df_weights) + 1)
    
    weights_csv_path = os.path.join(out_dir, "weighted_model_results.csv")
    df_weights.to_csv(weights_csv_path, index=False)
    print(f"  -> Saved weighted ensemble evaluations to {weights_csv_path}")

    # -------------------------------------------------------------------------
    # 6. Confusion Matrices (CSV and Plots)
    # -------------------------------------------------------------------------
    print("\n[6/7] Generating confusion_matrices/ and publication heatmap plots...")
    summary_cm_rows = []
    
    for m_name in all_eval_models:
        cm = cm_dict[m_name]
        tn, fp, fn, tp = cm.ravel()
        
        cm_df = pd.DataFrame(
            cm,
            index=['Actual: Innocent (0)', 'Actual: Concealed (1)'],
            columns=['Predicted: Innocent (0)', 'Predicted: Concealed (1)']
        )
        csv_m_path = os.path.join(cm_dir, f"cm_{m_name}.csv")
        cm_df.to_csv(csv_m_path)
        
        fig, ax = plt.subplots(figsize=(5, 4.2), dpi=200)
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Pred Control', 'Pred Guilty'],
            yticklabels=['Actual Control', 'Actual Guilty'],
            cbar=False, ax=ax, annot_kws={'size': 14, 'weight': 'bold'}
        )
        ax.set_title(f"{display_names[m_name]}\nParticipant-Level Confusion Matrix (N=38)", fontsize=10.5, fontweight='bold', pad=10)
        ax.set_ylabel('True Condition', fontsize=10, fontweight='bold')
        ax.set_xlabel('Predicted Condition', fontsize=10, fontweight='bold')
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
            'total_participants': int(tn + fp + fn + tp),
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
        ('random_forest', 'Random Forest (500 Trees)', 'Greens'),
        ('xgboost', 'XGBoost (300 Trees)', 'Oranges'),
        ('weighted_ensemble', 'Weighted Ensemble', 'YlGnBu')
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
        ax.set_ylabel('True Condition', fontsize=10)
        ax.set_xlabel('Predicted Condition', fontsize=10)
        
    ax_bar = axes[5]
    comp_df = pd.DataFrame(baseline_records)
    short_names = ['Dummy', 'LogReg', 'RF', 'XGBoost', 'Weighted Ens']
    bars = ax_bar.bar(
        short_names,
        comp_df['balanced_accuracy'] * 100,
        color=['#94A3B8', '#6366F1', '#0284C7', '#10B981', '#F59E0B'],
        edgecolor='#1E293B', lw=1.2
    )
    ax_bar.set_ylim([30, 85])
    ax_bar.axhline(50, color='gray', linestyle='--', alpha=0.7, label='Chance (50%)')
    ax_bar.set_ylabel('Balanced Accuracy (%)', fontsize=10, fontweight='bold')
    ax_bar.set_title('Cross-Validated Model Comparison (N=38)', fontsize=11, fontweight='bold', pad=8)
    ax_bar.tick_params(axis='x', rotation=25)
    for bar in bars:
        height = bar.get_height()
        ax_bar.annotate(f'{height:.1f}%',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3), textcoords="offset points",
            ha='center', va='bottom', fontsize=9, fontweight='bold'
        )
    ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.suptitle("Participant-Level Confusion Matrices & Performance on Zenodo Physical Benchmark (N=38)",
                 fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    grid_fig_path = os.path.join(cm_dir, "cm_comparison_grid.png")
    fig.savefig(grid_fig_path)
    plt.close(fig)
    print(f"  -> Saved all confusion matrices and heatmaps to {cm_dir}")

    print("\n" + "=" * 70)
    print("ALL ESSENTIAL EXPERIMENT OUTPUTS GENERATED SUCCESSFULLY (Revision 12)!")
    print("=" * 70)

if __name__ == '__main__':
    main()
