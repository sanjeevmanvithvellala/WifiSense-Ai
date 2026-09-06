"""
Unified Feature Extraction Engine for WiFiSense AI.
Combines time-domain, frequency-domain, and CSI-specific spatial features into fixed-length vectors.
"""

import numpy as np
from typing import Dict, Any, Optional, List
from ml.features.time_domain import extract_time_domain_features
from ml.features.frequency_domain import extract_frequency_domain_features
from ml.features.csi_domain import extract_csi_domain_features


class FeatureConfig:
    """Configuration options for feature extraction."""

    def __init__(
        self,
        include_time_domain: bool = True,
        include_frequency_domain: bool = True,
        include_csi_domain: bool = True,
        sampling_rate_hz: float = 50.0,
    ):
        self.include_time_domain = include_time_domain
        self.include_frequency_domain = include_frequency_domain
        self.include_csi_domain = include_csi_domain
        self.sampling_rate_hz = sampling_rate_hz

    def to_dict(self) -> Dict[str, Any]:
        return {
            "include_time_domain": self.include_time_domain,
            "include_frequency_domain": self.include_frequency_domain,
            "include_csi_domain": self.include_csi_domain,
            "sampling_rate_hz": self.sampling_rate_hz,
        }


class FeatureExtractor:
    """Extracts unified feature vectors from preprocessed CSI sliding windows."""

    def __init__(self, config: Optional[FeatureConfig] = None):
        self.config = config or FeatureConfig()

    def extract_window_features(
        self,
        window_2d: np.ndarray,
        phase_window_2d: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Extracts combined feature vector from a single 2D window of shape (window_size, subcarriers).
        """
        parts = []

        # 1. Time domain
        if self.config.include_time_domain:
            t_feats = extract_time_domain_features(window_2d)
            parts.append(t_feats)

        # 2. Frequency domain
        if self.config.include_frequency_domain:
            f_feats = extract_frequency_domain_features(
                window_2d,
                sampling_rate_hz=self.config.sampling_rate_hz
            )
            parts.append(f_feats)

        # 3. CSI domain
        if self.config.include_csi_domain:
            c_feats = extract_csi_domain_features(window_2d, phase_window_2d)
            parts.append(c_feats)

        if not parts:
            return window_2d.flatten()

        combined = np.concatenate(parts)
        # Clean any remaining NaNs or Infs
        combined = np.nan_to_num(combined, nan=0.0, posinf=100.0, neginf=-100.0)
        return combined.astype(np.float32)

    def extract_batch(
        self,
        windows: np.ndarray,
        phase_windows: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Extracts features for a 3D batch of windows (num_windows, window_size, subcarriers).
        
        Returns:
            2D feature matrix of shape (num_windows, num_features).
        """
        if windows.ndim == 2:
            return np.expand_dims(self.extract_window_features(windows), axis=0)

        num_windows = windows.shape[0]
        feats_list = []
        for i in range(num_windows):
            p_win = phase_windows[i] if phase_windows is not None and i < phase_windows.shape[0] else None
            feat_vec = self.extract_window_features(windows[i], p_win)
            feats_list.append(feat_vec)

        return np.array(feats_list, dtype=np.float32)
