export type EnvironmentType = 
  | 'Residential'
  | 'Classroom'
  | 'Office'
  | 'Healthcare'
  | 'Industrial'
  | 'Hospitality'
  | 'Public Space'
  | 'Custom';

export interface Environment {
  id: string;
  name: string;
  type: EnvironmentType;
  description: string;
  multipath_scale: number;
  noise_floor: number;
  is_calibrated: boolean;
  calibration_data?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface Dataset {
  id: string;
  name: string;
  adapter_id: string;
  is_synthetic: boolean;
  activities: string[];
  environments: string[];
  subjects: string[];
  sampling_rate: number;
  subcarriers: number;
  antennas: number;
  bandwidth: number;
  csi_representation: string;
  source_path?: string;
  status: string;
  license: string;
  description?: string;
}

export interface MLModel {
  id: string;
  name: string;
  architecture: string;
  version: string;
  dataset_id?: string;
  is_synthetic_trained: boolean;
  training_environments: string[];
  test_environments: string[];
  classes: string[];
  metrics: {
    accuracy?: number;
    precision_macro?: number;
    recall_macro?: number;
    f1_macro?: number;
    f1_weighted?: number;
    labels?: string[];
    confusion_matrix?: number[][];
    per_class?: Record<string, { precision: number; recall: number; f1_score: number; support: number }>;
    inference_latency_ms_per_sample?: number;
    sample_count?: number;
  };
  model_path?: string;
  status: string;
  created_at?: string;
}

export interface Experiment {
  id: string;
  name: string;
  experiment_type: 'same_environment' | 'cross_environment' | 'multi_environment' | 'adaptation';
  dataset_id: string;
  is_synthetic: boolean;
  training_environments: string[];
  test_environments: string[];
  model_architecture: string;
  random_seed: number;
  training_samples_count: number;
  test_samples_count: number;
  classes: string[];
  metrics: {
    accuracy?: number;
    f1_macro?: number;
    precision_macro?: number;
    recall_macro?: number;
    confusion_matrix?: number[][];
    labels?: string[];
    per_class?: Record<string, any>;
  };
  adaptation_comparison?: {
    strategy: string;
    baseline_metrics: { accuracy: number; f1_macro: number };
    adapted_metrics: { accuracy: number; f1_macro: number };
    accuracy_delta: number;
    f1_macro_delta: number;
    adapted_sample_count: number;
  };
  duration_sec: number;
  status: string;
  created_at?: string;
}

export interface Prediction {
  id: number;
  timestamp: number;
  environment_type: string;
  activity: string;
  confidence: number;
  presence: string;
  anomaly_score: number;
  is_anomaly: boolean;
  is_synthetic: boolean;
  created_at?: string;
}

export interface EventLog {
  id: number;
  timestamp: number;
  event_type: string;
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  environment_type: string;
  confidence: number;
  is_synthetic: boolean;
  created_at?: string;
}

export interface ReplayFrame {
  type: string;
  timestamp: number;
  environment: string;
  dataset_id: string;
  is_synthetic: boolean;
  is_replay: boolean;
  source_mode: string;
  subcarrier_count: number;
  frame_amplitude: number[];
  heatmap_matrix: number[][];
  inference: {
    activity: string;
    confidence: number;
    class_probabilities?: Record<string, number>;
    presence: string;
    presence_confidence: number;
    anomaly_score: number;
    is_anomaly: boolean;
    is_synthetic: boolean;
    environment_type: string;
    dynamic_energy?: number;
    latency_ms?: number;
  };
}

export interface HealthStatus {
  status: string;
  timestamp: number;
  services: {
    backend: string;
    database: string;
    ml_engine: string;
    websocket: string;
    active_ws_connections: number;
  };
  system_resources: {
    cpu_percent: number;
    memory_percent: number;
    memory_used_mb: number;
    memory_total_mb: number;
  };
  active_classifier: string;
  active_anomaly_detector: string;
}
