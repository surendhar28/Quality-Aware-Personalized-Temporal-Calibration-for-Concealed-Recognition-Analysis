"""
Quality-Aware Assessment and Abstention Engine for GazeGuard AI.
Computes objective data-quality metrics and implements transparent, configurable abstention rules.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from ..schemas.canonical import (
    GazeSample,
    QualityMetrics,
    QualityStatus,
    AbstentionReason,
)


class QualityThresholds:
    """Configurable quality assessment thresholds."""
    def __init__(
        self,
        min_valid_sample_ratio: float = 0.60,
        max_missing_ratio: float = 0.40,
        min_samples_first_500ms: int = 8,        # ~16 Hz minimum in early window
        min_sampling_rate_hz: float = 20.0,
        max_timestamp_jitter_ms: float = 40.0,
        min_tracker_confidence: float = 0.40      # only applied when hardware provides confidence
    ):
        self.min_valid_sample_ratio = min_valid_sample_ratio
        self.max_missing_ratio = max_missing_ratio
        self.min_samples_first_500ms = min_samples_first_500ms
        self.min_sampling_rate_hz = min_sampling_rate_hz
        self.max_timestamp_jitter_ms = max_timestamp_jitter_ms
        self.min_tracker_confidence = min_tracker_confidence


class QualityChecker:
    """Calculates tracking quality metrics on trial gaze sample sequences."""

    def __init__(self, thresholds: Optional[QualityThresholds] = None):
        self.thresholds = thresholds or QualityThresholds()

    def assess_trial_samples(self, samples: List[GazeSample], trial_duration_ms: float = 2000.0) -> QualityMetrics:
        """
        Analyzes gaze sample list and returns a validated QualityMetrics record.
        """
        if not samples:
            return QualityMetrics(
                total_samples=0,
                valid_samples=0,
                valid_ratio=0.0,
                missing_ratio=1.0,
                mean_sampling_hz=0.0,
                timestamp_jitter_ms=999.0,
                samples_in_first_500ms=0,
                valid_ratio_first_500ms=0.0,
                status=QualityStatus.INSUFFICIENT,
                warnings=["Zero samples recorded during trial"]
            )

        total_samples = len(samples)
        valid_samples = sum(1 for s in samples if s.valid and 0.0 <= s.x <= 1.0 and 0.0 <= s.y <= 1.0)
        valid_ratio = valid_samples / total_samples if total_samples > 0 else 0.0
        missing_ratio = 1.0 - valid_ratio

        # Timestamp analysis
        timestamps = [s.timestamp_ms for s in samples]
        diffs = np.diff(timestamps) if len(timestamps) > 1 else np.array([0.0])
        
        # Calculate mean sampling rate in Hz
        total_time_span_s = (timestamps[-1] - timestamps[0]) / 1000.0 if len(timestamps) > 1 else 0.001
        mean_sampling_hz = (total_samples / total_time_span_s) if total_time_span_s > 0 else 0.0

        # Timestamp jitter (standard deviation of inter-sample intervals)
        timestamp_jitter_ms = float(np.std(diffs)) if len(diffs) > 1 else 0.0

        # Samples within early temporal hypothesis window [0, 500 ms]
        first_500_samples = [s for s in samples if s.timestamp_ms <= 500.0]
        samples_in_first_500ms = len(first_500_samples)
        valid_in_500ms = sum(1 for s in first_500_samples if s.valid and 0.0 <= s.x <= 1.0 and 0.0 <= s.y <= 1.0)
        valid_ratio_first_500ms = (valid_in_500ms / samples_in_first_500ms) if samples_in_first_500ms > 0 else 0.0

        warnings = []
        if valid_ratio < self.thresholds.min_valid_sample_ratio:
            warnings.append(f"Low overall valid sample ratio: {valid_ratio:.2%} < {self.thresholds.min_valid_sample_ratio:.0%}")
        
        if samples_in_first_500ms < self.thresholds.min_samples_first_500ms:
            warnings.append(f"Insufficient samples in early 0-500ms window ({samples_in_first_500ms} < {self.thresholds.min_samples_first_500ms})")

        if timestamp_jitter_ms > self.thresholds.max_timestamp_jitter_ms:
            warnings.append(f"High timestamp jitter: {timestamp_jitter_ms:.1f}ms > {self.thresholds.max_timestamp_jitter_ms:.1f}ms")

        # Determine qualitative status
        if valid_ratio >= 0.85 and samples_in_first_500ms >= 15 and timestamp_jitter_ms <= 20.0:
            status = QualityStatus.EXCELLENT
        elif valid_ratio >= self.thresholds.min_valid_sample_ratio and samples_in_first_500ms >= self.thresholds.min_samples_first_500ms:
            status = QualityStatus.ACCEPTABLE
        elif valid_ratio >= 0.40:
            status = QualityStatus.MARGINAL
        else:
            status = QualityStatus.INSUFFICIENT

        return QualityMetrics(
            total_samples=total_samples,
            valid_samples=valid_samples,
            valid_ratio=round(valid_ratio, 4),
            missing_ratio=round(missing_ratio, 4),
            mean_sampling_hz=round(mean_sampling_hz, 2),
            timestamp_jitter_ms=round(timestamp_jitter_ms, 2),
            samples_in_first_500ms=samples_in_first_500ms,
            valid_ratio_first_500ms=round(valid_ratio_first_500ms, 4),
            status=status,
            warnings=warnings
        )

    def evaluate_abstention(
        self,
        metrics: QualityMetrics,
        samples: Optional[List[GazeSample]] = None,
        custom_min_ratio: Optional[float] = None
    ) -> Tuple[bool, AbstentionReason, str]:
        """
        Determines whether the system should abstain from making a familiarity prediction.
        Returns: (should_abstain: bool, reason: AbstentionReason, explanation: str)
        """
        min_ratio = custom_min_ratio if custom_min_ratio is not None else self.thresholds.min_valid_sample_ratio

        if metrics.total_samples == 0:
            return True, AbstentionReason.INSUFFICIENT_SAMPLES, "Zero gaze samples captured during trial."

        if metrics.valid_ratio < min_ratio:
            return (
                True,
                AbstentionReason.EXCESSIVE_MISSING_DATA,
                f"Valid sample ratio ({metrics.valid_ratio:.1%}) is below quality threshold ({min_ratio:.1%})."
            )

        if metrics.samples_in_first_500ms < self.thresholds.min_samples_first_500ms:
            return (
                True,
                AbstentionReason.INSUFFICIENT_SAMPLES,
                f"Only {metrics.samples_in_first_500ms} samples in initial 500ms window (minimum required: {self.thresholds.min_samples_first_500ms})."
            )

        if metrics.timestamp_jitter_ms > self.thresholds.max_timestamp_jitter_ms:
            return (
                True,
                AbstentionReason.HIGH_TIMESTAMP_JITTER,
                f"Severe timestamp jitter ({metrics.timestamp_jitter_ms:.1f} ms) compromises temporal alignment."
            )

        # Check hardware tracker confidence if available
        if samples:
            confidences = [s.tracker_confidence for s in samples if s.tracker_confidence is not None]
            if confidences and np.mean(confidences) < self.thresholds.min_tracker_confidence:
                return (
                    True,
                    AbstentionReason.LOW_CONFIDENCE,
                    f"Mean eye-tracker hardware confidence ({np.mean(confidences):.2f}) is below minimum threshold ({self.thresholds.min_tracker_confidence:.2f})."
                )

        return False, AbstentionReason.NONE, "Data quality meets research criteria for inference."
