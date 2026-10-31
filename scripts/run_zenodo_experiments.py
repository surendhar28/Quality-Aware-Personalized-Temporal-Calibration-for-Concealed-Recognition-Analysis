#!/usr/bin/env python3
"""
Scientific Experiment Suite executed on real Zenodo physical eye-tracking CIT data (Revision 12).
Loads data/processed/zenodo_features.csv (819 trials, 38 participants).
Implements participant-grouped StratifiedGroupKFold cross-validation with zero leakage using 11 features.
Logs authoritative scientific findings to experiments/results/final_baseline/, temporal_ablation/, and quality_abstention/.
"""

import os
import sys

# Ensure local scripts can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_fresh_grouped_experiment import main as run_baseline
from run_temporal_ablation import main as run_temporal
from run_quality_abstention import main as run_abstention
from verify_experiment import main as run_verification


def main():
    print("=" * 75)
    print("GAZEGUARD AI — FULL SCIENTIFIC EXPERIMENT SUITE (Revision 12)")
    print("Zenodo Physical Eye-Tracking Benchmark (DOI: 10.5281/zenodo.18525952)")
    print("=" * 75)

    print("\n>>> Phase 1: Authoritative Baseline Models (StratifiedGroupKFold, 11 Features)...")
    run_baseline()

    print("\n>>> Phase 2: Temporal Window Latency Slicing Ablation...")
    run_temporal()

    print("\n>>> Phase 3: Quality-Aware Abstention Trade-off Suite...")
    run_abstention()

    print("\n>>> Phase 4: Automated Reproducibility & Leakage Verification...")
    run_verification()

    print("\n" + "=" * 75)
    print("ALL ZENODO SCIENTIFIC EXPERIMENTS COMPLETED & FULLY VERIFIED!")
    print("=" * 75)


if __name__ == "__main__":
    main()
