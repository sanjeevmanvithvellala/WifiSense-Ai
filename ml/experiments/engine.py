"""
Reusable Experiment Engine for WiFiSense AI.
Executes Same-Environment, Cross-Environment, Multi-Environment, and Adaptation experiments.
CRITICAL RULE: All metrics are computed dynamically from actual predictions; never hard-coded.
"""

import time
import uuid
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ml.unified_model import CSISample
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource
from ml.adapters.registry import default_adapter_registry
from ml.preprocessing.pipeline import PreprocessingPipeline, PreprocessingConfig
from ml.features.extractor import FeatureExtractor, FeatureConfig
from ml.models.registry import default_model_registry
from ml.models.base import BaseCSIModel
from ml.environment.adaptation import EnvironmentAdaptationEngine
from ml.experiments.metrics import calculate_classification_metrics


class ExperimentEngine:
    """Orchestrates machine learning experiments and cross-environment adaptation benchmarking."""

    def __init__(self):
        self.preprocessor = PreprocessingPipeline()
        self.feature_extractor = FeatureExtractor()
        self.adaptation_engine = EnvironmentAdaptationEngine()

    def extract_features_and_labels(
        self,
        samples: List[CSISample],
        preprocessor: Optional[PreprocessingPipeline] = None,
        feature_extractor: Optional[FeatureExtractor] = None,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Processes samples into feature matrix X, label array y, and environment list."""
        prep = preprocessor or self.preprocessor
        feat_ext = feature_extractor or self.feature_extractor

        X_list = []
        y_list = []
        env_list = []

        for sample in samples:
            windows, _, phase_sanitized = prep.process_sample(sample)
            if windows.shape[0] == 0:
                continue
            feats = feat_ext.extract_batch(windows)
            label = sample.metadata.activity_label or "Unknown"
            env = sample.metadata.environment_type

            for f in feats:
                X_list.append(f)
                y_list.append(label)
                env_list.append(env)

        if not X_list:
            return np.empty((0, 64), dtype=np.float32), np.empty(0, dtype=object), []

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=object)
        return X, y, env_list

    def run_experiment(
        self,
        experiment_type: str,  # 'same_environment', 'cross_environment', 'multi_environment', 'adaptation'
        dataset_id: str,
        training_environments: List[str],
        test_environments: List[str],
        model_architecture: str = "Random Forest",
        custom_name: Optional[str] = None,
        random_seed: int = 42,
        dataset_source: Optional[CSIInputSource] = None,
        max_samples_per_env: int = 40,
    ) -> Dict[str, Any]:
        """Runs a complete rigorous experiment end-to-end and returns real evaluation metrics."""
        np.random.seed(random_seed)
        t_start = time.time()
        exp_id = f"exp_{experiment_type}_{uuid.uuid4().hex[:8]}"
        name = custom_name or f"{model_architecture} {experiment_type.replace('_', ' ').title()}"

        # 1. Resolve Adapter
        adapter = default_adapter_registry.get_adapter(dataset_id) or default_adapter_registry.detect_adapter(dataset_id)
        source = dataset_source or DatasetSource(dataset_id=dataset_id)

        # 2. Load Training Samples
        train_samples: List[CSISample] = []
        for env in training_environments:
            s_env = adapter.load_samples(source, max_samples=max_samples_per_env, environment_filter=env)
            train_samples.extend(s_env)

        # 3. Load Test Samples
        test_samples: List[CSISample] = []
        for env in test_environments:
            s_env = adapter.load_samples(source, max_samples=max_samples_per_env, environment_filter=env)
            test_samples.extend(s_env)

        # Fallback if source had zero samples: load from synthetic demo generator
        if not train_samples or not test_samples:
            syn_adapter = default_adapter_registry.get_adapter("synthetic_demo")
            if not train_samples:
                for env in training_environments:
                    train_samples.extend(syn_adapter.load_samples(source, max_samples=max_samples_per_env, environment_filter=env))
            if not test_samples:
                for env in test_environments:
                    test_samples.extend(syn_adapter.load_samples(source, max_samples=max_samples_per_env, environment_filter=env))

        # 4. Feature Extraction
        X_train, y_train, _ = self.extract_features_and_labels(train_samples)
        X_test, y_test, _ = self.extract_features_and_labels(test_samples)

        # If same environment and same sample pool, perform stratified train-test split
        if training_environments == test_environments and np.array_equal(X_train, X_test):
            n_total = len(X_train)
            indices = np.arange(n_total)
            np.random.shuffle(indices)
            split_idx = int(n_total * 0.75)
            train_idx, test_idx = indices[:split_idx], indices[split_idx:]
            X_train, y_train = X_train[train_idx], y_train[train_idx]
            X_test, y_test = X_test[test_idx], y_test[test_idx]

        # 5. Instantiate and Train Model
        model_id = f"m_{exp_id}"
        model = default_model_registry.create_model(
            architecture=model_architecture,
            model_id=model_id,
            name=f"Model for {name}"
        )

        train_summary = model.train(X_train, y_train)

        # 6. Evaluate on Test Set
        eval_metrics = model.evaluate(X_test, y_test)

        # 7. If Adaptation Experiment: Compare Baseline vs CORAL Adapted
        adaptation_comparison = None
        if experiment_type == "adaptation":
            adaptation_comparison = self.adaptation_engine.compare_adaptation(
                model=model,
                X_target=X_test,
                y_target=y_test,
                X_source_train=X_train,
                strategy="coral"
            )

        duration_sec = time.time() - t_start

        result = {
            "experiment_id": exp_id,
            "name": name,
            "experiment_type": experiment_type,
            "dataset_id": dataset_id,
            "is_synthetic": any(s.metadata.is_synthetic for s in train_samples),
            "training_environments": training_environments,
            "test_environments": test_environments,
            "model_architecture": model_architecture,
            "random_seed": random_seed,
            "training_samples_count": len(X_train),
            "test_samples_count": len(X_test),
            "classes": model.classes_,
            "metrics": eval_metrics,
            "adaptation_comparison": adaptation_comparison,
            "duration_sec": round(duration_sec, 2),
            "timestamp": time.time(),
            "status": "COMPLETED"
        }
        return result
