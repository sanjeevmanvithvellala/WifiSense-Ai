import {
  Environment,
  Dataset,
  MLModel,
  Experiment,
  Prediction,
  EventLog,
  HealthStatus
} from '../types';

const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errMsg = `API Error: ${res.status} ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errMsg = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
    } catch (_) {}
    throw new Error(errMsg);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Health
  getHealth: (): Promise<HealthStatus> => 
    fetch(`${API_BASE}/health`).then((res) => handleResponse<HealthStatus>(res)),

  // Environments
  getEnvironments: (): Promise<Environment[]> => 
    fetch(`${API_BASE}/environments`).then((res) => handleResponse<Environment[]>(res)),

  createEnvironment: (data: Partial<Environment>): Promise<Environment> =>
    fetch(`${API_BASE}/environments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then((res) => handleResponse<Environment>(res)),

  updateEnvironment: (id: string, data: Partial<Environment>): Promise<Environment> =>
    fetch(`${API_BASE}/environments/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then((res) => handleResponse<Environment>(res)),

  deleteEnvironment: (id: string): Promise<void> =>
    fetch(`${API_BASE}/environments/${id}`, { method: 'DELETE' }).then((res) => handleResponse<void>(res)),

  calibrateEnvironment: (id: string): Promise<any> =>
    fetch(`${API_BASE}/environments/${id}/calibrate`, { method: 'POST' }).then((res) => handleResponse<any>(res)),

  // Datasets
  getDatasets: (): Promise<Dataset[]> =>
    fetch(`${API_BASE}/datasets`).then((res) => handleResponse<Dataset[]>(res)),

  registerDataset: (data: Partial<Dataset>): Promise<Dataset> =>
    fetch(`${API_BASE}/datasets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then((res) => handleResponse<Dataset>(res)),

  inspectDataset: (id: string): Promise<any> =>
    fetch(`${API_BASE}/datasets/${id}/inspect`).then((res) => handleResponse<any>(res)),

  uploadCSIFile: (file: File, environmentType: string, activityLabel: string): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('environment_type', environmentType);
    formData.append('activity_label', activityLabel);
    return fetch(`${API_BASE}/datasets/upload`, {
      method: 'POST',
      body: formData,
    }).then((res) => handleResponse<any>(res));
  },

  // Models
  getModels: (): Promise<MLModel[]> =>
    fetch(`${API_BASE}/models`).then((res) => handleResponse<MLModel[]>(res)),

  getArchitectures: (): Promise<{ classifiers: string[]; anomaly_detectors: string[] }> =>
    fetch(`${API_BASE}/models/architectures`).then((res) => handleResponse<{ classifiers: string[]; anomaly_detectors: string[] }>(res)),

  getModelsComparison: (): Promise<{ comparison: any[] }> =>
    fetch(`${API_BASE}/models/comparison`).then((res) => handleResponse<{ comparison: any[] }>(res)),

  activateModel: (id: string): Promise<any> =>
    fetch(`${API_BASE}/models/${id}/activate`, { method: 'POST' }).then((res) => handleResponse<any>(res)),

  // Experiments
  getExperiments: (): Promise<Experiment[]> =>
    fetch(`${API_BASE}/experiments`).then((res) => handleResponse<Experiment[]>(res)),

  runExperiment: (data: any): Promise<Experiment> =>
    fetch(`${API_BASE}/experiments/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then((res) => handleResponse<Experiment>(res)),

  getExperiment: (id: string): Promise<Experiment> =>
    fetch(`${API_BASE}/experiments/${id}`).then((res) => handleResponse<Experiment>(res)),

  // Predictions & Events
  getPredictions: (limit = 50, env?: string, act?: string, onlyAnomalies = false): Promise<Prediction[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (env) params.append('environment', env);
    if (act) params.append('activity', act);
    if (onlyAnomalies) params.append('only_anomalies', 'true');
    return fetch(`${API_BASE}/predictions?${params}`).then((res) => handleResponse<Prediction[]>(res));
  },

  getEvents: (limit = 50, severity?: string, env?: string): Promise<EventLog[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (severity) params.append('severity', severity);
    if (env) params.append('environment', env);
    return fetch(`${API_BASE}/events?${params}`).then((res) => handleResponse<EventLog[]>(res));
  },

  // Analytics
  getAnalyticsSummary: (): Promise<any> =>
    fetch(`${API_BASE}/analytics/summary`).then((res) => handleResponse<any>(res)),

  // Settings
  getSettings: (): Promise<Record<string, { value: any; description: string }>> =>
    fetch(`${API_BASE}/settings`).then((res) => handleResponse<Record<string, { value: any; description: string }>>(res)),

  updateSettings: (data: Record<string, any>): Promise<any> =>
    fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then((res) => handleResponse<any>(res)),

  // Replay
  controlReplay: (data: {
    action: 'play' | 'pause' | 'resume' | 'stop' | 'reset';
    source_mode?: 'synthetic' | 'hardware_udp' | 'pc_wifi';
    dataset_id?: string;
    environment_type?: string;
    activity_scenario?: string;
    playback_speed?: number;
    add_anomaly?: boolean;
  }): Promise<any> =>
    fetch(`${API_BASE}/replay/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then((res) => handleResponse<any>(res)),

  getReplayStatus: (): Promise<any> =>
    fetch(`${API_BASE}/replay/status`).then((res) => handleResponse<any>(res)),
};
