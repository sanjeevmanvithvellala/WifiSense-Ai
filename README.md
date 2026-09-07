<div align="center">

# 📡 WiFiSense AI

### **An Environment-Agnostic and Privacy-Preserving Human Activity Intelligence Platform Using Wi-Fi CSI**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React: 18](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite-61DAFB.svg)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38B2AC.svg)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20%7C%20Compose-2496ED.svg)](https://www.docker.com/)
[![Privacy: Camera--Free](https://img.shields.io/badge/Privacy-100%25%20Camera--Free-brightgreen.svg)](#privacy-first-principles)

</div>

---

## 🌟 Overview

**WiFiSense AI** is an enterprise-grade, end-to-end software platform that transforms standard commercial Wi-Fi Channel State Information (CSI) into rich, real-time human activity intelligence, occupancy presence, and sudden-fall anomaly detection.

By leveraging commodity RF multipath disturbances, WiFiSense AI operates **completely without optical cameras, lenses, microphones, or wearable biometric sensors**, enabling non-intrusive monitoring inside private spaces (elderly bedrooms, healthcare wards, bathrooms, secure corporate environments).

```
                      Raw Wi-Fi CSI Packets (2.4 / 5 GHz)
                                      │
                                      ▼
                        Unified CSI Data Model (Layer 1)
                       [CSIMetadata + Multichannel CSI]
                                      │
                                      ▼
                    Signal Preprocessing Pipeline (Layer 2)
              [Hampel Outlier Filter ➔ Butterworth Lowpass/Bandpass ➔
               Phase Sanitization ➔ Baseline Clutter Cancellation]
                                      │
                                      ▼
                   Feature Extraction & Selection (Layer 3)
           [Time Stats ➔ FFT Spectral Entropy ➔ Spatial CSI Covariance]
                                      │
                                      ▼
                    Adaptive Machine Learning Hub (Layer 4)
             ┌───────────────────────┬────────────────────────┐
             ▼                       ▼                        ▼
     Supervised HAR          Anomaly Detector        Domain Adaptation
  (RF, SVM, 1D-CNN,       (Isolation Forest,         (CORAL Covariance
   CNN-GRU, Xformer)       Deep Autoencoder)             Alignment)
             │                       │                        │
             └───────────────────────┼────────────────────────┘
                                     │
                                     ▼
                FastAPI High-Speed WebSocket & REST Core (Layer 5)
                                     │
                                     ▼
                  Interactive React 18 / Vite HUD (Layer 6)
          [Real-time Heatmaps ➔ Live Doppler Waveforms ➔ HUD Alerts]
```

---

## 🚀 Key Platform Capabilities

- **Unified CSI Data Specification**: Standardized immutable schema converting Intel 5300, Atheros AR9580, ESP32 CSI tool, WallHack, and custom capture formats into a single high-performance representation.
- **Physics-Based CSI Synthesizer**: Realistic simulation of multipath scattering, Doppler shifts, and frequency-selective fading for 8 canonical activities (*Walking, Sitting, Standing, Running, Lying, Waving, Falling, Absent*).
- **Environment Calibration & CORAL Domain Adaptation**: Overcomes the fundamental domain-shift obstacle in Wi-Fi sensing by computing differential static clutter cancellation and correlation alignment between source and target rooms.
- **Comprehensive ML Architecture Suite**:
  - **Classifiers**: Random Forest, SVM, 1D Convolutional Neural Networks, CNN-GRU temporal networks, and Multi-Head CSI Transformers.
  - **Anomaly Detectors**: Unsupervised Isolation Forests and Deep Autoencoder reconstruction scoring for rapid fall detection.
- **High-Throughput Replay & Live Telemetry**: Full-duplex WebSocket streaming feeding interactive subcarrier heatmaps, live Doppler spectrograms, and occupancy tracking at 50–100 FPS.
- **Privacy-by-Design**: 100% optical-free and audio-free; zero facial/biometric tracking.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite, Pydantic, WebSockets.
- **ML / Signal Processing**: PyTorch, Scikit-learn, SciPy, NumPy.
- **Frontend**: React 18, TypeScript, Vite, Lucide Icons, Recharts, TailwindCSS.
- **DevOps**: Docker, Docker Compose, Nginx.

---

## ⚡ Quickstart Guide

### Option 1: Local Development

#### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-org/wifisense-ai.git
cd wifisense-ai

# Install Python requirements
pip install -r requirements.txt

# Run initial database setup & seeder
python -m backend.app.services.seed

# Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Navigate to `http://localhost:5173` in your browser.

---

### Option 2: Docker Compose (Production Bundle)

```bash
docker compose up --build -d
```

- **Frontend Dashboard**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/api`
- **WebSocket Streaming**: `ws://localhost:8000/ws/replay`
- **Swagger Documentation**: `http://localhost:8000/docs`

---

## 📂 Project Structure

```
wifisense-ai/
├── backend/                  # FastAPI Application Core
│   ├── app/
│   │   ├── api/              # RESTful Endpoints
│   │   ├── core/             # Configuration & Database Connection
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── schemas/          # Pydantic Request/Response Schemas
│   │   ├── services/         # Seeders & Business Logic
│   │   ├── websocket/        # Streaming Manager & Real-time Replay
│   │   └── main.py           # Application Entrypoint & Lifespan
├── ml/                       # Signal Processing & ML Pipelines
│   ├── adapters/             # Hardware Formats (ESP-Fi, Intel 5300, Atheros, Wallhack)
│   ├── environment/          # CORAL Domain Adaptation & Baseline Calibration
│   ├── experiments/          # Cross-environment Benchmark Suites
│   ├── features/             # Time, Frequency, and CSI Spatial Feature Extraction
│   ├── inference/            # Unified Real-time Prediction Engine
│   ├── models/               # RF, SVM, CNN1D, CNN-GRU, Transformer, IF, AE
│   ├── preprocessing/        # Hampel, Butterworth, Phase Sanitization, Windows
│   ├── synthetic_generator.py# Doppler & Multipath Physics Simulation
│   └── unified_model.py      # Standardized CSISample & CSIMetadata Data Model
├── frontend/                 # React 18 + Vite Web Application
│   ├── src/
│   │   ├── components/       # Waveform Visualizer, Subcarrier Heatmap, Cards
│   │   ├── pages/            # Dashboard, Live Analysis, Experiments, Models
│   │   ├── services/         # Axios API Client
│   │   └── types/            # TypeScript Schema Definitions
├── docker/                   # Dockerfiles and Nginx Proxy Configuration
├── docs/                     # Comprehensive System Documentation
└── tests/                    # Unit & Integration Test Suites
```

---

## 🧪 Running Automated Tests

```bash
# Run complete test suite with coverage
python -m pytest tests/ -v
```

---

## 🔒 Privacy-First Principles

1. **Zero Camera Sensors**: Optical devices are absent by design.
2. **Zero Audio Recording**: Complete acoustic privacy.
3. **No Biometric Profiling**: Recognizes kinetic physical states (walking, sitting, falling) without identity reconstruction.
4. **Edge / On-Premises Native**: Inferences execute locally on commodity edge compute without external telemetry leakage.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
