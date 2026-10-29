#!/usr/bin/env python3
"""
Generates the 5 standard research Jupyter notebooks in notebooks/
"""

import os
import json


def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.9"}
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def main():
    os.makedirs("notebooks", exist_ok=True)

    # 01_dataset_audit.ipynb
    nb1_cells = [
        {"cell_type": "markdown", "metadata": {}, "source": [
            "# Notebook 01: Dataset Audit and Provenance Verification\n",
            "**GazeGuard AI — Quality-Aware Personalized Temporal Calibration (QPTC)**\n\n",
            "This notebook audits the primary Zenodo 18525952 CIT benchmark dataset (Celniak et al., 2026).\n",
            "It checks file availability, verifies column schemas, calculates sampling rates, and logs missingness."
        ]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "import os\n",
            "import sys\n",
            "sys.path.insert(0, os.path.abspath('..'))\n\n",
            "from backend.app.data.audit import DatasetAuditor\n\n",
            "auditor = DatasetAuditor(raw_data_dir='../data/raw', synthetic_data_dir='../data/synthetic')\n",
            "report = auditor.run_audit(target='auto')\n",
            "print(f'Dataset Name:    {report.dataset_name}')\n",
            "print(f'Persistent DOI:  {report.provenance_doi}')\n",
            "print(f'License:         {report.license}')\n",
            "print(f'Sampling Rate:   {report.sampling_rate_hz} Hz')\n",
            "print(f'Files Detected:  {report.files_detected}')\n",
            "print(f'Audit Passed:    {report.audit_passed}')\n",
            "print('Diagnostic Issues / Notes:')\n",
            "for issue in report.data_quality_issues:\n",
            "    print('  •', issue)"
        ]}
    ]
    with open("notebooks/01_dataset_audit.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb1_cells), f, indent=2)

    # 02_feature_extraction.ipynb
    nb2_cells = [
        {"cell_type": "markdown", "metadata": {}, "source": [
            "# Notebook 02: I-VT Fixation Detection and Multi-Window Feature Extraction\n",
            "Demonstrates the velocity-threshold identification (I-VT) algorithm on continuous gaze streams\n",
            "and extracts features across the early 0-500ms orienting window and later appraisal windows."
        ]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "import os\n",
            "import sys\n",
            "sys.path.insert(0, os.path.abspath('..'))\n\n",
            "from backend.app.data.synthetic_adapter import SyntheticDatasetAdapter\n",
            "from backend.app.features.extractor import FeatureExtractor\n\n",
            "adapter = SyntheticDatasetAdapter()\n",
            "trials = adapter.load_participant_trials('', 'SYNTH_P01')\n",
            "extractor = FeatureExtractor()\n",
            "sample_trial = [t for t in trials if t.condition.value == 'probe'][0]\n\n",
            "windows = extractor.extract_all_windows(sample_trial)\n",
            "for w_name, wf in windows.items():\n",
            "    print(f'=== {w_name} ===')\n",
            "    print(f'  Fixation Count: {wf.fixation_count}')\n",
            "    print(f'  Mean Duration:  {wf.mean_fixation_duration_ms} ms')\n",
            "    print(f'  Total Duration: {wf.total_fixation_duration_ms} ms')\n",
            "    print(f'  First Latency:  {wf.first_fixation_latency_ms} ms')"
        ]}
    ]
    with open("notebooks/02_feature_extraction.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb2_cells), f, indent=2)

    # 03_baseline_models.ipynb
    nb3_cells = [
        {"cell_type": "markdown", "metadata": {}, "source": [
            "# Notebook 03: Baseline Model Comparison (Held-Out Participant Cross-Validation)\n",
            "Evaluates DummyClassifier, Logistic Regression, Random Forest, and XGBoost under GroupKFold CV."
        ]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "import os\n",
            "import sys\n",
            "sys.path.insert(0, os.path.abspath('..'))\n\n",
            "from backend.app.data.synthetic_adapter import SyntheticDatasetAdapter\n",
            "from backend.app.evaluation.evaluator import ExperimentEvaluator\n\n",
            "cohort = SyntheticDatasetAdapter().generate_full_benchmark_cohort(n_participants=8)\n",
            "evaluator = ExperimentEvaluator()\n",
            "results = evaluator.run_experiment_1_baselines(cohort)\n",
            "for m_name, m_res in results['models'].items():\n",
            "    print(f\"{m_name.upper()}: ROC-AUC={m_res['roc_auc']:.3f}, Balanced Acc={m_res['balanced_accuracy']:.3f}, F1={m_res['f1']:.3f}\")"
        ]}
    ]
    with open("notebooks/03_baseline_models.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb3_cells), f, indent=2)

    # 04_personalized_calibration.ipynb
    nb4_cells = [
        {"cell_type": "markdown", "metadata": {}, "source": [
            "# Notebook 04: Personalized Calibration (Mode A vs. Mode B)\n",
            "Tests whether participant-specific z-score calibration using neutral trials improves classification over population baselines."
        ]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "import os\n",
            "import sys\n",
            "sys.path.insert(0, os.path.abspath('..'))\n\n",
            "from backend.app.data.synthetic_adapter import SyntheticDatasetAdapter\n",
            "from backend.app.evaluation.evaluator import ExperimentEvaluator\n\n",
            "cohort = SyntheticDatasetAdapter().generate_full_benchmark_cohort(n_participants=8)\n",
            "evaluator = ExperimentEvaluator()\n",
            "res = evaluator.run_experiment_2_personalization_ablation(cohort)\n",
            "print('Mode A (Population Baseline) Balanced Acc:', res['population_baseline']['balanced_accuracy'])\n",
            "print('Mode B (Personalized QPTC) Balanced Acc:   ', res['personalized_qptc']['balanced_accuracy'])\n",
            "print('Delta Balanced Accuracy:                    ', res['delta_balanced_accuracy'])"
        ]}
    ]
    with open("notebooks/04_personalized_calibration.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb4_cells), f, indent=2)

    # 05_temporal_quality_ablation.ipynb
    nb5_cells = [
        {"cell_type": "markdown", "metadata": {}, "source": [
            "# Notebook 05: Temporal Window and Quality Abstention Ablation\n",
            "Analyzes temporal window contributions and computes the coverage versus error trade-off curve."
        ]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "import os\n",
            "import sys\n",
            "sys.path.insert(0, os.path.abspath('..'))\n\n",
            "from backend.app.data.synthetic_adapter import SyntheticDatasetAdapter\n",
            "from backend.app.evaluation.evaluator import ExperimentEvaluator\n\n",
            "cohort = SyntheticDatasetAdapter().generate_full_benchmark_cohort(n_participants=8)\n",
            "evaluator = ExperimentEvaluator()\n",
            "win_res = evaluator.run_experiment_3_temporal_window_ablation(cohort)\n",
            "for win_name, w_data in win_res['windows'].items():\n",
            "    print(f\"{win_name}: Balanced Acc={w_data['balanced_accuracy']:.3f}\")\n\n",
            "tradeoff = evaluator.run_experiment_4_quality_abstention(cohort)\n",
            "print('Quality Abstention Trade-off:')\n",
            "for row in tradeoff['tradeoff_curve']:\n",
            "    print(f\"  Threshold={row['quality_threshold']}: Coverage={row['coverage']:.2%}, Error Rate={row['error_rate']:.2%}\")"
        ]}
    ]
    with open("notebooks/05_temporal_quality_ablation.ipynb", "w", encoding="utf-8") as f:
        json.dump(make_notebook(nb5_cells), f, indent=2)

    print("All 5 Jupyter research notebooks generated successfully.")


if __name__ == "__main__":
    main()
