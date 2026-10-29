# GazeGuard AI — Experimental Protocol and Scientific Analysis Plan

## 1. Research Question and Hypotheses

**Primary Research Question:**
Does participant-specific calibration, combined with early temporal fixation analysis (0–500 ms) and tracking-quality assessment, improve the reliability of familiarity-related classification when gaze measurements are noisy?

### Formal Hypotheses:
- **$H_1$ (Early Temporal Window Hypothesis):** Fixation duration divergence between familiar (probe) and unfamiliar (irrelevant) stimuli is most pronounced in the initial 0–500 ms window following stimulus onset, reflecting automatic visual orienting.
- **$H_2$ (Personalized Baseline Normalization):** Normalizing fixation duration against participant-specific baseline statistics ($\text{Mode B}$) reduces inter-individual idiosyncratic variance and improves cross-participant generalization compared to raw population features ($\text{Mode A}$).
- **$H_3$ (Quality-Aware Abstention):** Systematically rejecting trials that fail minimum sampling density and jitter thresholds lowers the classification error rate among accepted predictions without excessive coverage loss.

## 2. Experimental Procedure

```mermaid
sequenceDiagram
    participant Participant
    participant Browser as Browser Client
    participant API as GazeGuard Backend
    participant DB as SQLite Storage

    Participant->>Browser: 1. Review Information Sheet & Provide Consent
    Browser->>API: POST /api/sessions (Pseudonym, Consent flags)
    API-->>Browser: Session ID Generated

    Participant->>Browser: 2. 9-Point Spatial Calibration Sequence
    Browser->>API: POST /api/calibration (Spatial Targets & Drift)
    API-->>Browser: Calibration Status (Acceptable / Repeat Recommended)

    loop CIT Stimulus Battery (6 - 12 Trials)
        Browser->>Participant: Display Fixation Cross '+' (500 ms)
        Browser->>Participant: Present Visual Stimulus (2000 ms)
        Browser->>Browser: Sample Gaze Coordinates (60 Hz)
        Browser->>API: POST /api/trials (Gaze Samples & Timestamp Stream)
        API->>API: Assess Quality & Extract Multi-Window Features
        API->>API: Run Quality-Aware Inference (Predict / Abstain)
        API->>DB: Store Trial Record & Feature Vector
    end

    Browser->>API: GET /api/reports/{session_id}
    API-->>Browser: Return Explainable Scientific Report with SHAP
```

## 3. Machine Learning Evaluation Protocol
- **Cross-Validation Split:** `GroupKFold` ($k=5$) partitioned strictly by `participant_id`. No participant's trials appear simultaneously in both training and test sets.
- **Evaluation Metrics:**
  - ROC-AUC
  - Balanced Accuracy
  - Precision, Recall, F1 Score
  - Brier Score Loss
  - 95% Bootstrap Confidence Intervals (500 resamples)
- **Coverage vs. Error Trade-off:** Evaluated across quality thresholds $\theta \in [0.30, 0.85]$.
