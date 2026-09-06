"""Unit tests for Feature Extractor and Synthetic Generator."""
import numpy as np
import pytest
from ml.synthetic_generator import SyntheticCSIGenerator
from ml.features.extractor import FeatureExtractor, FeatureConfig


def test_synthetic_generator_activities():
    generator = SyntheticCSIGenerator(random_seed=42)
    activities = ["Walking", "Sitting", "Standing", "Running", "Falling", "Empty"]

    for act in activities:
        sample = generator.generate_sample(
            activity=act,
            duration_sec=1.0,
            sampling_rate=50.0,
            subcarrier_count=32,
            antenna_count=1,
        )
        assert sample.amplitude.shape == (50, 32)
        assert sample.metadata.is_synthetic is True
        assert sample.metadata.activity_label == act
        assert sample.amplitude.min() >= 0.0


def test_feature_extractor():
    generator = SyntheticCSIGenerator(random_seed=42)
    sample = generator.generate_sample(
        activity="Walking",
        duration_sec=1.5,
        sampling_rate=50.0,
        subcarrier_count=32,
    )

    extractor = FeatureExtractor(FeatureConfig())
    window = sample.amplitude[:30, :]
    feat_vec = extractor.extract_window_features(window)

    assert isinstance(feat_vec, np.ndarray)
    assert len(feat_vec) > 10
    assert not np.isnan(feat_vec).any()
