"""
Time-domain statistical feature extraction for Wi-Fi CSI time windows.
Computes Mean, Std, Variance, RMS, Peak-to-Peak, Energy, Zero-Crossing Rate, Skewness, and Kurtosis.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any


def extract_time_domain_features(window_2d: np.ndarray) -> np.ndarray:
    """
    Extracts time-domain features for a window of shape (window_size, subcarriers).
    
    Returns:
        1D feature vector of concatenated subcarrier statistical descriptors.
    """
    # window_2d shape: (T, S)
    T, S = window_2d.shape

    # 1. Mean across time for each subcarrier (S,)
    means = np.mean(window_2d, axis=0)

    # 2. Standard deviation (S,)
    stds = np.std(window_2d, axis=0)

    # 3. Variance (S,)
    vars_ = np.var(window_2d, axis=0)

    # 4. Root Mean Square (RMS) (S,)
    rms = np.sqrt(np.mean(window_2d ** 2, axis=0))

    # 5. Peak-to-Peak (max - min) (S,)
    p2p = np.ptp(window_2d, axis=0)

    # 6. Energy (S,)
    energy = np.sum(window_2d ** 2, axis=0) / max(1, T)

    # 7. Mean-crossing rate (similar to zero-crossing for zero-centered data) (S,)
    centered = window_2d - means[None, :]
    signs = np.sign(centered)
    diffs = np.diff(signs, axis=0)
    mcr = np.sum(np.abs(diffs) > 0, axis=0) / max(1, T - 1)

    # 8. Skewness and Kurtosis (S,)
    skew = stats.skew(window_2d, axis=0, nan_policy="omit")
    skew = np.nan_to_num(skew, nan=0.0)
    
    kurt = stats.kurtosis(window_2d, axis=0, nan_policy="omit")
    kurt = np.nan_to_num(kurt, nan=0.0)

    # Summary statistics across all subcarriers (aggregate metrics)
    global_mean = np.array([np.mean(means), np.mean(stds), np.mean(vars_), np.mean(rms), np.mean(p2p), np.mean(energy), np.mean(mcr)])

    # Concatenate per-subcarrier and global statistics
    features = np.concatenate([means, stds, vars_, rms, p2p, energy, mcr, skew, kurt, global_mean])
    return features.astype(np.float32)
