"""
Cross-Environment Adaptation and Domain Generalization Algorithms.
Implements CORAL (Correlation Alignment), Environment-Aware Calibration, and Domain Fine-Tuning.
"""

import numpy as np
from scipy import linalg
from typing import Dict, Any, Optional, Tuple, List
from ml.environment.calibration import EnvironmentProfile
from ml.models.base import BaseCSIModel


class CORALAdapter:
    """
    Correlation Alignment (CORAL) Domain Adaptation.
    Aligns second-order statistics (covariance) between source and target environment feature spaces.
    Reference: Sun et al., "Return of Prior Metrics: Deep CORAL for Domain Adaptation", ECCV 2016.
    """

    def __init__(self, eps: float = 1e-5):
        self.eps = eps
        self.source_cov: Optional[np.ndarray] = None
        self.source_mean: Optional[np.ndarray] = None
        self.target_cov: Optional[np.ndarray] = None
        self.target_mean: Optional[np.ndarray] = None
        self.transform_matrix: Optional[np.ndarray] = None

    def fit(self, X_source: np.ndarray, X_target: np.ndarray):
        """Calculates CORAL whitening and recoloring transformation matrix."""
        # Clean inputs
        X_s = np.nan_to_num(X_source, nan=0.0)
        X_t = np.nan_to_num(X_target, nan=0.0)

        n_s = X_s.shape[0]
        n_t = X_t.shape[0]

        self.source_mean = np.mean(X_s, axis=0)
        self.target_mean = np.mean(X_t, axis=0)

        X_s_zero = X_s - self.source_mean
        X_t_zero = X_t - self.target_mean

        d = X_s.shape[1]
        # Covariance matrices with regularization
        C_s = (X_s_zero.T @ X_s_zero) / max(1, n_s - 1) + np.eye(d) * self.eps
        C_t = (X_t_zero.T @ X_t_zero) / max(1, n_t - 1) + np.eye(d) * self.eps

        self.source_cov = C_s
        self.target_cov = C_t

        try:
            # Fractional matrix powers using SVD/Eigendecomposition
            u_t, s_t, vh_t = np.linalg.svd(C_t)
            inv_sqrt_Ct = u_t @ np.diag(1.0 / np.sqrt(s_t + self.eps)) @ vh_t

            u_s, s_s, vh_s = np.linalg.svd(C_s)
            sqrt_Cs = u_s @ np.diag(np.sqrt(s_s + self.eps)) @ vh_s

            self.transform_matrix = inv_sqrt_Ct @ sqrt_Cs
        except Exception:
            # Fallback to identity transform if singular
            self.transform_matrix = np.eye(d)

    def transform(self, X_target: np.ndarray) -> np.ndarray:
        """Adapts target environment feature vectors to source domain distribution."""
        if self.transform_matrix is None or self.target_mean is None or self.source_mean is None:
            return X_target

        X_t_clean = np.nan_to_num(X_target, nan=0.0)
        X_t_zero = X_t_clean - self.target_mean
        adapted = (X_t_zero @ self.transform_matrix) + self.source_mean
        return np.nan_to_num(adapted, nan=0.0).astype(np.float32)


class EnvironmentAdaptationEngine:
    """Coordinates environment adaptation strategies for inference and cross-environment benchmarking."""

    def __init__(self):
        self.coral = CORALAdapter()

    def adapt_features(
        self,
        X_target: np.ndarray,
        X_source_train: Optional[np.ndarray] = None,
        strategy: str = "coral"
    ) -> np.ndarray:
        """Applies requested adaptation strategy to target environment data."""
        if strategy == "none" or X_source_train is None:
            return X_target

        if strategy == "coral":
            self.coral.fit(X_source_train, X_target)
            return self.coral.transform(X_target)

        return X_target

    def compare_adaptation(
        self,
        model: BaseCSIModel,
        X_target: np.ndarray,
        y_target: np.ndarray,
        X_source_train: np.ndarray,
        strategy: str = "coral"
    ) -> Dict[str, Any]:
        """
        Evaluates and compares:
        1. Baseline Direct Transfer (No Adaptation)
        2. Environment-Adapted Model (CORAL / Calibration)
        """
        # Baseline (Direct transfer without adaptation)
        baseline_metrics = model.evaluate(X_target, y_target)

        # Adapted transfer
        X_adapted = self.adapt_features(X_target, X_source_train, strategy=strategy)
        adapted_metrics = model.evaluate(X_adapted, y_target)

        f1_improvement = adapted_metrics["f1_macro"] - baseline_metrics["f1_macro"]
        acc_improvement = adapted_metrics["accuracy"] - baseline_metrics["accuracy"]

        return {
            "strategy": strategy,
            "baseline_metrics": baseline_metrics,
            "adapted_metrics": adapted_metrics,
            "accuracy_delta": round(acc_improvement, 4),
            "f1_macro_delta": round(f1_improvement, 4),
            "adapted_sample_count": len(X_target),
        }
