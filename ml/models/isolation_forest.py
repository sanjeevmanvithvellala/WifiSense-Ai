"""
Isolation Forest Anomaly Detector for Wi-Fi CSI Signals.
Detects erratic interference, abnormal movement, unexpected physical intrusions or irregular signal spikes.
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Optional
from ml.models.base import BaseAnomalyDetector


class IsolationForestAnomalyDetector(BaseAnomalyDetector):
    """Isolation Forest anomaly detection model."""

    def __init__(
        self,
        model_id: str = "iforest_01",
        name: str = "Isolation Forest Anomaly Detector",
        contamination: float = 0.05,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        super().__init__(model_id, name, "Isolation Forest")
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.threshold = 0.5
        self.detector = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X: np.ndarray, **kwargs) -> Dict[str, Any]:
        """Fits normal baseline activity distribution."""
        self.detector.fit(X)
        self.is_trained = True
        return {
            "model_id": self.model_id,
            "algorithm": self.algorithm,
            "contamination": self.contamination,
            "n_estimators": self.n_estimators,
            "fitted_samples": len(X)
        }

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Returns anomaly scores normalized between 0.0 (normal) and 1.0 (highly anomalous).
        IsolationForest decision_function outputs negative scores for anomalies.
        """
        if not self.is_trained:
            return np.zeros(len(X), dtype=np.float32)

        # raw score: lower means more anomalous
        raw_scores = self.detector.decision_function(X)
        # Invert and normalize to [0, 1] range: 0.5 is approximately the decision boundary
        # Sigmoid transform: 1 / (1 + exp(8 * raw_score))
        scaled_scores = 1.0 / (1.0 + np.exp(6.0 * raw_scores))
        return np.clip(scaled_scores, 0.0, 1.0).astype(np.float32)

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model_id": self.model_id,
            "name": self.name,
            "algorithm": self.algorithm,
            "contamination": self.contamination,
            "threshold": self.threshold,
            "is_trained": self.is_trained,
            "detector": self.detector
        }, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.model_id = data["model_id"]
        self.name = data["name"]
        self.algorithm = data["algorithm"]
        self.contamination = data.get("contamination", 0.05)
        self.threshold = data.get("threshold", 0.5)
        self.is_trained = data["is_trained"]
        self.detector = data["detector"]
