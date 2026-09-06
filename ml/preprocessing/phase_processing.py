"""
Phase unwrapping and sanitization for Wi-Fi CSI phase information.
Implements linear phase sanitization to remove carrier frequency offset (CFO) and sampling timing offset (STO).
"""

import numpy as np
from typing import Optional


def unwrap_phase(phase_data: np.ndarray) -> np.ndarray:
    """Unwraps phase data along the subcarrier axis (axis=1) and time axis (axis=0)."""
    if phase_data is None or phase_data.size == 0:
        return phase_data
    # Unwrap along subcarriers first
    unwrapped = np.unwrap(phase_data, axis=-1)
    # Then along time
    unwrapped = np.unwrap(unwrapped, axis=0)
    return unwrapped.astype(np.float32)


def sanitize_linear_phase(phase_data: np.ndarray, subcarrier_indices: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Performs linear transformation to eliminate initial phase offset and slope error
    caused by packet detection delay and unsynchronized local oscillators.
    
    Formula:
        theta_sanitized(k) = theta(k) - a * k - b
    where a and b are determined by linear regression over subcarrier indices k.
    """
    if phase_data is None or phase_data.size == 0:
        return phase_data

    T, S = phase_data.shape[0], phase_data.shape[-1]
    if subcarrier_indices is None:
        subcarrier_indices = np.arange(S)

    # Unwrap first
    unwrapped = unwrap_phase(phase_data)
    sanitized = np.zeros_like(unwrapped)

    k = subcarrier_indices
    k_mean = np.mean(k)
    k_var = np.var(k) if np.var(k) > 1e-6 else 1.0

    for t in range(T):
        theta_t = unwrapped[t]
        theta_mean = np.mean(theta_t)
        slope_a = np.sum((k - k_mean) * (theta_t - theta_mean)) / (S * k_var)
        offset_b = theta_mean - slope_a * k_mean
        sanitized[t] = theta_t - (slope_a * k + offset_b)

    return sanitized.astype(np.float32)
