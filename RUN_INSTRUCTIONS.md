# 🚀 How to Run WiFiSense AI

This guide provides step-by-step instructions for running **WiFiSense AI** locally using the newly created Python virtual environment (`venv`) and the React 18 / Vite frontend dashboard.

---

## 📋 System Prerequisites

1. **Python**: 3.10+ (Python 3.11 recommended) — *Pre-configured in `venv`*
2. **Node.js**: 18+ and `npm` (for frontend UI)
3. **PowerShell / Terminal**: Any standard shell

---

## ⚡ Option 1: One-Click Launch (Recommended for Windows)

Simply double-click:
- **`start_dev.bat`** (or run `.\start_dev.ps1` in PowerShell)

This automatically activates the `venv`, seeds the database if needed, and launches both the backend API server (`http://localhost:8000`) and Vite frontend (`http://localhost:5173`) in dedicated windows.

---

## 🛠️ Option 2: Step-by-Step Manual Launch

### **Step 1: Activate the Python Virtual Environment**

Open your terminal in the project root directory (`C:\Users\sanje\Desktop\Wifi Sense`):

#### On Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*

#### On Windows (Command Prompt `cmd`):
```cmd
venv\Scripts\activate.bat
```

#### On Linux / macOS:
```bash
source venv/bin/activate
```

---

### **Step 2: Initialize Database & Seed Models (One-Time)**

Run the database seeder to populate default environments (Office, Living Room, Classroom), generate baseline synthetic demo datasets, and pre-train demo classifiers:

```powershell
python -m backend.app.services.seed
```

---

### **Step 3: Start the Backend REST & WebSocket Server**

Launch the FastAPI application on port `8000`:

```powershell
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **API Base URL**: `http://localhost:8000/api`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **WebSocket Replay Endpoint**: `ws://localhost:8000/ws/replay`

---

### **Step 4: Start the Frontend UI Server**

Open a **second terminal window**, navigate to the `frontend` directory, and start the Vite dev server:

```powershell
cd frontend
npm run dev
```

The web dashboard will be available at:
👉 **`http://localhost:5173`**

---

## 🧪 Step 5: Running Automated Tests

To run the complete test suite using the virtual environment:

```powershell
# Activate venv if not already active
.\venv\Scripts\Activate.ps1

# Run unit and integration tests
python -m pytest tests/ -v
```

---

## 🐳 Option 2: Run via Docker Compose (Containerized)

If you prefer running everything in isolated Docker containers:

```powershell
# Build and launch backend & frontend in background
docker compose up --build -d

# Check status
docker compose ps

# View live logs
docker compose logs -f
```

- **Frontend HUD**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/api`
- **Swagger Documentation**: `http://localhost:8000/docs`

To stop containers:
```powershell
docker compose down
```

---

## 🕹️ Interactive Feature Walkthrough in UI

Once you open `http://localhost:5173`:

1. **Live Analysis & Telemetry Replay (`/live`)**:
   - Select an environment (*e.g., Living Room*) and dataset (*e.g., Living Room Activity Dataset*).
   - Click **Start Live Stream**.
   - Watch the live **Subcarrier Amplitude Heatmap**, **Doppler Waveform Visualizer**, real-time **Human Activity Recognition badge**, and **Anomaly Detection score**.

2. **Cross-Environment Experiment Studio (`/experiments`)**:
   - Click **Run New Experiment**.
   - Pick a Source Environment (*e.g., Residential*) and Target Environment (*e.g., Office*).
   - Select an architecture (*e.g., Random Forest or 1D CNN*) and adaptation method (*e.g., CORAL Domain Adaptation*).
   - Click **Execute Experiment** to view dynamically computed accuracy recovery and confusion matrices.

3. **Model Training & Comparison (`/models`)**:
   - Train new models (Random Forest, SVM, 1D CNN, CNN-GRU, Transformer, Isolation Forest, Autoencoder).
   - Inspect accuracy, F1-scores, inference latency, and parameter counts.

4. **Environment Calibration (`/environments`)**:
   - Calibrate static ambient multipath baselines for physical rooms.

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell, then re-run `.\venv\Scripts\Activate.ps1`. |
| Port 8000 already in use | Change port in command: `uvicorn backend.app.main:app --port 8001 --reload` |
| Port 5173 already in use | Vite will automatically suggest port 5174. |
| Node modules missing | Run `cd frontend && npm install` |
