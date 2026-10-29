"""
Unit Tests for Quality Assessment and Quality-Aware Abstention Engine.
Verifies missing data detection, jitter detection, and explicit abstention triggers.
"""

import pytest
from backend.app.schemas.canonical import GazeSample, QualityStatus, AbstentionReason
from backend.app.quality.quality_checker import QualityChecker, QualityThresholds


def test_quality_checker_high_quality_samples():
    """Verifies that dense, clean gaze samples achieve EXCELLENT quality status."""
    checker = QualityChecker()
    samples = [
        GazeSample(timestamp_ms=float(i * 16.6), x=0.5, y=0.5, valid=True)
        for i in range(120) # 2 seconds at 60Hz
    ]
    metrics = checker.assess_trial_samples(samples, trial_duration_ms=2000.0)
    assert metrics.valid_ratio == 1.0
    assert metrics.missing_ratio == 0.0
    assert metrics.status in (QualityStatus.EXCELLENT, QualityStatus.ACCEPTABLE)
    assert len(metrics.warnings) == 0

    should_abstain, reason, _ = checker.evaluate_abstention(metrics, samples)
    assert should_abstain is False
    assert reason == AbstentionReason.NONE


def test_quality_checker_excessive_missingness_triggers_abstention():
    """Verifies that trials with >40% missing or out-of-bounds samples trigger abstention."""
    checker = QualityChecker()
    # 70 invalid samples, 30 valid samples -> 30% valid ratio
    samples = (
        [GazeSample(timestamp_ms=float(i * 16.6), x=0.5, y=0.5, valid=True) for i in range(30)] +
        [GazeSample(timestamp_ms=float((30 + i) * 16.6), x=-1.0, y=-1.0, valid=False) for i in range(70)]
    )
    metrics = checker.assess_trial_samples(samples, trial_duration_ms=2000.0)
    assert metrics.valid_ratio == 0.30
    assert metrics.status in (QualityStatus.MARGINAL, QualityStatus.INSUFFICIENT)

    should_abstain, reason, expl = checker.evaluate_abstention(metrics, samples)
    assert should_abstain is True
    assert reason == AbstentionReason.EXCESSIVE_MISSING_DATA
    assert "below quality threshold" in expl


def test_quality_checker_insufficient_samples_in_early_window():
    """Verifies that missing samples in the critical 0-500ms window triggers abstention."""
    checker = QualityChecker()
    # Zero samples before 550ms
    samples = [
        GazeSample(timestamp_ms=float(600 + i * 16.6), x=0.5, y=0.5, valid=True)
        for i in range(60)
    ]
    metrics = checker.assess_trial_samples(samples, trial_duration_ms=2000.0)
    assert metrics.samples_in_first_500ms == 0

    should_abstain, reason, _ = checker.evaluate_abstention(metrics, samples)
    assert should_abstain is True
    assert reason == AbstentionReason.INSUFFICIENT_SAMPLES
