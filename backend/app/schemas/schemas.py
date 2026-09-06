"""
Pydantic API Request/Response Schemas for WiFiSense AI.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# Environment Schemas
class EnvironmentBase(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = ""
    multipath_scale: Optional[float] = 1.0
    noise_floor: Optional[float] = 0.05
    is_calibrated: Optional[bool] = False
    calibration_data: Optional[Dict[str, Any]] = {}


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    multipath_scale: Optional[float] = None
    noise_floor: Optional[float] = None
    is_calibrated: Optional[bool] = None
    calibration_data: Optional[Dict[str, Any]] = None


class EnvironmentOut(EnvironmentBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Dataset Schemas
class DatasetBase(BaseModel):
    id: str
    name: str
    adapter_id: str
    is_synthetic: bool = False
    activities: List[str] = []
    environments: List[str] = []
    subjects: List[str] = []
    sampling_rate: float = 50.0
    subcarriers: int = 64
    antennas: int = 1
    bandwidth: float = 20.0
    csi_representation: str = "amplitude"
    source_path: Optional[str] = None
    status: str = "Ready"
    license: str = "Open"
    description: Optional[str] = ""


class DatasetCreate(DatasetBase):
    pass


class DatasetOut(DatasetBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Model Schemas
class MLModelBase(BaseModel):
    id: str
    name: str
    architecture: str
    version: str = "1.0.0"
    dataset_id: Optional[str] = None
    is_synthetic_trained: bool = True
    training_environments: List[str] = []
    test_environments: List[str] = []
    classes: List[str] = []
    metrics: Dict[str, Any] = {}
    model_path: Optional[str] = None
    status: str = "Trained"


class MLModelCreate(MLModelBase):
    pass


class MLModelOut(MLModelBase):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Experiment Schemas
class ExperimentRunRequest(BaseModel):
    name: Optional[str] = None
    experiment_type: str = "cross_environment"  # 'same_environment', 'cross_environment', 'multi_environment', 'adaptation'
    dataset_id: str = "synthetic_demo_dataset"
    training_environments: List[str] = ["Office"]
    test_environments: List[str] = ["Classroom"]
    model_architecture: str = "Random Forest"
    random_seed: int = 42
    max_samples_per_env: int = 40


class ExperimentOut(BaseModel):
    id: str
    name: str
    experiment_type: str
    dataset_id: str
    is_synthetic: bool
    training_environments: List[str]
    test_environments: List[str]
    model_architecture: str
    random_seed: int
    training_samples_count: int
    test_samples_count: int
    classes: List[str]
    metrics: Dict[str, Any]
    adaptation_comparison: Optional[Dict[str, Any]] = None
    duration_sec: float
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Prediction & Event Schemas
class PredictionOut(BaseModel):
    id: int
    timestamp: float
    environment_id: Optional[str] = None
    environment_type: str
    activity: str
    confidence: float
    presence: str
    anomaly_score: float
    is_anomaly: bool
    is_synthetic: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventOut(BaseModel):
    id: int
    timestamp: float
    event_type: str
    title: str
    description: Optional[str] = ""
    severity: str
    environment_id: Optional[str] = None
    environment_type: str
    confidence: float
    is_synthetic: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Live Stream / Replay Request
class ReplayControlRequest(BaseModel):
    action: str = "play"  # 'play', 'pause', 'stop', 'reset'
    source_mode: Optional[str] = "synthetic"  # 'synthetic', 'hardware_udp', 'pc_wifi'
    dataset_id: str = "synthetic_demo_dataset"
    environment_type: str = "Office"
    model_id: Optional[str] = None
    activity_scenario: Optional[str] = "Walking"
    playback_speed: float = 1.0
    add_anomaly: bool = False
