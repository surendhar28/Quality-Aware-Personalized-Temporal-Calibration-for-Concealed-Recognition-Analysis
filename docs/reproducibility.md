# GazeGuard AI — Reproducibility Guide & Verification Workflow (Revision 12)

This document provides complete instructions for independently replicating the GazeGuard AI physical benchmark experiments, verifying data integrity, executing 5-fold cross-validation, and regenerating paper figures.

---

## 1. System Requirements & Environment Setup

- **Python Version:** 3.10 or 3.11 (Tested on Python 3.11.9)
- **Dependencies:** Exact pinned package versions are provided in `requirements-lock.txt`.

To install dependencies in a clean virtual environment:
```bash
python -m venv env
# Windows:
.\env\Scripts\activate
# Linux/macOS:
source env/bin/activate

pip install -r requirements-lock.txt
```

---

## 2. Dataset Provenance & Hash Verification

The physical eye-tracking benchmark dataset is hosted on Zenodo:
- **DOI:** `10.5281/zenodo.18525952`
- **Location:** `data/processed/zenodo_features.csv`
- **Expected Dimensions:** Exactly 819 rows, 23 columns, 38 unique participants.
- **Expected SHA-256 Hash:** `7a7275b274f84ce9ce5558ca1f737eb702c08e6c7bf5a08bc60aaa020bc2eb59`

Verify dataset integrity:
```bash
python scripts/verify_experiment.py
```

---

## 3. Step-by-Step Experiment Execution

### Step 1: Run Authoritative Fresh Baseline Experiment
Executes 5-fold `StratifiedGroupKFold` across 38 biological participants using the 11 baseline predictors.
Computes both trial-level and participant-level aggregated out-of-fold metrics along with 10,000 participant-stratified bootstrap confidence intervals.

```bash
python scripts/run_fresh_grouped_experiment.py
```

**Artifacts Generated:**
- `outputs/final_baseline/fold_assignments.csv`
- `outputs/final_baseline/oof_predictions.csv`
- `outputs/final_baseline/participant_predictions.csv`
- `outputs/final_baseline/participant_metrics.csv`
- `outputs/final_baseline/metrics.json`
- `outputs/final_baseline/audit.json`
- `outputs/final_baseline/environment.json`

### Step 2: Run Temporal Window Ablation
Evaluates diagnostic contributions across early ($0–500\text{ ms}$), mid ($500–1000\text{ ms}$), late ($1000–2000\text{ ms}$), and full exploration ($0–7500\text{ ms}$) windows.

```bash
python scripts/run_temporal_ablation.py
```

**Artifacts Generated:**
- `outputs/temporal_ablation_results.csv`
- `experiments/results/temporal_ablation/temporal_ablation_results.csv`
- `experiments/results/temporal_ablation/temporal_ablation_metrics.json`

### Step 3: Run Quality-Aware Abstention Trade-off
Measures trial coverage vs. balanced accuracy across valid gaze sample thresholds $\theta \in [0.00, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]$.

```bash
python scripts/run_quality_abstention.py
```

**Artifacts Generated:**
- `outputs/quality_abstention_results.csv`
- `experiments/results/quality_abstention/quality_abstention_results.csv`
- `experiments/results/quality_abstention/quality_abstention_metrics.json`

### Step 4: Run Automated Verification Suite
Validates all 8 reproducibility criteria (hashes, dimensions, fold grouping, zero test leakage, OOF prediction counts, participant probability aggregation, recalculated metrics match).

```bash
python scripts/verify_experiment.py
```

---

## 4. Directory Layout for Experiments and Outputs

```
data/
  manifests/
    dataset_manifest.json          # Dataset hash and schema manifest
  processed/
    zenodo_features.csv            # Canonical 819-row derived feature table

experiments/
  config.yaml                      # Unified configuration (StratifiedGroupKFold, 11 features)
  results/
    final_baseline/                # Fresh baseline results and environment metadata
    temporal_ablation/             # Temporal window evaluation metrics
    quality_abstention/            # Abstention trade-off curve metrics
    personalization/               # Proposed QPTC normalization documentation

outputs/
  final_baseline/                  # Official reproducible release outputs
    fold_assignments.csv
    oof_predictions.csv
    participant_predictions.csv
    participant_metrics.csv
    metrics.json
    audit.json
    environment.json
  historical_revision11/           # Archived previous 7-feature outputs (labeled historical)
  baseline_metrics.csv             # Convenience symlink/copy of fresh metrics
  oof_predictions.csv              # Convenience symlink/copy of fresh OOF predictions
  fold_assignments.csv             # Convenience symlink/copy of fresh fold assignments
  participant_predictions.csv      # Convenience symlink/copy of fresh participant predictions
  temporal_ablation_results.csv    # Fresh temporal ablation results
  quality_abstention_results.csv   # Fresh quality abstention results
```
