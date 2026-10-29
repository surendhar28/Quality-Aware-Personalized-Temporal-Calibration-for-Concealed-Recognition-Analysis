"""
Unit Tests for Fixation Detection and Multi-Window Feature Extraction.
Verifies mathematical correctness of I-VT detector and temporal window slicing.
"""

import pytest
import numpy as np
from backend.app.schemas.canonical import GazeSample, TrialData, StimulusCondition
from backend.app.features.extractor import IVTFixationDetector, FeatureExtractor


def test_ivt_fixation_detector_steady_gaze():
    """Tests that stationary gaze samples are correctly grouped into a single fixation."""
    detector = IVTFixationDetector(
        velocity_threshold_norm_per_sec=0.5,
        min_fixation_duration_ms=80.0
    )
    # 20 samples at 60Hz (~333ms) centered at (0.40, 0.50)
    samples = [
        GazeSample(timestamp_ms=float(i * 16.6), x=0.40 + np.sin(i)*0.001, y=0.50, valid=True)
        for i in range(20)
    ]
    fixations = detector.detect_fixations(samples)
    assert len(fixations) == 1
    assert fixations[0].duration_ms >= 250.0
    assert abs(fixations[0].center_x - 0.40) < 0.01
    assert abs(fixations[0].center_y - 0.50) < 0.01


def test_ivt_fixation_detector_saccade_split():
    """Tests that a sudden rapid shift (saccade) splits into two distinct fixations."""
    detector = IVTFixationDetector(
        velocity_threshold_norm_per_sec=0.5,
        min_fixation_duration_ms=80.0
    )
    # Cluster 1: 10 samples at (0.2, 0.2)
    c1 = [GazeSample(timestamp_ms=float(i * 16.6), x=0.2, y=0.2, valid=True) for i in range(10)]
    # Big jump at t=166ms to (0.8, 0.8)
    # Cluster 2: 10 samples at (0.8, 0.8)
    c2 = [GazeSample(timestamp_ms=float(180 + i * 16.6), x=0.8, y=0.8, valid=True) for i in range(10)]
    
    samples = c1 + c2
    fixations = detector.detect_fixations(samples)
    assert len(fixations) == 2
    assert abs(fixations[0].center_x - 0.2) < 0.02
    assert abs(fixations[1].center_x - 0.8) < 0.02


def test_feature_extractor_temporal_windows():
    """Verifies that fixations are accurately apportioned across predefined temporal windows."""
    extractor = FeatureExtractor()
    # Trial with a 300ms fixation starting at t=100ms (within 0-500ms window)
    # and a 400ms fixation starting at t=700ms (within 500-1000ms window)
    samples = (
        [GazeSample(timestamp_ms=float(100 + i * 16.6), x=0.3, y=0.3, valid=True) for i in range(18)] +
        [GazeSample(timestamp_ms=float(700 + i * 16.6), x=0.7, y=0.7, valid=True) for i in range(15)]
    )
    trial = TrialData(
        trial_id="TEST_01",
        stimulus_id="STIM_01",
        stimulus_name="Test Stimulus",
        condition=StimulusCondition.PROBE,
        onset_timestamp_ms=0.0,
        duration_ms=2000.0,
        samples=samples
    )

    windows = extractor.extract_all_windows(trial)
    assert "w0_500" in windows
    assert "w500_1000" in windows
    assert "w1000_2000" in windows
    assert "w_overall" in windows

    # Window 0-500 should capture the first fixation
    assert windows["w0_500"].fixation_count >= 1
    assert windows["w0_500"].mean_fixation_duration_ms > 150.0

    # Window 500-1000 should capture the second fixation
    assert windows["w500_1000"].fixation_count >= 1

    # Window 1000-2000 should have 0 fixations
    assert windows["w1000_2000"].fixation_count == 0
    assert windows["w1000_2000"].first_fixation_latency_ms is None
