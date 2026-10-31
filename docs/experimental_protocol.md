# GazeGuard AI — Experimental Protocol and Scientific Analysis Plan (Revision 12)

## 1. Research Question and Hypotheses

**Primary Research Question:**
Can eye-tracking-derived temporal fixation features reliably distinguish participant familiarity in a Concealed Information Test (CIT) paradigm under strict, leak-free participant-grouped cross-validation?

### Hypotheses & Research Scope:
- **$H_1$ (Temporal Window Contribution):** Fixation duration differences between probe and irrelevant stimuli vary systematically across early ($0–500\text{ ms}$), intermediate ($500–1000\text{ ms}$), and late exploration ($1000–2000\text{ ms}$) windows.
- **$H_2$ (Personalized Calibration — Proposed / Pending Validation):** Participant-specific z-score baseline normalization is hypothesized to stabilize individual baseline variance, but requires empirical validation against sufficiently powered neutral calibration trials.
- **$H_3$ (Quality-Aware Abstention — Proposed / Pending Validation):** Discarding trials below a valid gaze sample threshold is hypothesized to reduce classification error on retained trials while preserving acceptable coverage ($>90\%$).

---

## 2. Dataset and Primary Evaluation Unit

- **Physical Benchmark Dataset:** Zenodo Record 18525952 (Tobii Pro Fusion, 250 Hz, 3-screen CIT paradigm).
- **Sample Size:** 819 trials across 38 processed biological participants (20 guilty / familiar, 18 innocent / control).
- **Target Variable:** `familiarity_label` (Binary: 1 = Guilty / Familiar condition, 0 = Innocent / Control condition).
  > **Note on Ground Truth:** The ground-truth label reflects the participant's assignment in the mock-crime study. It is constant across all trials for a given participant and reflects condition-level familiarity rather than stimulus-level recognition.
- **Primary Unit of Evaluation:** **Participant**. Model probabilities are generated out-of-fold for every trial, and predictions are aggregated per participant using the mean of held-out row probabilities:
  $$\bar{p}_i = \frac{1}{M_i} \sum_{j=1}^{M_i} \hat{p}_{i,j}$$
  The binary participant-level decision is assigned at $\bar{p}_i \ge 0.50$.

---

## 3. Evaluated Predictors (11 Features)

| Feature Name | Domain / Window | Description |
| :--- | :--- | :--- |
| `valid_sample_ratio` | Signal Quality | Ratio of valid eye-tracker gaze samples over trial duration |
| `early_window_sample_count` | 0–500 ms Quality | Number of recorded samples during the initial 500 ms window |
| `early_probe_fix_dur` | 0–500 ms | Total fixation duration on the probe stimulus during initial 500 ms (ms) |
| `early_irrel_fix_dur` | 0–500 ms | Mean fixation duration on irrelevant stimuli during initial 500 ms (ms) |
| `early_probe_diff` | 0–500 ms | Probe fixation duration minus irrelevant fixation duration (ms) |
| `mid_probe_diff` | 500–1000 ms | Intermediate appraisal dwell difference (Probe minus Irrelevant) (ms) |
| `late_probe_diff` | 1000–2000 ms | Late visual exploration dwell difference (Probe minus Irrelevant) (ms) |
| `total_probe_diff` | 0–7500 ms | Full trial dwell difference across complete stimulus presentation (ms) |
| `mean_fix_duration` | Trial Aggregate | Mean duration across all parsed fixations in trial (ms) |
| `median_fix_duration` | Trial Aggregate | Median duration across all parsed fixations in trial (ms) |
| `fixation_count` | Trial Aggregate | Total number of discrete fixation events parsed in trial |

---

## 4. Cross-Validation and Model Training Protocol

- **Validation Strategy:** `StratifiedGroupKFold` ($k=5$, `shuffle=True`, `random_state=42`).
  - **Group Variable:** `participant_id`.
  - **Stratification Variable:** `familiarity_label`.
  - **Leakage Constraint:** Zero overlap between training and testing participant IDs ($\text{Train} \cap \text{Test} = \emptyset$). Every participant appears in exactly one test fold.
- **Preprocessing:**
  - Imputation: Median imputation fitted strictly within the outer training fold.
  - Scaling: `StandardScaler` applied strictly within the outer training fold (used for Logistic Regression only; tree models operate directly on unscaled features).
  - No probability calibration (`CalibratedClassifierCV` removed to prevent unstratified internal splitting).
- **Evaluated Baseline Models:**
  1. **Dummy Classifier:** Stratified chance baseline (`strategy="stratified"`).
  2. **Logistic Regression:** $L_2$ penalty, $C=1.0$, `class_weight="balanced"`, `max_iter=3000`.
  3. **Random Forest Classifier:** 500 estimators, maximum depth 5, `min_samples_leaf=3`, `class_weight="balanced"`.
  4. **XGBoost Classifier:** 300 estimators, maximum depth 3, learning rate 0.03, subsample 0.8, colsample_bytree 0.8, $L_2$ regularization $\lambda=2$.

---

## 5. Statistical Uncertainty and Significance

- **Confidence Intervals:** 10,000 participant-stratified bootstrap resamples. Control and guilty participant pools are resampled with replacement separately to preserve empirical class balance across all replicates.
- **Reported Metrics:**
  - Balanced Accuracy (Primary metric for balanced class representation)
  - ROC-AUC (Area Under the Receiver Operating Characteristic Curve)
  - Brier Score Loss (Calibration and probability error)
  - Precision, Recall (Sensitivity), Specificity, and F1-Score
  - Out-of-Fold Confusion Matrices (True Negatives, False Positives, False Negatives, True Positives)
