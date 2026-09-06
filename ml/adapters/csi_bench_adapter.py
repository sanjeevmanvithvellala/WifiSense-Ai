"""
CSI-Bench Dataset Adapter.
Dataset: CSI-Bench (Benchmark dataset for Cross-Environment Wi-Fi CSI Activity Recognition).
Multi-environment data with Intel 5300 or Atheros NIC structures (30 to 114 subcarriers).
"""

import os
import glob
import numpy as np
from typing import List, Dict, Any, Optional
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource, FileSource
from ml.unified_model import CSISample, CSIMetadata


class CSIBenchAdapter(CSIAdapter):
    """Adapter for the multi-environment CSI-Bench dataset."""

    @property
    def adapter_id(self) -> str:
        return "csi_bench"

    @property
    def dataset_name(self) -> str:
        return "CSI-Bench Multi-Environment Dataset"

    @property
    def is_synthetic(self) -> bool:
        return False

    def can_handle(self, source_path_or_metadata: Any) -> bool:
        if isinstance(source_path_or_metadata, str):
            p = source_path_or_metadata.lower()
            if "csi-bench" in p or "csibench" in p:
                return True
            if os.path.isdir(source_path_or_metadata):
                files = os.listdir(source_path_or_metadata)
                if any("env_" in f.lower() or "room_" in f.lower() for f in files):
                    return True
        return False

    def get_dataset_metadata(self, source: Optional[CSIInputSource] = None) -> Dict[str, Any]:
        is_avail = source.is_available() if source is not None else False
        return {
            "dataset_id": "csi_bench",
            "name": self.dataset_name,
            "adapter_id": self.adapter_id,
            "is_synthetic": False,
            "activities": ["walking", "sitting", "standing", "lying", "waving", "falling"],
            "environments": ["Office", "Classroom", "Residential", "MeetingRoom", "Lab"],
            "sampling_rate": 100.0,
            "subcarriers": 90,  # 30 subcarriers x 3 antennas
            "antennas": 3,
            "bandwidth": 20.0,
            "csi_representation": "amplitude",
            "status": "Available (Files detected)" if is_avail else "Registered (Awaiting Local Dataset Import)",
            "license": "Research Use Only",
            "description": "Standardized benchmark for cross-environment CSI activity evaluation across multiple distinct rooms."
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
            if not file_paths:
                file_paths = glob.glob(os.path.join(source.root_path, "**", "*.csv"), recursive=True)
        else:
            file_paths = []

        for fpath in file_paths:
            if max_samples and len(samples) >= max_samples:
                break
            try:
                fname = os.path.basename(fpath).lower()
                inferred_act = "unknown"
                for act in ["walk", "sit", "stand", "lie", "wave", "fall"]:
                    if act in fname:
                        inferred_act = act.capitalize()
                        break

                inferred_env = "Office"
                for env in ["office", "classroom", "residential", "meeting", "lab"]:
                    if env in fpath.lower():
                        inferred_env = env.capitalize()
                        break

                if environment_filter and inferred_env.lower() != environment_filter.lower():
                    continue
                if activity_filter and inferred_act.lower() != activity_filter.lower():
                    continue

                if fpath.endswith(".npy"):
                    amp = np.load(fpath)
                else:
                    amp = np.loadtxt(fpath, delimiter=",")

                if amp.ndim == 1:
                    amp = amp.reshape(-1, 30)

                metadata = CSIMetadata(
                    dataset_id="csi_bench",
                    sample_id=os.path.splitext(os.path.basename(fpath))[0],
                    environment_id=f"env_{inferred_env.lower()}",
                    environment_type=inferred_env,
                    activity_label=inferred_act,
                    subcarrier_count=amp.shape[-1],
                    sampling_rate=100.0,
                    source_file=fpath,
                    is_synthetic=False
                )
                sample = CSISample(metadata=metadata, amplitude=amp)
                sample.validate()
                samples.append(sample)
            except Exception:
                continue

        return samples
