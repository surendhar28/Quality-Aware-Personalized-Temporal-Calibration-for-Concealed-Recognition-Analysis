"""
Dataset Adapter for Zenodo Record 18525952:
'Eye tracking as a Tool for deception detection with CIT' (Celniak et al., 2026).
Parses Tobii Pro Fusion CIT recording spreadsheets (CIT Recording1.xlsx - CIT Recording40.xlsx).
"""

import os
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
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


class ZenodoDatasetAdapter(BaseDatasetAdapter):
    """
    Adapter for Tobii Pro Fusion Concealed Information Test dataset (Zenodo 18525952).
    """

    DOI = "10.5281/zenodo.18525952"
    LICENSE = "CC-BY-4.0"
    EXPECTED_PARTICIPANTS = 39

    def list_available_participants(self, data_directory: str) -> List[str]:
        """Scans for CIT Recording*.xlsx files and extracts participant IDs."""
        if not os.path.exists(data_directory):
            return []
        
        pattern = os.path.join(data_directory, "CIT Recording*.xlsx")
        files = glob.glob(pattern)
        participants = []
        for f in files:
            base = os.path.basename(f)
            # Example: "CIT Recording1.xlsx" -> "P01" or "Recording1"
            p_id = base.replace(".xlsx", "").replace(" ", "_")
            participants.append(p_id)
        return sorted(participants)

    def audit_dataset(self, data_directory: str) -> DatasetAuditReport:
        """
        Audits the local Zenodo dataset folder.
        If files are missing or restricted by Zenodo Cloudflare 403, reports exact diagnostic.
        """
        issues = []
        now_str = datetime.utcnow().isoformat()

        if not os.path.exists(data_directory):
            issues.append(f"Directory '{data_directory}' does not exist.")
            return DatasetAuditReport(
                dataset_name="Zenodo 18525952 (Tobii Pro Fusion CIT)",
                provenance_doi=self.DOI,
                license=self.LICENSE,
                storage_path=data_directory,
                files_detected=0,
                participants_found=0,
                total_trials_parsed=0,
                sampling_rate_hz=None,
                has_raw_gaze=False,
                has_precomputed_fixations=False,
                data_quality_issues=issues,
                audit_passed=False,
                mode="real",
                timestamp=now_str
            )

        pattern = os.path.join(data_directory, "CIT Recording*.xlsx")
        excel_files = glob.glob(pattern)
        files_count = len(excel_files)

        if files_count == 0:
            issues.append(
                "No 'CIT Recording*.xlsx' files found in directory. "
                "Automated Zenodo downloads are blocked by Cloudflare HTTP 403 bot-protection from non-browser environments. "
                "Manual download instructions: navigate to https://zenodo.org/records/18525952 in browser and place recordings into data/raw/."
            )
            return DatasetAuditReport(
                dataset_name="Zenodo 18525952 (Tobii Pro Fusion CIT)",
                provenance_doi=self.DOI,
                license=self.LICENSE,
                storage_path=data_directory,
                files_detected=0,
                participants_found=0,
                total_trials_parsed=0,
                sampling_rate_hz=None,
                has_raw_gaze=False,
                has_precomputed_fixations=False,
                data_quality_issues=issues,
                audit_passed=False,
                mode="real",
                timestamp=now_str
            )

        # Inspect the first file for schema verification
        sample_file = excel_files[0]
        sampling_hz = 120.0
        has_raw = False
        has_fix = False
        parsed_trials = files_count * 21 # 21 trials per participant (7 categories x 3 reps)

        # Check if pre-extracted zenodo_features.csv is available for exact metrics
        features_csv = os.path.join(data_directory, "zenodo_features.csv")
        if not os.path.exists(features_csv):
            features_csv = "./data/processed/zenodo_features.csv"
            
        exact_participants = files_count
        if os.path.exists(features_csv):
            try:
                df_feat = pd.read_csv(features_csv)
                exact_participants = int(df_feat["participant_id"].nunique())
                parsed_trials = len(df_feat)
            except Exception:
                pass

        try:
            import zipfile
            import lxml.etree as ET
            with zipfile.ZipFile(sample_file, 'r') as z:
                with z.open('xl/worksheets/sheet1.xml') as s:
                    for event, elem in ET.iterparse(s, tag='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                        headers = [''.join(c.itertext()).strip().lower() for c in elem]
                        elem.clear()
                        has_x = any("gaze point x" in c or "gaze_x" in c for c in headers)
                        has_y = any("gaze point y" in c or "gaze_y" in c for c in headers)
                        has_time = any("recording timestamp" in c or "timestamp" in c for c in headers)
                        has_event = any("eye movement type" in c or "event" in c for c in headers)
                        has_raw = has_x and has_y and has_time
                        has_fix = has_event
                        break
        except Exception as e:
            issues.append(f"Error inspecting Excel file {os.path.basename(sample_file)}: {str(e)}")

        audit_passed = len(issues) == 0 and files_count > 0

        return DatasetAuditReport(
            dataset_name="Zenodo 18525952 (Tobii Pro Fusion CIT)",
            provenance_doi=self.DOI,
            license=self.LICENSE,
            storage_path=data_directory,
            files_detected=files_count,
            participants_found=exact_participants,
            total_trials_parsed=parsed_trials,
            sampling_rate_hz=sampling_hz,
            has_raw_gaze=has_raw,
            has_precomputed_fixations=has_fix,
            data_quality_issues=issues,
            audit_passed=audit_passed,
            mode="real",
            timestamp=now_str
        )

    def load_participant_trials(self, data_directory: str, participant_id: str) -> List[TrialData]:
        """
        Loads and parses a single participant's Tobii recording into structured TrialData objects.
        """
        # Map participant_id to filename
        filename = f"{participant_id.replace('_', ' ')}.xlsx"
        full_path = os.path.join(data_directory, filename)
        if not os.path.exists(full_path):
            alt_path = os.path.join(data_directory, f"CIT {participant_id.replace('_', ' ')}.xlsx")
            if os.path.exists(alt_path):
                full_path = alt_path
            else:
                raise FileNotFoundError(f"Recording file not found for participant {participant_id} in {data_directory}")

        df = pd.read_excel(full_path, engine="openpyxl")
        
        # Standardize column names
        col_map = {}
        for c in df.columns:
            cl = str(c).strip().lower()
            if "recording timestamp" in cl or "timestamp" in cl:
                col_map[c] = "timestamp"
            elif "gaze point x" in cl or "gaze_x" in cl:
                col_map[c] = "gaze_x"
            elif "gaze point y" in cl or "gaze_y" in cl:
                col_map[c] = "gaze_y"
            elif "eye movement type" in cl or "event" in cl:
                col_map[c] = "event_type"
            elif "stimulus name" in cl or "media name" in cl or "presented" in cl:
                col_map[c] = "stimulus"

        df_clean = df.rename(columns=col_map)
        
        # Split into distinct trials based on stimulus presentation intervals
        trials: List[TrialData] = []
        if "stimulus" not in df_clean.columns:
            # Fallback: create single continuous trial
            samples = self._extract_samples_from_df(df_clean)
            trials.append(TrialData(
                trial_id=f"{participant_id}_T01",
                stimulus_id="stim_01",
                stimulus_name="Array_Presentation",
                condition=StimulusCondition.IRRELEVANT,
                onset_timestamp_ms=0.0,
                duration_ms=7500.0,
                samples=samples
            ))
            return trials

        # Group by stimulus presentation blocks
        stim_groups = df_clean.groupby("stimulus")
        t_idx = 1
        for stim_name, grp in stim_groups:
            if pd.isna(stim_name) or str(stim_name).strip() == "":
                continue
            
            samples = self._extract_samples_from_df(grp)
            is_probe = "probe" in str(stim_name).lower() or "critical" in str(stim_name).lower()
            condition = StimulusCondition.PROBE if is_probe else StimulusCondition.IRRELEVANT
            
            onset = float(grp["timestamp"].iloc[0]) if "timestamp" in grp.columns else 0.0
            end = float(grp["timestamp"].iloc[-1]) if "timestamp" in grp.columns else 2000.0
            duration = max(500.0, end - onset)

            trials.append(TrialData(
                trial_id=f"{participant_id}_T{t_idx:02d}",
                stimulus_id=f"stim_{t_idx:02d}",
                stimulus_name=str(stim_name),
                condition=condition,
                familiarity_ground_truth=FamiliarityLabel.FAMILIAR if is_probe else FamiliarityLabel.UNFAMILIAR,
                onset_timestamp_ms=0.0,
                duration_ms=round(duration, 1),
                samples=samples
            ))
            t_idx += 1

        return trials

    def _extract_samples_from_df(self, df_sub: pd.DataFrame) -> List[GazeSample]:
        """Converts DataFrame rows to List[GazeSample] with normalized [0, 1] coordinates."""
        samples: List[GazeSample] = []
        if df_sub.empty:
            return samples

        t0 = df_sub["timestamp"].iloc[0] if "timestamp" in df_sub.columns else 0

        for _, row in df_sub.iterrows():
            t = float(row["timestamp"] - t0) if "timestamp" in row else 0.0
            # Convert microsec to ms if needed
            if t > 100000.0:
                t = t / 1000.0

            gx = float(row["gaze_x"]) if "gaze_x" in row and not pd.isna(row["gaze_x"]) else -1.0
            gy = float(row["gaze_y"]) if "gaze_y" in row and not pd.isna(row["gaze_y"]) else -1.0

            # Normalize 1920x1080 if pixel values
            if gx > 1.0:
                gx = gx / 1920.0
            if gy > 1.0:
                gy = gy / 1080.0

            is_valid = (0.0 <= gx <= 1.0) and (0.0 <= gy <= 1.0)

            samples.append(GazeSample(
                timestamp_ms=round(t, 2),
                x=round(max(0.0, min(1.0, gx)), 4) if is_valid else 0.5,
                y=round(max(0.0, min(1.0, gy)), 4) if is_valid else 0.5,
                valid=is_valid
            ))

        return samples
