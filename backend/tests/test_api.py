"""
Integration Tests for FastAPI API Endpoints.
Verifies health checks, dataset auditing, session registration with consent,
trial ingestion with quality abstention, and experiment runs.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verifies that GET /api/health returns status online."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "GazeGuard AI Backend"
    assert "models" in data


def test_dataset_audit_endpoint():
    """Verifies that POST /api/datasets/audit returns valid audit report."""
    response = client.post("/api/datasets/audit?target=auto")
    assert response.status_code == 200
    report = response.json()
    assert "dataset_name" in report
    assert "data_quality_issues" in report
    assert "files_detected" in report


def test_consent_and_session_creation():
    """Verifies that session creation strictly enforces consent confirmation."""
    # Attempt creation without consent -> Must fail with 400
    bad_payload = {
        "participant_pseudonym": "P_UNCONSENTED",
        "has_read_information_sheet": False,
        "agreed_to_eye_tracking": False,
        "agreed_to_data_retention": False,
        "camera_permitted": False
    }
    bad_res = client.post("/api/sessions", json=bad_payload)
    assert bad_res.status_code == 400

    # Valid consent -> Succeeds
    good_payload = {
        "participant_pseudonym": "P_CONSENTED_01",
        "has_read_information_sheet": True,
        "agreed_to_eye_tracking": True,
        "agreed_to_data_retention": True,
        "camera_permitted": True
    }
    good_res = client.post("/api/sessions", json=good_payload)
    assert good_res.status_code == 200
    sess_data = good_res.json()
    assert "session_id" in sess_data
    assert sess_data["status"] == "active"


def test_trial_submission_and_abstention():
    """Tests trial submission and verifies quality evaluation response."""
    # Create valid session
    sess_res = client.post("/api/sessions", json={
        "participant_pseudonym": "P_TRIAL_TEST",
        "has_read_information_sheet": True,
        "agreed_to_eye_tracking": True,
        "agreed_to_data_retention": True,
        "camera_permitted": True
    })
    session_id = sess_res.json()["session_id"]

    import uuid
    unique_trial_id = f"TRIAL_API_{uuid.uuid4().hex[:8]}"
    trial_payload = {
        "trial_id": unique_trial_id,
        "stimulus_id": "STIM_WATCH",
        "stimulus_name": "Gold Watch",
        "condition": "probe",
        "familiarity_ground_truth": 1,
        "onset_timestamp_ms": 0.0,
        "duration_ms": 2000.0,
        "samples": [
            {"timestamp_ms": float(i * 16.6), "x": 0.5, "y": 0.5, "valid": True}
            for i in range(60)
        ]
    }
    trial_res = client.post(f"/api/trials?session_id={session_id}", json=trial_payload)
    assert trial_res.status_code == 200
    trial_data = trial_res.json()
    assert "status" in trial_data
    assert "quality_metrics" in trial_data
    assert "windows" in trial_data


def test_experiment_run_endpoint():
    """Verifies that POST /api/experiments/run executes baseline comparison."""
    exp_res = client.post("/api/experiments/run", json={
        "experiment_number": 1,
        "dataset": "synthetic_benchmark"
    })
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["experiment_id"] == "EXP_01_BASELINES"
    assert "models" in exp_data
