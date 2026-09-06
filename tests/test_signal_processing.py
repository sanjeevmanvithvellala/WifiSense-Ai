"""Unit tests for Signal Preprocessing Pipeline."""
import numpy as np
import pytest
from ml.unified_model import CSIMetadata, CSISample
from ml.preprocessing.filters import (
    apply_hampel_filter,
    butterworth_lowpass_filter,
    moving_average_smooth,
)
from ml.preprocessing.normalization import (
    zscore_normalize,
    minmax_normalize,
    environment_aware_normalize,
)
from ml.preprocessing.phase_processing import sanitize_linear_phase
from ml.preprocessing.windowing import create_sliding_windows
from ml.preprocessing.pipeline import PreprocessingPipeline, PreprocessingConfig


@pytest.fixture
def dummy_sample():
    num_packets = 100
    num_sub = 32

    t = np.linspace(0, 2.0, num_packets)
    amplitude = np.sin(2 * np.pi * 3 * t[:, None]) + 10.0
    amplitude = np.tile(amplitude, (1, num_sub)).astype(np.float32)
    # Add outlier
    amplitude[50, 10] = 50.0

    phase = np.linspace(-np.pi, np.pi, num_packets)[:, None]
    phase = np.tile(phase, (1, num_sub)).astype(np.float32)

    meta = CSIMetadata(
        dataset_id="test_ds",
        sample_id="test_filter",
        subcarrier_count=num_sub,
        antenna_count=1,
        sampling_rate=50.0,
        activity_label="Walking",
    )
    return CSISample(
        metadata=meta,
        amplitude=amplitude,
        phase=phase,
    )


def test_filters(dummy_sample):
    amp = dummy_sample.amplitude
    # Hampel
    cleaned = apply_hampel_filter(amp, window_size=5, n_sigmas=3.0)
    assert cleaned.shape == amp.shape
    assert cleaned[50, 10] < 40.0

    # Butterworth lowpass
    lowpassed = butterworth_lowpass_filter(amp, cutoff_hz=10.0, sampling_rate_hz=50.0)
    assert lowpassed.shape == amp.shape

    # Moving average
    ma = moving_average_smooth(amp, window_size=3)
    assert ma.shape == amp.shape


def test_normalization(dummy_sample):
    amp = dummy_sample.amplitude
    z_norm, mean, std = zscore_normalize(amp)
    assert z_norm.shape == amp.shape
    assert np.abs(np.mean(z_norm)) < 0.2

    mm_norm, d_min, d_max = minmax_normalize(amp)
    assert mm_norm.min() >= -1e-5
    assert mm_norm.max() <= 1.0 + 1e-5

    baseline = np.mean(amp, axis=0)
    calibrated = environment_aware_normalize(amp, baseline)
    assert calibrated.shape == amp.shape


def test_phase_processing(dummy_sample):
    sanitized = sanitize_linear_phase(dummy_sample.phase)
    assert sanitized.shape == dummy_sample.phase.shape
    assert not np.isnan(sanitized).any()


def test_windowing(dummy_sample):
    windows, indices = create_sliding_windows(dummy_sample.amplitude, window_size=30, overlap_ratio=0.5)
    assert len(windows) > 0
    assert windows.shape[1] == 30
    assert windows.shape[2] == dummy_sample.subcarriers


def test_preprocessing_pipeline(dummy_sample):
    pipeline = PreprocessingPipeline(PreprocessingConfig(window_size=30, window_overlap_ratio=0.5))
    windows, indices, phase = pipeline.process_sample(dummy_sample)
    assert len(windows) > 0
    assert windows.shape[1] == 30
    assert not np.isnan(windows).any()
