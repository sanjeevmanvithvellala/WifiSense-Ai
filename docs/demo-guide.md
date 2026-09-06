# Complete Demo & Verification Guide

This guide walks through all capabilities of WiFiSense AI from data ingestion to live subcarrier streaming and domain adaptation benchmarking.

## 1. Quick Launch

```bash
# Terminal 1 - Launch Backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Launch Frontend
cd frontend
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 2. Walkthrough Features

### Step 1: Real-time Live Analysis & Replay
1. Navigate to **Live Analysis** (`/live`).
2. Select an active environment (e.g., *Living Room*) and a dataset replay (e.g., *Living Room Activity Dataset*).
3. Click **Start Live Stream**.
4. Observe the high-speed live visualization:
   - **Subcarrier Amplitude Heatmap**: Dynamic frequency-selective disturbance across all active subcarrier indices.
   - **Signal Waveform Visualizer**: Multichannel time-series variations.
   - **Instantaneous Activity Classification**: Real-time HAR prediction badge with confidence meter.
   - **Anomaly Score & Presence Status**: Automatic detection of falls and room occupancy.

### Step 2: Cross-Environment Adaptation Experiment
1. Navigate to **Experiments** (`/experiments`).
2. Click **Run New Experiment**.
3. Select:
   - **Source Environment / Dataset**: Residential Living Room.
   - **Target Environment / Dataset**: Modern Office Space.
   - **Model Architecture**: Random Forest or 1D CNN.
   - **Adaptation Method**: CORAL Domain Adaptation.
4. Click **Execute Experiment**.
5. Inspect the dynamic results:
   - Baseline Source Accuracy
   - Direct Cross-Domain Accuracy (drop due to multipath shift)
   - Adapted Accuracy (recovered domain generalization)
   - Confusion Matrix and Per-Class F1 comparison.

### Step 3: Train New Models & Compare Architectures
1. Navigate to **Models** (`/models`).
2. Click **Train New Model**.
3. Select an architecture: Random Forest, SVM, 1D CNN, CNN-GRU, Transformer, Isolation Forest, or Autoencoder.
4. Configure training hyperparameters (epochs, learning rate, window size).
5. Review the resulting validation accuracy, confusion matrix, and parameter count.

### Step 4: Manage Environments & Baseline Calibration
1. Navigate to **Environments** (`/environments`).
2. View existing physical zones and router configurations.
3. Click **Calibrate Baseline** on any environment to capture the static ambient CSI baseline profile.
