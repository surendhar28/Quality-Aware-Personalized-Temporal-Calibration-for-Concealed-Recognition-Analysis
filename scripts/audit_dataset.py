#!/usr/bin/env python3
"""
CLI script to audit raw dataset files or synthetic test benchmark.
Usage: python scripts/audit_dataset.py [--target real|synthetic|auto]
"""

import sys
import os
import argparse
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.data.audit import DatasetAuditor


def main():
    parser = argparse.ArgumentParser(description="Audit GazeGuard AI Eye-Tracking Datasets")
    parser.add_argument("--target", default="auto", choices=["auto", "real", "synthetic"],
                        help="Target dataset to audit (default: auto)")
    args = parser.parse_args()

    auditor = DatasetAuditor()
    report = auditor.run_audit(target=args.target)

    print("=" * 60)
    print(f"DATASET AUDIT REPORT: {report.dataset_name}")
    print("=" * 60)
    print(f"Mode:                   {report.mode.upper()}")
    print(f"DOI / Source:           {report.provenance_doi}")
    print(f"License:                {report.license}")
    print(f"Storage Path:           {report.storage_path}")
    print(f"Files Detected:         {report.files_detected}")
    print(f"Participants Found:     {report.participants_found}")
    print(f"Total Trials Parsed:    {report.total_trials_parsed}")
    print(f"Estimated Sample Rate:  {report.sampling_rate_hz} Hz")
    print(f"Raw Coordinates Found:  {report.has_raw_gaze}")
    print(f"Precomputed Fixations:  {report.has_precomputed_fixations}")
    print(f"Audit Result:           {'PASSED' if report.audit_passed else 'ATTENTION REQUIRED'}")
    print("-" * 60)
    print("Diagnostic Notes:")
    for issue in report.data_quality_issues:
        print(f"  • {issue}")
    print("=" * 60)


if __name__ == "__main__":
    main()
