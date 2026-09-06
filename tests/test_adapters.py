"""Unit tests for Dataset Adapters and Registry."""
import os
import tempfile
import numpy as np
import pytest
from ml.adapters.base import DatasetSource, FileSource
from ml.adapters.synthetic_adapter import SyntheticDemoAdapter
from ml.adapters.generic_csv_adapter import GenericCSVAdapter
from ml.adapters.registry import AdapterRegistry


def test_synthetic_adapter():
    adapter = SyntheticDemoAdapter()
    assert adapter.adapter_id == "synthetic_demo"
    assert adapter.is_synthetic is True

    source = DatasetSource(dataset_id="synthetic_demo_dataset")
    samples = adapter.load_samples(source, max_samples=4)
    assert len(samples) == 4
    assert samples[0].metadata.is_synthetic is True
    assert samples[0].amplitude.ndim >= 2


def test_generic_csv_adapter():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        f.write("timestamp,sub_0,sub_1,sub_2,sub_3\n")
        for i in range(50):
            t = i * 0.01
            f.write(f"{t},12.5,14.2,11.8,13.0\n")
        temp_path = f.name

    try:
        adapter = GenericCSVAdapter()
        assert adapter.can_handle(temp_path) is True

        source = FileSource(file_path=temp_path)
        samples = adapter.load_samples(source)
        assert len(samples) == 1
        sample = samples[0]
        assert sample.amplitude.shape == (50, 5)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_adapter_registry():
    registry = AdapterRegistry()
    available = [a["adapter_id"] for a in registry.list_adapters()]
    assert "synthetic_demo" in available
    assert "generic_csv" in available
    assert "esp_fi" in available
    assert "csi_bench" in available
    assert "eighty_mhz" in available
    assert "wallhack18k" in available

    adapter = registry.get_adapter("synthetic_demo")
    assert adapter is not None
