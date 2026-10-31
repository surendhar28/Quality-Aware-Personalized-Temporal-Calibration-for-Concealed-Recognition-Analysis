#!/usr/bin/env python3
"""
GazeGuard AI — Reproducible Quality-Aware Abstention Suite (Revision 12)
Evaluates trade-off between trial coverage and diagnostic performance across valid gaze sample thresholds:
theta in [0.00, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90].
Uses StratifiedGroupKFold (N=38 participants, 819 trials).
Outputs saved to experiments/results/quality_abstention/ and outputs/
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    roc_auc_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    brier_score_loss,
)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "processed", "zenodo_features.csv")
    
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        sys.exit(1)
        
    df = pd.read_csv(data_path)
    total_trials = len(df)
    
    features = [
        "valid_sample_ratio", "early_window_sample_count", "early_probe_fix_dur",
        "early_irrel_fix_dur", "early_probe_diff", "mid_probe_diff", "late_probe_diff",
        "total_probe_diff", "mean_fix_duration", "median_fix_duration", "fixation_count"
    ]
    
    thresholds = [0.00, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    results = []

    print("=" * 75)
    print("RUNNING REPRODUCIBLE QUALITY ABSTENTION SUITE (Revision 12)")
    print("=" * 75)

    for th in thresholds:
        q_mask = (df["valid_sample_ratio"] >= th).values
        retained = int(q_mask.sum())
        abstained = total_trials - retained
        coverage = float(retained / total_trials)
        
        if retained < 30:
            continue
            
        df_th = df[q_mask].copy()
        X_th = df_th[features].copy()
        y_th = df_th["familiarity_label"].values
        groups_th = df_th["participant_id"].values
        
        sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        oof_probs = np.zeros(len(df_th), dtype=float)
        oof_preds = np.zeros(len(df_th), dtype=int)
        
        for tr_idx, val_idx in sgkf.split(X_th, y_th, groups_th):
            pipe = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("model", RandomForestClassifier(
                    n_estimators=500, max_depth=5, min_samples_leaf=3,
                    class_weight="balanced", random_state=42
                ))
            ])
            pipe.fit(X_th.iloc[tr_idx], y_th[tr_idx])
            probs = pipe.predict_proba(X_th.iloc[val_idx])[:, 1]
            oof_probs[val_idx] = probs
            oof_preds[val_idx] = (probs >= 0.5).astype(int)

        # Participant aggregation
        part_true = []
        part_probs = []
        for pid in df_th["participant_id"].unique():
            mask = df_th["participant_id"] == pid
            part_true.append(y_th[mask][0])
            part_probs.append(oof_probs[mask].mean())
            
        y_pt = np.array(part_true)
        y_pp = np.array(part_probs)
        y_pred = (y_pp >= 0.5).astype(int)

        bacc_part = balanced_accuracy_score(y_pt, y_pred) if len(np.unique(y_pt)) > 1 else 0.5
        auc_part = roc_auc_score(y_pt, y_pp) if len(np.unique(y_pt)) > 1 else 0.5
        
        tbacc = balanced_accuracy_score(y_th, oof_preds)
        tauc = roc_auc_score(y_th, oof_probs)
        prec = precision_score(y_th, oof_preds, zero_division=0)
        rec = recall_score(y_th, oof_preds, zero_division=0)
        f1 = f1_score(y_th, oof_preds, zero_division=0)

        results.append({
            "threshold_theta": round(th, 2),
            "coverage_ratio": round(coverage, 4),
            "coverage_pct": round(coverage * 100, 2),
            "retained_trials": retained,
            "abstained_trials": abstained,
            "retained_participants": int(df_th["participant_id"].nunique()),
            "participant_balanced_accuracy": round(bacc_part, 4),
            "participant_roc_auc": round(auc_part, 4),
            "trial_balanced_accuracy": round(tbacc, 4),
            "trial_balanced_accuracy_pct": round(tbacc * 100, 2),
            "trial_roc_auc": round(tauc, 4),
            "error_rate": round(1.0 - tbacc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4)
        })

        print(f"  Theta >= {th:.2f} | Coverage: {coverage*100:5.1f}% ({retained}/{total_trials}) | Part Bal Acc: {bacc_part*100:5.2f}% | Trial Bal Acc: {tbacc*100:5.2f}%")

    df_res = pd.DataFrame(results)

    save_dirs = [
        os.path.join(base_dir, "experiments", "results", "quality_abstention"),
        os.path.join(base_dir, "outputs")
    ]
    for d in save_dirs:
        os.makedirs(d, exist_ok=True)
        df_res.to_csv(os.path.join(d, "quality_abstention_results.csv"), index=False)

    with open(os.path.join(base_dir, "experiments", "results", "quality_abstention", "quality_abstention_metrics.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 75)
    print("QUALITY ABSTENTION SUITE COMPLETED AND SAVED!")
    print("=" * 75)


if __name__ == "__main__":
    main()
