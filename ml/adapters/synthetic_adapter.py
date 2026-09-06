"""
Synthetic Demo Data Adapter for WiFiSense AI.
Provides instant plug-and-play CSI data without requiring external hardware or dataset downloads.
"""

from typing import List, Dict, Any, Optional
import os
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource, FileSource, ReplaySource
from ml.synthetic_generator import SyntheticCSIGenerator, DEMO_ACTIVITIES, ENVIRONMENT_PROFILES
from ml.unified_model import CSISample


class SyntheticDemoAdapter(CSIAdapter):
    """Adapter for in-memory and generated Synthetic Demo Data."""

    def __init__(self):
        self.generator = SyntheticCSIGenerator(random_seed=42)

    @property
    def adapter_id(self) -> str:
        return "synthetic_demo"

    @property
    def dataset_name(self) -> str:
        return "Synthetic Demo Dataset"

    @property
    def is_synthetic(self) -> bool:
        return True  # Strictly True

    def can_handle(self, source_path_or_metadata: Any) -> bool:
        if isinstance(source_path_or_metadata, str):
            if "synthetic" in source_path_or_metadata.lower() or "demo" in source_path_or_metadata.lower():
                return True
        elif isinstance(source_path_or_metadata, dict):
            if source_path_or_metadata.get("is_synthetic") or source_path_or_metadata.get("adapter_id") == "synthetic_demo":
                return True
        return False

    def get_dataset_metadata(self, source: Optional[CSIInputSource] = None) -> Dict[str, Any]:
        return {
            "dataset_id": "synthetic_demo_dataset",
            "name": self.dataset_name,
            "adapter_id": self.adapter_id,
            "is_synthetic": True,
            "activities": DEMO_ACTIVITIES,
            "environments": list(ENVIRONMENT_PROFILES.keys()),
            "sampling_rate": 50.0,
            "subcarriers": 64,
            "antennas": 1,
            "bandwidth": 20.0,
            "csi_representation": "amplitude",
            "description": "Clearly labeled synthetic CSI signals generated to test and verify the processing and inference pipelines.",
            "status": "Available (In-Memory / Instant Demo)",
            "license": "Open Demonstration / Simulation",
        }

    def load_samples(
        self,
        source: CSIInputSource,
        max_samples: Optional[int] = None,
        environment_filter: Optional[str] = None,
        activity_filter: Optional[str] = None
    ) -> List[CSISample]:
        # Generate samples matching the filters
        envs = [environment_filter] if environment_filter else ["Office", "Classroom", "Residential", "Healthcare"]
        activities = [activity_filter] if activity_filter else DEMO_ACTIVITIES
        
        samples_per_act = max(1, 15 if max_samples is None else max(1, max_samples // (len(envs) * len(activities))))
        
        all_samples: List[CSISample] = []
        for env in envs:
            env_id = f"env_{env.lower().replace(' ', '_')}_01"
            for act in activities:
                for i in range(samples_per_act):
                    sample = self.generator.generate_sample(
                        activity=act,
                        environment_id=env_id,
                        environment_type=env,
                        duration_sec=3.0,
                        sample_id=f"syn_{env.lower()[:3]}_{act.lower()}_{i+1:03d}",
                        subject_id=f"sub_sim_{(i%3)+1:02d}",
                        add_anomaly=(act == "Falling" and i == 0)
                    )
                    all_samples.append(sample)
                    if max_samples and len(all_samples) >= max_samples:
                        return all_samples
        return all_samples
