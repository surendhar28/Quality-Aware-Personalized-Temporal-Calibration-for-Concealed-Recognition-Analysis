export type QualityStatus = 'excellent' | 'acceptable' | 'marginal' | 'insufficient';

export type StimulusCondition = 'probe' | 'irrelevant' | 'target' | 'calibration';

export type ModelType = 'dummy' | 'logistic_regression' | 'random_forest' | 'xgboost';

export interface GazeSample {
  timestamp_ms: number;
  x: number;
  y: number;
  valid: boolean;
  pupil_diameter?: number;
  tracker_confidence?: number;
}

export interface FixationEvent {
  start_time_ms: number;
  end_time_ms: number;
  duration_ms: number;
  center_x: number;
  center_y: number;
  stimulus_id?: string;
}

export interface QualityMetrics {
  total_samples: number;
  valid_samples: number;
  valid_ratio: number;
  missing_ratio: number;
  mean_sampling_hz: number;
  timestamp_jitter_ms: number;
  samples_in_first_500ms: number;
  valid_ratio_first_500ms: number;
  status: QualityStatus;
  warnings: string[];
}

export interface WindowFeatures {
  window_name: string;
  start_ms: number;
  end_ms: number;
  fixation_count: number;
  total_fixation_duration_ms: number;
  mean_fixation_duration_ms: number;
  median_fixation_duration_ms: number;
  first_fixation_duration_ms: number;
  first_fixation_latency_ms: number | null;
  valid_sample_ratio: number;
}

export interface SHAPContribution {
  feature_name: string;
  feature_value: number;
  shap_value: number;
}

export interface TrialData {
  trial_id: string;
  stimulus_id: string;
  stimulus_name: string;
  condition: StimulusCondition;
  familiarity_ground_truth?: number;
  onset_timestamp_ms: number;
  duration_ms: number;
  samples: GazeSample[];
  precomputed_fixations?: FixationEvent[];
}

export interface PredictionResult {
  status: 'accepted' | 'insufficient_evidence' | 'error';
  prediction: number | null;
  probability: number | null;
  confidence_interval?: number[];
  abstention_reason?: string;
  quality_metrics: QualityMetrics;
  shap_contributions: SHAPContribution[];
  scientific_disclaimer: string;
}

export interface DatasetAuditReport {
  dataset_name: string;
  provenance_doi: string;
  license: string;
  storage_path: string;
  files_detected: number;
  participants_found: number;
  total_trials_parsed: number;
  sampling_rate_hz: number | null;
  has_raw_gaze: boolean;
  has_precomputed_fixations: boolean;
  data_quality_issues: string[];
  audit_passed: boolean;
  mode: 'real' | 'synthetic';
  timestamp: string;
}

export interface SessionState {
  sessionId: string;
  participantPseudonym: string;
  hasConsented: boolean;
  cameraPermitted: boolean;
  calibrationCompleted: boolean;
  calibrationQuality?: QualityStatus;
}
