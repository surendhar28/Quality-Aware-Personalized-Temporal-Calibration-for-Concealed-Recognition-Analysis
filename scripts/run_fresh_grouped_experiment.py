#!/usr/bin/env python3
"""
GazeGuard AI — Authoritative Reproducible Fresh Baseline Experiment (Revision 12)
Evaluates Logistic Regression, Random Forest, and XGBoost on 819 real Zenodo trials (N=38 participants).
Protocol:
- StratifiedGroupKFold (5 splits, shuffle=True, seed=42)
- 11 features defined in experiments/config.yaml
- Preprocessing fit strictly within outer training folds (Median Imputation, StandardScaler for LR only)
- Primary unit of evaluation: Participant (mean held-out row probability aggregation)
- 10,000 participant-stratified bootstrap replicates for 95% confidence intervals
- Outputs saved to outputs/final_baseline/ and experiments/results/final_baseline/
"""

import os
import sys
import json
import platform
import hashlib
from datetime import datetime
import yaml
import numpy as np
import pandas as pd
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


def get_environment_info():
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "sklearn_version": __import__("sklearn").__version__,
        "xgboost_version": xgb.__version__,
        "execution_timestamp": datetime.utcnow().isoformat() + "Z",
    }


def compute_participant_stratified_bootstrap_ci(y_true, y_prob, metric_fn, n_replicates=10000, random_state=42):
    """
    Participant-stratified bootstrap for calculating robust 95% confidence intervals.
    Separates control (0) and guilty (1) participant pools, resampling each with replacement.
    """
    rng = np.random.RandomState(random_state)
    idx_0 = np.where(y_true == 0)[0]
    idx_1 = np.where(y_true == 1)[0]
    n_0 = len(idx_0)
    n_1 = len(idx_1)
    
    scores = []
    for _ in range(n_replicates):
        boot_0 = rng.choice(idx_0, size=n_0, replace=True)
        boot_1 = rng.choice(idx_1, size=n_1, replace=True)
        boot_idx = np.concatenate([boot_0, boot_1])
        
        y_b = y_true[boot_idx]
        p_b = y_prob[boot_idx]
        
        try:
            scores.append(metric_fn(y_b, p_b))
        except Exception:
            continue
            
    if not scores:
        return 0.0, 1.0
    return round(float(np.percentile(scores, 2.5)), 4), round(float(np.percentile(scores, 97.5)), 4)


def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "experiments", "config.yaml")
    config = load_config(config_path)

    data_rel = config.get("dataset", {}).get("input", "data/processed/zenodo_features.csv")
    data_path = os.path.join(base_dir, data_rel)
    
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        sys.exit(1)
        
    df = pd.read_csv(data_path)
    
    # Validation checks
    expected_rows = config.get("dataset", {}).get("expected_rows", 819)
    expected_participants = config.get("dataset", {}).get("expected_participants", 38)
    
    actual_rows = len(df)
    actual_participants = df["participant_id"].nunique()
    
    print("=" * 75)
    print("GAZEGUARD AI — FRESH BASELINE EXPERIMENT (Revision 12)")
    print(f"Dataset: {data_path}")
    print(f"Rows: {actual_rows} (Expected: {expected_rows})")
    print(f"Participants: {actual_participants} (Expected: {expected_participants})")
    print("=" * 75)
    
    if actual_rows != expected_rows or actual_participants != expected_participants:
        print(f"Warning: Data dimension mismatch! Rows: {actual_rows}, Participants: {actual_participants}")

    # Feature List (11 features)
    features = config.get("features", [
        "valid_sample_ratio",
        "early_window_sample_count",
        "early_probe_fix_dur",
        "early_irrel_fix_dur",
        "early_probe_diff",
        "mid_probe_diff",
        "late_probe_diff",
        "total_probe_diff",
        "mean_fix_duration",
        "median_fix_duration",
        "fixation_count"
    ])
    
    missing_feats = [f for f in features if f not in df.columns]
    if missing_feats:
        print(f"Error: Missing features in dataset: {missing_feats}")
        sys.exit(1)
        
    X = df[features].copy()
    y = df["familiarity_label"].values
    groups = df["participant_id"].values
    
    # Hash dataset for provenance audit
    with open(data_path, "rb") as f:
        dataset_sha256 = hashlib.sha256(f.read()).hexdigest()

    # StratifiedGroupKFold Setup
    eval_cfg = config.get("evaluation", {})
    n_splits = eval_cfg.get("n_splits", 5)
    seed = eval_cfg.get("random_seed", 42)
    shuffle = eval_cfg.get("shuffle", True)
    bootstrap_reps = eval_cfg.get("bootstrap_replicates", 10000)
    decision_threshold = eval_cfg.get("decision_threshold", 0.5)

    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=seed)

    # Models to evaluate (Pure, leak-free pipelines)
    models = {
        "dummy": Pipeline([
            ("model", DummyClassifier(strategy="stratified", random_state=seed))
        ]),
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(
                C=config.get("models", {}).get("logistic_regression", {}).get("C", 1.0),
                penalty=config.get("models", {}).get("logistic_regression", {}).get("penalty", "l2"),
                class_weight=config.get("models", {}).get("logistic_regression", {}).get("class_weight", "balanced"),
                max_iter=config.get("models", {}).get("logistic_regression", {}).get("max_iter", 3000),
                random_state=seed
            ))
        ]),
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(
                n_estimators=config.get("models", {}).get("random_forest", {}).get("n_estimators", 500),
                max_depth=config.get("models", {}).get("random_forest", {}).get("max_depth", 5),
                min_samples_leaf=config.get("models", {}).get("random_forest", {}).get("min_samples_leaf", 3),
                class_weight=config.get("models", {}).get("random_forest", {}).get("class_weight", "balanced"),
                random_state=seed
            ))
        ]),
        "xgboost": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", xgb.XGBClassifier(
                n_estimators=config.get("models", {}).get("xgboost", {}).get("n_estimators", 300),
                max_depth=config.get("models", {}).get("xgboost", {}).get("max_depth", 3),
                learning_rate=config.get("models", {}).get("xgboost", {}).get("learning_rate", 0.03),
                subsample=config.get("models", {}).get("xgboost", {}).get("subsample", 0.8),
                colsample_bytree=config.get("models", {}).get("xgboost", {}).get("colsample_bytree", 0.8),
                reg_lambda=config.get("models", {}).get("xgboost", {}).get("reg_lambda", 2),
                random_state=seed,
                eval_metric="logloss"
            ))
        ])
    }

    # Tracking arrays for Out-of-Fold (OOF) predictions
    fold_assignments = np.zeros(len(df), dtype=int)
    oof_probs = {m: np.zeros(len(df), dtype=float) for m in models}
    oof_preds = {m: np.zeros(len(df), dtype=int) for m in models}

    print("\nExecuting StratifiedGroupKFold Cross-Validation...")
    for fold, (train_idx, val_idx) in enumerate(sgkf.split(X, y, groups)):
        val_parts = np.unique(groups[val_idx])
        train_parts = np.unique(groups[train_idx])
        
        # Verify zero leakage
        overlap = set(val_parts).intersection(set(train_parts))
        assert len(overlap) == 0, f"Critical error: Participant leakage in fold {fold}: {overlap}"
        
        fold_assignments[val_idx] = fold
        
        X_train, y_train = X.iloc[train_idx], y[train_idx]
        X_val, y_val = X.iloc[val_idx], y[val_idx]

        for m_name, pipe in models.items():
            pipe.fit(X_train, y_train)
            if hasattr(pipe, "predict_proba"):
                probs = pipe.predict_proba(X_val)[:, 1]
            else:
                probs = pipe.predict(X_val).astype(float)
            oof_probs[m_name][val_idx] = probs
            oof_preds[m_name][val_idx] = (probs >= decision_threshold).astype(int)

        print(f"  Fold {fold}: {len(val_idx)} trials, {len(val_parts)} participants ({len(train_parts)} train participants)")

    # -------------------------------------------------------------------------
    # 1. Trial-Level OOF DataFrame & Fold Assignments
    # -------------------------------------------------------------------------
    df_oof = pd.DataFrame({
        "trial_index": np.arange(len(df)),
        "participant_id": df["participant_id"],
        "trial_id": df["trial_id"],
        "stimulus_name": df["stimulus_name"],
        "category": df["category"],
        "repetition": df["repetition"],
        "fold": fold_assignments,
        "y_true": y,
        "valid_sample_ratio": df["valid_sample_ratio"].round(4),
        "dummy_prob": oof_probs["dummy"].round(4),
        "dummy_pred": oof_preds["dummy"],
        "lr_prob": oof_probs["logistic_regression"].round(4),
        "lr_pred": oof_preds["logistic_regression"],
        "logistic_regression_prob": oof_probs["logistic_regression"].round(4),
        "logistic_regression_pred": oof_preds["logistic_regression"],
        "rf_prob": oof_probs["random_forest"].round(4),
        "rf_pred": oof_preds["random_forest"],
        "random_forest_prob": oof_probs["random_forest"].round(4),
        "random_forest_pred": oof_preds["random_forest"],
        "xgb_prob": oof_probs["xgboost"].round(4),
        "xgb_pred": oof_preds["xgboost"],
        "xgboost_prob": oof_probs["xgboost"].round(4),
        "xgboost_pred": oof_preds["xgboost"]
    })

    df_folds = df[["participant_id", "trial_id", "stimulus_name", "category", "repetition", "valid_sample_ratio", "familiarity_label"]].copy()
    df_folds.insert(0, "fold", fold_assignments)

    # -------------------------------------------------------------------------
    # 2. Participant-Level Aggregation (Primary Unit)
    # -------------------------------------------------------------------------
    part_records = []
    for pid, pgroup in df_oof.groupby("participant_id", sort=False):
        meta = df[df["participant_id"] == pid].iloc[0]
        n_trials = len(pgroup)
        n_guilty = int((pgroup["y_true"] == 1).sum())
        n_control = int((pgroup["y_true"] == 0).sum())
        ground_truth = 1 if n_guilty > n_control else 0
        
        prob_dummy = float(pgroup["dummy_prob"].mean())
        prob_lr = float(pgroup["lr_prob"].mean())
        prob_rf = float(pgroup["rf_prob"].mean())
        prob_xgb = float(pgroup["xgb_prob"].mean())
        
        pred_dummy = int(prob_dummy >= decision_threshold)
        pred_lr = int(prob_lr >= decision_threshold)
        pred_rf = int(prob_rf >= decision_threshold)
        pred_xgb = int(prob_xgb >= decision_threshold)
        
        part_records.append({
            "participant_id": pid,
            "assigned_fold": int(pgroup["fold"].iloc[0]),
            "gender": meta.get("gender", "Unknown"),
            "group": meta.get("group", "Unknown"),
            "calibration_accuracy_deg": round(float(meta.get("calibration_accuracy_deg", 0.0)), 3),
            "total_trials": n_trials,
            "ground_truth": ground_truth,
            "mean_valid_sample_ratio": round(float(pgroup["valid_sample_ratio"].mean()), 4),
            "dummy_prob": round(prob_dummy, 4),
            "dummy_pred": pred_dummy,
            "lr_prob": round(prob_lr, 4),
            "lr_pred": pred_lr,
            "logistic_regression_prob": round(prob_lr, 4),
            "logistic_regression_pred": pred_lr,
            "rf_prob": round(prob_rf, 4),
            "rf_pred": pred_rf,
            "random_forest_prob": round(prob_rf, 4),
            "random_forest_pred": pred_rf,
            "xgb_prob": round(prob_xgb, 4),
            "xgb_pred": pred_xgb,
            "xgboost_prob": round(prob_xgb, 4),
            "xgboost_pred": pred_xgb,
            "dummy_correct": int(pred_dummy == ground_truth),
            "lr_correct": int(pred_lr == ground_truth),
            "rf_correct": int(pred_rf == ground_truth),
            "xgb_correct": int(pred_xgb == ground_truth),
        })

    df_participants = pd.DataFrame(part_records)

    # -------------------------------------------------------------------------
    # 3. Participant-Level Benchmark Metrics & 10,000 Bootstrap CIs
    # -------------------------------------------------------------------------
    y_part_true = df_participants["ground_truth"].values
    
    part_metrics = []
    metrics_json = {
        "metadata": {
            "experiment_name": "gazeguard_fresh_baseline",
            "version": "2.0.0",
            "primary_unit": "participant",
            "n_participants": len(df_participants),
            "total_trials": len(df),
            "n_splits": n_splits,
            "bootstrap_replicates": bootstrap_reps,
            "decision_threshold": decision_threshold,
            "features_used": features,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        },
        "participant_level_results": {},
        "trial_level_results": {}
    }

    print("\nComputing Participant-Level Metrics & 10,000 Bootstrap Confidence Intervals...")
    for m_name in models.keys():
        p_probs = df_participants[f"{m_name}_prob"].values
        p_preds = df_participants[f"{m_name}_pred"].values
        
        bacc = balanced_accuracy_score(y_part_true, p_preds)
        bacc_ci = compute_participant_stratified_bootstrap_ci(
            y_part_true, p_probs,
            lambda yt, yp: balanced_accuracy_score(yt, (yp >= decision_threshold).astype(int)),
            n_replicates=bootstrap_reps, random_state=seed
        )
        
        auc = roc_auc_score(y_part_true, p_probs)
        auc_ci = compute_participant_stratified_bootstrap_ci(
            y_part_true, p_probs,
            lambda yt, yp: roc_auc_score(yt, yp),
            n_replicates=bootstrap_reps, random_state=seed
        )
        
        brier = brier_score_loss(y_part_true, p_probs)
        prec = precision_score(y_part_true, p_preds, zero_division=0)
        rec = recall_score(y_part_true, p_preds, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_part_true, p_preds).ravel()
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = f1_score(y_part_true, p_preds, zero_division=0)
        
        res_record = {
            "model": m_name,
            "unit": "participant",
            "balanced_accuracy": round(bacc, 4),
            "balanced_acc_ci_95": list(bacc_ci),
            "roc_auc": round(auc, 4),
            "roc_auc_ci_95": list(auc_ci),
            "brier_score": round(brier, 4),
            "precision": round(prec, 4),
            "recall_sensitivity": round(rec, 4),
            "specificity": round(spec, 4),
            "f1_score": round(f1, 4),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
            "sample_count": len(y_part_true)
        }
        part_metrics.append(res_record)
        metrics_json["participant_level_results"][m_name] = res_record

        print(f"  {m_name:20s} | Bal Acc: {bacc*100:5.2f}% (95% CI: {bacc_ci[0]*100:.1f}-{bacc_ci[1]*100:.1f}%) | AUC: {auc:.3f} (95% CI: {auc_ci[0]:.3f}-{auc_ci[1]:.3f})")

    # Trial-level metrics for comparison
    for m_name in models.keys():
        t_probs = df_oof[f"{m_name}_prob"].values
        t_preds = df_oof[f"{m_name}_pred"].values
        
        tbacc = balanced_accuracy_score(y, t_preds)
        tauc = roc_auc_score(y, t_probs)
        tbrier = brier_score_loss(y, t_probs)
        tprec = precision_score(y, t_preds, zero_division=0)
        trec = recall_score(y, t_preds, zero_division=0)
        ttn, tfp, tfn, ttp = confusion_matrix(y, t_preds).ravel()
        tspec = ttn / (ttn + tfp) if (ttn + tfp) > 0 else 0.0
        tf1 = f1_score(y, t_preds, zero_division=0)
        
        metrics_json["trial_level_results"][m_name] = {
            "model": m_name,
            "unit": "trial",
            "balanced_accuracy": round(tbacc, 4),
            "roc_auc": round(tauc, 4),
            "brier_score": round(tbrier, 4),
            "precision": round(tprec, 4),
            "recall": round(trec, 4),
            "specificity": round(tspec, 4),
            "f1_score": round(tf1, 4),
            "true_negatives": int(ttn),
            "false_positives": int(tfp),
            "false_negatives": int(tfn),
            "true_positives": int(ttp),
            "sample_count": len(y)
        }

    df_part_metrics = pd.DataFrame(part_metrics)

    # -------------------------------------------------------------------------
    # 4. Save Outputs to outputs/final_baseline/ and experiments/results/final_baseline/
    # -------------------------------------------------------------------------
    save_dirs = [
        os.path.join(base_dir, "outputs", "final_baseline"),
        os.path.join(base_dir, "experiments", "results", "final_baseline"),
    ]
    
    audit_data = {
        "dataset_sha256": dataset_sha256,
        "dataset_rows": actual_rows,
        "dataset_participants": actual_participants,
        "features": features,
        "n_features": len(features),
        "split_strategy": "StratifiedGroupKFold",
        "n_splits": n_splits,
        "primary_unit": "participant",
        "leakage_check_passed": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    env_data = get_environment_info()

    for s_dir in save_dirs:
        os.makedirs(s_dir, exist_ok=True)
        df_folds.to_csv(os.path.join(s_dir, "fold_assignments.csv"), index=False)
        df_oof.to_csv(os.path.join(s_dir, "oof_predictions.csv"), index=False)
        df_participants.to_csv(os.path.join(s_dir, "participant_predictions.csv"), index=False)
        df_part_metrics.to_csv(os.path.join(s_dir, "participant_metrics.csv"), index=False)
        with open(os.path.join(s_dir, "metrics.json"), "w") as f:
            json.dump(metrics_json, f, indent=2)
        with open(os.path.join(s_dir, "audit.json"), "w") as f:
            json.dump(audit_data, f, indent=2)
        with open(os.path.join(s_dir, "environment.json"), "w") as f:
            json.dump(env_data, f, indent=2)

    # Also update root outputs/ for primary consumption
    root_out = os.path.join(base_dir, "outputs")
    df_folds.to_csv(os.path.join(root_out, "fold_assignments.csv"), index=False)
    df_oof.to_csv(os.path.join(root_out, "oof_predictions.csv"), index=False)
    df_participants.to_csv(os.path.join(root_out, "participant_predictions.csv"), index=False)
    
    # Save root baseline_metrics.csv with both participant-level and trial-level clarity
    root_baseline_df = pd.DataFrame([
        {
            "model": m,
            "unit": "participant",
            "balanced_accuracy": metrics_json["participant_level_results"][m]["balanced_accuracy"],
            "balanced_acc_ci_lower_95": metrics_json["participant_level_results"][m]["balanced_acc_ci_95"][0],
            "balanced_acc_ci_upper_95": metrics_json["participant_level_results"][m]["balanced_acc_ci_95"][1],
            "roc_auc": metrics_json["participant_level_results"][m]["roc_auc"],
            "roc_auc_ci_lower_95": metrics_json["participant_level_results"][m]["roc_auc_ci_95"][0],
            "roc_auc_ci_upper_95": metrics_json["participant_level_results"][m]["roc_auc_ci_95"][1],
            "precision": metrics_json["participant_level_results"][m]["precision"],
            "recall": metrics_json["participant_level_results"][m]["recall_sensitivity"],
            "specificity": metrics_json["participant_level_results"][m]["specificity"],
            "f1_score": metrics_json["participant_level_results"][m]["f1_score"],
            "brier_score": metrics_json["participant_level_results"][m]["brier_score"],
            "sample_count": metrics_json["participant_level_results"][m]["sample_count"]
        }
        for m in models.keys()
    ])
    root_baseline_df.to_csv(os.path.join(root_out, "baseline_metrics.csv"), index=False)

    print("\n" + "=" * 75)
    print("FRESH BASELINE EXPERIMENT COMPLETED SUCCESSFULLY!")
    print(f"Results archived to: outputs/final_baseline/ and experiments/results/final_baseline/")
    print("=" * 75)

if __name__ == "__main__":
    main()
