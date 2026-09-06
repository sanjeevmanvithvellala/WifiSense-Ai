"""
Support Vector Machine (SVM) Classifier for Wi-Fi CSI Feature Vectors.
"""

import os
import joblib
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List, Optional, Tuple
from ml.models.base import BaseCSIModel


class SVMCSIClassifier(BaseCSIModel):
    """SVM Classifier with RBF kernel and probability calibration."""

    def __init__(
        self,
        model_id: str = "svm_baseline_01",
        name: str = "SVM HAR Classifier",
        C: float = 1.0,
        kernel: str = "rbf",
        gamma: str = "scale",
        random_state: int = 42
    ):
        super().__init__(model_id, name, "SVM")
        self.C = C
        self.kernel = kernel
        self.gamma = gamma
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.clf = SVC(
            C=C,
            kernel=kernel,
            gamma=gamma,
            probability=True,
            random_state=random_state
        )

    def train(
        self,
        X: np.ndarray,
        y: List[str] | np.ndarray,
        validation_data: Optional[Tuple[np.ndarray, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        y_arr = np.array(y)
        self.classes_ = sorted(list(set(y_arr)))

        X_scaled = self.scaler.fit_transform(X)
        self.clf.fit(X_scaled, y_arr)
        self.is_trained = True

        train_metrics = self.evaluate(X, y_arr)
        val_metrics = self.evaluate(validation_data[0], validation_data[1]) if validation_data is not None else None

        self.training_metadata = {
            "model_id": self.model_id,
            "architecture": self.architecture,
            "C": self.C,
            "kernel": self.kernel,
            "train_metrics": train_metrics,
            "val_metrics": val_metrics,
            "classes": self.classes_,
        }
        return self.training_metadata

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")
        X_scaled = self.scaler.transform(X)
        return self.clf.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")
        X_scaled = self.scaler.transform(X)
        return self.clf.predict_proba(X_scaled)

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model_id": self.model_id,
            "name": self.name,
            "architecture": self.architecture,
            "classes": self.classes_,
            "is_trained": self.is_trained,
            "training_metadata": self.training_metadata,
            "scaler": self.scaler,
            "clf": self.clf
        }, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.model_id = data["model_id"]
        self.name = data["name"]
        self.architecture = data["architecture"]
        self.classes_ = data["classes"]
        self.is_trained = data["is_trained"]
        self.training_metadata = data.get("training_metadata", {})
        self.scaler = data["scaler"]
        self.clf = data["clf"]
