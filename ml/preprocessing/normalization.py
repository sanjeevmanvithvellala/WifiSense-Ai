"""
Normalization routines for Wi-Fi CSI amplitude and features.
Supports Standardization (Z-score), Min-Max, Per-Window normalization, and Environment-Aware Normalization.
"""

import numpy as np
from typing import Optional, Dict, Any, Tuple


def zscore_normalize(data: np.ndarray, eps: float = 1e-8) -> Tuple[np.ndarray, float, float]:
    """Applies Z-score standardization: (X - mu) / sigma."""
    mean = np.mean(data)
    std = np.std(data)
    if std < eps:
        std = 1.0
    normalized = (data - mean) / (std + eps)
    return normalized.astype(np.float32), float(mean), float(std)


def minmax_normalize(
    data: np.ndarray,
    feature_range: Tuple[float, float] = (0.0, 1.0),
    eps: float = 1e-8
) -> Tuple[np.ndarray, float, float]:
    """Applies Min-Max scaling to target range."""
    d_min = np.min(data)
    d_max = np.max(data)
    scale = d_max - d_min
    if scale < eps:
        scale = 1.0
    norm_0_1 = (data - d_min) / (scale + eps)
    res = norm_0_1 * (feature_range[1] - feature_range[0]) + feature_range[0]
    return res.astype(np.float32), float(d_min), float(d_max)


def per_window_normalize(window_data: np.ndarray, method: str = "zscore") -> np.ndarray:
    """Normalizes an individual window segment independently."""
    if method == "minmax":
        norm, _, _ = minmax_normalize(window_data)
        return norm
    else:
        norm, _, _ = zscore_normalize(window_data)
        return norm


def environment_aware_normalize(
    data: np.ndarray,
    ambient_baseline: Optional[np.ndarray] = None,
    env_scale_factor: float = 1.0,
    eps: float = 1e-6
) -> np.ndarray:
    """
    Applies environment-aware calibration/normalization:
    1. Removes static ambient multipath reflections: data_dynamic = data - baseline
    2. Rescales by environment multipath dispersion factor.
    """
    cleaned = data.copy()
    if ambient_baseline is not None:
        if ambient_baseline.shape == data.shape:
            cleaned = cleaned - ambient_baseline
        elif ambient_baseline.ndim == 1 and cleaned.shape[-1] == ambient_baseline.shape[0]:
            cleaned = cleaned - ambient_baseline[None, :]
        elif ambient_baseline.ndim == 2 and cleaned.ndim == 2:
            # Broadcast mean baseline along subcarriers
            base_mean = np.mean(ambient_baseline, axis=0)
            cleaned = cleaned - base_mean[None, :]

    if env_scale_factor > 0 and abs(env_scale_factor - 1.0) > 1e-4:
        cleaned = cleaned / (env_scale_factor + eps)

    # Final zero-center
    norm, _, _ = zscore_normalize(cleaned)
    return norm
