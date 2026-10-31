# Quality-Aware-Personalized-Temporal-Calibration-for-Concealed-Recognition-Analysis
### GazeGuard AI: Research Platform & Interactive Scientific Benchmark (Revision 12)

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License: CC-BY 4.0](https://img.shields.io/badge/License-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Verification](https://img.shields.io/badge/Reproducibility-8%2F8%20Checks%20Passed-emerald.svg)]()

---

## Research Status and Experimental Scope

GazeGuard AI is an experimental research platform for studying eye-tracking-derived features in a Concealed Information Test (CIT) setting.

### Experimentally Evaluated

- An 819-row derived-feature table containing 38 processed participant IDs.
- Eleven numeric predictors (`valid_sample_ratio`, `early_window_sample_count`, `early_probe_fix_dur`, `early_irrel_fix_dur`, `early_probe_diff`, `mid_probe_diff`, `late_probe_diff`, `total_probe_diff`, `mean_fix_duration`, `median_fix_duration`, `fixation_count`).
- Five-fold stratified participant-grouped cross-validation (`StratifiedGroupKFold`, $k=5$, `random_state=42`).
- Logistic Regression, Random Forest (500 trees) and XGBoost (300 trees) baselines.
- Participant-level mean aggregation of out-of-fold prediction scores.
- Participant-stratified bootstrap uncertainty estimates (10,000 resamples).

### Proposed or Pending Validation

- Raw eye-tracking workbook processing and complete feature-provenance verification.
- Participant-specific baseline calibration.
- Validation-selected quality-aware abstention.
- Temporal-window ablation using the final reproducible experiment.
- Fold-specific SHAP analysis.
- Independent external validation.

### Research Disclaimer

The evaluated target is a supplied participant-condition label that remains constant within each participant. Model predictions must not be interpreted as stimulus-specific recognition, deception, guilt, intent or evidence of dishonesty. The current baseline experiment does not establish the effectiveness of the complete QPTC framework.

---

## 1. Verified Benchmark Dataset & Provenance

- **Title**: Eye tracking as a Tool for deception detection with CIT
- **Persistent DOI**: [10.5281/zenodo.18525952](https://zenodo.org/records/18525952)
- **Authors**: Weronika Celniak, Dominika Słapczyńska, Beata Jarszak, Piotr Augustyniak (AGH University of Krakow & Forensic Laboratory of Police Headquarters in Katowice)
- **Publication Date**: February 8, 2026 | **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)
- **Apparatus**: Tobii Pro Fusion Desktop Eye Tracker (120–250 Hz) on 27-inch Full HD Monitor.
- **Recording Files**: 39 workbooks (`CIT Recording1.xlsx` through `CIT Recording40.xlsx`, excluding #14).
- **Participants**: 38 biological participants (Recordings 25 and 27 both correspond to `Participant25`).
- **Canonical Feature Table**: `data/processed/zenodo_features.csv` (819 rows, SHA-256: `7a7275b274f84ce9ce5558ca1f737eb702c08e6c7bf5a08bc60aaa020bc2eb59`).

---

## 2. Benchmark Evaluation Results (Revision 12 Fresh Baseline)

Evaluated under leak-free 5-fold `StratifiedGroupKFold` cross-validation grouped strictly by `participant_id` ($N=38$ participants, 819 trials), with **10,000 participant-stratified bootstrap resamples** for 95% Confidence Intervals:

| Architecture | Balanced Accuracy [95% CI] | ROC-AUC [95% CI] | Precision | Recall | Specificity | F1 Score | Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dummy (Chance Baseline)** | 39.47% [23.7%, 55.3%] | 0.346 [0.186, 0.523] | 0.381 | 0.400 | 0.389 | 0.390 | 0.375 |
| **Logistic Regression ($L_2$)** | 65.79% [50.0%, 79.0%] | 0.709 [0.529, 0.875] | 0.696 | 0.800 | 0.611 | 0.744 | 0.222 |
| **Random Forest (500 Trees)** | **71.05%** [55.3%, 84.2%] | **0.781** [0.615, 0.920] | **0.750** | **0.750** | **0.667** | **0.750** | **0.210** |
| **XGBoost Classifier** | 65.79% [50.0%, 81.6%] | 0.704 [0.526, 0.862] | 0.727 | 0.800 | 0.611 | 0.762 | 0.246 |

*External Reference:* A 94.9% accuracy figure was reported in external literature using alternative cross-validation methods without participant grouping constraints.

---

## 3. Reproducibility & Automated Verification

### Execute the Fresh Baseline Experiment
```bash
python scripts/run_fresh_grouped_experiment.py
```

### Execute Temporal Window & Quality Abstention Ablations
```bash
python scripts/run_temporal_ablation.py
python scripts/run_quality_abstention.py
```

### Run Automated 8-Point Reproducibility Suite
```bash
python scripts/verify_experiment.py
```

All 8 verification checks must pass:
1. Dataset SHA-256 matches `data/manifests/dataset_manifest.json`
2. Exactly 819 rows and 38 processed participant IDs
3. All 11 features present and verified
4. Zero participant leakage across cross-validation folds
5. Exactly 819 out-of-fold predictions
6. Participant predictions equal the mean of held-out row probabilities
7. Dynamically recalculated metrics match saved `metrics.json`
8. Runtime environment provenance validated

---

## 4. Quick Start: Interactive Research Application

### 1. Start the FastAPI Backend
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 2. Start the React Frontend Dashboard
```bash
cd frontend
npm run dev
```
- Dashboard URL: `http://localhost:5173`

### 3. Run Backend Test Suite
```bash
python -m pytest backend/tests -v
```

---

## 5. Repository Documentation Index

- [`docs/experimental_protocol.md`](file:///e:/karthianna/docs/experimental_protocol.md): Formal analysis plan, StratifiedGroupKFold specification, and bootstrap methodology.
- [`docs/data_dictionary.md`](file:///e:/karthianna/docs/data_dictionary.md): Specification for all 11 features and trial metadata.
- [`docs/reproducibility.md`](file:///e:/karthianna/docs/reproducibility.md): Complete instructions for environment setup and experiment reproduction.
- [`docs/model_card.md`](file:///e:/karthianna/docs/model_card.md): Model performance, primary evaluation units, and limitations.
- [`docs/limitations.md`](file:///e:/karthianna/docs/limitations.md): Participant/session provenance (39 workbooks to 38 participants) and target label constraints.
- [`docs/ethics_and_privacy.md`](file:///e:/karthianna/docs/ethics_and_privacy.md): Distinguishing verified safeguards from intended protections.
- [`docs/architecture.md`](file:///e:/karthianna/docs/architecture.md): Delineation of evaluated baseline modules and proposed QPTC modules.
