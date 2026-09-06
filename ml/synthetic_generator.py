"""
Synthetic CSI Data Generator for WiFiSense AI.
CRITICAL RULE: All data generated here is explicitly labeled as 'Synthetic Demo Data'.
Used exclusively for development, offline testing, UI demonstration, and algorithm verification
without requiring live physical hardware.
"""

import numpy as np
import time
from typing import List, Dict, Any, Optional
from ml.unified_model import CSISample, CSIMetadata


# Standard canonical demo activities
DEMO_ACTIVITIES = [
    "Walking",
    "Sitting",
    "Standing",
    "Running",
    "Lying",
    "Waving",
    "Falling",
    "Empty"  # Absent
]

# Environment multipath profiles
ENVIRONMENT_PROFILES = {
    "Office": {"multipath_scale": 1.0, "noise_floor": 0.05, "base_attenuation": 1.2, "type": "Office"},
    "Classroom": {"multipath_scale": 1.4, "noise_floor": 0.08, "base_attenuation": 1.5, "type": "Classroom"},
    "Residential": {"multipath_scale": 0.8, "noise_floor": 0.04, "base_attenuation": 1.0, "type": "Residential"},
    "Healthcare": {"multipath_scale": 0.9, "noise_floor": 0.03, "base_attenuation": 1.1, "type": "Healthcare"},
    "Industrial": {"multipath_scale": 2.2, "noise_floor": 0.15, "base_attenuation": 2.0, "type": "Industrial"},
    "Hospitality": {"multipath_scale": 1.1, "noise_floor": 0.06, "base_attenuation": 1.3, "type": "Hospitality"},
    "Public Space": {"multipath_scale": 1.8, "noise_floor": 0.12, "base_attenuation": 1.7, "type": "Public Space"},
    "Custom": {"multipath_scale": 1.0, "noise_floor": 0.05, "base_attenuation": 1.0, "type": "Custom"},
}


class SyntheticCSIGenerator:
    """
    Generates synthetic Wi-Fi Channel State Information matrices mimicking
    realistic multipath, Doppler shifts, and frequency-selective fading.
    """

    def __init__(self, random_seed: Optional[int] = 42):
        if random_seed is not None:
            np.random.seed(random_seed)

    def generate_sample(
        self,
        activity: str = "Walking",
        environment_id: str = "env_office_01",
        environment_type: str = "Office",
        duration_sec: float = 3.0,
        sampling_rate: float = 50.0,
        subcarrier_count: int = 64,
        antenna_count: int = 1,
        sample_id: Optional[str] = None,
        subject_id: str = "subject_sim_01",
        add_anomaly: bool = False,
    ) -> CSISample:
        """
        Synthesizes a CSISample for a given activity and environment.
        """
        if sample_id is None:
            sample_id = f"syn_{activity.lower()}_{int(time.time()*1000) % 100000}"

        num_steps = int(duration_sec * sampling_rate)
        t = np.linspace(0, duration_sec, num_steps)
        subcarrier_indices = np.arange(subcarrier_count)

        # 1. Environment baseline multipath profile
        env_profile = ENVIRONMENT_PROFILES.get(environment_type, ENVIRONMENT_PROFILES["Office"])
        multipath_factor = env_profile["multipath_scale"]
        noise_level = env_profile["noise_floor"]
        base_atten = env_profile["base_attenuation"]

        # Frequency-selective static channel response (Rician / Rayleigh static profile across subcarriers)
        static_subcarrier_response = (
            np.sin(subcarrier_indices * 0.15) * 4.0
            + np.cos(subcarrier_indices * 0.05) * 2.0
            + 15.0 * base_atten
        )  # (S,)
        
        # 2D Static baseline: (T, S)
        csi_matrix = np.tile(static_subcarrier_response, (num_steps, 1))

        # 2. Activity Dynamic Doppler & Amplitude Signatures
        activity_lower = activity.lower()
        
        if "empty" in activity_lower or "absent" in activity_lower:
            # Static room, only thermal noise and slight environmental drift
            dynamic_component = np.zeros((num_steps, subcarrier_count))
            is_present = False
        else:
            is_present = True
            dynamic_component = np.zeros((num_steps, subcarrier_count))

            if "walk" in activity_lower:
                # 1.8 - 2.2 Hz walking stride Doppler + subcarrier phase shifts
                stride_freq = 1.8 + np.random.uniform(-0.2, 0.2)
                for s in range(subcarrier_count):
                    phase_shift = s * 0.08
                    carrier_weight = 1.0 + 0.3 * np.sin(s * 0.2)
                    dynamic_component[:, s] = (
                        carrier_weight * 3.5 * np.sin(2 * np.pi * stride_freq * t + phase_shift)
                        + carrier_weight * 1.2 * np.sin(2 * np.pi * (2 * stride_freq) * t + phase_shift)
                    )

            elif "run" in activity_lower:
                # 3.2 - 4.5 Hz rapid movement, strong Doppler and wider frequency dispersion
                run_freq = 3.6 + np.random.uniform(-0.3, 0.3)
                for s in range(subcarrier_count):
                    carrier_weight = 1.2 + 0.5 * np.cos(s * 0.3)
                    dynamic_component[:, s] = (
                        carrier_weight * 6.5 * np.sin(2 * np.pi * run_freq * t + s * 0.12)
                        + carrier_weight * 2.8 * np.sin(2 * np.pi * (2.2 * run_freq) * t)
                    )

            elif "sit" in activity_lower:
                # Low frequency posture / slight torso sway (0.3 Hz)
                for s in range(subcarrier_count):
                    dynamic_component[:, s] = 0.6 * np.sin(2 * np.pi * 0.35 * t + s * 0.05)

            elif "stand" in activity_lower:
                # Very subtle chest expansion / breathing ~ 0.22 Hz
                for s in range(subcarrier_count):
                    dynamic_component[:, s] = 0.3 * np.sin(2 * np.pi * 0.22 * t + s * 0.02)

            elif "wave" in activity_lower:
                # Localized arm movement ~ 2.0 Hz on middle subcarriers
                for s in range(subcarrier_count):
                    loc_factor = np.exp(-((s - 32) ** 2) / 200.0)  # localized to antenna/subcarriers
                    dynamic_component[:, s] = loc_factor * 4.2 * np.sin(2 * np.pi * 2.1 * t)

            elif "fall" in activity_lower:
                # Rapid impact shock at t ≈ 1.2s, sudden drop, then cessation of motion
                fall_start_idx = int(0.35 * num_steps)
                fall_duration_idx = int(0.25 * num_steps)
                fall_end_idx = fall_start_idx + fall_duration_idx
                
                # Pre-fall walking/standing
                dynamic_component[:fall_start_idx, :] = 1.0 * np.sin(2 * np.pi * 1.5 * t[:fall_start_idx, None])
                
                # Impact transient (huge spike across all subcarriers)
                for step_i in range(fall_start_idx, min(fall_end_idx, num_steps)):
                    rel_prog = (step_i - fall_start_idx) / max(1, fall_duration_idx)
                    spike = 12.0 * np.sin(np.pi * rel_prog) * np.exp(-1.5 * rel_prog)
                    dynamic_component[step_i, :] = spike * (1.0 + 0.2 * np.random.randn(subcarrier_count))
                
                # Post-fall: person on the floor, breathing only
                if fall_end_idx < num_steps:
                    post_t = t[fall_end_idx:] - t[fall_end_idx]
                    dynamic_component[fall_end_idx:, :] = 0.25 * np.sin(2 * np.pi * 0.18 * post_t[:, None])

            elif "ly" in activity_lower:  # Lying
                # Minimal movement, regular shallow breathing
                for s in range(subcarrier_count):
                    dynamic_component[:, s] = 0.2 * np.sin(2 * np.pi * 0.18 * t + s * 0.01)

            else:
                # Generic movement
                dynamic_component = np.tile(1.5 * np.sin(2 * np.pi * 1.0 * t[:, None]), (1, subcarrier_count))

        # 3. Add multipath scaling
        csi_matrix += dynamic_component * multipath_factor

        # 4. Inject synthetic anomaly if requested (erratic burst / jamming / non-biological transient)
        if add_anomaly:
            anomaly_start = int(0.4 * num_steps)
            anomaly_end = int(0.7 * num_steps)
            burst = np.random.uniform(8.0, 18.0, (anomaly_end - anomaly_start, subcarrier_count))
            csi_matrix[anomaly_start:anomaly_end, :] += burst

        # 5. Add thermal noise
        noise = np.random.normal(0.0, noise_level * 5.0, csi_matrix.shape)
        csi_matrix = np.clip(csi_matrix + noise, a_min=0.1, a_max=120.0).astype(np.float32)

        # 6. Generate matching phase data (synthesized relative phase across subcarriers)
        phase_matrix = np.zeros_like(csi_matrix)
        for s in range(subcarrier_count):
            phase_matrix[:, s] = np.mod(s * 0.18 + dynamic_component[:, s] * 0.1 + np.pi, 2 * np.pi) - np.pi

        metadata = CSIMetadata(
            dataset_id="synthetic_demo_dataset",
            sample_id=sample_id,
            timestamp=time.time(),
            environment_id=environment_id,
            environment_type=environment_type,
            subject_id=subject_id,
            activity_label="Empty" if not is_present else activity,
            antenna_count=antenna_count,
            subcarrier_count=subcarrier_count,
            sampling_rate=sampling_rate,
            bandwidth=20.0,
            csi_representation="amplitude",
            source_file="synthetic_generator://in-memory",
            is_synthetic=True,  # CRITICAL: Always explicit
            quality_metadata={
                "presence": "Present" if is_present else "Absent",
                "is_anomalous": add_anomaly,
                "label_clarification": "Synthetic Demo Data - For testing and demonstration only"
            }
        )

        return CSISample(
            metadata=metadata,
            amplitude=csi_matrix,
            phase=phase_matrix
        )

    def generate_batch(
        self,
        samples_per_activity: int = 15,
        environments: Optional[List[str]] = None,
        duration_sec: float = 3.0
    ) -> List[CSISample]:
        """Generates a balanced dataset of synthetic CSI samples for training/testing."""
        if environments is None:
            environments = ["Office", "Classroom", "Residential", "Healthcare"]

        batch = []
        for env in environments:
            env_id = f"env_{env.lower().replace(' ', '_')}_01"
            for activity in DEMO_ACTIVITIES:
                for i in range(samples_per_activity):
                    sample = self.generate_sample(
                        activity=activity,
                        environment_id=env_id,
                        environment_type=env,
                        duration_sec=duration_sec,
                        sample_id=f"syn_{env.lower()}_{activity.lower()}_{i+1:03d}",
                        subject_id=f"sub_sim_{(i%4)+1:02d}",
                        add_anomaly=(activity == "Falling" and i == 0) or (i == samples_per_activity - 1 and activity == "Running")
                    )
                    batch.append(sample)
        return batch
