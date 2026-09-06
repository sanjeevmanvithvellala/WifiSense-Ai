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

---

## 🎤 Presentation Speech

<details>
<summary>Click here to view the video demo presentation speech</summary>

### Opening

Hello everyone.

Today, I am presenting our project **WiFiSense AI** — a privacy-preserving human activity sensing platform that uses **Wi-Fi signals and artificial intelligence to understand what is happening inside an environment without using cameras, microphones, or wearable devices.**

Let me start with a simple question.

**What if a Wi-Fi router could do more than just provide internet?**

What if the same Wi-Fi signals already present in our homes, hospitals, offices, and other environments could help us understand whether a person is walking, sitting, standing, or potentially experiencing an abnormal event?

That is the idea behind WiFiSense AI.

---

### 1. The Problem

Traditional human monitoring systems usually depend on either **cameras or wearable sensors**.

Cameras can provide detailed information, but they introduce significant privacy concerns. They are especially uncomfortable in places such as bedrooms, bathrooms, hospitals, and elderly-care environments.

Wearable devices solve some privacy problems, but they require the person to continuously wear and maintain the device. Batteries can run out, devices can be forgotten, and some users simply may not want to wear a sensor.

So we asked:

**Can we sense human activity without directly observing the person?**

This is where Wi-Fi sensing comes in.

---

### 2. The Core Technology — CSI

Our system uses something called **Channel State Information**, or **CSI**.

Whenever a Wi-Fi signal travels from a transmitter to a receiver, it interacts with the surrounding environment.

It can be reflected, scattered, or affected by objects and human movement.

Therefore, when a person moves inside a room, the Wi-Fi channel changes.

CSI provides a fine-grained representation of these channel changes across different Wi-Fi subcarriers.

So conceptually, our system works like this:

**Human movement → changes in Wi-Fi propagation → changes in CSI → signal processing → AI model → activity intelligence.**

Research has demonstrated that CSI can be used for device-free human activity recognition, while also highlighting the challenge of environmental variation.

And that is exactly the problem our platform is designed to address.

---

### 3. Our Solution

WiFiSense AI is not just a single machine-learning model.

It is an **end-to-end platform**.

The overall pipeline is:

**CSI data acquisition → preprocessing → signal representation → machine-learning or deep-learning model → activity/anomaly prediction → visualization and analysis.**

Our platform also includes **environment management, model training, experimentation, domain adaptation, and real-time signal visualization.**

Let me demonstrate the major components.

---

### 4. Live Analysis

First, I will open the **Live Analysis** section.

Here I can select an environment, for example, our **Living Room**, and select a CSI dataset for replay.

Now I click **Start Live Stream**.

As the stream starts, the system begins processing the incoming CSI data.

The first visualization is the **Subcarrier Amplitude Heatmap**.

Each column represents a Wi-Fi subcarrier, while the changing intensity represents variations in the received signal.

When human movement occurs, the signal pattern changes.

This gives us a visual representation of something that normally cannot be seen with the human eye — the disturbance of the wireless channel caused by activity.

Below that, we have the **Signal Waveform Visualizer**.

This shows the temporal variation of the signal across the active channels.

So instead of looking at a static dataset, we can actually observe the signal changing over time.

---

### 5. Real-Time Activity Recognition

Now we come to the intelligence layer.

The system takes the processed CSI information and feeds it into an activity-recognition model.

The platform can work with multiple model architectures, including:

* Random Forest
* SVM
* 1D CNN
* CNN-GRU
* Transformer

The model can then classify activities such as:

**Walking, sitting, standing, and other configured activities.**

The dashboard displays the current prediction together with its confidence score.

So we are moving from:

**Raw wireless signal**

to

**meaningful human activity information.**

And the important part is that we are not using a camera to observe the person.

---

### 6. Anomaly Detection

WiFiSense AI also contains an **anomaly detection layer**.

Instead of only asking:

*"What activity is happening?"*

we can also ask:

**"Is something unusual happening?"**

For example, a sudden and abnormal change in the CSI pattern can produce an elevated anomaly score.

This can be useful for scenarios such as elderly-care environments, assisted living, or safety monitoring.

The goal is not to identify the person's identity.

The goal is to understand the **state of the environment and the activity taking place inside it.**

---

### 7. The Biggest Challenge — Different Environments

Now we come to one of the most important parts of our project.

Suppose I train my model in this room.

The model learns the CSI patterns associated with walking, sitting, and standing.

Now I take exactly the same model and move it into another room.

For example:

**Living Room → Office**

The model may suddenly perform worse.

Why?

Because Wi-Fi signals don't travel through every environment in the same way.

Different rooms have different:

* walls
* furniture
* layouts
* reflective surfaces
* router positions
* multipath propagation characteristics

Therefore, the CSI distribution can change even when the human activity remains the same.

This is known as **domain shift** or **cross-environment variation**.

This is a recognized challenge in Wi-Fi-based human activity recognition, and domain adaptation has been investigated specifically to improve cross-scene recognition.

---

### 8. CORAL Domain Adaptation

This is where one of the key features of WiFiSense AI comes in.

Our platform provides a **Cross-Environment Adaptation Experiment**.

I navigate to the **Experiments** section and create a new experiment.

For example:

**Source Environment:** Residential Living Room

**Target Environment:** Modern Office

**Model:** Random Forest or 1D CNN

**Adaptation Method:** CORAL Domain Adaptation

First, we evaluate the model directly on the target environment.

We can observe the reduction in performance caused by the environmental difference.

Then we apply **CORAL**, which stands for **Correlation Alignment**.

The basic idea is to reduce the statistical difference between the source and target feature distributions.

In simple words:

**Instead of completely retraining the model for every new room, we try to make the learned representation more compatible with the new environment.**

The experiment then allows us to compare:

**Source Accuracy → Direct Cross-Domain Accuracy → Adapted Accuracy**

along with the **confusion matrix and per-class F1 scores**.

This makes the system more practical for deployment across different environments.

CORAL-based approaches have specifically been explored for addressing distribution differences between source and target environments in Wi-Fi activity recognition.

---

### 9. Model Training and Comparison

Next, I will open the **Models** section.

One of the advantages of our platform is that we are not restricted to a single model.

We can train and compare different approaches.

For traditional machine learning, we have:

**Random Forest and SVM.**

For deep learning:

**1D CNN, CNN-GRU, and Transformer.**

And for anomaly detection:

**Isolation Forest and Autoencoder.**

We can configure training parameters such as:

* number of epochs
* learning rate
* window size
* and other model-specific parameters.

After training, the platform provides evaluation information such as:

**validation accuracy, confusion matrix, F1 score, and model parameter count.**

This allows us to compare not only which model is accurate, but also how complex that model is.

---

### 10. Environment Calibration

The next component is **Environment Management**.

Before deploying a sensing system into a room, it is useful to understand what the wireless environment looks like under normal conditions.

So our platform provides **baseline calibration**.

For example, we can select a room and click **Calibrate Baseline**.

The system captures the static ambient CSI profile of that environment.

Later, when new CSI data arrives, the system can compare the current signal characteristics against the baseline.

Conceptually:

**Empty/normal environment → baseline CSI profile → new observations → detect deviations.**

This gives the system an environmental reference point.

---

### 11. Why This Is Useful

Now let's consider the real-world applications.

WiFiSense AI can potentially be applied to:

**Healthcare**

For example, monitoring activity patterns or detecting abnormal events without placing cameras inside sensitive spaces.

**Elderly Care**

The system could help detect unusual activity or potential falls.

**Smart Homes**

It could provide occupancy and activity awareness without requiring users to wear devices.

**Workplaces**

It could assist with occupancy monitoring and safety-related applications.

**Energy Management**

Occupancy information can potentially be used to make heating, cooling, lighting, or other building systems more responsive.

**Privacy-Preserving Monitoring**

And this is perhaps the biggest advantage.

The system focuses on the **wireless signal disturbance**, rather than visually recording the person.

---

### 12. Privacy

Privacy is a fundamental design consideration of WiFiSense AI.

There is no requirement for a camera to continuously record the environment.

There is no requirement for a person to wear a sensor.

The system is designed around wireless signal measurements and can be deployed in an edge or on-premises architecture depending on the implementation.

Most importantly, the objective is **activity understanding rather than visual identification.**

So instead of asking:

**"Who is this person?"**

the system is primarily asking:

**"What is happening in this environment?"**

That distinction makes WiFi sensing particularly interesting for privacy-sensitive applications.

---

### 13. Complete System Architecture

So, if I summarize the complete architecture:

We start with the **Wi-Fi CSI data**.

↓

We perform **signal processing and preprocessing**.

↓

The processed signal is converted into suitable windows/features for machine-learning models.

↓

The model performs **activity classification or anomaly detection**.

↓

If we are moving between environments, the **domain adaptation layer**, such as CORAL, helps address the distribution difference.

↓

The **FastAPI backend** manages the processing, experiments, model operations, and APIs.

↓

Finally, the **frontend dashboard** presents everything through interactive visualizations.

So the complete system connects:

**Wireless sensing + signal processing + machine learning + deep learning + domain adaptation + real-time visualization**

into one platform.

---

### 14. Final Impact

What makes WiFiSense AI different is that we are not simply demonstrating that Wi-Fi can recognize human movement.

We are trying to address the problems that appear when such a system moves toward real-world deployment.

We consider:

**Different environments.**

**Different models.**

**Real-time visualization.**

**Anomaly detection.**

**Environmental calibration.**

And most importantly:

**Privacy.**

The ultimate goal is to transform existing wireless infrastructure into an intelligent sensing layer without requiring people to constantly wear devices or be continuously recorded by cameras.

---

### Closing

So, to summarize:

**WiFiSense AI turns Wi-Fi signals into human activity intelligence.**

It captures changes in **Channel State Information**, processes those signals, applies machine learning and deep learning models, detects activities and anomalies, and uses **domain adaptation** to address changes between environments.

And the entire process can be visualized through a single interactive platform.

The vision is simple:

> **No cameras.**
>
> **No wearables.**
>
> **No intrusive monitoring.**
>
> **Just Wi-Fi — reimagined as an intelligent sensing system.**

Thank you.

</details>

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
