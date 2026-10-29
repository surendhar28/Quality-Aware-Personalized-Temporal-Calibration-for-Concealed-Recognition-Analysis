"""
Machine Learning Model Pipeline and Probability Calibration for GazeGuard AI.
Implements scikit-learn compatible pipelines for Dummy, Logistic Regression, Random Forest, and XGBoost.
Provides Sigmoid/Isotonic probability calibration and SHAP feature attribution.
"""

import os
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import joblib

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline
import shap

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from ..schemas.canonical import ModelType, SHAPContribution


class GazeMLPipeline:
    """
    Standardized, leak-free machine learning training, calibration, and explainability pipeline.
    """

    SUPPORTED_MODELS = [
        ModelType.DUMMY,
        ModelType.LOGISTIC_REGRESSION,
        ModelType.RANDOM_FOREST,
    ]
    if HAS_XGBOOST:
        SUPPORTED_MODELS.append(ModelType.XGBOOST)

    def __init__(
        self,
        model_type: ModelType = ModelType.RANDOM_FOREST,
        calibrate_probabilities: bool = True,
        calibration_method: str = "sigmoid",
        random_state: int = 42
    ):
        self.model_type = model_type
        self.calibrate_probabilities = calibrate_probabilities
        self.calibration_method = calibration_method
        self.random_state = random_state
        
        self.pipeline: Optional[Pipeline] = None
        self.feature_names: List[str] = []
        self.is_fitted: bool = False
        self.shap_explainer: Optional[Any] = None

    def _build_raw_classifier(self) -> BaseEstimator:
        if self.model_type == ModelType.DUMMY:
            return DummyClassifier(strategy="prior", random_state=self.random_state)
        elif self.model_type == ModelType.LOGISTIC_REGRESSION:
            return LogisticRegression(penalty="l2", C=1.0, max_iter=1000, random_state=self.random_state)
        elif self.model_type == ModelType.RANDOM_FOREST:
            return RandomForestClassifier(n_estimators=100, max_depth=4, min_samples_split=3, random_state=self.random_state)
        elif self.model_type == ModelType.XGBOOST:
            if not HAS_XGBOOST:
                raise RuntimeError("XGBoost package is not installed.")
            return XGBClassifier(n_estimators=80, max_depth=3, learning_rate=0.05, eval_metric="logloss", random_state=self.random_state)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        """
        Fits preprocessor, classifier, and probability calibrator on training data.
        """
        self.feature_names = feature_names
        base_clf = self._build_raw_classifier()

        # Build pipeline with median imputation and robust scaling
        steps = [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
            ("classifier", base_clf)
        ]
        self.pipeline = Pipeline(steps)

        # Calibrate probabilities if requested (and model is not Dummy)
        if self.calibrate_probabilities and self.model_type != ModelType.DUMMY and len(np.unique(y)) > 1:
            # Fit calibrated classifier using 3-fold cross-validation inside training set
            calibrated_pipe = CalibratedClassifierCV(
                estimator=self.pipeline,
                method=self.calibration_method,
                cv=min(3, np.min(np.bincount(y)))
            )
            calibrated_pipe.fit(X, y)
            self.pipeline = calibrated_pipe
        else:
            self.pipeline.fit(X, y)

        self.is_fitted = True
        self._init_shap_explainer(X)

    def _init_shap_explainer(self, X_train: np.ndarray):
        """Initializes SHAP explainer on preprocessed training samples."""
        try:
            if self.model_type in (ModelType.RANDOM_FOREST, ModelType.XGBOOST):
                # Retrieve base estimator from pipeline
                if isinstance(self.pipeline, CalibratedClassifierCV):
                    base_est = self.pipeline.calibrated_classifiers_[0].estimator.named_steps["classifier"]
                else:
                    base_est = self.pipeline.named_steps["classifier"]
                self.shap_explainer = shap.TreeExplainer(base_est)
            elif self.model_type == ModelType.LOGISTIC_REGRESSION:
                if isinstance(self.pipeline, CalibratedClassifierCV):
                    base_pipe = self.pipeline.calibrated_classifiers_[0].estimator
                else:
                    base_pipe = self.pipeline
                # Linear explainer on transformed features
                imputer = base_pipe.named_steps["imputer"]
                scaler = base_pipe.named_steps["scaler"]
                X_trans = scaler.transform(imputer.transform(X_train))
                self.shap_explainer = shap.LinearExplainer(base_pipe.named_steps["classifier"], X_trans)
        except Exception:
            self.shap_explainer = None

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns calibrated probabilities for [class_0, class_1]."""
        if not self.is_fitted or self.pipeline is None:
            raise RuntimeError("Pipeline must be fitted before predict_proba.")
        return self.pipeline.predict_proba(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Returns binary prediction."""
        if not self.is_fitted or self.pipeline is None:
            raise RuntimeError("Pipeline must be fitted before predict.")
        return self.pipeline.predict(X)

    def explain_instance(self, x_single: np.ndarray) -> List[SHAPContribution]:
        """
        Computes SHAP feature contributions for a single trial sample.
        Returns top features contributing to the familiarity classification.
        """
        if not self.is_fitted or self.shap_explainer is None:
            return []

        x_2d = x_single.reshape(1, -1)
        contributions: List[SHAPContribution] = []

        try:
            # Transform instance through pipeline preprocessing
            if isinstance(self.pipeline, CalibratedClassifierCV):
                base_pipe = self.pipeline.calibrated_classifiers_[0].estimator
            else:
                base_pipe = self.pipeline

            imputer = base_pipe.named_steps["imputer"]
            scaler = base_pipe.named_steps["scaler"]
            x_trans = scaler.transform(imputer.transform(x_2d))

            shap_vals = self.shap_explainer.shap_values(x_trans)
            
            # Handle different SHAP output formats (binary class index 1)
            if isinstance(shap_vals, list) and len(shap_vals) >= 2:
                vals = shap_vals[1][0]
            elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
                vals = shap_vals[0, :, 1]
            elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 2:
                vals = shap_vals[0]
            else:
                vals = np.array(shap_vals).flatten()

            for i, name in enumerate(self.feature_names):
                if i < len(vals):
                    contributions.append(SHAPContribution(
                        feature_name=name,
                        feature_value=round(float(x_single[i]), 4),
                        shap_value=round(float(vals[i]), 4)
                    ))

            # Sort descending by absolute impact
            contributions.sort(key=lambda c: abs(c.shap_value), reverse=True)
            return contributions[:8] # Return top 8 most influential features

        except Exception:
            return []

    def save_artifact(self, filepath: str):
        """Persists trained model and metadata."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        payload = {
            "pipeline": self.pipeline,
            "model_type": self.model_type.value,
            "feature_names": self.feature_names,
            "calibrate_probabilities": self.calibrate_probabilities,
            "calibration_method": self.calibration_method,
            "version": "1.0.0"
        }
        joblib.dump(payload, filepath)

    @classmethod
    def load_artifact(cls, filepath: str) -> "GazeMLPipeline":
        """Loads trusted local model artifact."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model artifact not found at {filepath}")
        payload = joblib.load(filepath)
        instance = cls(
            model_type=ModelType(payload["model_type"]),
            calibrate_probabilities=payload.get("calibrate_probabilities", True),
            calibration_method=payload.get("calibration_method", "sigmoid")
        )
        instance.pipeline = payload["pipeline"]
        instance.feature_names = payload["feature_names"]
        instance.is_fitted = True
        return instance
