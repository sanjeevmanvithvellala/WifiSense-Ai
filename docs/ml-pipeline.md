# Signal Processing & ML Pipeline

## 1. Signal Preprocessing Pipeline

Raw Wi-Fi Channel State Information carries environmental noise, high-frequency transients, carrier frequency offsets (CFO), and packet-to-packet phase drifts. The WiFiSense AI preprocessing pipeline transforms raw complex CSI matrices through the following stages:

```
Raw CSI Amplitude & Phase (T x Subcarriers x Rx x Tx)
  │
  ├─► Hampel Filter (Temporal outlier removal per subcarrier)
  │
  ├─► Butterworth Filter (Lowpass / Bandpass filtering for human Doppler bands: 0.1 - 25 Hz)
  │
  ├─► Phase Processing (Unwrapping across subcarriers & linear phase detrending/sanitization)
  │
  ├─► Ambient Baseline Calibration (Differential ambient cancellation)
  │
  ├─► Normalization (Z-score or Min-Max per window)
  │
  └─► Sliding Window Segmentation (e.g., 2.0s window with 50% stride)
```

## 2. Feature Extraction Engine

The platform extracts multi-domain statistical, spectral, and spatial representations:

- **Time Domain**: Mean, standard deviation, RMS, variance, kurtosis, skewness, crest factor, peak-to-peak amplitude, energy, zero-crossing rate.
- **Frequency Domain**: Fast Fourier Transform (FFT) dominant frequencies, spectral energy distribution, spectral entropy, spectral centroid, spectral rolloff.
- **CSI & Spatial Domain**: Inter-subcarrier Pearson correlation, Doppler velocity spectrum estimates, inter-antenna phase differences (spatial diversity).

## 3. Machine Learning Models

### Classification Models
1. **Random Forest Classifier**: High interpretability, robust against noise, fast inference (<1.5ms).
2. **Support Vector Machine (SVM)**: Effective in high-dimensional feature spaces with linear or RBF kernels.
3. **1D Convolutional Neural Network (CNN-1D)**: Temporal subcarrier pattern extraction directly from sliding windows.
4. **CNN-GRU Hybrid Network**: Spatial convolutional features fed into Gated Recurrent Units for temporal gait and transition tracking.
5. **CSI Temporal Transformer**: Multi-head self-attention network capturing long-range dependencies across subcarrier sequences.

### Anomaly Detection Models
1. **Isolation Forest**: Unsupervised tree-based anomaly scoring for rapid fall and unexpected motion detection.
2. **Deep CSI Autoencoder**: Reconstruction error scoring based on an encoder-decoder network trained exclusively on ambient/normal daily activities.
