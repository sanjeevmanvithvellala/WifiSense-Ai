"""Unit tests for Unified CSI Data Model."""
import numpy as np
import pytest
from ml.unified_model import CSIMetadata, CSISample


def test_metadata_creation():
    meta = CSIMetadata(
        dataset_id="test_ds",
        sample_id="sample_001",
        environment_id="living_room",
        environment_type="Residential",
        activity_label="walking",
        antenna_count=3,
        subcarrier_count=64,
        sampling_rate=100.0,
        bandwidth=40.0,
        is_synthetic=True,
    )
    assert meta.subcarrier_count == 64
    assert meta.antenna_count == 3
    assert meta.is_synthetic is True
    assert meta.activity_label == "walking"

    d = meta.to_dict()
    assert d["dataset_id"] == "test_ds"
    assert d["activity_label"] == "walking"


def test_sample_validation_and_properties():
    num_packets = 100
    num_sub = 64
    num_ant = 3

    amplitude = np.random.uniform(5.0, 30.0, size=(num_packets, num_ant, num_sub)).astype(np.float32)
    phase = np.random.uniform(-np.pi, np.pi, size=(num_packets, num_ant, num_sub)).astype(np.float32)

    meta = CSIMetadata(
        dataset_id="test_ds",
        sample_id="test_001",
        antenna_count=num_ant,
        subcarrier_count=num_sub,
        sampling_rate=100.0,
        activity_label="walking",
    )

    sample = CSISample(
        metadata=meta,
        amplitude=amplitude,
        phase=phase,
    )

    assert sample.time_steps == num_packets
    assert sample.subcarriers == num_sub
    assert sample.antennas == num_ant
    assert sample.get_2d_amplitude().shape == (num_packets, num_ant * num_sub)

    val = sample.validate()
    assert val["valid"] is True
    assert val["nan_count"] == 0

    d = sample.to_dict(include_raw_preview=True)
    assert "preview_amplitude" in d
    assert d["sample_id"] == "test_001"
