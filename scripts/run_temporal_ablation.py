#!/usr/bin/env python3
"""
GazeGuard AI — Reproducible Temporal Window Ablation Suite (Revision 12)
Evaluates diagnostic contribution across time windows using StratifiedGroupKFold (N=38 participants).
Windows:
1. Early Orienting (0-500 ms)
2. Intermediate Appraisal (500-1000 ms)
3. Late Exploration (1000-2000 ms)
4. Full Trial Viewing (0-7500 ms)
5. Multi-Temporal Baseline (All 11 features)
Outputs saved to experiments/results/temporal_ablation/ and outputs/
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
    y = df["familiarity_label"].values
    groups = df["participant_id"].values
    
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    
    windows = [
        (
            "Early Window (0-500 ms)",
            "0-500 ms",
            ["early_probe_diff", "early_probe_fix_dur", "early_irrel_fix_dur", "early_window_sample_count"]
        ),
        (
            "Mid Window (500-1000 ms)",
            "500-1000 ms",
            ["mid_probe_diff"]
        ),
        (
            "Late Window (1000-2000 ms)",
            "1000-2000 ms",
            ["late_probe_diff"]
        ),
        (
            "Full Trial Exploration (0-7500 ms)",
            "0-7500 ms",
            ["total_probe_diff", "mean_fix_duration", "median_fix_duration", "fixation_count"]
        ),
        (
            "Multi-Temporal Baseline (All 11 Features)",
            "All Windows",
            [
                "valid_sample_ratio", "early_window_sample_count", "early_probe_fix_dur",
                "early_irrel_fix_dur", "early_probe_diff", "mid_probe_diff", "late_probe_diff",
                "total_probe_diff", "mean_fix_duration", "median_fix_duration", "fixation_count"
            ]
        ),
    ]

    print("=" * 75)
    print("RUNNING REPRODUCIBLE TEMPORAL WINDOW ABLATION (Revision 12)")
    print("=" * 75)

    results = []

    for name, t_range, feats in windows:
        X_sub = df[feats].copy()
        oof_probs = np.zeros(len(df), dtype=float)
        oof_preds = np.zeros(len(df), dtype=int)
        
        for tr_idx, val_idx in sgkf.split(X_sub, y, groups):
            pipe = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("model", RandomForestClassifier(
                    n_estimators=500, max_depth=5, min_samples_leaf=3,
                    class_weight="balanced", random_state=42
                ))
            ])
            pipe.fit(X_sub.iloc[tr_idx], y[tr_idx])
            probs = pipe.predict_proba(X_sub.iloc[val_idx])[:, 1]
            oof_probs[val_idx] = probs
            oof_preds[val_idx] = (probs >= 0.5).astype(int)

        # Participant-level aggregation
        part_true = []
        part_probs = []
        for pid in df["participant_id"].unique():
            mask = df["participant_id"] == pid
            part_true.append(y[mask][0])
            part_probs.append(oof_probs[mask].mean())
            
        y_pt = np.array(part_true)
        y_pp = np.array(part_probs)
        y_pred = (y_pp >= 0.5).astype(int)

        bacc_part = balanced_accuracy_score(y_pt, y_pred)
        auc_part = roc_auc_score(y_pt, y_pp)
        brier_part = brier_score_loss(y_pt, y_pp)
        prec = precision_score(y_pt, y_pred, zero_division=0)
        rec = recall_score(y_pt, y_pred, zero_division=0)
        f1 = f1_score(y_pt, y_pred, zero_division=0)

        # Trial-level metrics
        tbacc = balanced_accuracy_score(y, oof_preds)
        tauc = roc_auc_score(y, oof_probs)

        results.append({
            "window_name": name,
            "temporal_range_ms": t_range,
            "features_included": ", ".join(feats),
            "n_features": len(feats),
            "participant_balanced_accuracy": round(bacc_part, 4),
            "participant_balanced_accuracy_pct": round(bacc_part * 100, 2),
            "participant_roc_auc": round(auc_part, 4),
            "participant_precision": round(prec, 4),
            "participant_recall": round(rec, 4),
            "participant_f1_score": round(f1, 4),
            "participant_brier_score": round(brier_part, 4),
            "trial_balanced_accuracy": round(tbacc, 4),
            "trial_roc_auc": round(tauc, 4),
            "sample_participants": len(y_pt)
        })

        print(f"  {name:38s} | Part Bal Acc: {bacc_part*100:5.2f}% | Part AUC: {auc_part:.3f} | Trial Bal Acc: {tbacc*100:5.2f}%")

    df_res = pd.DataFrame(results)

    save_dirs = [
        os.path.join(base_dir, "experiments", "results", "temporal_ablation"),
        os.path.join(base_dir, "outputs")
    ]
    for d in save_dirs:
        os.makedirs(d, exist_ok=True)
        df_res.to_csv(os.path.join(d, "temporal_ablation_results.csv"), index=False)

    with open(os.path.join(base_dir, "experiments", "results", "temporal_ablation", "temporal_ablation_metrics.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 75)
    print("TEMPORAL ABLATION COMPLETED AND SAVED!")
    print("=" * 75)


if __name__ == "__main__":
    main()
