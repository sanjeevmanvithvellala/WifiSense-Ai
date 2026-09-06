"""
Signal filtering and denoising algorithms for Wi-Fi CSI matrices.
Uses SciPy signal processing functions for Butterworth, bandpass, Hampel, and moving average filtering.
"""

import numpy as np
from scipy import signal
from typing import Optional, Tuple


def hampel_filter_1d(x: np.ndarray, window_size: int = 5, n_sigmas: float = 3.0) -> np.ndarray:
    """
    Hampel filter for outlier detection and replacement with local median.
    """
    n = len(x)
    y = x.copy()
    k = 1.4826  # scale factor for Gaussian distribution
    
    half_window = window_size // 2
    for i in range(half_window, n - half_window):
        window = x[i - half_window : i + half_window + 1]
        med = np.median(window)
        mad = k * np.median(np.abs(window - med))
        if mad > 1e-6 and np.abs(x[i] - med) > n_sigmas * mad:
            y[i] = med
    return y


def apply_hampel_filter(data: np.ndarray, window_size: int = 5, n_sigmas: float = 3.0) -> np.ndarray:
    """
    Applies Hampel outlier removal across all subcarriers (columns) of a 2D CSI matrix (time_steps, subcarriers).
    """
    filtered = np.zeros_like(data)
    if data.ndim == 1:
        return hampel_filter_1d(data, window_size, n_sigmas)
    for col in range(data.shape[1]):
        filtered[:, col] = hampel_filter_1d(data[:, col], window_size, n_sigmas)
    return filtered


def butterworth_lowpass_filter(
    data: np.ndarray,
    cutoff_hz: float = 10.0,
    sampling_rate_hz: float = 50.0,
    order: int = 4
) -> np.ndarray:
    """
    Applies zero-phase forward-backward Butterworth low-pass filter (filtfilt).
    Removes high-frequency burst and thermal noise above human movement Doppler range.
    """
    nyquist = 0.5 * sampling_rate_hz
    normal_cutoff = min(cutoff_hz / nyquist, 0.99)
    if normal_cutoff <= 0:
        return data

    b, a = signal.butter(order, normal_cutoff, btype="low", analog=False)
    
    if data.shape[0] <= max(order * 3, 15):
        # Array too short for filtfilt boundary extension
        return data

    if data.ndim == 1:
        return signal.filtfilt(b, a, data, axis=0).astype(np.float32)
    else:
        return signal.filtfilt(b, a, data, axis=0).astype(np.float32)


def butterworth_bandpass_filter(
    data: np.ndarray,
    lowcut_hz: float = 0.5,
    highcut_hz: float = 15.0,
    sampling_rate_hz: float = 50.0,
    order: int = 3
) -> np.ndarray:
    """
    Applies zero-phase Butterworth band-pass filter.
    Removes static DC component (< lowcut) and high-frequency noise (> highcut).
    """
    nyquist = 0.5 * sampling_rate_hz
    low = max(lowcut_hz / nyquist, 0.01)
    high = min(highcut_hz / nyquist, 0.99)
    if low >= high:
        return data

    b, a = signal.butter(order, [low, high], btype="band", analog=False)

    if data.shape[0] <= max(order * 3, 15):
        return data

    return signal.filtfilt(b, a, data, axis=0).astype(np.float32)


def moving_average_smooth(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Applies moving average smoothing along the time axis."""
    if window_size <= 1 or data.shape[0] < window_size:
        return data
    kernel = np.ones(window_size) / window_size
    if data.ndim == 1:
        return np.convolve(data, kernel, mode="same")
    smoothed = np.zeros_like(data)
    for col in range(data.shape[1]):
        smoothed[:, col] = np.convolve(data[:, col], kernel, mode="same")
    return smoothed.astype(np.float32)
