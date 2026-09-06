"""
Generic File and CSV Adapter for custom user uploads.
Supports CSV, NPY, NPZ, and TXT files containing 2D or 3D numerical CSI matrices.
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource, FileSource
from ml.unified_model import CSISample, CSIMetadata


class GenericCSVAdapter(CSIAdapter):
    """Adapter for arbitrary user-uploaded CSV / NPY files."""

    @property
    def adapter_id(self) -> str:
        return "generic_csv"

    @property
    def dataset_name(self) -> str:
        return "Custom File / Generic CSV Adapter"

    @property
    def is_synthetic(self) -> bool:
        return False

    def can_handle(self, source_path_or_metadata: Any) -> bool:
        if isinstance(source_path_or_metadata, str):
            ext = os.path.splitext(source_path_or_metadata)[1].lower()
            if ext in [".csv", ".npy", ".npz", ".txt"]:
                return True
        return True  # Fallback adapter

    def get_dataset_metadata(self, source: Optional[CSIInputSource] = None) -> Dict[str, Any]:
        is_avail = source.is_available() if source is not None else False
        return {
            "dataset_id": "custom_file",
            "name": self.dataset_name,
            "adapter_id": self.adapter_id,
            "is_synthetic": False,
            "activities": ["custom_activity"],
            "environments": ["Custom"],
            "sampling_rate": 50.0,
            "subcarriers": 64,
            "antennas": 1,
            "bandwidth": 20.0,
            "csi_representation": "amplitude",
            "status": "Available" if is_avail else "Awaiting File",
            "description": "Flexible parser for custom user-uploaded Wi-Fi CSI amplitude CSV/NPY files."
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
            fpath = source.file_path
            try:
                if fpath.endswith(".npy"):
                    amp = np.load(fpath)
                elif fpath.endswith(".npz"):
                    npz = np.load(fpath)
                    amp = npz[list(npz.keys())[0]]
                elif fpath.endswith(".csv") or fpath.endswith(".txt"):
                    df = pd.read_csv(fpath)
                    num_cols = df.select_dtypes(include=[np.number]).columns
                    amp = df[num_cols].values if len(num_cols) > 0 else np.loadtxt(fpath, delimiter=",")
                else:
                    return []

                if amp.ndim == 1:
                    amp = amp.reshape(-1, min(64, len(amp)))

                metadata = CSIMetadata(
                    dataset_id="custom_upload",
                    sample_id=os.path.splitext(os.path.basename(fpath))[0],
                    environment_id="env_custom_01",
                    environment_type=environment_filter or "Custom",
                    activity_label=activity_filter or "CustomActivity",
                    subcarrier_count=amp.shape[-1] if amp.ndim > 1 else 64,
                    sampling_rate=50.0,
                    source_file=fpath,
                    is_synthetic=False
                )
                sample = CSISample(metadata=metadata, amplitude=amp)
                sample.validate()
                samples.append(sample)
            except Exception:
                pass

        return samples
