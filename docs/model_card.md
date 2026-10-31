# GazeGuard AI — Model Card: Fresh Baseline Experiment (Revision 12)

## 1. Model Details
- **Model Name:** GazeGuard AI Baseline Models
- **Model Versions:** 
  - Dummy Classifier (Stratified Chance Baseline)
  - Logistic Regression ($L_2$ Regularized, `class_weight="balanced"`, `max_iter=3000`)
  - Random Forest Classifier (500 Estimators, Depth 5, `min_samples_leaf=3`, `class_weight="balanced"`)
  - XGBoost Classifier (300 Estimators, Depth 3, Learning Rate 0.03, Subsample 0.8, Colsample 0.8, $\lambda=2$)
- **Task:** Binary classification of participant familiarity condition in a Concealed Information Test paradigm (`0: Innocent/Control`, `1: Guilty/Familiar`).
- **Developers:** GazeGuard AI Research Team
- **License:** Open Academic Research License (MIT)

---

## 2. Intended Use and Scope Boundaries

- **Primary Intended Use:** Academic investigation of whether eye-tracking-derived temporal fixation features reflect participant familiarity in a mock-crime CIT setting under participant-stratified cross-validation.
- **Out-of-Scope and Prohibited Uses:** 
  - Forensic credibility assessment or lie detection in legal, judicial, or law enforcement proceedings.
  - Automated polygraph replacement or employee pre-employment integrity screening.
  - Inferring deceit, guilt, psychological intent, or dishonesty.

---

## 3. Training and Evaluation Data

- **Primary Physical Benchmark:** Zenodo Record 18525952 (Celniak et al., 2026), physical Tobii Pro Fusion Desktop Eye Tracker (250 Hz).
- **Cohort Size:** 38 processed biological participants across 39 recording workbooks (819 trials total).
- **Validation Strategy:** `StratifiedGroupKFold` ($k=5$, `shuffle=True`, `random_state=42`) grouped strictly by `participant_id`. Zero training/test participant overlap.
- **Primary Evaluation Unit:** Participant ($N=38$), aggregated via the mean of held-out row probabilities. Decision threshold = 0.50.

---

## 4. Evaluated Features (11 Predictors)

1. `valid_sample_ratio`: Ratio of valid tracker gaze samples.
2. `early_window_sample_count`: Acquired sample count in first 500 ms.
3. `early_probe_fix_dur`: Probe fixation duration in 0–500 ms (ms).
4. `early_irrel_fix_dur`: Mean irrelevant fixation duration in 0–500 ms (ms).
5. `early_probe_diff`: Probe minus irrelevant dwell difference in 0–500 ms (ms).
6. `mid_probe_diff`: Probe minus irrelevant dwell difference in 500–1000 ms (ms).
7. `late_probe_diff`: Probe minus irrelevant dwell difference in 1000–2000 ms (ms).
8. `total_probe_diff`: Full trial probe minus irrelevant dwell difference (0–7500 ms) (ms).
9. `mean_fix_duration`: Mean duration of parsed fixations in trial (ms).
10. `median_fix_duration`: Median duration of parsed fixations in trial (ms).
11. `fixation_count`: Total parsed fixation events in trial.

---

## 5. Performance Metrics (Participant-Level Primary Unit, $N=38$)

Metrics evaluated on held-out participant predictions with **10,000 participant-stratified bootstrap replicates** for 95% Confidence Intervals:

| Architecture | Balanced Accuracy [95% CI] | ROC-AUC [95% CI] | Precision | Recall | Specificity | F1 Score | Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dummy (Chance Baseline)** | 39.47% [23.7%, 55.3%] | 0.346 [0.186, 0.523] | 0.381 | 0.400 | 0.389 | 0.390 | 0.375 |
| **Logistic Regression ($L_2$)** | 65.79% [50.0%, 79.0%] | 0.709 [0.529, 0.875] | 0.696 | 0.800 | 0.611 | 0.744 | 0.222 |
| **Random Forest (500 Trees)** | **71.05%** [55.3%, 84.2%] | **0.781** [0.615, 0.920] | **0.750** | **0.750** | **0.667** | **0.750** | **0.210** |
| **XGBoost Classifier** | 65.79% [50.0%, 81.6%] | 0.704 [0.526, 0.862] | 0.727 | 0.800 | 0.611 | 0.762 | 0.246 |

*Trial-level metrics across all 819 individual rows:*
- Random Forest Trial Balanced Accuracy: 62.46%, Trial ROC-AUC: 0.672.
- Logistic Regression Trial Balanced Accuracy: 62.13%, Trial ROC-AUC: 0.671.
- XGBoost Trial Balanced Accuracy: 60.18%, Trial ROC-AUC: 0.649.

---

## 6. Research Disclaimer & Limitations

The target variable `familiarity_label` is an experimental condition assignment that remains constant within each participant. Predictions reflect cross-participant statistical differences on this laboratory dataset and do not establish deception detection or the efficacy of the proposed QPTC personalization framework.
