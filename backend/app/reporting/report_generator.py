"""
Explainable Scientific Report Generator for GazeGuard AI.
Generates structured session reports adhering to ethical and scientific standards:
- Reports calibrated familiarity probabilities exclusively.
- Highlights quality metrics and abstention states.
- Incorporates SHAP feature attributions with non-causal caveats.
- Enforces strict forensic disclaimers against deception/guilt claims.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..schemas.canonical import (
    PredictionResult,
    QualityMetrics,
    QualityStatus,
    SHAPContribution,
    WindowFeatures,
)


class ReportGenerator:
    """Generates comprehensive, ethical research reports for participant sessions."""

    MANDATORY_SCIENTIFIC_DISCLAIMER = (
        "CRITICAL RESEARCH NOTICE: GazeGuard AI is an experimental scientific instrument designed "
        "to measure eye-movement fixation patterns relative to visual stimuli in controlled CIT paradigms. "
        "Under NO circumstances should this report or its outputs be used to infer deception, dishonesty, "
        "guilt, or individual credibility in legal, employment, or forensic contexts. "
        "Eye movements are influenced by cognitive salience, visual saliency, emotional arousal, fatigue, "
        "and idiosyncratic gaze habits, and do not constitute direct evidence of mental state."
    )

    def generate_session_report(
        self,
        session_id: str,
        participant_pseudonym: str,
        trial_evaluations: List[Dict[str, Any]],
        calibration_summary: Optional[Dict[str, Any]] = None,
        overall_quality_status: QualityStatus = QualityStatus.ACCEPTABLE
    ) -> Dict[str, Any]:
        """
        Compiles trial-by-trial predictions, SHAP explanations, quality assessments,
        and temporal timelines into a downloadable report.
        """
        now_str = datetime.utcnow().isoformat()
        
        total_trials = len(trial_evaluations)
        accepted_trials = sum(1 for t in trial_evaluations if t.get("status") == "accepted")
        abstained_trials = total_trials - accepted_trials
        coverage = (accepted_trials / total_trials) if total_trials > 0 else 0.0

        # Mean familiarity probability on accepted probe trials
        probe_probs = [
            t["probability"] for t in trial_evaluations 
            if t.get("status") == "accepted" and t.get("probability") is not None and t.get("condition") == "probe"
        ]
        mean_probe_familiarity = float(round(sum(probe_probs) / len(probe_probs), 4)) if probe_probs else None

        irrelevant_probs = [
            t["probability"] for t in trial_evaluations 
            if t.get("status") == "accepted" and t.get("probability") is not None and t.get("condition") == "irrelevant"
        ]
        mean_irrelevant_familiarity = float(round(sum(irrelevant_probs) / len(irrelevant_probs), 4)) if irrelevant_probs else None

        return {
            "report_id": f"REP_{session_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "generated_at": now_str,
            "session_id": session_id,
            "participant_pseudonym": participant_pseudonym,
            "disclaimer": self.MANDATORY_SCIENTIFIC_DISCLAIMER,
            "executive_summary": {
                "total_stimuli_evaluated": total_trials,
                "accepted_predictions": accepted_trials,
                "abstained_predictions": abstained_trials,
                "quality_coverage_ratio": round(coverage, 4),
                "overall_tracking_quality": overall_quality_status.value,
                "mean_probe_familiarity_score": mean_probe_familiarity,
                "mean_irrelevant_familiarity_score": mean_irrelevant_familiarity,
                "calibration_status": calibration_summary.get("quality_status", "uncalibrated") if calibration_summary else "none"
            },
            "calibration_metadata": calibration_summary,
            "trials": trial_evaluations,
            "methodology_notes": [
                "Target construct: Calibrated probability of visual recognition pattern under Concealed Information Test.",
                "Feature set: Multi-window fixation duration and count across early [0-500ms] and late intervals.",
                "Normalization: Participant-specific z-score calibration against unfamiliar baseline trials.",
                "Abstention rule: Trials with <60% valid gaze samples or severe timestamp jitter are rejected."
            ],
            "limitations": [
                "Webcam-based gaze estimates possess higher angular spatial error (~1.5°-3.0°) compared to dedicated Tobii Pro desktop hardware (~0.4°-0.8°).",
                "Fixations < 80ms are excluded by I-VT filter; blink intervals are treated as missing data.",
                "Attribution explanations (SHAP) reflect correlative model feature weighting and must not be interpreted causally."
            ]
        }
