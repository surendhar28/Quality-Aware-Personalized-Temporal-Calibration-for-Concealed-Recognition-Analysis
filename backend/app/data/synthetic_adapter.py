"""
Synthetic Dataset Generator and Adapter for GazeGuard AI.
STRICT USAGE POLICY: Exclusively for software verification, end-to-end integration tests,
offline dashboard demos, and algorithmic ablation testing.
MUST NEVER BE PRESENTED OR INTERPRETED AS SCIENTIFIC FINDINGS.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np

from .base_adapter import BaseDatasetAdapter
from ..schemas.canonical import (
    TrialData,
    GazeSample,
    FixationEvent,
    StimulusCondition,
    FamiliarityLabel,
    DatasetAuditReport,
)


class SyntheticDatasetAdapter(BaseDatasetAdapter):
    """
    Generates deterministic, schema-compliant synthetic eye-tracking trials
    with known mathematical properties for testing and CI/CD validation.
    """

    PROVENANCE = "SYNTHETIC_TEST_FIXTURE_DO_NOT_TREAT_AS_SCIENTIFIC_EVIDENCE"
    LICENSE = "MIT_SYNTHETIC_TEST_DATA"

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.rng = np.random.RandomState(random_seed)

    def list_available_participants(self, data_directory: str) -> List[str]:
        """Returns standard list of 20 synthetic participant IDs."""
        return [f"SYNTH_P{i:02d}" for i in range(1, 21)]

    def audit_dataset(self, data_directory: str) -> DatasetAuditReport:
        """Returns structured audit report for synthetic fixture."""
        now_str = datetime.utcnow().isoformat()
        return DatasetAuditReport(
            dataset_name="GazeGuard Synthetic CIT Benchmark Fixture",
            provenance_doi="N/A (Synthetic Benchmark)",
            license=self.LICENSE,
            storage_path=data_directory,
            files_detected=20,
            participants_found=20,
            total_trials_parsed=240, # 20 participants * 12 trials
            sampling_rate_hz=60.0,
            has_raw_gaze=True,
            has_precomputed_fixations=True,
            data_quality_issues=[
                "NOTICE: This dataset consists of mathematically generated synthetic fixtures for software testing.",
                "DO NOT USE SYNTHETIC RESULTS TO DRAW EMPIRICAL FORENSIC OR PSYCHOPHYSIOLOGICAL CONCLUSIONS."
            ],
            audit_passed=True,
            mode="synthetic",
            timestamp=now_str
        )

    def generate_single_trial(
        self,
        participant_id: str,
        trial_id: str,
        condition: StimulusCondition,
        duration_ms: float = 2000.0,
        sampling_rate_hz: float = 60.0,
        noise_level: float = 0.02,
        missing_rate: float = 0.05
    ) -> TrialData:
        """
        Generates a synthetic trial with physiologically plausible fixation dynamics:
        - PROBE: longer early fixation duration (mean ~310ms vs ~230ms for irrelevant)
        - IRRELEVANT: standard exploratory fixations
        - CALIBRATION: stable center fixation target
        """
        dt_ms = 1000.0 / sampling_rate_hz
        timestamps = np.arange(0.0, duration_ms, dt_ms)
        n_samples = len(timestamps)

        is_probe = condition == StimulusCondition.PROBE
        is_calib = condition == StimulusCondition.CALIBRATION

        # Target center coordinates
        if is_calib:
            base_x, base_y = 0.50, 0.50
        elif is_probe:
            # Probe targets often attract initial fixation
            base_x, base_y = 0.35, 0.40
        else:
            base_x, base_y = 0.65, 0.60

        samples: List[GazeSample] = []
        fixations: List[FixationEvent] = []

        # Generate 3-5 fixations across trial
        current_time = 0.0
        fix_idx = 1
        
        while current_time < duration_ms - 150.0:
            if is_probe and fix_idx == 1:
                # Early recognition hypothesis: lengthened initial fixation
                dur = float(self.rng.normal(loc=320.0, scale=35.0))
            elif is_probe:
                dur = float(self.rng.normal(loc=280.0, scale=30.0))
            else:
                dur = float(self.rng.normal(loc=230.0, scale=25.0))
            
            dur = max(90.0, min(600.0, dur))
            end_time = min(duration_ms, current_time + dur)

            # Fixation center with small drift
            fx = float(np.clip(base_x + self.rng.normal(0, 0.04), 0.1, 0.9))
            fy = float(np.clip(base_y + self.rng.normal(0, 0.04), 0.1, 0.9))

            fixations.append(FixationEvent(
                start_time_ms=round(current_time, 1),
                end_time_ms=round(end_time, 1),
                duration_ms=round(end_time - current_time, 1),
                center_x=round(fx, 4),
                center_y=round(fy, 4)
            ))

            # Inter-fixation saccade gap
            saccade_dur = float(self.rng.uniform(30.0, 70.0))
            current_time = end_time + saccade_dur
            # Shift target for next fixation
            base_x = float(np.clip(base_x + self.rng.uniform(-0.2, 0.2), 0.15, 0.85))
            base_y = float(np.clip(base_y + self.rng.uniform(-0.2, 0.2), 0.15, 0.85))
            fix_idx += 1

        # Populate sample-by-sample trajectory
        for t in timestamps:
            # Check which fixation this timestamp falls in
            in_fix = None
            for f in fixations:
                if f.start_time_ms <= t <= f.end_time_ms:
                    in_fix = f
                    break
            
            if in_fix:
                sx = in_fix.center_x + self.rng.normal(0, noise_level)
                sy = in_fix.center_y + self.rng.normal(0, noise_level)
            else:
                # Saccadic sample
                sx = base_x + self.rng.normal(0, noise_level * 2)
                sy = base_y + self.rng.normal(0, noise_level * 2)

            # Simulate occasional missing samples / blinks
            is_valid = self.rng.uniform(0, 1) > missing_rate

            samples.append(GazeSample(
                timestamp_ms=round(float(t), 2),
                x=round(float(np.clip(sx, 0.0, 1.0)), 4) if is_valid else 0.5,
                y=round(float(np.clip(sy, 0.0, 1.0)), 4) if is_valid else 0.5,
                valid=bool(is_valid)
            ))

        familiarity_label = FamiliarityLabel.FAMILIAR if is_probe else FamiliarityLabel.UNFAMILIAR

        return TrialData(
            trial_id=trial_id,
            stimulus_id=f"SYNTH_STIM_{condition.value.upper()}",
            stimulus_name=f"Synthetic {condition.value.title()} Item",
            condition=condition,
            familiarity_ground_truth=familiarity_label,
            onset_timestamp_ms=0.0,
            duration_ms=duration_ms,
            samples=samples,
            precomputed_fixations=fixations
        )

    def load_participant_trials(self, data_directory: str, participant_id: str) -> List[TrialData]:
        """
        Generates 12 standard synthetic trials for the given participant:
        - 3 Calibration trials (Neutral)
        - 3 Probe trials (Familiar condition)
        - 6 Irrelevant trials (Unfamiliar condition)
        """
        trials: List[TrialData] = []
        
        # 1. Calibration trials (neutral baseline)
        for i in range(1, 4):
            trials.append(self.generate_single_trial(
                participant_id=participant_id,
                trial_id=f"{participant_id}_CALIB_{i:02d}",
                condition=StimulusCondition.CALIBRATION,
                duration_ms=1500.0
            ))

        # 2. Experimental trials (3 Probes, 6 Irrelevants)
        trial_seq = [
            (StimulusCondition.IRRELEVANT, 1),
            (StimulusCondition.PROBE, 1),
            (StimulusCondition.IRRELEVANT, 2),
            (StimulusCondition.IRRELEVANT, 3),
            (StimulusCondition.PROBE, 2),
            (StimulusCondition.IRRELEVANT, 4),
            (StimulusCondition.IRRELEVANT, 5),
            (StimulusCondition.PROBE, 3),
            (StimulusCondition.IRRELEVANT, 6),
        ]

        for cond, idx in trial_seq:
            trials.append(self.generate_single_trial(
                participant_id=participant_id,
                trial_id=f"{participant_id}_{cond.value.upper()}_{idx:02d}",
                condition=cond,
                duration_ms=2000.0
            ))

        return trials

    def generate_full_benchmark_cohort(self, n_participants: int = 20) -> Dict[str, List[TrialData]]:
        """Generates cohort of N participants for offline cross-validation and benchmarking."""
        cohort = {}
        for i in range(1, n_participants + 1):
            p_id = f"SYNTH_P{i:02d}"
            cohort[p_id] = self.load_participant_trials("", p_id)
        return cohort
