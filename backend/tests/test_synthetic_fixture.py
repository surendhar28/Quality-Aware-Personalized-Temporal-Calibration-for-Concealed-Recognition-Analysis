"""
Verification Tests for Synthetic Mathematical Fixture.
Explicitly checks known mathematical ground-truth values to prove feature calculations are correct.
STRICT TEST DATA NOTICE: This fixture is used exclusively for algebraic and algorithmic verification.
"""

import pytest
import numpy as np
from backend.app.schemas.canonical import (
    TrialData,
    GazeSample,
    StimulusCondition,
    FamiliarityLabel,
)
from backend.app.features.extractor import FeatureExtractor
from backend.app.quality.quality_checker import QualityChecker


def test_mathematical_feature_calculations_on_synthetic_fixture():
    """
    Mathematical proof of feature calculations:
    Constructs a trial with EXACT known timestamps and coordinates:
    - Exactly 1 fixation from t=100ms to t=400ms (duration = 300.0ms)
    - Exactly 1 fixation from t=600ms to t=900ms (duration = 300.0ms)
    - Total valid samples = 100, sampling rate = 50 Hz (20ms step, total 2000ms)
    """
    samples = []
    # 0 to 1000ms in steps of 20ms (50 samples)
    for i in range(50):
        t = float(i * 20.0)
        # Moving saccade at 0-80ms (high velocity > 1.0/sec)
        if t < 100.0:
            x, y = float(0.05 + (i * 0.08)), float(0.05 + (i * 0.08))
        # Stable Fixation 1 at 100-400ms (16 samples at exactly (0.4, 0.4))
        elif 100.0 <= t <= 400.0:
            x, y = 0.4000, 0.4000
        # Moving saccade at 420-580ms (high velocity > 1.0/sec)
        elif 400.0 < t < 600.0:
            step = float((t - 400.0) / 20.0)
            x, y = float(0.40 + (step * 0.04)), float(0.40 + (step * 0.04))
        # Stable Fixation 2 at 600-900ms (16 samples at exactly (0.8, 0.8))
        elif 600.0 <= t <= 900.0:
            x, y = 0.8000, 0.8000
        else:
            x, y = float(0.80 - ((t - 900.0) / 20.0 * 0.07)), float(0.80 - ((t - 900.0) / 20.0 * 0.07))
        
        samples.append(GazeSample(timestamp_ms=t, x=x, y=y, valid=True))

    trial = TrialData(
        trial_id="MATH_FIXTURE_01",
        stimulus_id="MATH_PROBE",
        stimulus_name="Algebraic Ground Truth Fixture",
        condition=StimulusCondition.PROBE,
        familiarity_ground_truth=FamiliarityLabel.FAMILIAR,
        onset_timestamp_ms=0.0,
        duration_ms=1000.0,
        samples=samples
    )

    extractor = FeatureExtractor()
    windows = extractor.extract_all_windows(trial)
    quality = QualityChecker().assess_trial_samples(trial.samples, trial.duration_ms)

    # 1. Quality checks: 50 samples, 100% valid, 50 Hz
    assert quality.total_samples == 50
    assert quality.valid_samples == 50
    assert quality.valid_ratio == 1.0
    assert abs(quality.mean_sampling_hz - 50.0) < 2.0

    # 2. Window 0-500ms feature checks:
    # Contains Fixation 1: exactly 300ms duration, starts at t=100ms
    w0_500 = windows["w0_500"]
    assert w0_500.fixation_count == 1
    assert abs(w0_500.total_fixation_duration_ms - 300.0) < 5.0
    assert abs(w0_500.first_fixation_duration_ms - 300.0) < 5.0
    assert abs(w0_500.first_fixation_latency_ms - 100.0) < 5.0

    # 3. Window 500-1000ms feature checks:
    # Contains Fixation 2: exactly 300ms duration, starts at t=600ms
    w500_1000 = windows["w500_1000"]
    assert w500_1000.fixation_count == 1
    assert abs(w500_1000.total_fixation_duration_ms - 300.0) < 5.0

    # 4. Overall trial window:
    # Contains both Fixation 1 and 2: total = 600ms, mean = 300ms, count = 2
    w_overall = windows["w_overall"]
    assert w_overall.fixation_count == 2
    assert abs(w_overall.total_fixation_duration_ms - 600.0) < 10.0
    assert abs(w_overall.mean_fixation_duration_ms - 300.0) < 5.0
