"""
Wallhack1.8k / TU Wien Through-Wall Dataset Adapter.
Dataset: Wallhack1.8k (Wi-Fi CSI through-wall human sensing benchmark from TU Wien).
"""

import os
import glob
import numpy as np
from typing import List, Dict, Any, Optional
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource, FileSource
from ml.unified_model import CSISample, CSIMetadata


class WallhackAdapter(CSIAdapter):
    """Adapter for the Wallhack1.8k Through-Wall CSI Dataset."""

    @property
    def adapter_id(self) -> str:
        return "wallhack18k"

    @property
    def dataset_name(self) -> str:
        return "Wallhack1.8k TU Wien Dataset"

    @property
    def is_synthetic(self) -> bool:
        return False

    def can_handle(self, source_path_or_metadata: Any) -> bool:
        if isinstance(source_path_or_metadata, str):
            p = source_path_or_metadata.lower()
            if "wallhack" in p or "tu_wien" in p or "through_wall" in p:
                return True
        return False

    def get_dataset_metadata(self, source: Optional[CSIInputSource] = None) -> Dict[str, Any]:
        is_avail = source.is_available() if source is not None else False
        return {
            "dataset_id": "wallhack18k",
            "name": self.dataset_name,
            "adapter_id": self.adapter_id,
            "is_synthetic": False,
            "activities": ["walking", "standing", "sitting", "empty", "falling"],
            "environments": ["Residential", "Office", "Industrial"],
            "sampling_rate": 100.0,
            "subcarriers": 64,
            "antennas": 2,
            "bandwidth": 20.0,
            "csi_representation": "amplitude",
            "status": "Available (Files detected)" if is_avail else "Registered (Awaiting Local Dataset Import)",
            "license": "TU Wien Open Data",
            "description": "Through-wall Wi-Fi CSI sensing dataset evaluating attenuation and multipath through concrete and drywall."
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
                file_paths = glob.glob(os.path.join(source.root_path, "**", "*.npz"), recursive=True)
        else:
            file_paths = []

        for fpath in file_paths:
            if max_samples and len(samples) >= max_samples:
                break
            try:
                if fpath.endswith(".npz"):
                    npz = np.load(fpath)
                    amp = npz.get("csi_amp", npz.get("arr_0", None))
                else:
                    amp = np.load(fpath)

                if amp is None:
                    continue

                fname = os.path.basename(fpath).lower()
                inferred_act = "Walking"
                for act in ["walk", "stand", "sit", "empty", "fall"]:
                    if act in fname:
                        inferred_act = act.capitalize()
                        break

                metadata = CSIMetadata(
                    dataset_id="wallhack18k",
                    sample_id=os.path.splitext(os.path.basename(fpath))[0],
                    environment_id="env_through_wall_01",
                    environment_type="Residential",
                    activity_label=inferred_act,
                    subcarrier_count=amp.shape[-1] if amp.ndim > 1 else 64,
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
