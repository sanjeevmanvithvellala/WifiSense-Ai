"""
Real-time Inference Engine for WiFiSense AI.
Processes incoming CSI streaming windows, extracts features, performs activity HAR classification,
presence detection, and anomaly scoring.
"""

import time
import numpy as np
from typing import Dict, Any, Optional, List
from ml.unified_model import CSISample
from ml.preprocessing.pipeline import PreprocessingPipeline, PreprocessingConfig
from ml.features.extractor import FeatureExtractor, FeatureConfig
from ml.models.base import BaseCSIModel, BaseAnomalyDetector
from ml.models.random_forest import RandomForestCSIClassifier
from ml.models.isolation_forest import IsolationForestAnomalyDetector
from ml.synthetic_generator import SyntheticCSIGenerator


class InferenceEngine:
    """High-performance inference engine for live CSI replay and batch evaluation."""

    def __init__(
        self,
        classifier: Optional[BaseCSIModel] = None,
        anomaly_detector: Optional[BaseAnomalyDetector] = None,
        preprocessor: Optional[PreprocessingPipeline] = None,
        feature_extractor: Optional[FeatureExtractor] = None,
    ):
        self.preprocessor = preprocessor or PreprocessingPipeline()
        self.feature_extractor = feature_extractor or FeatureExtractor()
        self.classifier = classifier
        self.anomaly_detector = anomaly_detector
        self._ensure_default_models()

    def _ensure_default_models(self):
        """Bootstraps fast lightweight demo models if none are explicitly loaded."""
        if self.classifier is None or not self.classifier.is_trained:
            # Train demo classifier on fast synthetic demo data immediately
            gen = SyntheticCSIGenerator(random_seed=42)
            batch = gen.generate_batch(samples_per_activity=2)
            
            X_list, y_list = [], []
            for s in batch:
                wins, _, _ = self.preprocessor.process_sample(s)
                feats = self.feature_extractor.extract_batch(wins)
                for f in feats:
                    X_list.append(f)
                    y_list.append(s.metadata.activity_label)
                    
            X = np.array(X_list, dtype=np.float32)
            y = np.array(y_list, dtype=object)

            self.classifier = RandomForestCSIClassifier(
                model_id="rf_demo_default",
                name="Default Demo HAR Classifier",
                n_estimators=15,
                max_depth=8
            )
            self.classifier.train(X, y)

        if self.anomaly_detector is None or not self.anomaly_detector.is_trained:
            # Train normal distribution detector on non-falling, non-empty data
            gen = SyntheticCSIGenerator(random_seed=42)
            norm_batch = [gen.generate_sample(activity=act) for act in ["Walking", "Sitting", "Standing"] for _ in range(2)]
            X_norm = []
            for s in norm_batch:
                wins, _, _ = self.preprocessor.process_sample(s)
                feats = self.feature_extractor.extract_batch(wins)
                for f in feats:
                    X_norm.append(f)
            
            self.anomaly_detector = IsolationForestAnomalyDetector(
                model_id="iforest_demo_default",
                name="Default Demo Anomaly Detector",
                n_estimators=15
            )
            self.anomaly_detector.fit(np.array(X_norm, dtype=np.float32))

    def set_classifier(self, classifier: BaseCSIModel):
        self.classifier = classifier

    def set_anomaly_detector(self, detector: BaseAnomalyDetector):
        self.anomaly_detector = detector

    def process_window(
        self,
        window_2d: np.ndarray,
        environment_type: str = "Office",
        ambient_baseline: Optional[np.ndarray] = None,
        is_synthetic: bool = False
    ) -> Dict[str, Any]:
        """
        Executes inference on a single 2D time-window matrix of shape (window_size, subcarriers).
        
        Returns real-time activity intelligence payload.
        """
        t0 = time.time()
        
        # 1. Preprocess
        proc_win = self.preprocessor.process_matrix(
            window_2d,
            ambient_baseline=ambient_baseline
        )

        # 2. Extract features
        feats = self.feature_extractor.extract_window_features(proc_win)
        feats_2d = np.expand_dims(feats, axis=0)

        # 3. HAR Activity Classification
        if self.classifier is not None and self.classifier.is_trained:
            pred_activity = str(self.classifier.predict(feats_2d)[0])
            probas = self.classifier.predict_proba(feats_2d)[0]
            max_idx = int(np.argmax(probas))
            confidence = float(probas[max_idx])
            class_probs = {cls_name: round(float(probas[i]), 3) for i, cls_name in enumerate(self.classifier.classes_)}
        else:
            pred_activity = "Unknown"
            confidence = 0.0
            class_probs = {}

        # 4. Presence Detection (heuristic + model probability)
        # Calculate dynamic Doppler variance and energy
        dynamic_energy = float(np.var(proc_win))
        if pred_activity.lower() in ["empty", "absent"] or dynamic_energy < 0.02:
            presence_status = "Absent"
            presence_confidence = round(float(class_probs.get("Empty", 0.95)), 3)
        else:
            presence_status = "Present"
            presence_confidence = round(1.0 - float(class_probs.get("Empty", 0.05)), 3)

        # 5. Anomaly Detection
        if self.anomaly_detector is not None and self.anomaly_detector.is_trained:
            anomaly_score = float(self.anomaly_detector.score_samples(feats_2d)[0])
            is_anomaly = bool(anomaly_score >= self.anomaly_detector.threshold or pred_activity.lower() == "falling")
        else:
            anomaly_score = 0.05
            is_anomaly = False

        latency_ms = (time.time() - t0) * 1000.0

        return {
            "activity": pred_activity,
            "confidence": round(confidence, 4),
            "class_probabilities": class_probs,
            "presence": presence_status,
            "presence_confidence": round(presence_confidence, 4),
            "anomaly_score": round(anomaly_score, 4),
            "is_anomaly": is_anomaly,
            "environment_type": environment_type,
            "dynamic_energy": round(dynamic_energy, 4),
            "latency_ms": round(latency_ms, 2),
            "is_synthetic": is_synthetic,
            "timestamp": time.time()
        }


# Singleton default inference engine
default_inference_engine = InferenceEngine()
