#!/usr/bin/env python3
"""
Scientific Experiment Suite executed on real Zenodo physical eye-tracking CIT data.
Loads data/processed/zenodo_features.csv (819 trials, 38 participants).
Implements participant-grouped 5-fold cross-validation with zero leakage.
Logs authentic scientific findings to experiments/results/.
"""

import os
import sys
import json
from datetime import datetime
import numpy as np
import pandas as pd
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

def evaluate_models_grouped_cv(X, y, groups, n_splits=5, random_state=42):
    gkf = GroupKFold(n_splits=n_splits)
    
    models = {
        "dummy": DummyClassifier(strategy="stratified", random_state=random_state),
        "logistic_regression": CalibratedClassifierCV(
            LogisticRegression(class_weight="balanced", random_state=random_state, max_iter=1000),
            cv=3, method="sigmoid"
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=random_state
        ),
        "xgboost": xgb.XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05, random_state=random_state, eval_metric="logloss"
        )
    }
    
    results = {}
    
    for m_name, model in models.items():
        all_y_true = []
        all_y_pred = []
        all_y_prob = []
        
        for train_idx, val_idx in gkf.split(X, y, groups):
            X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
            X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
            
            # Preprocessing: Impute and Scale
            scaler = StandardScaler()
            X_tr_sc = scaler.fit_transform(np.nan_to_num(X_tr, nan=0.0))
            X_val_sc = scaler.transform(np.nan_to_num(X_val, nan=0.0))
            
            model.fit(X_tr_sc, y_tr)
            preds = model.predict(X_val_sc)
            probs = model.predict_proba(X_val_sc)[:, 1] if hasattr(model, "predict_proba") else preds.astype(float)
            
            all_y_true.extend(y_val)
            all_y_pred.extend(preds)
            all_y_prob.extend(probs)
            
        y_true_arr = np.array(all_y_true)
        y_pred_arr = np.array(all_y_pred)
        y_prob_arr = np.array(all_y_prob)
        
        bacc = float(balanced_accuracy_score(y_true_arr, y_pred_arr))
        auc = float(roc_auc_score(y_true_arr, y_prob_arr))
        prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
        rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
        f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))
        brier = float(brier_score_loss(y_true_arr, y_prob_arr))
        cm = confusion_matrix(y_true_arr, y_pred_arr).tolist()
        
        bacc_ci = bootstrap_ci(y_true_arr, y_pred_arr, balanced_accuracy_score, random_state=random_state)
        auc_ci = bootstrap_ci(y_true_arr, y_prob_arr, roc_auc_score, random_state=random_state)
        
        results[m_name] = {
            "model_name": m_name,
            "balanced_accuracy": round(bacc, 4),
            "balanced_accuracy_ci_95": list(bacc_ci),
            "roc_auc": round(auc, 4),
            "roc_auc_ci_95": list(auc_ci),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "brier_score": round(brier, 4),
            "confusion_matrix": cm,
            "sample_count": len(y_true_arr)
        }
        
    return results

def main():
    print("=" * 70)
    print("GazeGuard AI — Scientific Evaluation on Verified Zenodo Dataset")
    print("Record 18525952: Tobii Pro Fusion Eye Tracker (38 Participants, 819 Trials)")
    print("=" * 70)
    
    csv_path = r"E:\karthianna\data\processed\zenodo_features.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        sys.exit(1)
        
    df = pd.read_csv(csv_path)
    print(f"\nLoaded {len(df)} trials from {df['participant_id'].nunique()} participants.")
    print("Class counts (0=control, 1=guilty):", dict(df['familiarity_label'].value_counts()))
    
    os.makedirs("./experiments/results", exist_ok=True)
    
    # Feature subsets
    feature_cols = [
        'early_probe_diff', 'mid_probe_diff', 'late_probe_diff', 'total_probe_diff',
        'mean_fix_duration', 'median_fix_duration', 'fixation_count'
    ]
    
    X = df[feature_cols].copy()
    y = df['familiarity_label'].copy()
    groups = df['participant_id'].copy()
    
    # -------------------------------------------------------------------------
    # Experiment 1: Baseline Models Comparison
    # -------------------------------------------------------------------------
    print("\n[1/5] Running Experiment 1: Baseline Models Comparison (GroupKFold CV)...")
    exp1_models = evaluate_models_grouped_cv(X, y, groups)
    exp1 = {
        "experiment_id": "EXP-01-BASELINES-ZENODO",
        "description": "Participant-grouped cross-validation of baseline models on 38 Tobii participants",
        "data_provenance": "Zenodo DOI 10.5281/zenodo.18525952",
        "timestamp": datetime.utcnow().isoformat(),
        "n_participants": int(df['participant_id'].nunique()),
        "total_trials": len(df),
        "models": exp1_models
    }
    with open("./experiments/results/exp01_baselines.json", "w") as f:
        json.dump(exp1, f, indent=2)
    print(f"  -> Dummy: Acc={exp1_models['dummy']['balanced_accuracy']:.3f}, AUC={exp1_models['dummy']['roc_auc']:.3f}")
    print(f"  -> LogReg: Acc={exp1_models['logistic_regression']['balanced_accuracy']:.3f}, AUC={exp1_models['logistic_regression']['roc_auc']:.3f}")
    print(f"  -> RandomForest: Acc={exp1_models['random_forest']['balanced_accuracy']:.3f}, AUC={exp1_models['random_forest']['roc_auc']:.3f}")
    print(f"  -> XGBoost: Acc={exp1_models['xgboost']['balanced_accuracy']:.3f}, AUC={exp1_models['xgboost']['roc_auc']:.3f}")
    
    # -------------------------------------------------------------------------
    # Experiment 2: Personalized Calibration Ablation (Mode A vs Mode B)
    # -------------------------------------------------------------------------
    print("\n[2/5] Running Experiment 2: Personalized Calibration Ablation (Mode A vs Mode B)...")
    # Mode A: Raw population features
    mode_a_res = evaluate_models_grouped_cv(X, y, groups)['random_forest']
    
    # Mode B: Participant-normalized features (computed using repetition 1 as baseline, rep 2&3 as test)
    # Or z-score per participant on neutral features without probe leakage
    df_norm = df.copy()
    for col in feature_cols:
        # compute participant mean and std on repetition 1 (baseline calibration)
        baseline_stats = df[df['repetition'] == 1].groupby('participant_id')[col].agg(['mean', 'std'])
        for p_id in df['participant_id'].unique():
            if p_id in baseline_stats.index:
                mu = baseline_stats.loc[p_id, 'mean']
                sigma = baseline_stats.loc[p_id, 'std']
                sigma = sigma if (pd.notna(sigma) and sigma > 1e-3) else 1.0
            else:
                mu = df[col].mean()
                sigma = df[col].std() or 1.0
            mask = df_norm['participant_id'] == p_id
            df_norm.loc[mask, col] = (df_norm.loc[mask, col] - mu) / (sigma + 1e-4)
            
    # Evaluate test trials (repetition 2 & 3) under Mode B
    test_mask = df_norm['repetition'].isin([2, 3])
    X_b = df_norm.loc[test_mask, feature_cols]
    y_b = df_norm.loc[test_mask, 'familiarity_label']
    groups_b = df_norm.loc[test_mask, 'participant_id']
    
    mode_b_res = evaluate_models_grouped_cv(X_b, y_b, groups_b)['random_forest']
    
    delta_bacc = mode_b_res['balanced_accuracy'] - mode_a_res['balanced_accuracy']
    exp2 = {
        "experiment_id": "EXP-02-PERSONALIZATION-ZENODO",
        "description": "Comparison of population baseline (Mode A) vs Personalized baseline (Mode B)",
        "data_provenance": "Zenodo DOI 10.5281/zenodo.18525952",
        "timestamp": datetime.utcnow().isoformat(),
        "mode_a_population": mode_a_res,
        "mode_b_personalized": mode_b_res,
        "delta_balanced_accuracy": round(delta_bacc, 4),
        "personalization_supported": bool(delta_bacc > 0)
    }
    with open("./experiments/results/exp02_personalization.json", "w") as f:
        json.dump(exp2, f, indent=2)
    print(f"  -> Mode A (Population) Balanced Acc: {mode_a_res['balanced_accuracy']:.3f}")
    print(f"  -> Mode B (Personalized) Balanced Acc: {mode_b_res['balanced_accuracy']:.3f} (Delta: {delta_bacc*100:+.1f}%)")
    
    # -------------------------------------------------------------------------
    # Experiment 3: Temporal Window Contribution Ablation
    # -------------------------------------------------------------------------
    print("\n[3/5] Running Experiment 3: Temporal Window Contribution Ablation...")
    window_definitions = {
        "early_0_500ms": ['early_probe_diff'],
        "mid_500_1000ms": ['mid_probe_diff'],
        "late_1000_2000ms": ['late_probe_diff'],
        "overall_trial": ['total_probe_diff', 'mean_fix_duration', 'fixation_count'],
        "multi_temporal_qptc": feature_cols
    }
    window_results = {}
    for w_name, cols in window_definitions.items():
        w_res = evaluate_models_grouped_cv(df[cols], y, groups)['random_forest']
        window_results[w_name] = w_res
        print(f"  -> {w_name:20s}: Balanced Acc={w_res['balanced_accuracy']:.3f}, AUC={w_res['roc_auc']:.3f}")
        
    exp3 = {
        "experiment_id": "EXP-03-TEMPORAL-WINDOWS-ZENODO",
        "description": "Evaluation of familiarity classification across distinct temporal windows",
        "data_provenance": "Zenodo DOI 10.5281/zenodo.18525952",
        "timestamp": datetime.utcnow().isoformat(),
        "windows": window_results
    }
    with open("./experiments/results/exp03_temporal_windows.json", "w") as f:
        json.dump(exp3, f, indent=2)
        
    # -------------------------------------------------------------------------
    # Experiment 4: Quality-Aware Abstention Trade-off
    # -------------------------------------------------------------------------
    print("\n[4/5] Running Experiment 4: Quality-Aware Abstention Trade-off...")
    thresholds = [0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    tradeoffs = []
    
    for th in thresholds:
        # Filter trials meeting quality threshold on valid sample ratio
        q_mask = df['valid_sample_ratio'] >= th
        coverage = float(q_mask.mean())
        if coverage > 0.15:
            df_th = df[q_mask]
            th_res = evaluate_models_grouped_cv(
                df_th[feature_cols], df_th['familiarity_label'], df_th['participant_id']
            )['random_forest']
            tradeoffs.append({
                "threshold": th,
                "coverage": round(coverage, 3),
                "retained_trials": int(q_mask.sum()),
                "balanced_accuracy": th_res['balanced_accuracy'],
                "roc_auc": th_res['roc_auc'],
                "error_rate": round(1.0 - th_res['balanced_accuracy'], 4)
            })
            print(f"  -> Threshold {th:.2f}: Coverage={coverage*100:.1f}%, Balanced Acc={th_res['balanced_accuracy']:.3f}, Error={1.0 - th_res['balanced_accuracy']:.3f}")
            
    exp4 = {
        "experiment_id": "EXP-04-QUALITY-ABSTENTION-ZENODO",
        "description": "Coverage vs error trade-off under varying valid gaze sample thresholds",
        "data_provenance": "Zenodo DOI 10.5281/zenodo.18525952",
        "timestamp": datetime.utcnow().isoformat(),
        "tradeoff_curve": tradeoffs
    }
    with open("./experiments/results/exp04_quality_abstention.json", "w") as f:
        json.dump(exp4, f, indent=2)
        
    # -------------------------------------------------------------------------
    # Experiment 6: Robustness Under Signal Degradation
    # -------------------------------------------------------------------------
    print("\n[5/5] Running Experiment 6: Robustness Under Injected Signal Degradation...")
    noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    robustness_results = []
    
    rng = np.random.RandomState(42)
    for nl in noise_levels:
        X_noisy = X.copy()
        if nl > 0:
            for c in feature_cols:
                # Add Gaussian noise proportional to feature std
                scale = X[c].std() or 1.0
                X_noisy[c] += rng.normal(0, nl * scale, size=len(X))
                
        r_res = evaluate_models_grouped_cv(X_noisy, y, groups)['random_forest']
        robustness_results.append({
            "noise_level": nl,
            "balanced_accuracy": r_res['balanced_accuracy'],
            "roc_auc": r_res['roc_auc']
        })
        print(f"  -> Noise Level {nl*100:4.1f}%: Balanced Acc={r_res['balanced_accuracy']:.3f}, AUC={r_res['roc_auc']:.3f}")
        
    exp6 = {
        "experiment_id": "EXP-06-ROBUSTNESS-ZENODO",
        "description": "Model stability under noise corruption and measurement jitter",
        "data_provenance": "Zenodo DOI 10.5281/zenodo.18525952",
        "timestamp": datetime.utcnow().isoformat(),
        "noise_degradation_curve": robustness_results
    }
    with open("./experiments/results/exp06_robustness.json", "w") as f:
        json.dump(exp6, f, indent=2)
        
    print("\n" + "=" * 70)
    print("Zenodo Real Physical Experiments successfully completed!")
    print("Results logged to experiments/results/")
    print("=" * 70)

if __name__ == '__main__':
    main()
