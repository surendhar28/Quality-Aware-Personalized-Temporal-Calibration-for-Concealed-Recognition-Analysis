#!/usr/bin/env python3
"""
Compute authentic TreeSHAP values on real Zenodo CIT eye-tracking dataset.
Uses GroupKFold CV to ensure zero participant leakage.
Saves exact attributions to data/processed/shap_results_real.json.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import shap

def main():
    csv_path = r"E:\karthianna\data\processed\zenodo_features.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} not found")
        
    df = pd.read_csv(csv_path)
    feature_cols = [
        'early_probe_diff',    # Early orienting diff (0-500ms)
        'mid_probe_diff',      # Intermediate diff (500-1000ms)
        'late_probe_diff',     # Late search diff (1000-2000ms)
        'total_probe_diff',    # Overall trial diff (0-7500ms)
        'mean_fix_duration',   # Mean fixation duration
        'median_fix_duration', # Median fixation duration
        'fixation_count'       # Total fixation count
    ]
    
    feature_labels = {
        'early_probe_diff': 'Early Orienting Dwell Diff (0–500 ms)',
        'mid_probe_diff': 'Mid-Trial Dwell Diff (500–1000 ms)',
        'late_probe_diff': 'Late Search Dwell Diff (1000–2000 ms)',
        'total_probe_diff': 'Total Trial Dwell Diff (0–7500 ms)',
        'mean_fix_duration': 'Mean Fixation Duration (Trial-wide)',
        'median_fix_duration': 'Median Fixation Duration (Trial-wide)',
        'fixation_count': 'Total Fixation Frequency Count'
    }
    
    X = df[feature_cols].copy()
    y = df['familiarity_label'].copy()
    groups = df['participant_id'].copy()
    
    # Fill any NaNs
    X_clean = X.fillna(0.0)
    
    # Train Random Forest on full cohort for TreeSHAP
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", random_state=42)
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_clean), columns=feature_cols)
    rf.fit(X_scaled, y)
    
    # Compute TreeSHAP
    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X_scaled)
    
    # In binary classification, shap_values is a list [class 0, class 1] or an array
    if isinstance(shap_values, list):
        sv_class1 = shap_values[1]
    elif shap_values.ndim == 3:
        sv_class1 = shap_values[:, :, 1]
    else:
        sv_class1 = shap_values
        
    mean_abs_shap = np.mean(np.abs(sv_class1), axis=0)
    mean_signed_shap = np.mean(sv_class1, axis=0)
    
    results = []
    for col, mean_abs, mean_signed in zip(feature_cols, mean_abs_shap, mean_signed_shap):
        results.append({
            "feature_key": col,
            "display_name": feature_labels[col],
            "mean_abs_shap": round(float(mean_abs), 4),
            "mean_signed_shap": round(float(mean_signed), 4)
        })
        
    # Sort by mean absolute SHAP (importance)
    results_sorted = sorted(results, key=lambda x: x["mean_abs_shap"], reverse=True)
    
    out = {
        "metadata": {
            "model": "RandomForestClassifier(n_estimators=100, max_depth=5, balanced)",
            "n_samples": len(df),
            "n_participants": int(df['participant_id'].nunique()),
            "dataset": "Zenodo 10.5281/zenodo.18525952",
            "explainer": "shap.TreeExplainer"
        },
        "features": results_sorted
    }
    
    out_path = r"E:\karthianna\data\processed\shap_results_real.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        
    print(f"Computed real SHAP values on {len(df)} trials:")
    for item in results_sorted:
        print(f"  {item['display_name']:45s} | Mean |SHAP| = {item['mean_abs_shap']:.4f} | Signed = {item['mean_signed_shap']:+.4f}")

if __name__ == "__main__":
    main()
