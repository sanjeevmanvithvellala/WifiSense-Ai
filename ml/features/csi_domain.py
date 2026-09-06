"""
CSI-specific domain feature extraction.
Computes cross-subcarrier correlation, subcarrier variance profiles, and temporal variation indices.
"""

import numpy as np
from typing import Optional


def extract_csi_domain_features(
    window_2d: np.ndarray,
    phase_window_2d: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Extracts specialized Wi-Fi CSI spatial and temporal diversity features.
    """
    T, S = window_2d.shape

    # 1. Temporal Variation (first-order packet-to-packet derivative)
    time_diff = np.diff(window_2d, axis=0)  # (T-1, S)
    temp_var_mean = np.mean(np.abs(time_diff), axis=0)  # (S,)
    temp_var_std = np.std(time_diff, axis=0)  # (S,)

    # 2. Subcarrier Spatial Profile Variance (across subcarriers at each timestep)
    spatial_std_over_time = np.std(window_2d, axis=1)  # (T,)
    mean_spatial_std = np.mean(spatial_std_over_time)
    std_spatial_std = np.std(spatial_std_over_time)

    # 3. Cross-Subcarrier Correlation Matrix
    if S >= 2 and T >= 2:
        corr_matrix = np.corrcoef(window_2d, rowvar=False)
        corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)
        # Extract upper triangle correlation values
        triu_indices = np.triu_indices(S, k=1)
        mean_cross_corr = np.mean(corr_matrix[triu_indices]) if len(triu_indices[0]) > 0 else 0.0
        min_cross_corr = np.min(corr_matrix[triu_indices]) if len(triu_indices[0]) > 0 else 0.0
        max_cross_corr = np.max(corr_matrix[triu_indices]) if len(triu_indices[0]) > 0 else 0.0
    else:
        mean_cross_corr, min_cross_corr, max_cross_corr = 0.0, 0.0, 0.0

    # 4. Phase features if available
    if phase_window_2d is not None and phase_window_2d.shape == window_2d.shape:
        phase_std = np.std(phase_window_2d, axis=0)  # (S,)
        mean_phase_std = np.mean(phase_std)
        phase_diff = np.diff(phase_window_2d, axis=0)
        phase_temp_var = np.mean(np.abs(phase_diff))
    else:
        phase_std = np.zeros(S, dtype=np.float32)
        mean_phase_std = 0.0
        phase_temp_var = 0.0

    summary_csi = np.array([
        mean_spatial_std,
        std_spatial_std,
        mean_cross_corr,
        min_cross_corr,
        max_cross_corr,
        mean_phase_std,
        phase_temp_var
    ])

    features = np.concatenate([
        temp_var_mean,
        temp_var_std,
        phase_std,
        summary_csi
    ])
    return features.astype(np.float32)
