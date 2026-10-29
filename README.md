# Quality-Aware-Personalized-Temporal-Calibration-for-Concealed-Recognition-Analysis
### GazeGuard AI: Research Platform & Interactive Scientific Benchmark

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License: CC-BY 4.0](https://img.shields.io/badge/License-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passed-emerald.svg)]()

> **RESEARCH DISCLAIMER:**  
> GazeGuard AI is an experimental scientific instrument investigating Concealed Information Test (CIT) gaze dynamics.  
> **Under NO circumstances should this system be used to label individuals as liars, deceptive, guilty, or dishonest.**  
> Eye movements reflect idiosyncratic gaze habits, cognitive salience, and visual orienting, and do NOT constitute proof of deception.

---

## 1. Project Overview & Research Contribution
GazeGuard AI investigates the following core research question:
> **Does participant-specific calibration, combined with temporal fixation analysis (0–500 ms) and tracking-quality assessment, improve the reliability of familiarity-related classification when gaze measurements are noisy?**

The framework investigates **Quality-Aware Personalized Temporal Calibration (QPTC)**:
1. **Multi-Window Temporal Slicing**: Isolates early involuntary orienting ($[0, 500\text{ ms}]$) from intermediate ($[500, 1000\text{ ms}]$) and late exploratory viewing ($[1000, 2000\text{ ms}]$).
2. **Personalized Baseline Calibration (Mode B)**: Computes participant-specific z-score normalization anchored strictly in neutral exposure trials, preventing cross-trial label leakage.
3. **Quality-Aware Abstention Engine**: Transparently rejects trials with $<60\%$ valid gaze density or high timestamp jitter, reducing classification error without excessive coverage loss.
4. **Explainable SHAP Feature Attributions**: Provides per-stimulus feature importance without making unwarranted causal claims regarding mental states.

---

## 2. Benchmark Datasets & Provenance

### Primary Real Dataset
- **Title**: Eye tracking as a Tool for deception detection with CIT
- **Persistent DOI**: [10.5281/zenodo.18525952](https://zenodo.org/records/18525952)
- **Authors**: Weronika Celniak, Dominika Słapczyńska, Beata Jarszak, Piotr Augustyniak (AGH University of Krakow & Forensic Laboratory of Police Headquarters in Katowice)
- **Publication Date**: February 8, 2026 | **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)
- **Apparatus**: Tobii Pro Fusion Desktop Eye Tracker (120–250 Hz) on 27-inch Full HD Monitor.
- **Cohort**: 39 participants (20 experimental guilty group, 19 innocent control group).

### Automated Download Notice & Synthetic Fallback
Zenodo applies automated Cloudflare bot protection (`HTTP 403 Forbidden`) on direct non-browser requests from agent/server environments.
- **To use real hardware files**: Navigate to `https://zenodo.org/records/18525952` in a browser, download `CIT Recording1.xlsx` through `CIT Recording40.xlsx`, and place them into `data/raw/`.
- **Synthetic Test Mode**: When real files are not present in `data/raw/`, GazeGuard AI automatically operates in clearly watermarked **Synthetic Test Mode**, ensuring fully reproducible software verification.

---

## 3. Quick Start & Execution Commands

### Prerequisites
- Python 3.11+
- Node.js v18+ and npm

### 1. Start the FastAPI Backend
```bash
# In project root
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 2. Start the React Frontend
```bash
cd frontend
cmd /c npm run dev
```
- Open browser at: `http://localhost:5173`

---

## 4. Automated Test Suite
To run all 19 unit and integration tests across feature extraction, personalized calibration, leakage prevention, quality abstention, and API routes:

```bash
python -m pytest backend/tests -v
```

**Results:**
- `test_features.py`: 3 passed (IVT velocity threshold detector, multi-window slicing)
- `test_quality_abstention.py`: 3 passed (sample density, missingness, jitter rejection)
- `test_calibration.py`: 3 passed (z-score computation, leakage prevention, variance safeguard)
- `test_ml_pipeline.py`: 4 passed (Dummy, Logistic Regression, Random Forest, XGBoost)
- `test_api.py`: 5 passed (health, dataset audit, consent enforcement, trial ingestion, experiment run)
- `test_synthetic_fixture.py`: 1 passed (exact mathematical proof of feature calculations)
- **Total:** **19 passed in ~15s**

---

## 5. Research Scripts & Reproducibility

### Audit Datasets
```bash
python scripts/audit_dataset.py --target auto
```

### Run Scientific Ablation Experiments
```bash
python scripts/run_experiments.py
```
Outputs complete JSON results to `experiments/results/`:
- `exp01_baselines.json`: Dummy vs LogReg vs Random Forest vs XGBoost.
- `exp02_personalization.json`: Mode A (Population) vs Mode B (Personalized QPTC) ablation.
- `exp03_temporal_windows.json`: Early window (0–500 ms) contribution ablation.
- `exp04_quality_abstention.json`: Coverage vs error rate trade-off curve.
- `exp06_robustness.json`: Tracking noise and missing sample stress tests.

### Research Jupyter Notebooks
- `notebooks/01_dataset_audit.ipynb`: Dataset inspection and schema audit.
- `notebooks/02_feature_extraction.ipynb`: I-VT algorithm and window extraction.
- `notebooks/03_baseline_models.ipynb`: Grouped cross-validation model evaluation.
- `notebooks/04_personalized_calibration.ipynb`: Personalization delta verification.
- `notebooks/05_temporal_quality_ablation.ipynb`: Temporal and abstention ablation curves.

---

## 6. Frontend Navigation (9 Dedicated Scientific Pages)
1. **Research Dashboard (`/`)**: High-level metrics, dataset audit status, live tracking-quality distributions, active provenance indicator.
2. **Consent & Participant Setup (`/consent`)**: Ethical disclosure, voluntary consent confirmation, pseudonymous identifier generation, camera test with graceful fallback, clear local data option.
3. **Calibration (`/calibration`)**: 9-point spatial calibration sequence, gaze dot feedback, spatial error vs completion rate distinction, repeat calibration option.
4. **Stimulus Experiment (`/experiment`)**: Randomized CIT presentation, 500 ms central fixation cross, 2000 ms stimulus presentation, real-time gaze recording with 0–500 ms early window indicators.
5. **Signal Analysis (`/signal`)**: Time-series plots $X(t), Y(t)$, I-VT fixation boundaries, stimulus onset markers, missing interval diagnostics.
6. **Model Comparison (`/models`)**: Logistic Regression vs Random Forest vs XGBoost vs Dummy, ROC-AUC, Balanced Accuracy, Confusion Matrix, Brier loss, 95% bootstrap confidence intervals.
7. **Explainable Report (`/report`)**: Calibrated familiarity probability (never guilt/deception!), SHAP feature attributions, quality warnings, abstention badges, export JSON and print options.
8. **Research Experiments (`/research`)**: Interactive workspace running Experiments 1, 2, 3, 4, and 6 with interactive Recharts graphs.
9. **Settings & Documentation (`/settings`)**: Temporal window lengths, quality thresholds, storage paths, and BibTeX citations for Celniak et al. (2026).

---

## 7. Forensic & Ethical Boundaries
- **No Accusations:** GazeGuard AI is an academic research instrument. It never labels individuals as deceptive, liars, or guilty.
- **No Raw Video Storage:** Raw webcam video is never recorded or stored. Processing is performed ephemerally in browser client memory.
- **Prohibited Deployments:** Employment integrity testing, criminal interrogations, border credibility screening, and disciplinary determinations are strictly prohibited.
