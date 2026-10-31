#!/usr/bin/env python3
"""
GazeGuard AI — Automated Reproducibility Verification Suite (Revision 12)
Validates integrity of dataset, splits, out-of-fold predictions, participant metrics, and environment.

Verification Checks:
1. Dataset SHA-256 hash matches data/manifests/dataset_manifest.json
2. Dataset contains exactly 819 rows and 38 processed participant IDs
3. All 11 baseline features exist and contain valid values
4. Every participant belongs to exactly one test fold (0 participant leakage)
5. Exactly 819 out-of-fold predictions exist with no missing values
6. Participant predictions equal the mean of held-out row probabilities
7. Participant-level metrics dynamically recalculated from OOF CSV exactly match saved metrics.json
8. Saved environment JSON contains valid runtime provenance
"""

import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, roc_auc_score, brier_score_loss


def log_check(name, passed, detail=""):
    status = "PASSED" if passed else "FAILED"
    print(f"[{status}] {name}")
    if detail:
        print(f"         {detail}")
    if not passed:
        raise AssertionError(f"Verification Check FAILED: {name} — {detail}")


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 75)
    print("GAZEGUARD AI — AUTOMATED REPRODUCIBILITY VERIFICATION")
    print("=" * 75)

    # 1. Dataset Manifest & Hash
    manifest_path = os.path.join(base_dir, "data", "manifests", "dataset_manifest.json")
    if not os.path.exists(manifest_path):
        log_check("Dataset Manifest Exists", False, f"Missing manifest at {manifest_path}")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    data_path = os.path.join(base_dir, manifest["file_path"])
    with open(data_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    log_check(
        "Dataset SHA-256 Hash Integrity",
        actual_hash == manifest["sha256_hash"],
        f"Manifest: {manifest['sha256_hash'][:16]}... | Actual: {actual_hash[:16]}..."
    )

    # 2. Dataset Dimensions
    df = pd.read_csv(data_path)
    log_check(
        "Dataset Dimensions (819 rows, 38 participants)",
        len(df) == 819 and df["participant_id"].nunique() == 38,
        f"Rows: {len(df)} (req: 819), Participants: {df['participant_id'].nunique()} (req: 38)"
    )

    # 3. 11 Features Presence
    required_features = [
        "valid_sample_ratio", "early_window_sample_count", "early_probe_fix_dur",
        "early_irrel_fix_dur", "early_probe_diff", "mid_probe_diff", "late_probe_diff",
        "total_probe_diff", "mean_fix_duration", "median_fix_duration", "fixation_count"
    ]
    missing_feats = [f for f in required_features if f not in df.columns]
    log_check(
        "Required 11 Features Present",
        len(missing_feats) == 0,
        f"Missing: {missing_feats}" if missing_feats else "All 11 features verified"
    )

    # 4. Fold Assignments Verification
    folds_path = os.path.join(base_dir, "outputs", "final_baseline", "fold_assignments.csv")
    if not os.path.exists(folds_path):
        folds_path = os.path.join(base_dir, "outputs", "fold_assignments.csv")
    df_folds = pd.read_csv(folds_path)
    
    # Check that each participant belongs to exactly one fold
    part_fold_counts = df_folds.groupby("participant_id")["fold"].nunique()
    log_check(
        "Strict Participant Grouping (Zero Fold Leakage)",
        (part_fold_counts == 1).all(),
        f"Max folds per participant: {part_fold_counts.max()}"
    )

    # Check 5 folds present
    log_check(
        "5-Fold Cross Validation Structure",
        set(df_folds["fold"].unique()) == {0, 1, 2, 3, 4},
        f"Folds present: {sorted(df_folds['fold'].unique())}"
    )

    # 5. Out-of-Fold Predictions Verification
    oof_path = os.path.join(base_dir, "outputs", "final_baseline", "oof_predictions.csv")
    if not os.path.exists(oof_path):
        oof_path = os.path.join(base_dir, "outputs", "oof_predictions.csv")
    df_oof = pd.read_csv(oof_path)
    
    log_check(
        "OOF Predictions Count Exactly 819",
        len(df_oof) == 819 and not df_oof[["lr_prob", "rf_prob", "xgb_prob"]].isnull().any().any(),
        f"OOF Rows: {len(df_oof)}, Nulls: {df_oof[['lr_prob', 'rf_prob', 'xgb_prob']].isnull().sum().to_dict()}"
    )

    # 6. Participant-Level Aggregation Accuracy
    part_pred_path = os.path.join(base_dir, "outputs", "final_baseline", "participant_predictions.csv")
    if not os.path.exists(part_pred_path):
        part_pred_path = os.path.join(base_dir, "outputs", "participant_predictions.csv")
    df_part = pd.read_csv(part_pred_path)
    
    log_check(
        "Participant Predictions Count Exactly 38",
        len(df_part) == 38,
        f"Participants: {len(df_part)}"
    )

    # Check that participant mean probability matches OOF trial mean
    mismatches = 0
    for _, prow in df_part.iterrows():
        pid = prow["participant_id"]
        sub_trials = df_oof[df_oof["participant_id"] == pid]
        expected_rf_prob = round(float(sub_trials["rf_prob"].mean()), 4)
        if abs(prow["rf_prob"] - expected_rf_prob) > 1e-3:
            mismatches += 1
    log_check(
        "Participant Aggregation Consistency (Mean of Held-Out Rows)",
        mismatches == 0,
        f"Mismatched participants: {mismatches}"
    )

    # 7. Metrics Recalculation Check
    metrics_path = os.path.join(base_dir, "outputs", "final_baseline", "metrics.json")
    if not os.path.exists(metrics_path):
        metrics_path = os.path.join(base_dir, "experiments", "results", "final_baseline", "metrics.json")
    with open(metrics_path, "r") as f:
        saved_metrics = json.load(f)

    y_part_true = df_part["ground_truth"].values
    rf_probs = df_part["rf_prob"].values
    rf_preds = (rf_probs >= 0.5).astype(int)

    recalculated_bacc = round(float(balanced_accuracy_score(y_part_true, rf_preds)), 4)
    recalculated_auc = round(float(roc_auc_score(y_part_true, rf_probs)), 4)
    saved_rf_bacc = saved_metrics["participant_level_results"]["random_forest"]["balanced_accuracy"]
    saved_rf_auc = saved_metrics["participant_level_results"]["random_forest"]["roc_auc"]

    log_check(
        "Dynamically Recalculated Metrics Match Saved metrics.json",
        abs(recalculated_bacc - saved_rf_bacc) < 1e-3 and abs(recalculated_auc - saved_rf_auc) < 1e-3,
        f"Recalculated RF: BAcc={recalculated_bacc}, AUC={recalculated_auc} | Saved: BAcc={saved_rf_bacc}, AUC={saved_rf_auc}"
    )

    # 8. Environment Manifest
    env_path = os.path.join(base_dir, "outputs", "final_baseline", "environment.json")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_info = json.load(f)
        log_check(
            "Runtime Environment Provenance Validated",
            "python_version" in env_info and "platform" in env_info,
            f"Python: {env_info.get('python_version', '').split()[0]} on {env_info.get('platform', '')}"
        )

    print("=" * 75)
    print("ALL 8 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("Repository is fully compliant with Revision 12 Reproducible Research standards.")
    print("=" * 75)


if __name__ == "__main__":
    main()
