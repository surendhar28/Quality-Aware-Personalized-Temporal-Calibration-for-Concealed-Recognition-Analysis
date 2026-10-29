"""
Deterministic Fixation Detection and Multi-Window Feature Extraction Engine for GazeGuard AI.
Implements I-VT (Velocity Threshold Identification) algorithm and extracts temporal features across
predefined windows: [0-500ms], [500-1000ms], [1000-2000ms], and overall trial duration.
"""

from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from ..schemas.canonical import (
    GazeSample,
    FixationEvent,
    WindowFeatures,
    TrialData,
    QualityMetrics,
)


class IVTFixationDetector:
    """
    Velocity-Threshold Identification (I-VT) fixation detection algorithm.
    Calculates point-to-point angular or normalized velocity.
    Deterministic and configurable.
    """
    def __init__(
        self,
        velocity_threshold_norm_per_sec: float = 0.50, # equivalent to ~30-40 deg/s on standard displays
        min_fixation_duration_ms: float = 80.0,        # Minimum duration for valid physiological fixation
        max_fixation_merge_distance: float = 0.05,     # Normalized distance for merging nearby fixations
        max_merge_time_gap_ms: float = 75.0            # Max time between fixations to merge
    ):
        self.velocity_threshold = velocity_threshold_norm_per_sec
        self.min_duration_ms = min_fixation_duration_ms
        self.max_merge_dist = max_fixation_merge_distance
        self.max_merge_gap = max_merge_time_gap_ms

    def detect_fixations(self, samples: List[GazeSample]) -> List[FixationEvent]:
        """
        Classifies continuous gaze samples into discrete fixation events.
        """
        valid_samples = [s for s in samples if s.valid and 0.0 <= s.x <= 1.0 and 0.0 <= s.y <= 1.0]
        if len(valid_samples) < 2:
            return []

        # Sort strictly by timestamp
        valid_samples.sort(key=lambda s: s.timestamp_ms)

        # 1. Point-to-point velocity calculation
        velocities = []
        for i in range(1, len(valid_samples)):
            dt_s = (valid_samples[i].timestamp_ms - valid_samples[i - 1].timestamp_ms) / 1000.0
            if dt_s <= 0.0:
                velocities.append(0.0)
                continue
            dx = valid_samples[i].x - valid_samples[i - 1].x
            dy = valid_samples[i].y - valid_samples[i - 1].y
            dist = np.sqrt(dx * dx + dy * dy)
            v = dist / dt_s
            velocities.append(v)

        # 2. Group consecutive below-threshold samples into proto-fixations
        raw_fixations: List[List[GazeSample]] = []
        current_cluster: List[GazeSample] = [valid_samples[0]]

        for i, v in enumerate(velocities):
            curr_sample = valid_samples[i + 1]
            if v <= self.velocity_threshold:
                current_cluster.append(curr_sample)
            else:
                if len(current_cluster) >= 2:
                    raw_fixations.append(current_cluster)
                current_cluster = [curr_sample]

        if len(current_cluster) >= 2:
            raw_fixations.append(current_cluster)

        # 3. Create preliminary fixation events meeting minimum duration
        events: List[FixationEvent] = []
        for cluster in raw_fixations:
            t_start = cluster[0].timestamp_ms
            t_end = cluster[-1].timestamp_ms
            duration = t_end - t_start
            if duration >= self.min_duration_ms:
                cx = float(np.mean([s.x for s in cluster]))
                cy = float(np.mean([s.y for s in cluster]))
                events.append(FixationEvent(
                    start_time_ms=round(t_start, 2),
                    end_time_ms=round(t_end, 2),
                    duration_ms=round(duration, 2),
                    center_x=round(cx, 4),
                    center_y=round(cy, 4)
                ))

        # 4. Merge close consecutive fixations separated by brief blinks/saccades
        if not events:
            return []

        merged: List[FixationEvent] = [events[0]]
        for curr in events[1:]:
            prev = merged[-1]
            time_gap = curr.start_time_ms - prev.end_time_ms
            dist = np.sqrt((curr.center_x - prev.center_x) ** 2 + (curr.center_y - prev.center_y) ** 2)

            if 0 <= time_gap <= self.max_merge_gap and dist <= self.max_merge_dist:
                # Merge into previous fixation
                new_start = prev.start_time_ms
                new_end = curr.end_time_ms
                new_duration = new_end - new_start
                # Weighted center
                total_dur = prev.duration_ms + curr.duration_ms
                new_cx = (prev.center_x * prev.duration_ms + curr.center_x * curr.duration_ms) / total_dur
                new_cy = (prev.center_y * prev.duration_ms + curr.center_y * curr.duration_ms) / total_dur
                merged[-1] = FixationEvent(
                    start_time_ms=round(new_start, 2),
                    end_time_ms=round(new_end, 2),
                    duration_ms=round(new_duration, 2),
                    center_x=round(new_cx, 4),
                    center_y=round(new_cy, 4)
                )
            else:
                merged.append(curr)

        return merged


class FeatureExtractor:
    """
    Extracts summary features across multiple predefined temporal windows.
    """
    def __init__(self, detector: Optional[IVTFixationDetector] = None):
        self.detector = detector or IVTFixationDetector()

    def get_or_detect_fixations(self, trial: TrialData) -> List[FixationEvent]:
        """Returns precomputed fixations if present in data, otherwise detects using I-VT."""
        if trial.precomputed_fixations is not None and len(trial.precomputed_fixations) > 0:
            return trial.precomputed_fixations
        return self.detector.detect_fixations(trial.samples)

    def extract_window_features(
        self,
        fixations: List[FixationEvent],
        samples: List[GazeSample],
        window_name: str,
        start_ms: float,
        end_ms: float
    ) -> WindowFeatures:
        """
        Calculates fixation metrics within the given [start_ms, end_ms] window.
        Correctly handles fixations overlapping window boundaries.
        """
        # Gaze samples within window
        window_samples = [s for s in samples if start_ms <= s.timestamp_ms <= end_ms]
        valid_in_win = sum(1 for s in window_samples if s.valid and 0.0 <= s.x <= 1.0 and 0.0 <= s.y <= 1.0)
        valid_ratio = (valid_in_win / len(window_samples)) if window_samples else 0.0

        # Fixations overlapping this window
        overlap_fixations = []
        for f in fixations:
            # Overlap interval: [max(start_ms, f.start), min(end_ms, f.end)]
            overlap_start = max(start_ms, f.start_time_ms)
            overlap_end = min(end_ms, f.end_time_ms)
            if overlap_end > overlap_start:
                duration_in_window = overlap_end - overlap_start
                overlap_fixations.append({
                    "fixation": f,
                    "effective_duration": duration_in_window,
                    "start_time": f.start_time_ms
                })

        count = len(overlap_fixations)
        if count == 0:
            return WindowFeatures(
                window_name=window_name,
                start_ms=start_ms,
                end_ms=end_ms,
                fixation_count=0,
                total_fixation_duration_ms=0.0,
                mean_fixation_duration_ms=0.0,
                median_fixation_duration_ms=0.0,
                first_fixation_duration_ms=0.0,
                first_fixation_latency_ms=None,
                valid_sample_ratio=round(valid_ratio, 4)
            )

        durations = [item["effective_duration"] for item in overlap_fixations]
        total_duration = float(np.sum(durations))
        mean_duration = float(np.mean(durations))
        median_duration = float(np.median(durations))
        first_duration = float(overlap_fixations[0]["effective_duration"])
        first_latency = float(overlap_fixations[0]["start_time"])

        return WindowFeatures(
            window_name=window_name,
            start_ms=start_ms,
            end_ms=end_ms,
            fixation_count=count,
            total_fixation_duration_ms=round(total_duration, 2),
            mean_fixation_duration_ms=round(mean_duration, 2),
            median_fixation_duration_ms=round(median_duration, 2),
            first_fixation_duration_ms=round(first_duration, 2),
            first_fixation_latency_ms=round(first_latency, 2),
            valid_sample_ratio=round(valid_ratio, 4)
        )

    def extract_all_windows(self, trial: TrialData) -> Dict[str, WindowFeatures]:
        """
        Extracts WindowFeatures across the four standard experimental windows:
        - w0_500: Early recognition window [0, 500ms]
        - w500_1000: Intermediate window [500, 1000ms]
        - w1000_2000: Late window [1000, 2000ms]
        - w_overall: Total trial duration [0, trial.duration_ms]
        """
        fixations = self.get_or_detect_fixations(trial)
        samples = trial.samples

        w0_500 = self.extract_window_features(fixations, samples, "w0_500", 0.0, 500.0)
        w500_1000 = self.extract_window_features(fixations, samples, "w500_1000", 500.0, 1000.0)
        w1000_2000 = self.extract_window_features(fixations, samples, "w1000_2000", 1000.0, 2000.0)
        w_overall = self.extract_window_features(fixations, samples, "w_overall", 0.0, trial.duration_ms)

        return {
            "w0_500": w0_500,
            "w500_1000": w500_1000,
            "w1000_2000": w1000_2000,
            "w_overall": w_overall
        }

    def extract_flat_feature_dict(self, trial: TrialData) -> Dict[str, float]:
        """
        Flattens multi-window features into a clean dictionary of scalar floats
        suitable for tabular machine learning pipelines.
        """
        windows = self.extract_all_windows(trial)
        flat: Dict[str, float] = {}

        for w_name, wf in windows.items():
            flat[f"{w_name}_fix_count"] = float(wf.fixation_count)
            flat[f"{w_name}_total_dur"] = float(wf.total_fixation_duration_ms)
            flat[f"{w_name}_mean_dur"] = float(wf.mean_fixation_duration_ms)
            flat[f"{w_name}_median_dur"] = float(wf.median_fixation_duration_ms)
            flat[f"{w_name}_first_dur"] = float(wf.first_fixation_duration_ms)
            flat[f"{w_name}_first_latency"] = float(wf.first_fixation_latency_ms) if wf.first_fixation_latency_ms is not None else 999.0
            flat[f"{w_name}_valid_ratio"] = float(wf.valid_sample_ratio)

        return flat
