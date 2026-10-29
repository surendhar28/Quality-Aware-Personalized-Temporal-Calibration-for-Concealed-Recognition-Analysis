# GazeGuard AI — Ethical Governance, Privacy, and Forensic Boundaries

## 1. Ethical Governance and Human-Subject Rights

GazeGuard AI is designed strictly in accordance with ethical guidelines for psychophysiological research and digital human-subject experiments.

### Core Ethical Commitments:
1. **Voluntary Informed Consent:** No eye tracking, gaze estimation, or experimental presentation can be initiated until the participant reviews the information disclosure and explicitly confirms voluntary consent.
2. **Right to Terminate and Withdraw:** Participants retain the right to terminate recording at any point during calibration or stimulus presentation. A dedicated button clears locally stored session data immediately.
3. **Strict Non-Accusatory Classification:** The model predicts **experimental familiarity patterns under laboratory CIT conditions**. The application strictly prohibits labeling any individual as a liar, guilty, deceptive, untruthful, or suspicious based on eye movements.

## 2. Privacy and Data Minimization Architecture

### 2.1 Video Stream Minimization
- **Raw Webcam Video is NEVER Stored or Transmitted:** Gaze estimation models (e.g., WebGazer.js) process camera frames in ephemeral client-side memory.
- Only derived numerical coordinate samples $(x_i, y_i)$ and millisecond timestamps $(t_i)$ are sent to the backend.

### 2.2 Pseudonymization
- All experimental sessions are registered under random pseudonymous codes (e.g., `SUB_4092`).
- Real names, email addresses, IP addresses, and identifying demographic variables are never collected.

### 2.3 Data Retention and Deletion
- SQLite records are retained for a configurable retention window (default: 30 days) for scientific verification.
- Researchers and participants can trigger deletion of their session features via the repository API layer.

## 3. High-Stakes and Forensic Prohibition Notice

> [!CAUTION]
> **PROHIBITED USE CASES:**
> GazeGuard AI is an academic research instrument. It MUST NOT be deployed, used, or referenced for:
> - Criminal interrogations, policing, or accusations of guilt.
> - Pre-employment screening or employee integrity evaluations.
> - Border control, immigration determinations, or asylum credibility assessments.
> - Academic disciplinary hearings or fraud investigations.
> 
> Eye movements reflect visual saliency, individual interest, attention capture, anxiety, and idiosyncratic scanning behaviors, and cannot establish ground-truth honesty.
