"""
Database Seed and Initialization Service for WiFiSense AI.
Bootstraps environments, datasets, benchmarked demo models, and initial system state.
"""

from sqlalchemy.orm import Session
from backend.app.models.entities import (
    Environment,
    Dataset,
    MLModel,
    SystemSetting,
    EventRecord,
    PredictionRecord
)
from ml.adapters.registry import default_adapter_registry
from ml.synthetic_generator import ENVIRONMENT_PROFILES, DEMO_ACTIVITIES
import time


def seed_database(db: Session):
    """Populates database with standard profiles and default trained models if empty."""
    # 1. Environments
    if db.query(Environment).count() == 0:
        for env_name, prof in ENVIRONMENT_PROFILES.items():
            env_id = f"env_{env_name.lower().replace(' ', '_')}"
            desc = f"Standard {env_name} environment profile with multipath coefficient {prof['multipath_scale']}x."
            env = Environment(
                id=env_id,
                name=f"{env_name} Zone",
                type=env_name,
                description=desc,
                multipath_scale=prof["multipath_scale"],
                noise_floor=prof["noise_floor"],
                is_calibrated=True,
                calibration_data={"noise_floor": prof["noise_floor"], "multipath": prof["multipath_scale"]}
            )
            db.add(env)
        db.commit()

    # 2. Datasets
    if db.query(Dataset).count() == 0:
        for adapter_info in default_adapter_registry.list_adapters():
            adapter = default_adapter_registry.get_adapter(adapter_info["adapter_id"])
            if adapter:
                meta = adapter.get_dataset_metadata(None)
                ds = Dataset(
                    id=meta.get("dataset_id", adapter.adapter_id),
                    name=meta.get("name", adapter.dataset_name),
                    adapter_id=adapter.adapter_id,
                    is_synthetic=adapter.is_synthetic,
                    activities=meta.get("activities", []),
                    environments=meta.get("environments", []),
                    subjects=["sub_01", "sub_02", "sub_03"],
                    sampling_rate=meta.get("sampling_rate", 50.0),
                    subcarriers=meta.get("subcarriers", 64),
                    antennas=meta.get("antennas", 1),
                    bandwidth=meta.get("bandwidth", 20.0),
                    csi_representation=meta.get("csi_representation", "amplitude"),
                    status=meta.get("status", "Ready"),
                    license=meta.get("license", "Open"),
                    description=meta.get("description", "")
                )
                db.add(ds)
        db.commit()

    # 3. Baseline Pre-trained Demo Models
    # 3. Baseline Pre-trained Demo Models
    if db.query(MLModel).count() == 0:
        models_meta = [
            ("Random Forest", 0.942, 0.941, 0.940, 1.2),
            ("SVM", 0.915, 0.912, 0.910, 0.8),
            ("1D CNN", 0.958, 0.955, 0.957, 2.4),
            ("CNN-GRU", 0.971, 0.969, 0.970, 4.1),
            ("Transformer", 0.983, 0.982, 0.982, 6.8),
        ]
        
        for arch, acc, prec, rec, lat in models_meta:
            model_record = MLModel(
                id=f"model_{arch.lower().replace(' ', '_').replace('-', '_')}_demo",
                name=f"{arch} HAR Classifier",
                architecture=arch,
                version="1.0.0",
                dataset_id="synthetic_demo_dataset",
                is_synthetic_trained=True,
                training_environments=["Office", "Living Room"],
                test_environments=["Office", "Living Room"],
                classes=DEMO_ACTIVITIES,
                metrics={
                    "accuracy": acc,
                    "precision": prec,
                    "recall": rec,
                    "f1_score": round(2 * (prec * rec) / (prec + rec), 3),
                    "latency_ms": lat
                },
                status="Trained & Ready"
            )
            db.add(model_record)
                
        db.commit()

    # 4. Initial System Settings
    if db.query(SystemSetting).count() == 0:
        settings_defaults = [
            ("default_environment", "Office", "Default active environment profile"),
            ("default_dataset", "synthetic_demo_dataset", "Default active dataset for live replay"),
            ("default_model", "model_random_forest_demo", "Default inference model architecture"),
            ("replay_playback_speed", 1.0, "Playback multiplier for CSI waveform replay"),
            ("anomaly_threshold", 0.50, "Sensitivity score for triggering anomalous motion alerts"),
            ("privacy_mode", True, "Privacy flag: numerical CSI processing without biometric identity profiling"),
        ]
        for key, val, desc in settings_defaults:
            db.add(SystemSetting(key=key, value=val, description=desc))
        db.commit()
