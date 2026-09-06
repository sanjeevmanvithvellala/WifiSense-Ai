"""Unit tests for ML and Anomaly Detection Models."""
import numpy as np
import pytest
from ml.synthetic_generator import SyntheticCSIGenerator
from ml.features.extractor import FeatureExtractor
from ml.models.random_forest import RandomForestCSIClassifier
from ml.models.svm import SVMCSIClassifier
from ml.models.isolation_forest import IsolationForestAnomalyDetector
from ml.models.registry import ModelRegistry


@pytest.fixture
def feature_data():
    gen = SyntheticCSIGenerator(random_seed=123)
    extractor = FeatureExtractor()

    samples = [
        gen.generate_sample(activity="Walking", duration_sec=0.5),
        gen.generate_sample(activity="Walking", duration_sec=0.5),
        gen.generate_sample(activity="Sitting", duration_sec=0.5),
        gen.generate_sample(activity="Sitting", duration_sec=0.5),
        gen.generate_sample(activity="Falling", duration_sec=0.5),
        gen.generate_sample(activity="Falling", duration_sec=0.5),
    ]
    X_list = []
    y_list = []
    for s in samples:
        window = s.amplitude[:20, :]
        feat = extractor.extract_window_features(window)
        X_list.append(feat)
        y_list.append(s.metadata.activity_label)

    return np.array(X_list, dtype=np.float32), np.array(y_list)


def test_random_forest_model(feature_data):
    X, y = feature_data
    rf = RandomForestCSIClassifier(model_id="rf_test", n_estimators=10, random_state=42)
    rf.train(X, y)
    assert rf.is_trained

    preds = rf.predict(X)
    assert len(preds) == len(y)

    probs = rf.predict_proba(X)
    assert probs.shape[0] == len(y)
    assert probs.shape[1] == len(np.unique(y))


def test_svm_model(feature_data):
    X, y = feature_data
    svm = SVMCSIClassifier(model_id="svm_test", kernel="linear", random_state=42)
    svm.train(X, y)
    assert svm.is_trained

    preds = svm.predict(X)
    assert len(preds) == len(y)


def test_isolation_forest(feature_data):
    X, _ = feature_data
    iso = IsolationForestAnomalyDetector(model_id="iso_test", n_estimators=10, random_state=42)
    iso.fit(X)
    assert iso.is_trained

    scores = iso.score_samples(X)
    assert len(scores) == len(X)
    assert (scores >= 0.0).all() and (scores <= 1.0).all()


def test_model_registry():
    registry = ModelRegistry()
    archs = registry.list_architectures()
    assert "Random Forest" in archs
    assert "SVM" in archs
    assert "1D CNN" in archs
    assert "CNN-GRU" in archs
    assert "Transformer" in archs

    anom_archs = registry.list_anomaly_architectures()
    assert "Isolation Forest" in anom_archs
    assert "Deep Autoencoder" in anom_archs
