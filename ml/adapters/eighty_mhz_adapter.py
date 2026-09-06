"""
80-MHz Wi-Fi CSI Dataset Adapter.
Dataset: 80-MHz Wi-Fi CSI Dataset (IEEE 802.11ac VHT80 channel state information with 234/242 subcarriers).
"""

import os
import glob
import numpy as np
from typing import List, Dict, Any, Optional
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource, FileSource
from ml.unified_model import CSISample, CSIMetadata


class EightyMHzAdapter(CSIAdapter):
    """Adapter for 80-MHz wideband CSI datasets."""

    @property
    def adapter_id(self) -> str:
        return "eighty_mhz"

    @property
    def dataset_name(self) -> str:
        return "80-MHz Wi-Fi CSI Dataset"

    @property
    def is_synthetic(self) -> bool:
        return False

    def can_handle(self, source_path_or_metadata: Any) -> bool:
        if isinstance(source_path_or_metadata, str):
            p = source_path_or_metadata.lower()
            if "80mhz" in p or "80_mhz" in p or "vht80" in p or "80-mhz" in p:
                return True
        return False

    def get_dataset_metadata(self, source: Optional[CSIInputSource] = None) -> Dict[str, Any]:
        is_avail = source.is_available() if source is not None else False
        return {
            "dataset_id": "eighty_mhz_csi",
            "name": self.dataset_name,
            "adapter_id": self.adapter_id,
            "is_synthetic": False,
            "activities": ["walking", "sitting", "standing", "waving", "falling"],
            "environments": ["Office", "Residential", "Laboratory"],
            "sampling_rate": 100.0,
            "subcarriers": 242,
            "antennas": 1,
            "bandwidth": 80.0,
            "csi_representation": "amplitude",
            "status": "Available (Files detected)" if is_avail else "Registered (Awaiting Local Dataset Import)",
            "license": "Academic Open Dataset",
            "description": "High-resolution 80MHz bandwidth 802.11ac CSI dataset offering dense frequency-domain subcarrier profiling."
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
            file_paths = glob.glob(os.path.join(source.root_path, "**", "*.npy"), recursive=True)
        else:
            file_paths = []

        for fpath in file_paths:
            if max_samples and len(samples) >= max_samples:
                break
            try:
                amp = np.load(fpath)
                inferred_act = "Walking"
                for act in ["walk", "sit", "stand", "wave", "fall"]:
                    if act in fpath.lower():
                        inferred_act = act.capitalize()
                        break

                metadata = CSIMetadata(
                    dataset_id="eighty_mhz_csi",
                    sample_id=os.path.splitext(os.path.basename(fpath))[0],
                    environment_id="env_lab_80mhz",
                    environment_type="Office",
                    activity_label=inferred_act,
                    subcarrier_count=amp.shape[-1] if amp.ndim > 1 else 242,
                    sampling_rate=100.0,
                    bandwidth=80.0,
                    source_file=fpath,
                    is_synthetic=False
                )
                sample = CSISample(metadata=metadata, amplitude=amp)
                sample.validate()
                samples.append(sample)
            except Exception:
                continue

        return samples
