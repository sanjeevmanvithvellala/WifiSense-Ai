# WiFiSense AI Architecture

## 1. System Overview

WiFiSense AI is a modular, high-throughput, privacy-preserving software platform for analyzing Wi-Fi Channel State Information (CSI) to perform ambient human activity intelligence and presence detection.

```
+-----------------------------------------------------------------------------------+
|                              Data Ingestion Layer                                 |
|  +----------------+  +----------------+  +----------------+  +-----------------+  |
|  |  ESP32 CSI     |  |  Intel 5300    |  |  Atheros CSI   |  | Synthetic Gen   |  |
|  |  (ESP-Fi)      |  |  (CSI-Bench)   |  |  (80MHz/160M)  |  | (Physics-based) |  |
|  +--------+-------+  +--------+-------+  +--------+-------+  +--------+--------+  |
+-----------|-------------------|-------------------|-------------------|-----------+
            +-------------------+-------------------+-------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                           Unified CSI Data Model Layer                            |
|             CSIMetadata + CSISample (Complex, Amplitude, Phase, Timestamps)       |
+---------------------------------------+-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                            Signal Preprocessing Pipeline                          |
|  - Hampel Outlier Filtering     - Butterworth Bandpass / Lowpass Filtering        |
|  - Phase Unwrapping & Sanitization  - Environment Baseline Calibration & Normaliz. |
|  - Sliding Window Segmentation (Configurable duration & overlap)                  |
+---------------------------------------+-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                         Feature Extraction & Selection                            |
|  - Time Domain (Mean, RMS, Variance, Kurtosis, Skewness, Crest Factor, Energy)    |
|  - Frequency Domain (Spectral Entropy, Dominant Frequencies, Spectral Centroid)   |
|  - CSI Domain (Subcarrier Correlation, Doppler Velocity Estimate, Spatial Div.)   |
+---------------------------------------+-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                        Machine Learning & Inference Layer                         |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  | Supervised HAR     |  | Anomaly Detection  |  | Environment Adaptation      |  |
|  | (RF, SVM, CNN1D,   |  | (Isolation Forest, |  | (CORAL Covariance Alignment,|  |
|  |  CNN-GRU, Xformer) |  |  Deep Autoencoder) |  |  Ambient Baseline Calib.)   |  |
|  +--------------------+  +--------------------+  +-----------------------------+  |
+---------------------------------------+-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                       FastAPI REST & WebSocket Server                             |
|  - REST: Environments, Datasets, Models, Experiments, Analytics, Settings         |
|  - WebSocket (/ws/replay): Real-time Subcarrier Streaming & Inference Broadcast   |
+---------------------------------------+-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                       React 18 + Vite + TailwindCSS UI                            |
|  - Real-time Subcarrier Heatmaps & Waveform Visualizers (Canvas/SVG)              |
|  - Activity Intelligence Dashboard, Anomaly Alerting & Experiment Studio          |
+-----------------------------------------------------------------------------------+
```

## 2. Component Directory Structure

```
wifisense-ai/
├── backend/
│   └── app/
│       ├── api/               # REST API route handlers
│       ├── core/              # Config, DB connection, logging
│       ├── models/            # SQLAlchemy database ORM entities
│       ├── schemas/           # Pydantic validation & serialization models
│       ├── services/          # Database seeding & background workers
│       ├── websocket/         # Streaming replay engine & connection manager
│       └── main.py            # Application lifespan entrypoint
├── ml/
│   ├── adapters/              # Dataset converters (ESP-Fi, CSI-Bench, Wallhack, etc.)
│   ├── environment/           # CORAL domain adaptation & baseline calibration
│   ├── experiments/           # Benchmark suites (cross-env, multi-env evaluation)
│   ├── features/              # Time, Frequency, and CSI spatial feature extractors
│   ├── inference/             # Unified real-time prediction pipeline
│   ├── models/                # RF, SVM, CNN1D, CNN-GRU, Transformer, AE, IF
│   ├── preprocessing/         # Filters, phase unwrappers, normalizers, windowing
│   ├── synthetic_generator.py # Physical Wi-Fi CSI multipath & Doppler simulation
│   └── unified_model.py       # Core CSISample and CSIMetadata data contract
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components (Waveform, Heatmap, Modal)
│   │   ├── pages/             # Dashboard, Live Analysis, Experiments, Models, etc.
│   │   ├── services/          # Axios HTTP REST client
│   │   ├── hooks/             # WebSocket stream subscriber hook
│   │   └── types/             # TypeScript data types matching backend schemas
│   └── package.json
├── docker/                    # Container orchestration definitions
└── tests/                     # Unit, integration, and regression test suite
```
