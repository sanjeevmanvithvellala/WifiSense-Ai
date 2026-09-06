"""
Unified CSI Data Model for WiFiSense AI.
Represents standardized Wi-Fi Channel State Information regardless of source hardware or dataset.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import numpy as np
import json
import time


@dataclass
class CSIMetadata:
    """Metadata describing the CSI sample collection context."""
    dataset_id: str
    sample_id: str
    timestamp: float = field(default_factory=time.time)
    environment_id: str = "default_env"
    environment_type: str = "Office"  # Residential, Classroom, Office, Healthcare, Industrial, Hospitality, Public Space, Custom
    subject_id: Optional[str] = None
    activity_label: Optional[str] = None
    antenna_count: int = 1
    subcarrier_count: int = 64
    sampling_rate: float = 50.0  # Hz
    bandwidth: float = 20.0  # MHz (20, 40, 80, 160)
    csi_representation: str = "amplitude"  # 'amplitude', 'phase', 'complex'
    source_file: Optional[str] = None
    is_synthetic: bool = False
    quality_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "sample_id": self.sample_id,
            "timestamp": self.timestamp,
            "environment_id": self.environment_id,
            "environment_type": self.environment_type,
            "subject_id": self.subject_id,
            "activity_label": self.activity_label,
            "antenna_count": self.antenna_count,
            "subcarrier_count": self.subcarrier_count,
            "sampling_rate": self.sampling_rate,
            "bandwidth": self.bandwidth,
            "csi_representation": self.csi_representation,
            "source_file": self.source_file,
            "is_synthetic": self.is_synthetic,
            "quality_metadata": self.quality_metadata,
        }


@dataclass
class CSISample:
    """
    Standardized CSI Sample container.
    
    Shapes:
    - amplitude: 2D (time_steps, subcarriers) or 3D (time_steps, antennas, subcarriers)
    - phase: optional matching array
    - complex_csi: optional complex128 array
    """
    metadata: CSIMetadata
    amplitude: np.ndarray
    phase: Optional[np.ndarray] = None
    complex_csi: Optional[np.ndarray] = None

    def __post_init__(self):
        # Validate data types and shape conformity
        if not isinstance(self.amplitude, np.ndarray):
            self.amplitude = np.array(self.amplitude, dtype=np.float32)
        else:
            self.amplitude = self.amplitude.astype(np.float32)

        if self.phase is not None:
            if not isinstance(self.phase, np.ndarray):
                self.phase = np.array(self.phase, dtype=np.float32)
            else:
                self.phase = self.phase.astype(np.float32)

        if self.complex_csi is not None:
            if not isinstance(self.complex_csi, np.ndarray):
                self.complex_csi = np.array(self.complex_csi, dtype=np.complex64)

    @property
    def time_steps(self) -> int:
        return self.amplitude.shape[0] if self.amplitude.ndim >= 1 else 0

    @property
    def subcarriers(self) -> int:
        return self.amplitude.shape[-1] if self.amplitude.ndim >= 2 else self.metadata.subcarrier_count

    @property
    def antennas(self) -> int:
        if self.amplitude.ndim == 3:
            return self.amplitude.shape[1]
        return self.metadata.antenna_count

    def get_2d_amplitude(self) -> np.ndarray:
        """Returns 2D (time_steps, total_channels) array suitable for 2D matrix operations."""
        if self.amplitude.ndim == 3:
            # Flatten antennas and subcarriers: (T, A, S) -> (T, A*S)
            T, A, S = self.amplitude.shape
            return self.amplitude.reshape(T, A * S)
        return self.amplitude

    def validate(self) -> Dict[str, Any]:
        """Validates numerical integrity of the sample."""
        nan_count = int(np.isnan(self.amplitude).sum())
        inf_count = int(np.isinf(self.amplitude).sum())
        is_corrupt = (nan_count > 0) or (inf_count > 0) or (self.amplitude.size == 0)
        
        val_meta = {
            "valid": not is_corrupt,
            "nan_count": nan_count,
            "inf_count": inf_count,
            "shape": list(self.amplitude.shape),
            "mean": float(np.nanmean(self.amplitude)) if self.amplitude.size > 0 else 0.0,
            "std": float(np.nanstd(self.amplitude)) if self.amplitude.size > 0 else 0.0,
            "min": float(np.nanmin(self.amplitude)) if self.amplitude.size > 0 else 0.0,
            "max": float(np.nanmax(self.amplitude)) if self.amplitude.size > 0 else 0.0,
        }
        self.metadata.quality_metadata.update(val_meta)
        return val_meta

    def to_dict(self, include_raw_preview: bool = True) -> Dict[str, Any]:
        """Serializes metadata and preview representation for API transmission."""
        res = self.metadata.to_dict()
        res["shape"] = list(self.amplitude.shape)
        if include_raw_preview:
            # Send sample preview (first up to 30 timesteps and 16 subcarriers for efficiency)
            preview_amp = self.get_2d_amplitude()[:30, :min(32, self.subcarriers)].tolist()
            res["preview_amplitude"] = preview_amp
        return res
