"""
Repository layer providing a clean abstraction over the SQLite/SQLAlchemy database.
Enables pluggable storage backend replacement without changing business logic.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import SessionModel, CalibrationModel, TrialModel, FeatureModel, ExperimentRunModel


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session_id: str, participant_pseudonym: str, has_consented: bool, camera_permitted: bool, notes: Optional[str] = None) -> SessionModel:
        obj = SessionModel(
            id=session_id,
            participant_pseudonym=participant_pseudonym,
            has_consented=has_consented,
            camera_permitted=camera_permitted,
            notes=notes
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, session_id: str) -> Optional[SessionModel]:
        return self.db.query(SessionModel).filter(SessionModel.id == session_id).first()

    def list_all(self, limit: int = 50) -> List[SessionModel]:
        return self.db.query(SessionModel).order_by(SessionModel.created_at.desc()).limit(limit).all()

    def delete(self, session_id: str) -> bool:
        obj = self.get_by_id(session_id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False


class CalibrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        calibration_id: str,
        session_id: str,
        point_count: int,
        completion_ratio: float,
        mean_spatial_error_px: Optional[float],
        quality_status: str,
        baseline_stats: Optional[Dict[str, Any]] = None
    ) -> CalibrationModel:
        obj = CalibrationModel(
            id=calibration_id,
            session_id=session_id,
            point_count=point_count,
            completion_ratio=completion_ratio,
            mean_spatial_error_px=mean_spatial_error_px,
            quality_status=quality_status,
            baseline_stats=baseline_stats
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_session_id(self, session_id: str) -> List[CalibrationModel]:
        return self.db.query(CalibrationModel).filter(CalibrationModel.session_id == session_id).order_by(CalibrationModel.created_at.desc()).all()


class TrialRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        trial_id: str,
        session_id: str,
        trial_number: int,
        stimulus_id: str,
        stimulus_name: str,
        condition: str,
        familiarity_ground_truth: Optional[int],
        duration_ms: float,
        onset_timestamp_ms: float,
        samples_json: List[Dict[str, Any]],
        quality_json: Optional[Dict[str, Any]] = None
    ) -> TrialModel:
        obj = TrialModel(
            id=trial_id,
            session_id=session_id,
            trial_number=trial_number,
            stimulus_id=stimulus_id,
            stimulus_name=stimulus_name,
            condition=condition,
            familiarity_ground_truth=familiarity_ground_truth,
            duration_ms=duration_ms,
            onset_timestamp_ms=onset_timestamp_ms,
            samples_json=samples_json,
            quality_json=quality_json
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, trial_id: str) -> Optional[TrialModel]:
        return self.db.query(TrialModel).filter(TrialModel.id == trial_id).first()

    def get_by_session_id(self, session_id: str) -> List[TrialModel]:
        return self.db.query(TrialModel).filter(TrialModel.session_id == session_id).order_by(TrialModel.trial_number.asc()).all()


class FeatureRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        feature_id: str,
        session_id: str,
        trial_id: str,
        w0_500_json: Dict[str, Any],
        w500_1000_json: Dict[str, Any],
        w1000_2000_json: Dict[str, Any],
        w_overall_json: Dict[str, Any],
        norm_mean_fixation_diff: Optional[float] = None,
        norm_first_fixation_diff: Optional[float] = None,
        norm_fixation_count_diff: Optional[float] = None,
        quality_status: str = "acceptable",
        abstention_reason: str = "none",
        is_abstained: bool = False,
        predicted_label: Optional[int] = None,
        calibrated_probability: Optional[float] = None,
        shap_json: Optional[List[Dict[str, Any]]] = None
    ) -> FeatureModel:
        obj = FeatureModel(
            id=feature_id,
            session_id=session_id,
            trial_id=trial_id,
            w0_500_json=w0_500_json,
            w500_1000_json=w500_1000_json,
            w1000_2000_json=w1000_2000_json,
            w_overall_json=w_overall_json,
            norm_mean_fixation_diff=norm_mean_fixation_diff,
            norm_first_fixation_diff=norm_first_fixation_diff,
            norm_fixation_count_diff=norm_fixation_count_diff,
            quality_status=quality_status,
            abstention_reason=abstention_reason,
            is_abstained=is_abstained,
            predicted_label=predicted_label,
            calibrated_probability=calibrated_probability,
            shap_json=shap_json
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_session_id(self, session_id: str) -> List[FeatureModel]:
        return self.db.query(FeatureModel).filter(FeatureModel.session_id == session_id).all()


class ExperimentRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_run(
        self,
        experiment_id: str,
        experiment_name: str,
        dataset_name: str,
        configuration: Dict[str, Any],
        metrics_summary: Dict[str, Any],
        ablation_results: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> ExperimentRunModel:
        obj = ExperimentRunModel(
            id=experiment_id,
            experiment_name=experiment_name,
            dataset_name=dataset_name,
            configuration=configuration,
            metrics_summary=metrics_summary,
            ablation_results=ablation_results,
            notes=notes
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, experiment_id: str) -> Optional[ExperimentRunModel]:
        return self.db.query(ExperimentRunModel).filter(ExperimentRunModel.id == experiment_id).first()

    def list_all(self, limit: int = 50) -> List[ExperimentRunModel]:
        return self.db.query(ExperimentRunModel).order_by(ExperimentRunModel.created_at.desc()).limit(limit).all()
