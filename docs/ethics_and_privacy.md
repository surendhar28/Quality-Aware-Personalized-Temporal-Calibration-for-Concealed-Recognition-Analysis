# GazeGuard AI — Ethical Governance, Privacy, and Forensic Boundaries (Revision 12)

## 1. Ethical Governance and Human-Subject Rights

GazeGuard AI is designed strictly for psychophysiological research and academic inquiry. It is not an interrogation system, polygraph replacement, or lie detector.

### Core Scientific Commitments:
1. **Voluntary Informed Consent:** No gaze estimation or stimulus presentation can be initiated until the user reviews study disclosures and provides explicit consent.
2. **Right to Withdraw:** Participants retain the right to terminate recording at any point.
3. **Non-Accusatory Terminology:** Model outputs reflect statistical differences in eye movement distributions between laboratory experimental conditions. The platform strictly prohibits labeling individuals as guilty, deceptive, untruthful, or suspicious.

---

## 2. Distinction Between Implemented Safeguards and Intended Protections

To maintain scientific integrity, researchers must distinguish between verified implemented safeguards and proposed future capabilities:

### Implemented and Verified Safeguards
| Safeguard | Implementation Status | Verification Method |
| :--- | :--- | :--- |
| **Strict Participant Grouping** | **Implemented & Verified** | `StratifiedGroupKFold` verified with zero train/test participant overlap via `scripts/verify_experiment.py`. |
| **Data Minimization in Ingestion** | **Implemented & Verified** | Raw video frames are never captured, transmitted, or stored on backend servers; only numerical sample coordinates $(x, y, t)$ and extracted features are processed. |
| **Pseudonymized Data Models** | **Implemented & Verified** | Data tables use randomized identifiers (`Participant1`, `Participant2`, etc.) with no personally identifiable information (PII) stored. |
| **Quality-Aware Rejection Logging** | **Implemented & Verified** | Trials with degraded sample coverage are explicitly tagged and evaluated via coverage-accuracy trade-off curves. |

### Intended / Proposed Safeguards (Pending Full Verification)
| Safeguard | Implementation Status | Boundary Condition |
| :--- | :--- | :--- |
| **Client-Side Biometric Redaction** | *Proposed / In Development* | Removing subtle oculomotor biometrics that could re-identify unique gaze scanning signatures. |
| **Cryptographic Consent Revocation** | *Proposed* | Automated one-click cryptographic purging of all historical feature vectors across distributed databases. |
| **Federated Calibration Aggregation** | *Proposed* | Performing multi-site personalization without pooling raw eye-tracking trajectories across research centers. |

---

## 3. High-Stakes Forensic & Real-World Prohibition Notice

> [!CAUTION]
> **STRICT FORENSIC PROHIBITION:**
> GazeGuard AI is an academic research platform. It **MUST NOT** be deployed, referenced, or utilized for:
> - Criminal interrogations, law enforcement investigations, or legal evidence of guilt.
> - Pre-employment screening or workplace integrity monitoring.
> - Border control, immigration screening, or asylum credibility determinations.
> - Academic integrity tribunals or disciplinary proceedings.
>
> **Psychophysiological Rationale:**
> Gaze movements are driven by visual saliency, stimulus novelty, cognitive load, anxiety, fatigue, and individual neurodivergence. Eye-tracking measurements do not measure honesty and cannot establish intent, deception, or consciousness of guilt.
