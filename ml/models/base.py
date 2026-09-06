"""
Base interfaces and classes for WiFiSense AI ML models and Anomaly Detectors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import time


class BaseCSIModel(ABC):
    """Abstract interface for all Wi-Fi CSI activity classification models."""

    def __init__(self, model_id: str, name: str, architecture: str):
        self.model_id = model_id
        self.name = name
        self.architecture = architecture
        self.classes_: List[str] = []
        self.is_trained: bool = False
        self.training_metadata: Dict[str, Any] = {}

    @abstractmethod
    def train(
        self,
        X: np.ndarray,
        y: List[str] | np.ndarray,
        validation_data: Optional[Tuple[np.ndarray, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Trains the model and returns training summary metrics."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts class labels for feature or window array X."""
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predicts class probability distributions of shape (N, num_classes)."""
        pass

    def evaluate(self, X: np.ndarray, y: List[str] | np.ndarray) -> Dict[str, Any]:
        """Evaluates predictions against true labels and returns real calculated metrics."""
        from ml.experiments.metrics import calculate_classification_metrics
        y_true = np.array(y)
        t0 = time.time()
        y_pred = self.predict(X)
        latency_ms = (time.time() - t0) * 1000.0 / max(1, len(X))
        
        probas = self.predict_proba(X) if hasattr(self, "predict_proba") else None
        metrics = calculate_classification_metrics(y_true, y_pred, probas, self.classes_)
        metrics["inference_latency_ms_per_sample"] = round(latency_ms, 3)
        return metrics

    @abstractmethod
    def save(self, filepath: str):
        """Persists model weights and configuration to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str):
        """Restores model weights and configuration from disk."""
        pass


class BaseAnomalyDetector(ABC):
    """Abstract interface for Wi-Fi CSI Anomaly Detectors."""

    def __init__(self, model_id: str, name: str, algorithm: str):
        self.model_id = model_id
        self.name = name
        self.algorithm = algorithm
        self.is_trained: bool = False
        self.threshold: float = 0.5

    @abstractmethod
    def fit(self, X: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Fits baseline normal activity distribution."""
        pass

    @abstractmethod
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Returns continuous anomaly score [0.0 (normal) to 1.0 (anomalous)]."""
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Returns boolean flag: True if anomalous, False if normal."""
        scores = self.score_samples(X)
        return scores >= self.threshold

    @abstractmethod
    def save(self, filepath: str):
        pass

    @abstractmethod
    def load(self, filepath: str):
        pass
