"""Integration tests for Backend REST API Endpoints."""
import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import Base, engine


@pytest.fixture(scope="module")
def client():
    # Initialize DB tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data


def test_environments_endpoints(client):
    # List environments
    response = client.get("/api/environments")
    assert response.status_code == 200
    envs = response.json()
    assert isinstance(envs, list)

    # Create new unique environment
    unique_id = f"env_test_{uuid.uuid4().hex[:8]}"
    payload = {
        "id": unique_id,
        "name": f"Test Lab {unique_id}",
        "type": "Office",
        "description": "Integration test environment",
        "multipath_scale": 1.0,
        "noise_floor": 0.05,
        "is_calibrated": False,
        "calibration_data": {},
    }
    create_resp = client.post("/api/environments", json=payload)
    assert create_resp.status_code == 201
    created_env = create_resp.json()
    assert created_env["id"] == unique_id
    env_id = created_env["id"]

    # Get single environment
    get_resp = client.get(f"/api/environments/{env_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == env_id


def test_datasets_endpoints(client):
    # List datasets
    response = client.get("/api/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert isinstance(datasets, list)

    # Create unique synthetic dataset
    unique_ds_id = f"dataset_test_{uuid.uuid4().hex[:8]}"
    payload = {
        "id": unique_ds_id,
        "name": f"Test Dataset {unique_ds_id}",
        "adapter_id": "synthetic_demo",
        "is_synthetic": True,
        "activities": ["Walking", "Sitting"],
        "environments": ["Office"],
        "subjects": ["subject_01"],
        "sampling_rate": 50.0,
        "subcarriers": 64,
        "antennas": 1,
        "bandwidth": 20.0,
        "csi_representation": "amplitude",
        "status": "Ready",
        "license": "Open",
        "description": "Dataset generated during automated test",
    }
    create_resp = client.post("/api/datasets", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id"] == unique_ds_id
    assert created["adapter_id"] == "synthetic_demo"
    assert created["is_synthetic"] is True


def test_models_endpoints(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    models = response.json()
    assert isinstance(models, list)


def test_experiments_endpoints(client):
    response = client.get("/api/experiments")
    assert response.status_code == 200
    exps = response.json()
    assert isinstance(exps, list)


def test_analytics_endpoints(client):
    summary_resp = client.get("/api/analytics/summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert "metrics_summary" in summary
    assert "activity_distribution" in summary
    assert "environment_distribution" in summary


def test_settings_endpoints(client):
    settings_resp = client.get("/api/settings")
    assert settings_resp.status_code == 200
    settings = settings_resp.json()
    assert isinstance(settings, dict)
    assert len(settings) > 0
