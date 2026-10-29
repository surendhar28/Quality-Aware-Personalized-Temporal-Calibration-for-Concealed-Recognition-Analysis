"""
GazeGuard AI - Schema Definitions
Canonical schemas and enums for eye tracking, CIT paradigms, feature engineering, and inference.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StimulusCondition(str, Enum):
    PROBE = "probe"               # Familiar / critical crime item
    IRRELEVANT = "irrelevant"     # Unfamiliar / neutral control item
    TARGET = "target"             # Explicit task control item (if CIT 3-stimulus variant)
    CALIBRATION = "calibration"   # Dedicated calibration stimulus


class FamiliarityLabel(int, Enum):
    UNFAMILIAR = 0
    FAMILIAR = 1


class QualityStatus(str, Enum):
    EXCELLENT = "excellent"
    ACCEPTABLE = "acceptable"
    MARGINAL = "marginal"
    INSUFFICIENT = "insufficient"


class AbstentionReason(str, Enum):
    NONE = "none"
    INSUFFICIENT_SAMPLES = "insufficient_valid_samples"
    EXCESSIVE_MISSING_DATA = "excessive_missing_rate"
    HIGH_TIMESTAMP_JITTER = "high_timestamp_jitter"
    FAILED_CALIBRATION = "failed_calibration"
    OUT_OF_BOUNDS_GAZE = "out_of_bounds_gaze"
    LOW_CONFIDENCE = "tracker_confidence_below_threshold"


class DataSourceType(str, Enum):
    ZENODO_18525952 = "zenodo_18525952"
    WEBGALLERY_WEBCAM = "webcam_webgazer"
    SYNTHETIC = "synthetic_fixture"


class ModelType(str, Enum):
    DUMMY = "dummy"
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"


# --- Gaze and Tracking Data Schemas ---

class GazeSample(BaseModel):
    timestamp_ms: float = Field(..., description="Timestamp in milliseconds from experiment or trial onset")
    x: float = Field(..., description="Normalized horizontal coordinate [0.0 - 1.0]")
    y: float = Field(..., description="Normalized vertical coordinate [0.0 - 1.0]")
    valid: bool = Field(True, description="Flag indicating if sample was tracked successfully")
    pupil_diameter: Optional[float] = Field(None, description="Pupil size if recorded by hardware")
    tracker_confidence: Optional[float] = Field(None, description="Tracker confidence [0.0 - 1.0] if provided by hardware")


class FixationEvent(BaseModel):
    start_time_ms: float
    end_time_ms: float
    duration_ms: float
    center_x: float
    center_y: float
    stimulus_id: Optional[str] = None


class TrialData(BaseModel):
    trial_id: str
    stimulus_id: str
    stimulus_name: str
    condition: StimulusCondition
    familiarity_ground_truth: Optional[FamiliarityLabel] = None
    onset_timestamp_ms: float
    duration_ms: float
    samples: List[GazeSample] = Field(default_factory=list)
    precomputed_fixations: Optional[List[FixationEvent]] = None
    aoi_bounds: Optional[Dict[str, float]] = Field(None, description="Area of Interest box {x_min, y_min, x_max, y_max}")


# --- Quality Schemas ---

class QualityMetrics(BaseModel):
    total_samples: int
    valid_samples: int
    valid_ratio: float
    missing_ratio: float
    mean_sampling_hz: float
    timestamp_jitter_ms: float
    samples_in_first_500ms: int
    valid_ratio_first_500ms: float
    status: QualityStatus
    warnings: List[str] = Field(default_factory=list)


# --- Feature Engineering Schemas ---

class WindowFeatures(BaseModel):
    window_name: str
    start_ms: float
    end_ms: float
    fixation_count: int
    total_fixation_duration_ms: float
    mean_fixation_duration_ms: float
    median_fixation_duration_ms: float
    first_fixation_duration_ms: float
    first_fixation_latency_ms: Optional[float]
    valid_sample_ratio: float


class TrialFeatureRecord(BaseModel):
    trial_id: str
    participant_id: str
    stimulus_id: str
    condition: StimulusCondition
    familiarity_label: Optional[int] = None
    quality_status: QualityStatus
    abstention_reason: AbstentionReason = AbstentionReason.NONE
    
    # Temporal Window Features
    w0_500: WindowFeatures
    w500_1000: WindowFeatures
    w1000_2000: WindowFeatures
    w_overall: WindowFeatures
    
    # Normalized Features (Personalized or Population)
    normalized_mean_fixation_diff: Optional[float] = None
    normalized_first_fixation_diff: Optional[float] = None
    normalized_fixation_count_diff: Optional[float] = None


# --- Calibration Schemas ---

class CalibrationTarget(BaseModel):
    point_index: int
    target_x: float
    target_y: float
    recorded_points: List[Dict[str, float]] = Field(default_factory=list)
    mean_estimated_x: Optional[float] = None
    mean_estimated_y: Optional[float] = None
    spatial_error_px: Optional[float] = None


class ParticipantCalibrationBaseline(BaseModel):
    participant_id: str
    calibration_trials_count: int
    baseline_mean_fixation_ms: float
    baseline_std_fixation_ms: float
    baseline_first_fixation_ms: float
    baseline_std_first_fixation_ms: float
    mean_spatial_error_px: Optional[float] = None
    calibration_quality: QualityStatus
    created_at: str


# --- Prediction and Inference Schemas ---

class PredictionRequest(BaseModel):
    trial_id: str
    features: Dict[str, float]
    quality_metrics: QualityMetrics
    participant_id: Optional[str] = None
    calibration_id: Optional[str] = None
    quality_threshold: float = Field(0.60, description="Minimum valid sample ratio for non-abstention")


class SHAPContribution(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float


class PredictionResult(BaseModel):
    status: str = Field(..., description="'accepted' or 'insufficient_evidence'")
    prediction: Optional[int] = Field(None, description="0 = unfamiliar, 1 = familiar (recognition pattern)")
    probability: Optional[float] = Field(None, description="Calibrated posterior probability of familiarity pattern [0.0 - 1.0]")
    confidence_interval: Optional[List[float]] = None
    abstention_reason: Optional[str] = None
    quality_metrics: QualityMetrics
    shap_contributions: List[SHAPContribution] = Field(default_factory=list)
    scientific_disclaimer: str = (
        "Research Instrument Notice: This estimation reflects experimental eye-movement familiarity patterns "
        "under controlled stimuli. It does NOT establish dishonesty, lying, guilt, or participant credibility."
    )


# --- Dataset Audit Schemas ---

class DatasetAuditReport(BaseModel):
    dataset_name: str
    provenance_doi: str
    license: str
    storage_path: str
    files_detected: int
    participants_found: int
    total_trials_parsed: int
    sampling_rate_hz: Optional[float]
    has_raw_gaze: bool
    has_precomputed_fixations: bool
    data_quality_issues: List[str]
    audit_passed: bool
    mode: str = Field("real", description="'real' or 'synthetic'")
    timestamp: str


# --- Session and Consent Schemas ---

class ConsentRequest(BaseModel):
    participant_pseudonym: str
    has_read_information_sheet: bool
    agreed_to_eye_tracking: bool
    agreed_to_data_retention: bool
    camera_permitted: bool


class SessionResponse(BaseModel):
    session_id: str
    participant_pseudonym: str
    created_at: str
    status: str
    message: str
