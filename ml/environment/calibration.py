"""
Environment Calibration and Baseline Profile Engine.
Computes ambient multipath profiles and environment scaling metrics from static empty-room CSI recordings.
"""

import numpy as np
from typing import Dict, Any, Optional
from ml.unified_model import CSISample


class EnvironmentProfile:
    """Stores calibration parameters for a physical environment."""

    def __init__(
        self,
        environment_id: str,
        name: str,
        environment_type: str = "Office",
        description: str = "",
        multipath_factor: float = 1.0,
        noise_floor: float = 0.05,
        subcarrier_baseline: Optional[np.ndarray] = None,
        covariance_matrix: Optional[np.ndarray] = None,
        feature_mean: Optional[np.ndarray] = None,
    ):
        self.environment_id = environment_id
        self.name = name
        self.environment_type = environment_type
        self.description = description
        self.multipath_factor = multipath_factor
        self.noise_floor = noise_floor
        self.subcarrier_baseline = subcarrier_baseline
        self.covariance_matrix = covariance_matrix
        self.feature_mean = feature_mean
        self.is_calibrated = subcarrier_baseline is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment_id": self.environment_id,
            "name": self.name,
            "environment_type": self.environment_type,
            "description": self.description,
            "multipath_factor": round(float(self.multipath_factor), 3),
            "noise_floor": round(float(self.noise_floor), 4),
            "is_calibrated": self.is_calibrated,
            "subcarrier_count": len(self.subcarrier_baseline) if self.subcarrier_baseline is not None else 64,
        }


def calibrate_environment_from_samples(
    environment_id: str,
    name: str,
    environment_type: str,
    empty_samples: list[CSISample],
    description: str = ""
) -> EnvironmentProfile:
    """
    Computes static subcarrier baseline profile and noise metrics from empty room / ambient CSI samples.
    """
    if not empty_samples:
        return EnvironmentProfile(environment_id, name, environment_type, description)

    stacked_amps = []
    for sample in empty_samples:
        amp2d = sample.get_2d_amplitude()
        stacked_amps.append(amp2d)

    all_data = np.vstack(stacked_amps)
    subcarrier_baseline = np.mean(all_data, axis=0)  # (S,)
    subcarrier_std = np.std(all_data, axis=0)
    
    noise_floor = float(np.mean(subcarrier_std))
    multipath_factor = float(np.std(subcarrier_baseline) / max(1e-4, np.mean(subcarrier_baseline)))

    return EnvironmentProfile(
        environment_id=environment_id,
        name=name,
        environment_type=environment_type,
        description=description,
        multipath_factor=multipath_factor,
        noise_floor=noise_floor,
        subcarrier_baseline=subcarrier_baseline
    )
