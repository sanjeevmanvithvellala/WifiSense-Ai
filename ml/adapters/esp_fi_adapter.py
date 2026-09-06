"""
ESP-Fi HAR Dataset Adapter.
Dataset: ESP-Fi (Wi-Fi CSI Human Activity Recognition via ESP32)
Format: 64 subcarriers (active: ~52), 1 antenna, 20MHz bandwidth, typical 50-100Hz sampling.
"""

import os
import glob
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource, FileSource
from ml.unified_model import CSISample, CSIMetadata


class ESPFiAdapter(CSIAdapter):
    """Adapter for the ESP-Fi dataset."""

    @property
    def adapter_id(self) -> str:
        return "esp_fi"

    @property
    def dataset_name(self) -> str:
        return "ESP-Fi HAR Dataset"

    @property
    def is_synthetic(self) -> bool:
        return False  # Real dataset adapter

    def can_handle(self, source_path_or_metadata: Any) -> bool:
        if isinstance(source_path_or_metadata, str):
            path_lower = source_path_or_metadata.lower()
            if "esp-fi" in path_lower or "esp_fi" in path_lower or "esp32" in path_lower:
                return True
            if os.path.isdir(source_path_or_metadata):
                # Check for characteristic ESP32 CSI filenames or structure
                files = os.listdir(source_path_or_metadata)
                if any("esp" in f.lower() or "csi" in f.lower() for f in files):
                    return True
        return False

    def get_dataset_metadata(self, source: Optional[CSIInputSource] = None) -> Dict[str, Any]:
        is_avail = source.is_available() if source is not None else False
        return {
            "dataset_id": "esp_fi_har",
            "name": self.dataset_name,
            "adapter_id": self.adapter_id,
            "is_synthetic": False,
            "activities": ["walking", "running", "sitting", "standing", "falling", "waving"],
            "environments": ["Office", "Classroom", "Residential"],
            "sampling_rate": 50.0,
            "subcarriers": 64,
            "antennas": 1,
            "bandwidth": 20.0,
            "csi_representation": "amplitude",
            "source_type": "ESP32 CSI 802.11n",
            "status": "Available (Files detected)" if is_avail else "Registered (Awaiting Local Dataset Import)",
            "license": "Academic / Open Access",
            "description": "CSI activity dataset collected using low-cost ESP32 microcontrollers at 20MHz bandwidth."
        }

    def load_samples(
        self,
        source: CSIInputSource,
        max_samples: Optional[int] = None,
        environment_filter: Optional[str] = None,
        activity_filter: Optional[str] = None
    ) -> List[CSISample]:
        if not source.is_available():
            return []

        samples: List[CSISample] = []
        
        if isinstance(source, FileSource):
            file_paths = [source.file_path]
        elif isinstance(source, DatasetSource) and source.root_path:
            file_paths = glob.glob(os.path.join(source.root_path, "**", "*.csv"), recursive=True)
            if not file_paths:
                file_paths = glob.glob(os.path.join(source.root_path, "**", "*.npy"), recursive=True)
        else:
            file_paths = []

        for fpath in file_paths:
            if max_samples and len(samples) >= max_samples:
                break
            try:
                # Infer activity and environment from directory structure or filename if present
                fname = os.path.basename(fpath).lower()
                inferred_act = "unknown"
                for act in ["walk", "run", "sit", "stand", "fall", "wave", "jump", "lie"]:
                    if act in fname:
                        inferred_act = act.capitalize()
                        break

                inferred_env = "Office"
                for env in ["office", "classroom", "residential", "room", "lab"]:
                    if env in fpath.lower():
                        inferred_env = env.capitalize()
                        break

                if environment_filter and inferred_env.lower() != environment_filter.lower():
                    continue
                if activity_filter and inferred_act.lower() != activity_filter.lower():
                    continue

                if fpath.endswith(".npy"):
                    data = np.load(fpath)
                    if data.ndim == 2:
                        amp = data
                    elif data.ndim == 3:
                        amp = data[:, 0, :] if data.shape[1] == 1 else data.reshape(data.shape[0], -1)
                    else:
                        continue
                elif fpath.endswith(".csv"):
                    df = pd.read_csv(fpath)
                    # Filter numerical columns or CSI amplitude array columns
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 32:
                        amp = df[numeric_cols].values
                    else:
                        continue
                else:
                    continue

                metadata = CSIMetadata(
                    dataset_id="esp_fi_har",
                    sample_id=os.path.splitext(os.path.basename(fpath))[0],
                    environment_id=f"env_{inferred_env.lower()}",
                    environment_type=inferred_env,
                    activity_label=inferred_act,
                    subcarrier_count=amp.shape[1] if amp.ndim > 1 else 64,
                    sampling_rate=50.0,
                    bandwidth=20.0,
                    source_file=fpath,
                    is_synthetic=False
                )

                sample = CSISample(metadata=metadata, amplitude=amp)
                sample.validate()
                samples.append(sample)

            except Exception as e:
                # Corrupted or unparseable sample file skipped safely
                continue

        return samples
