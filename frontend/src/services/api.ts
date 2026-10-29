import {
  DatasetAuditReport,
  TrialData,
  PredictionResult,
  QualityMetrics,
} from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to reach backend service');
  return res.json();
}

export async function fetchDatasets(): Promise<any> {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error('Failed to fetch dataset catalog');
  return res.json();
}

export async function runDatasetAudit(target: 'real' | 'synthetic' | 'auto' = 'auto'): Promise<DatasetAuditReport> {
  const res = await fetch(`${API_BASE}/datasets/audit?target=${target}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to execute dataset audit');
  return res.json();
}

export async function createSession(payload: {
  participant_pseudonym: string;
  has_read_information_sheet: boolean;
  agreed_to_eye_tracking: boolean;
  agreed_to_data_retention: boolean;
  camera_permitted: boolean;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to create session' }));
    throw new Error(err.detail || 'Consent must be confirmed');
  }
  return res.json();
}

export async function submitCalibration(payload: {
  session_id: string;
  points: Array<{ target_x: number; target_y: number; estimated_x?: number; estimated_y?: number }>;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/calibration`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to record calibration');
  return res.json();
}

export async function submitTrial(sessionId: string, trial: TrialData): Promise<any> {
  const res = await fetch(`${API_BASE}/trials?session_id=${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trial),
  });
  if (!res.ok) throw new Error('Failed to submit trial data');
  return res.json();
}

export async function extractFeatures(trial: TrialData): Promise<any> {
  const res = await fetch(`${API_BASE}/features/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trial),
  });
  if (!res.ok) throw new Error('Failed to extract features');
  return res.json();
}

export async function runPrediction(payload: {
  trial_id: string;
  features: Record<string, number>;
  quality_metrics: QualityMetrics;
  quality_threshold?: number;
}): Promise<PredictionResult> {
  const res = await fetch(`${API_BASE}/predictions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to execute prediction');
  return res.json();
}

export async function runResearchExperiment(expNumber: number, dataset: string = 'synthetic_benchmark'): Promise<any> {
  const res = await fetch(`${API_BASE}/experiments/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ experiment_number: expNumber, dataset }),
  });
  if (!res.ok) throw new Error('Failed to run experiment');
  return res.json();
}

export async function fetchSessionReport(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/reports/${sessionId}`);
  if (!res.ok) throw new Error('Failed to load session report');
  return res.json();
}

export async function fetchSettings(): Promise<any> {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to load settings');
  return res.json();
}

export async function updateSettings(settings: Record<string, any>): Promise<any> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
}
