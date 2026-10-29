"""
Unit Tests for Personalized Calibration Engine.
Tests baseline computation, z-score normalization, variance safeguards,
and verifies strict test leakage prevention.
"""

import pytest
from backend.app.schemas.canonical import TrialData, GazeSample, StimulusCondition
from backend.app.calibration.calibrator import PersonalizedCalibrator


def create_mock_trial(trial_id: str, condition: StimulusCondition, mean_fix_ms: float = 250.0) -> TrialData:
    """Helper to create synthetic trial with known fixation duration."""
    samples = [
        GazeSample(timestamp_ms=float(i * 16.6), x=0.5, y=0.5, valid=True)
        for i in range(int(mean_fix_ms / 16.6))
    ]
    return TrialData(
        trial_id=trial_id,
        stimulus_id=f"STIM_{trial_id}",
        stimulus_name="Mock Item",
        condition=condition,
        onset_timestamp_ms=0.0,
        duration_ms=1500.0,
        samples=samples
    )


def test_personalized_calibrator_baseline_computation():
    """Verifies baseline statistics calculation on calibration trials."""
    calibrator = PersonalizedCalibrator(min_calibration_trials=3)
    calib_trials = [
        create_mock_trial("C1", StimulusCondition.CALIBRATION, mean_fix_ms=200.0),
        create_mock_trial("C2", StimulusCondition.CALIBRATION, mean_fix_ms=220.0),
        create_mock_trial("C3", StimulusCondition.CALIBRATION, mean_fix_ms=240.0),
    ]

    profile = calibrator.compute_participant_profile("P01", calib_trials)
    assert profile.participant_id == "P01"
    assert profile.calibration_trials_count == 3
    assert len(profile.feature_baselines) > 0


def test_personalized_calibrator_leak_prevention():
    """
    CRITICAL LEAKAGE TEST:
    Verifies that passing a PROBE stimulus as a calibration trial raises ValueError.
    """
    calibrator = PersonalizedCalibrator()
    corrupted_calib_trials = [
        create_mock_trial("C1", StimulusCondition.CALIBRATION),
        create_mock_trial("PROBE_LEAK", StimulusCondition.PROBE), # FORBIDDEN LEAK!
    ]

    with pytest.raises(ValueError, match="CRITICAL TEST LEAKAGE DETECTED"):
        calibrator.compute_participant_profile("P01", corrupted_calib_trials)


def test_normalization_with_epsilon_safeguard():
    """Tests z-score normalization when calibration variance is zero or near-zero."""
    calibrator = PersonalizedCalibrator(epsilon=1e-4)
    calib_trials = [
        create_mock_trial("C1", StimulusCondition.IRRELEVANT, mean_fix_ms=200.0),
        create_mock_trial("C2", StimulusCondition.IRRELEVANT, mean_fix_ms=200.0),
        create_mock_trial("C3", StimulusCondition.IRRELEVANT, mean_fix_ms=200.0),
    ]
    profile = calibrator.compute_participant_profile("P02", calib_trials)

    raw_features = {"w0_500_mean_dur": 250.0}
    norm_features = calibrator.normalize_trial_features(raw_features, profile)
    assert "w0_500_mean_dur_z" in norm_features
    # Check bounded within reasonable z limits [-5, 5]
    z_val = norm_features["w0_500_mean_dur_z"]
    assert -5.0 <= z_val <= 5.0
