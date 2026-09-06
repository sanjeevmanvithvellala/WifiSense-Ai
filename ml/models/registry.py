"""
Model Registry and Factory for WiFiSense AI.
Manages discovery, instantiation, checkpointing, and lifecycle of ML classifiers and anomaly detectors.
"""

import os
from typing import Dict, Any, List, Optional, Type
from ml.models.base import BaseCSIModel, BaseAnomalyDetector
from ml.models.random_forest import RandomForestCSIClassifier
from ml.models.svm import SVMCSIClassifier
from ml.models.cnn1d import CNN1DCSIClassifier
from ml.models.cnn_gru import CNNGRUClassifier
from ml.models.transformer import TransformerCSIClassifier
from ml.models.isolation_forest import IsolationForestAnomalyDetector
from ml.models.autoencoder import AutoencoderAnomalyDetector


class ModelRegistry:
    """Registry maintaining available model architectures and trained model instances."""

    def __init__(self, registry_dir: str = "./models/registry"):
        self.registry_dir = registry_dir
        os.makedirs(registry_dir, exist_ok=True)
        self._architectures: Dict[str, Type[BaseCSIModel]] = {
            "Random Forest": RandomForestCSIClassifier,
            "SVM": SVMCSIClassifier,
            "1D CNN": CNN1DCSIClassifier,
            "CNN-GRU": CNNGRUClassifier,
            "Transformer": TransformerCSIClassifier,
        }
        self._anomaly_architectures: Dict[str, Type[BaseAnomalyDetector]] = {
            "Isolation Forest": IsolationForestAnomalyDetector,
            "Deep Autoencoder": AutoencoderAnomalyDetector,
        }
        self._loaded_models: Dict[str, BaseCSIModel] = {}
        self._loaded_anomaly_detectors: Dict[str, BaseAnomalyDetector] = {}

    def list_architectures(self) -> List[str]:
        return list(self._architectures.keys())

    def list_anomaly_architectures(self) -> List[str]:
        return list(self._anomaly_architectures.keys())

    def create_model(
        self,
        architecture: str,
        model_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> BaseCSIModel:
        if architecture not in self._architectures:
            raise ValueError(f"Unknown architecture '{architecture}'. Available: {list(self._architectures.keys())}")
        cls = self._architectures[architecture]
        model_name = name or f"{architecture} Model"
        return cls(model_id=model_id, name=model_name, **kwargs)

    def create_anomaly_detector(
        self,
        algorithm: str,
        model_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> BaseAnomalyDetector:
        if algorithm not in self._anomaly_architectures:
            raise ValueError(f"Unknown anomaly algorithm '{algorithm}'. Available: {list(self._anomaly_architectures.keys())}")
        cls = self._anomaly_architectures[algorithm]
        detector_name = name or f"{algorithm} Detector"
        return cls(model_id=model_id, name=detector_name, **kwargs)

    def register_loaded_model(self, model: BaseCSIModel):
        self._loaded_models[model.model_id] = model

    def get_model(self, model_id: str) -> Optional[BaseCSIModel]:
        return self._loaded_models.get(model_id)

    def register_anomaly_detector(self, detector: BaseAnomalyDetector):
        self._loaded_anomaly_detectors[detector.model_id] = detector

    def get_anomaly_detector(self, model_id: str) -> Optional[BaseAnomalyDetector]:
        return self._loaded_anomaly_detectors.get(model_id)


# Singleton model registry instance
default_model_registry = ModelRegistry()
