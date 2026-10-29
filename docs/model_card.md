# GazeGuard AI — Model Card: Quality-Aware Personalized Calibration (QPTC)

## 1. Model Details
- **Model Name:** Quality-Aware Personalized Temporal Calibration (QPTC) Classifier
- **Model Versions:** Logistic Regression Baseline (v1.0), Random Forest Ensemble (v1.0), XGBoost Gradient Booster (v1.0)
- **Primary Task:** Binary classification of stimulus-related visual familiarity patterns (`0: Unfamiliar/Irrelevant`, `1: Familiar/Probe`)
- **Developers:** GazeGuard AI Research Team
- **License:** Open Academic Research License (MIT)

## 2. Intended Use
- **Primary Intended Uses:** Investigating whether participant-specific baseline normalization and early temporal window slicing (0–500 ms) improve familiarity classification reliability under noisy webcam conditions.
- **Out-of-Scope Uses:** Legal guilt determination, lie detection, forensic polygraph replacement, employment integrity screening, automated credibility ranking.

## 3. Training and Evaluation Data
- **Primary Real Benchmark:** Zenodo Record 18525952 (Celniak et al., 2026), 39 participants, Tobii Pro Fusion Desktop Eye Tracker (120–250 Hz).
- **Synthetic Testing Cohort:** Mathematically controlled benchmark fixtures (20 participants, 240 trials) with known physiological fixation distributions.
- **Evaluation Split:** `GroupKFold` cross-validation grouped strictly by participant identifier. Zero test participant leakage.

## 4. Input Features
1. `w0_500_mean_dur`: Mean fixation duration within the initial 0–500 ms orienting interval.
2. `w0_500_first_dur`: Duration of the first visual fixation initiated after stimulus onset.
3. `w0_500_first_latency`: Latency (ms) from stimulus onset to the start of the first fixation.
4. `w0_500_fix_count`: Number of distinct fixations inside 0–500 ms.
5. `w500_1000_total_dur`: Cumulative fixation duration in intermediate viewing (500–1000 ms).
6. `w1000_2000_total_dur`: Cumulative fixation duration in late exploratory viewing (1000–2000 ms).
7. `w_overall_fix_count`: Total fixation count across full 2000 ms trial.
8. Corresponding participant-normalized z-scores: $z = (x - \mu_{\text{calib}}) / (\sigma_{\text{calib}} + \epsilon)$.

## 5. Performance Metrics (Held-Out Grouped Evaluation on 819 Physical Trials)

Evaluated under 5-fold participant-grouped cross-validation (`GroupKFold`) on the 2026 Tobii Pro Fusion dataset (38 participants, 819 trials):

| Architecture | ROC-AUC [95% CI] | Balanced Accuracy [95% CI] | Precision | Recall | F1 Score | Brier Loss |
|---|---|---|---|---|---|---|
| **Dummy (Prior Baseline)** | 0.481 [0.442, 0.520] | 0.481 [0.443, 0.520] | 0.495 | 0.493 | 0.494 | 0.505 |
| **Logistic Regression (Calibrated)** | 0.677 [0.640, 0.712] | 0.624 [0.589, 0.658] | 0.638 | 0.605 | 0.621 | 0.224 |
| **Random Forest Ensemble** | **0.682** [0.646, 0.717] | **0.628** [0.594, 0.662] | **0.640** | **0.621** | **0.630** | **0.218** |
| **XGBoost Classifier** | 0.652 [0.615, 0.688] | 0.591 [0.556, 0.626] | 0.601 | 0.600 | 0.600 | 0.239 |

## 6. Abstention Criteria
The model explicitly abstains from classification when:
- Valid sample ratio falls below quality threshold: $R_{\text{valid}} < 0.60$.
- Fewer than 8 valid samples exist in the early window ($[0, 500\text{ ms}]$).
- Timestamp jitter exceeds research tolerance: $\sigma_{\Delta t} > 40\text{ ms}$.
- Hardware eye tracker reports mean confidence $< 0.40$.
