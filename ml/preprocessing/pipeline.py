"""
Unified Signal Preprocessing Pipeline for WiFiSense AI.
Coordinates validation, outlier removal, frequency filtering, normalization, and windowing.
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from ml.unified_model import CSISample
from ml.preprocessing.filters import (
    apply_hampel_filter,
    butterworth_lowpass_filter,
    butterworth_bandpass_filter,
    moving_average_smooth,
)
from ml.preprocessing.normalization import (
    zscore_normalize,
    minmax_normalize,
    environment_aware_normalize,
)
from ml.preprocessing.windowing import create_sliding_windows
from ml.preprocessing.phase_processing import sanitize_linear_phase


class PreprocessingConfig:
    """Configurable hyperparameters for signal preprocessing."""

    def __init__(
        self,
        enable_hampel: bool = True,
        hampel_window: int = 5,
        hampel_sigmas: float = 3.0,
        filter_type: str = "lowpass",  # 'none', 'lowpass', 'bandpass'
        lowpass_cutoff_hz: float = 12.0,
        bandpass_lowcut_hz: float = 0.5,
        bandpass_highcut_hz: float = 15.0,
        filter_order: int = 4,
        enable_moving_average: bool = True,
        moving_average_window: int = 3,
        normalization_method: str = "zscore",  # 'none', 'zscore', 'minmax', 'environment_aware'
        window_size: int = 50,  # e.g. 50 steps = 1.0s at 50Hz
        window_overlap_ratio: float = 0.5,
        sanitize_phase: bool = True,
    ):
        self.enable_hampel = enable_hampel
        self.hampel_window = hampel_window
        self.hampel_sigmas = hampel_sigmas
        self.filter_type = filter_type
        self.lowpass_cutoff_hz = lowpass_cutoff_hz
        self.bandpass_lowcut_hz = bandpass_lowcut_hz
        self.bandpass_highcut_hz = bandpass_highcut_hz
        self.filter_order = filter_order
        self.enable_moving_average = enable_moving_average
        self.moving_average_window = moving_average_window
        self.normalization_method = normalization_method
        self.window_size = window_size
        self.window_overlap_ratio = window_overlap_ratio
        self.sanitize_phase = sanitize_phase

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enable_hampel": self.enable_hampel,
            "hampel_window": self.hampel_window,
            "hampel_sigmas": self.hampel_sigmas,
            "filter_type": self.filter_type,
            "lowpass_cutoff_hz": self.lowpass_cutoff_hz,
            "bandpass_lowcut_hz": self.bandpass_lowcut_hz,
            "bandpass_highcut_hz": self.bandpass_highcut_hz,
            "filter_order": self.filter_order,
            "enable_moving_average": self.enable_moving_average,
            "moving_average_window": self.moving_average_window,
            "normalization_method": self.normalization_method,
            "window_size": self.window_size,
            "window_overlap_ratio": self.window_overlap_ratio,
            "sanitize_phase": self.sanitize_phase,
        }


class PreprocessingPipeline:
    """End-to-end signal conditioning pipeline."""

    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()

    def validate_and_clean(self, data: np.ndarray) -> np.ndarray:
        """Handles NaNs, Infs, and ensures float32 2D array."""
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=np.float32)
        
        # Replace NaNs / Infs with column-wise medians or zeros
        if np.isnan(data).any() or np.isinf(data).any():
            data = np.nan_to_num(data, nan=0.0, posinf=100.0, neginf=-100.0)
            
        return data.astype(np.float32)

    def process_matrix(
        self,
        raw_amplitude: np.ndarray,
        sampling_rate_hz: float = 50.0,
        ambient_baseline: Optional[np.ndarray] = None,
        env_scale_factor: float = 1.0,
    ) -> np.ndarray:
        """Processes a 2D CSI amplitude matrix (time_steps, subcarriers)."""
        data = self.validate_and_clean(raw_amplitude)
        if data.size == 0 or data.shape[0] < 3:
            return data

        # 1. Outlier Rejection (Hampel)
        if self.config.enable_hampel:
            data = apply_hampel_filter(data, window_size=self.config.hampel_window, n_sigmas=self.config.hampel_sigmas)

        # 2. Frequency Filtering (Butterworth)
        if self.config.filter_type == "lowpass":
            data = butterworth_lowpass_filter(
                data,
                cutoff_hz=self.config.lowpass_cutoff_hz,
                sampling_rate_hz=sampling_rate_hz,
                order=self.config.filter_order
            )
        elif self.config.filter_type == "bandpass":
            data = butterworth_bandpass_filter(
                data,
                lowcut_hz=self.config.bandpass_lowcut_hz,
                highcut_hz=self.config.bandpass_highcut_hz,
                sampling_rate_hz=sampling_rate_hz,
                order=self.config.filter_order
            )

        # 3. Moving Average Smoothing
        if self.config.enable_moving_average:
            data = moving_average_smooth(data, window_size=self.config.moving_average_window)

        # 4. Normalization
        if self.config.normalization_method == "zscore":
            data, _, _ = zscore_normalize(data)
        elif self.config.normalization_method == "minmax":
            data, _, _ = minmax_normalize(data)
        elif self.config.normalization_method == "environment_aware":
            data = environment_aware_normalize(data, ambient_baseline, env_scale_factor)

        return data.astype(np.float32)

    def process_sample(
        self,
        sample: CSISample,
        ambient_baseline: Optional[np.ndarray] = None,
        env_scale_factor: float = 1.0,
    ) -> Tuple[np.ndarray, List[Tuple[int, int]], Optional[np.ndarray]]:
        """
        Executes full preprocessing pipeline on a unified CSISample.
        
        Returns:
            windows: 3D array (num_windows, window_size, subcarriers)
            indices: list of window slice ranges
            processed_phase: optional sanitized phase array
        """
        amp_2d = sample.get_2d_amplitude()
        sampling_rate = sample.metadata.sampling_rate

        processed_amp = self.process_matrix(
            amp_2d,
            sampling_rate_hz=sampling_rate,
            ambient_baseline=ambient_baseline,
            env_scale_factor=env_scale_factor
        )

        # Phase sanitization if available
        processed_phase = None
        if sample.phase is not None and self.config.sanitize_phase:
            processed_phase = sanitize_linear_phase(sample.phase)

        # Sliding window segmentation
        windows, indices = create_sliding_windows(
            processed_amp,
            window_size=self.config.window_size,
            overlap_ratio=self.config.window_overlap_ratio
        )

        return windows, indices, processed_phase
