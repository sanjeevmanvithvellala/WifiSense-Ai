"""
Frequency-domain and spectral feature extraction for Wi-Fi CSI time windows.
Extracts FFT dominant frequency, spectral energy, spectral centroid, spectral entropy, and band power.
"""

import numpy as np
from typing import Tuple


def extract_frequency_domain_features(
    window_2d: np.ndarray,
    sampling_rate_hz: float = 50.0
) -> np.ndarray:
    """
    Extracts frequency-domain features for a window of shape (T, S).
    """
    T, S = window_2d.shape
    if T < 4:
        return np.zeros(S * 4 + 6, dtype=np.float32)

    # Compute one-sided FFT
    freqs = np.fft.rfftfreq(T, d=1.0 / sampling_rate_hz)
    fft_vals = np.fft.rfft(window_2d - np.mean(window_2d, axis=0, keepdims=True), axis=0)
    mag_spectrum = np.abs(fft_vals)  # (n_freqs, S)
    power_spectrum = mag_spectrum ** 2

    # 1. Dominant Frequency per subcarrier (frequency with maximum energy)
    dom_freq_idx = np.argmax(mag_spectrum, axis=0)
    dominant_freqs = freqs[dom_freq_idx]  # (S,)

    # 2. Spectral Energy per subcarrier
    spectral_energy = np.sum(power_spectrum, axis=0) / max(1, len(freqs))  # (S,)

    # 3. Spectral Centroid per subcarrier: sum(f * |X(f)|) / sum(|X(f)|)
    mag_sum = np.sum(mag_spectrum, axis=0) + 1e-8
    spectral_centroid = np.sum(freqs[:, None] * mag_spectrum, axis=0) / mag_sum  # (S,)

    # 4. Spectral Entropy per subcarrier
    # Normalized power spectral density
    psd_norm = power_spectrum / (np.sum(power_spectrum, axis=0, keepdims=True) + 1e-8)
    psd_norm = np.clip(psd_norm, 1e-12, 1.0)
    spectral_entropy = -np.sum(psd_norm * np.log2(psd_norm), axis=0) / np.log2(max(2, len(freqs)))  # (S,)

    # 5. Low vs High Movement Band Energy (e.g. 0.5 - 3.0 Hz vs 3.0 - 10.0 Hz)
    low_band_mask = (freqs >= 0.5) & (freqs <= 3.0)
    high_band_mask = (freqs > 3.0) & (freqs <= 10.0)

    low_band_energy = np.sum(power_spectrum[low_band_mask, :], axis=0) if np.any(low_band_mask) else np.zeros(S)
    high_band_energy = np.sum(power_spectrum[high_band_mask, :], axis=0) if np.any(high_band_mask) else np.zeros(S)

    # Aggregated spectral metrics across all subcarriers
    global_spectral = np.array([
        np.mean(dominant_freqs),
        np.mean(spectral_energy),
        np.mean(spectral_centroid),
        np.mean(spectral_entropy),
        np.mean(low_band_energy),
        np.mean(high_band_energy),
    ])

    features = np.concatenate([
        dominant_freqs,
        spectral_energy,
        spectral_centroid,
        spectral_entropy,
        low_band_energy,
        high_band_energy,
        global_spectral
    ])
    return features.astype(np.float32)
