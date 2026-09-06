"""
SQLAlchemy Database Entities for WiFiSense AI.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class Environment(Base):
    __tablename__ = "environments"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    type = Column(String(64), nullable=False)  # Residential, Classroom, Office, Healthcare, Industrial, etc.
    description = Column(Text, default="")
    multipath_scale = Column(Float, default=1.0)
    noise_floor = Column(Float, default=0.05)
    is_calibrated = Column(Boolean, default=False)
    calibration_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    predictions = relationship("PredictionRecord", back_populates="environment", cascade="all, delete-orphan")
    events = relationship("EventRecord", back_populates="environment", cascade="all, delete-orphan")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    adapter_id = Column(String(64), nullable=False)
    is_synthetic = Column(Boolean, default=False)
    activities = Column(JSON, default=list)
    environments = Column(JSON, default=list)
    subjects = Column(JSON, default=list)
    sampling_rate = Column(Float, default=50.0)
    subcarriers = Column(Integer, default=64)
    antennas = Column(Integer, default=1)
    bandwidth = Column(Float, default=20.0)
    csi_representation = Column(String(32), default="amplitude")
    source_path = Column(String(256), nullable=True)
    status = Column(String(64), default="Ready")
    license = Column(String(128), default="Open")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    samples = relationship("DatasetSample", back_populates="dataset", cascade="all, delete-orphan")


class DatasetSample(Base):
    __tablename__ = "dataset_samples"

    id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False)
    sample_id = Column(String(64), nullable=False)
    environment_type = Column(String(64), default="Office")
    activity_label = Column(String(64), default="Walking")
    subject_id = Column(String(64), nullable=True)
    sampling_rate = Column(Float, default=50.0)
    shape = Column(JSON, default=list)
    is_synthetic = Column(Boolean, default=False)
    preview_data = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="samples")


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    architecture = Column(String(64), nullable=False)  # Random Forest, SVM, 1D CNN, CNN-GRU, Transformer
    version = Column(String(32), default="1.0.0")
    dataset_id = Column(String(64), nullable=True)
    is_synthetic_trained = Column(Boolean, default=True)
    training_environments = Column(JSON, default=list)
    test_environments = Column(JSON, default=list)
    classes = Column(JSON, default=list)
    metrics = Column(JSON, default=dict)
    model_path = Column(String(256), nullable=True)
    status = Column(String(32), default="Trained")
    created_at = Column(DateTime, default=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    experiment_type = Column(String(64), nullable=False)  # same_environment, cross_environment, multi_environment, adaptation
    dataset_id = Column(String(64), nullable=False)
    is_synthetic = Column(Boolean, default=True)
    training_environments = Column(JSON, default=list)
    test_environments = Column(JSON, default=list)
    model_architecture = Column(String(64), nullable=False)
    random_seed = Column(Integer, default=42)
    training_samples_count = Column(Integer, default=0)
    test_samples_count = Column(Integer, default=0)
    classes = Column(JSON, default=list)
    metrics = Column(JSON, default=dict)
    adaptation_comparison = Column(JSON, nullable=True)
    duration_sec = Column(Float, default=0.0)
    status = Column(String(32), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, nullable=False)
    environment_id = Column(String(64), ForeignKey("environments.id"), nullable=True)
    environment_type = Column(String(64), default="Office")
    activity = Column(String(64), nullable=False)
    confidence = Column(Float, nullable=False)
    presence = Column(String(32), default="Present")
    anomaly_score = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    is_synthetic = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    environment = relationship("Environment", back_populates="predictions")


class EventRecord(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, nullable=False)
    event_type = Column(String(64), nullable=False)  # 'ACTIVITY_CHANGE', 'FALL_DETECTED', 'ANOMALY_TRIGGER', 'PRESENCE_CHANGE'
    title = Column(String(128), nullable=False)
    description = Column(Text, default="")
    severity = Column(String(32), default="info")  # 'info', 'warning', 'critical'
    environment_id = Column(String(64), ForeignKey("environments.id"), nullable=True)
    environment_type = Column(String(64), default="Office")
    confidence = Column(Float, default=1.0)
    is_synthetic = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    environment = relationship("Environment", back_populates="events")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(64), primary_key=True, index=True)
    value = Column(JSON, nullable=False)
    description = Column(String(256), default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
