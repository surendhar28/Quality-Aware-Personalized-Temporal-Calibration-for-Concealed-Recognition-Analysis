"""
SQLAlchemy ORM models for GazeGuard AI.
Stores pseudonymous sessions, calibrations, trials, feature records, and experiment runs.
Raw video is explicitly NOT stored by default.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .db import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True, index=True)
    participant_pseudonym = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    has_consented = Column(Boolean, default=False)
    camera_permitted = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    calibrations = relationship("CalibrationModel", back_populates="session", cascade="all, delete-orphan")
    trials = relationship("TrialModel", back_populates="session", cascade="all, delete-orphan")
    features = relationship("FeatureModel", back_populates="session", cascade="all, delete-orphan")


class CalibrationModel(Base):
    __tablename__ = "calibrations"

    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    point_count = Column(Integer, default=9)
    completion_ratio = Column(Float, default=0.0)
    mean_spatial_error_px = Column(Float, nullable=True)
    quality_status = Column(String(32), default="acceptable")
    baseline_stats = Column(JSON, nullable=True)

    session = relationship("SessionModel", back_populates="calibrations")


class TrialModel(Base):
    __tablename__ = "trials"

    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    trial_number = Column(Integer, nullable=False)
    stimulus_id = Column(String(64), nullable=False)
    stimulus_name = Column(String(128), nullable=False)
    condition = Column(String(32), nullable=False)  # probe, irrelevant, target, calibration
    familiarity_ground_truth = Column(Integer, nullable=True)  # 0 or 1
    duration_ms = Column(Float, default=2000.0)
    onset_timestamp_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Stored gaze samples and quality metrics (JSON)
    samples_json = Column(JSON, nullable=False)
    quality_json = Column(JSON, nullable=True)

    session = relationship("SessionModel", back_populates="trials")
    feature_record = relationship("FeatureModel", back_populates="trial", uselist=False, cascade="all, delete-orphan")


class FeatureModel(Base):
    __tablename__ = "features"

    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    trial_id = Column(String(64), ForeignKey("trials.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Temporal window feature metrics (JSON)
    w0_500_json = Column(JSON, nullable=False)
    w500_1000_json = Column(JSON, nullable=False)
    w1000_2000_json = Column(JSON, nullable=False)
    w_overall_json = Column(JSON, nullable=False)
    
    # Personalized normalized differences
    norm_mean_fixation_diff = Column(Float, nullable=True)
    norm_first_fixation_diff = Column(Float, nullable=True)
    norm_fixation_count_diff = Column(Float, nullable=True)
    
    # Status and abstention
    quality_status = Column(String(32), default="acceptable")
    abstention_reason = Column(String(64), default="none")
    is_abstained = Column(Boolean, default=False)
    
    # Model inference results if run
    predicted_label = Column(Integer, nullable=True)
    calibrated_probability = Column(Float, nullable=True)
    shap_json = Column(JSON, nullable=True)

    session = relationship("SessionModel", back_populates="features")
    trial = relationship("TrialModel", back_populates="feature_record")


class ExperimentRunModel(Base):
    __tablename__ = "experiment_runs"

    id = Column(String(64), primary_key=True, index=True)
    experiment_name = Column(String(128), nullable=False)
    dataset_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    configuration = Column(JSON, nullable=False)
    metrics_summary = Column(JSON, nullable=False)
    ablation_results = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
