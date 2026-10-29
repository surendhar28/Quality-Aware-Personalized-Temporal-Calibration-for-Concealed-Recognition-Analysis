"""
Unified Dataset Auditor for GazeGuard AI.
Audits configured raw and synthetic datasets, validates data integrity, and checks schema compliance.
"""

import os
from typing import Dict, Any, Optional
from ..schemas.canonical import DatasetAuditReport
from .zenodo_adapter import ZenodoDatasetAdapter
from .synthetic_adapter import SyntheticDatasetAdapter


class DatasetAuditor:
    """Orchestrates dataset audits across real hardware and synthetic testing sources."""

    def __init__(self, raw_data_dir: str = "./data/processed", fallback_data_dir: str = "./data/raw", synthetic_data_dir: str = "./data/synthetic"):
        self.raw_data_dir = raw_data_dir
        self.fallback_data_dir = fallback_data_dir
        self.synthetic_data_dir = synthetic_data_dir
        self.zenodo_adapter = ZenodoDatasetAdapter()
        self.synthetic_adapter = SyntheticDatasetAdapter()

    def run_audit(self, target: str = "auto") -> DatasetAuditReport:
        """
        Runs audit on specified target:
        - 'real' / 'zenodo': Audits data/processed/ or data/raw/ for Zenodo 18525952 Tobii recordings
        - 'synthetic': Audits synthetic test fixtures
        - 'auto': Checks if real files exist; if not, falls back to synthetic audit with explanatory notice.
        """
        search_dirs = [self.raw_data_dir, self.fallback_data_dir]
        
        if target in ("real", "zenodo"):
            for d in search_dirs:
                if os.path.exists(d) and len(self.zenodo_adapter.list_available_participants(d)) > 0:
                    return self.zenodo_adapter.audit_dataset(d)
            return self.zenodo_adapter.audit_dataset(self.raw_data_dir)
        elif target == "synthetic":
            return self.synthetic_adapter.audit_dataset(self.synthetic_data_dir)
        
        # 'auto' mode
        for d in search_dirs:
            if os.path.exists(d):
                real_report = self.zenodo_adapter.audit_dataset(d)
                if real_report.audit_passed and real_report.files_detected > 0:
                    return real_report
        
        # If real files are not present, return synthetic audit report with clear provenance explanation
        synth_report = self.synthetic_adapter.audit_dataset(self.synthetic_data_dir)
        synth_report.data_quality_issues.insert(
            0,
            f"Primary Zenodo dataset (DOI: 10.5281/zenodo.18525952) was not detected in {search_dirs}. "
            f"Active fallback: Synthetic Benchmark Mode enabled for reproducible software testing."
        )
        return synth_report

