#!/usr/bin/env python3
"""
CLI script to run reproducible scientific ablation experiments.
Saves comprehensive JSON results to experiments/results/.
Usage: python scripts/run_experiments.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from datetime import datetime
from backend.app.data.synthetic_adapter import SyntheticDatasetAdapter
from backend.app.evaluation.evaluator import ExperimentEvaluator


def main():
    print("=" * 65)
    print("GazeGuard AI — Reproducible Scientific Experiment Suite")
    print("Quality-Aware Personalized Temporal Calibration (QPTC)")
    print("=" * 65)

    os.makedirs("./experiments/results", exist_ok=True)
    adapter = SyntheticDatasetAdapter(random_seed=42)
    evaluator = ExperimentEvaluator(random_state=42)

    print("\n[1/5] Generating standard benchmark cohort (12 participants)...")
    cohort = adapter.generate_full_benchmark_cohort(n_participants=12)

    # Experiment 1
    print("\n[2/5] Running Experiment 1: Baseline Models Comparison...")
    exp1 = evaluator.run_experiment_1_baselines(cohort)
    with open("./experiments/results/exp01_baselines.json", "w") as f:
        json.dump(exp1, f, indent=2)
    print(f"  -> Saved to experiments/results/exp01_baselines.json")

    # Experiment 2
    print("\n[3/5] Running Experiment 2: Personalized Calibration Ablation...")
    exp2 = evaluator.run_experiment_2_personalization_ablation(cohort)
    with open("./experiments/results/exp02_personalization.json", "w") as f:
        json.dump(exp2, f, indent=2)
    print(f"  -> Delta Balanced Acc: +{(exp2['delta_balanced_accuracy'] * 100):.1f}%")
    print(f"  -> Saved to experiments/results/exp02_personalization.json")

    # Experiment 3
    print("\n[4/5] Running Experiment 3: Temporal Window Contribution Ablation...")
    exp3 = evaluator.run_experiment_3_temporal_window_ablation(cohort)
    with open("./experiments/results/exp03_temporal_windows.json", "w") as f:
        json.dump(exp3, f, indent=2)
    print(f"  -> Saved to experiments/results/exp03_temporal_windows.json")

    # Experiment 4
    print("\n[5/5] Running Experiment 4: Quality-Aware Abstention Trade-off...")
    exp4 = evaluator.run_experiment_4_quality_abstention(cohort)
    with open("./experiments/results/exp04_quality_abstention.json", "w") as f:
        json.dump(exp4, f, indent=2)
    print(f"  -> Saved to experiments/results/exp04_quality_abstention.json")

    # Experiment 6
    print("\n[Bonus] Running Experiment 6: Robustness Under Signal Degradation...")
    exp6 = evaluator.run_experiment_6_robustness_analysis(cohort)
    with open("./experiments/results/exp06_robustness.json", "w") as f:
        json.dump(exp6, f, indent=2)
    print(f"  -> Saved to experiments/results/exp06_robustness.json")

    print("\n" + "=" * 65)
    print("All scientific ablation experiments completed successfully.")
    print("Results logged to experiments/results/.")
    print("=" * 65)


if __name__ == "__main__":
    main()
