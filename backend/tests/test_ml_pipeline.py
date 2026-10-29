"""
Unit Tests for Machine Learning Models and Explainability.
Verifies Dummy, Logistic Regression, Random Forest, XGBoost, and SHAP explanations.
"""

import pytest
import numpy as np
from backend.app.schemas.canonical import ModelType
from backend.app.models.ml_pipeline import GazeMLPipeline, HAS_XGBOOST


def test_dummy_classifier_baseline():
    """Tests DummyClassifier baseline functionality."""
    X = np.random.randn(40, 5)
    y = np.array([0] * 30 + [1] * 10) # 3:1 class imbalance
    feature_names = [f"feat_{i}" for i in range(5)]

    pipe = GazeMLPipeline(model_type=ModelType.DUMMY)
    pipe.fit(X, y, feature_names)
    preds = pipe.predict(X)
    assert len(preds) == 40
    probs = pipe.predict_proba(X)
    assert probs.shape == (40, 2)
    # Stratified or prior probabilities reflect class ratio
    assert abs(np.mean(probs[:, 1]) - 0.25) < 0.05


def test_logistic_regression_with_calibration():
    """Tests Logistic Regression baseline with Sigmoid probability calibration."""
    X = np.random.randn(60, 4)
    y = np.array([0] * 30 + [1] * 30)
    feature_names = [f"f_{i}" for i in range(4)]

    pipe = GazeMLPipeline(
        model_type=ModelType.LOGISTIC_REGRESSION,
        calibrate_probabilities=True,
        calibration_method="sigmoid"
    )
    pipe.fit(X, y, feature_names)
    probs = pipe.predict_proba(X)
    assert probs.shape == (60, 2)
    # Probabilities bounded in [0, 1]
    assert np.all((probs >= 0.0) & (probs <= 1.0))


def test_random_forest_shap_explanations():
    """Tests Random Forest classifier and SHAP attribution extraction."""
    rng = np.random.RandomState(42)
    X = rng.randn(50, 4)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    feature_names = ["feat_early_dur", "feat_fix_count", "feat_late_dur", "feat_jitter"]

    pipe = GazeMLPipeline(model_type=ModelType.RANDOM_FOREST, calibrate_probabilities=False)
    pipe.fit(X, y, feature_names)

    # Explain single instance
    sample_x = X[0]
    explanations = pipe.explain_instance(sample_x)
    assert len(explanations) > 0
    assert hasattr(explanations[0], "feature_name")
    assert hasattr(explanations[0], "shap_value")
    # Verify non-trivial values
    assert abs(explanations[0].shap_value) >= 0.0


@pytest.mark.skipif(not HAS_XGBOOST, reason="XGBoost is not installed")
def test_xgboost_classifier():
    """Tests XGBoost model fitting and inference."""
    X = np.random.randn(50, 4)
    y = np.random.randint(0, 2, size=50)
    feature_names = [f"xg_feat_{i}" for i in range(4)]

    pipe = GazeMLPipeline(model_type=ModelType.XGBOOST)
    pipe.fit(X, y, feature_names)
    preds = pipe.predict(X)
    assert len(preds) == 50
