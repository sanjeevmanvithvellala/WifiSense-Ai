# WiFiSense AI REST & WebSocket API Reference

The WiFiSense AI Backend runs on FastAPI and exposes RESTful endpoints and high-speed bidirectional WebSocket streaming.

Base URL: `http://localhost:8000/api`
WebSocket URL: `ws://localhost:8000/ws/replay`
Interactive OpenAPI Docs: `http://localhost:8000/docs`

---

## 1. Health Endpoint

### `GET /api/health`
Returns backend service health, ML engine version, and database connectivity.

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## 2. Environments API

- `GET /api/environments`: List all registered physical environments.
- `POST /api/environments`: Create a new environment configuration.
- `GET /api/environments/{id}`: Retrieve environment metadata.
- `PUT /api/environments/{id}`: Update environment properties.
- `DELETE /api/environments/{id}`: Delete an environment.
- `POST /api/environments/{id}/calibrate`: Trigger ambient baseline calibration for an environment.

---

## 3. Datasets API

- `GET /api/datasets`: List all uploaded and synthetic datasets.
- `POST /api/datasets`: Register or generate a new dataset.
- `GET /api/datasets/{id}`: Retrieve dataset metadata and summary statistics.
- `DELETE /api/datasets/{id}`: Delete a dataset.

---

## 4. Models API

- `GET /api/models`: List all trained and benchmarked models.
- `POST /api/models/train`: Initiate asynchronous model training on a selected dataset.
- `GET /api/models/{id}`: Get model evaluation metrics, architecture parameters, and feature importance.
- `POST /api/models/predict`: Run single or batch CSI sample inference.

---

## 5. Experiments API

- `GET /api/experiments`: List all historical experiment runs and benchmarks.
- `POST /api/experiments/run`: Execute a cross-environment or adaptation experiment benchmark.
- `GET /api/experiments/{id}`: Fetch detailed experiment metrics, confusion matrices, and domain adaptation comparisons.

---

## 6. Live Replay & WebSocket Stream

### `POST /api/replay/start`
Starts a background streaming replay of a CSI dataset through the real-time inference engine.

**Request Body:**
```json
{
  "dataset_id": "dataset_living_room_synthetic",
  "playback_speed": 1.0,
  "loop": true,
  "model_id": "model_rf_01"
}
```

### `POST /api/replay/stop`
Stops active dataset replay streaming.

### `WebSocket /ws/replay`
Streams real-time subcarrier amplitude arrays, timestamps, instantaneous activity classifications, confidence scores, and anomaly warnings to connected frontend clients at the dataset's native sampling rate.

**Telemetry Packet Payload:**
```json
{
  "timestamp": 12.45,
  "activity": "walking",
  "confidence": 0.942,
  "presence": true,
  "anomaly_score": 0.04,
  "is_anomaly": false,
  "subcarrier_amplitudes": [14.2, 15.1, 13.8, ...],
  "fps": 100.0
}
```
