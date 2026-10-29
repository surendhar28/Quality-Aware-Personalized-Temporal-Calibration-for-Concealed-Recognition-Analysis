"""
Personalized Calibration Engine (Mode A: Population vs Mode B: Personalized QPTC) for GazeGuard AI.
Computes participant-specific baselines strictly from designated calibration/unfamiliar trials.
Safeguards against zero-variance, too few trials, missing features, and test leakage.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field
from ..schemas.canonical import (
    TrialData,
    StimulusCondition,
    QualityStatus,
    ParticipantCalibrationBaseline,
)
from ..features.extractor import FeatureExtractor


class BaselineStatistics(BaseModel):
    mean: float
    std: float
    count: int
    is_valid: bool
    fallback_used: bool = False


class ParticipantProfile(BaseModel):
    participant_id: str
    feature_baselines: Dict[str, BaselineStatistics]
    calibration_trials_count: int
    quality_status: QualityStatus
    warnings: List[str] = Field(default_factory=list)


class PersonalizedCalibrator:
    """
    Implements Quality-Aware Personalized Calibration (Mode B) and
    Population Normalization (Mode A) with leak-prevention guarantees.
    """

    def __init__(
        self,
        epsilon: float = 1e-4,
        min_calibration_trials: int = 3,
        min_variance_threshold: float = 1e-3,
        extractor: Optional[FeatureExtractor] = None
    ):
        self.epsilon = epsilon
        self.min_calibration_trials = min_calibration_trials
        self.min_variance_threshold = min_variance_threshold
        self.extractor = extractor or FeatureExtractor()

    def compute_participant_profile(
        self,
        participant_id: str,
        calibration_trials: List[TrialData],
        population_fallback: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> ParticipantProfile:
        """
        Computes baseline statistics (mean, std) for a single participant using
        strictly calibration or unfamiliar/irrelevant baseline trials.
        
        Strict Leak-Prevention Safeguard:
        Raises ValueError if any trial with condition == PROBE is passed as calibration.
        """
        # 1. Leak prevention check
        for t in calibration_trials:
            if t.condition == StimulusCondition.PROBE:
                raise ValueError(
                    f"CRITICAL TEST LEAKAGE DETECTED: Trial {t.trial_id} has condition '{t.condition}'. "
                    f"Probe/familiar stimuli MUST NEVER be used to calculate participant calibration baseline!"
                )

        warnings: List[str] = []
        n_trials = len(calibration_trials)

        if n_trials < self.min_calibration_trials:
            warnings.append(
                f"Participant {participant_id} has only {n_trials} calibration trials "
                f"(recommended minimum: {self.min_calibration_trials})."
            )

        # 2. Extract features for all calibration trials
        trial_features_list: List[Dict[str, float]] = [
            self.extractor.extract_flat_feature_dict(t) for t in calibration_trials
        ]

        if not trial_features_list:
            warnings.append(f"No valid calibration features extracted for {participant_id}.")
            return ParticipantProfile(
                participant_id=participant_id,
                feature_baselines={},
                calibration_trials_count=0,
                quality_status=QualityStatus.INSUFFICIENT,
                warnings=warnings
            )

        # 3. Compute per-feature mean and std
        feature_keys = trial_features_list[0].keys()
        baselines: Dict[str, BaselineStatistics] = {}

        for k in feature_keys:
            vals = [tf[k] for tf in trial_features_list if k in tf and not np.isnan(tf[k])]
            if len(vals) < 2:
                # Fallback to population if provided, or default
                if population_fallback and k in population_fallback:
                    pop_mean, pop_std = population_fallback[k]
                    baselines[k] = BaselineStatistics(
                        mean=pop_mean,
                        std=pop_std,
                        count=len(vals),
                        is_valid=True,
                        fallback_used=True
                    )
                    warnings.append(f"Feature '{k}' used population fallback due to insufficient participant samples.")
                else:
                    baselines[k] = BaselineStatistics(
                        mean=float(np.mean(vals)) if vals else 0.0,
                        std=1.0,
                        count=len(vals),
                        is_valid=False,
                        fallback_used=True
                    )
                continue

            mean_val = float(np.mean(vals))
            std_val = float(np.std(vals))

            # Safeguard for very low calibration variance
            if std_val < self.min_variance_threshold:
                warnings.append(f"Near-zero variance in feature '{k}' (std={std_val:.4f}). Epsilon safeguard active.")
                std_val = max(std_val, self.min_variance_threshold)

            baselines[k] = BaselineStatistics(
                mean=round(mean_val, 4),
                std=round(std_val, 4),
                count=len(vals),
                is_valid=True,
                fallback_used=False
            )

        quality_status = QualityStatus.ACCEPTABLE if n_trials >= self.min_calibration_trials else QualityStatus.MARGINAL

        return ParticipantProfile(
            participant_id=participant_id,
            feature_baselines=baselines,
            calibration_trials_count=n_trials,
            quality_status=quality_status,
            warnings=warnings
        )

    def normalize_trial_features(
        self,
        raw_features: Dict[str, float],
        profile: Optional[ParticipantProfile] = None,
        population_stats: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> Dict[str, float]:
        """
        Applies z-score normalization:
        z = (x - mean) / (std + epsilon)
        
        If profile is provided, uses Mode B (Personalized Calibration).
        If profile is None or invalid, falls back gracefully to Mode A (Population Baseline).
        """
        normalized: Dict[str, float] = {}

        for k, x_val in raw_features.items():
            if np.isnan(x_val):
                normalized[k] = 0.0
                continue

            mean = 0.0
            std = 1.0

            # Mode B: Participant Profile
            if profile and k in profile.feature_baselines and profile.feature_baselines[k].is_valid:
                b = profile.feature_baselines[k]
                mean = b.mean
                std = b.std
            # Mode A: Population Fallback
            elif population_stats and k in population_stats:
                mean, std = population_stats[k]

            z = (x_val - mean) / (std + self.epsilon)
            # Clip extreme numerical outliers to [-5.0, 5.0] to safeguard linear models
            normalized[f"{k}_z"] = float(np.clip(z, -5.0, 5.0))

        return normalized

    def compute_population_statistics(
        self,
        training_trials_by_participant: Dict[str, List[TrialData]]
    ) -> Dict[str, Tuple[float, float]]:
        """
        Computes grand population baseline across all training participants for Mode A.
        Strictly ignores probe/familiar stimuli to represent the neutral physiological baseline.
        """
        all_features: List[Dict[str, float]] = []

        for p_id, trials in training_trials_by_participant.items():
            baseline_trials = [t for t in trials if t.condition != StimulusCondition.PROBE]
            for t in baseline_trials:
                all_features.append(self.extractor.extract_flat_feature_dict(t))

        if not all_features:
            return {}

        keys = all_features[0].keys()
        pop_stats: Dict[str, Tuple[float, float]] = {}

        for k in keys:
            vals = [f[k] for f in all_features if k in f and not np.isnan(f[k])]
            if vals:
                mean_val = float(np.mean(vals))
                std_val = float(np.std(vals))
                if std_val < self.min_variance_threshold:
                    std_val = 1.0
                pop_stats[k] = (mean_val, std_val)

        return pop_stats
