# Privacy & Ethical Principles

WiFiSense AI is built around a **Privacy-First Architecture** for human activity recognition and ambient intelligence.

## Privacy Guarantees

1. **Zero Optical/Video Capture**: No camera sensors, lenses, or optical recording hardware exist anywhere in the pipeline.
2. **Zero Audio/Voice Recording**: No microphones, acoustic transducers, or ambient sound ingestion.
3. **No Biometric Facial or Identity Profiling**: Wi-Fi CSI data is strictly interpreted as kinetic wave disturbance patterns; the system cannot extract facial features, biometric identities, or optical signatures.
4. **Physical Occlusion & Wall Penetration Without Visual Exposure**: Enables elderly care fall detection and security occupancy sensing inside bathrooms, bedrooms, and private quarters where cameras are strictly invasive or prohibited.
5. **Edge & On-Premise Execution**: All preprocessing, feature extraction, and ML inferences run completely on-device or within local premises without streaming raw RF signal traces to external third-party cloud endpoints.

## Responsible AI & Scientific Integrity

- **Simulated vs Hardware Data Transparency**: All simulated datasets are permanently tagged with `is_synthetic = True` and labeled `Synthetic Demo Data` in the UI to prevent confounding with physical empirical datasets.
- **Reproducible Experimentation**: Cross-environment experiment benchmarks report non-cherry-picked macro F1, precision, recall, and confusion matrices computed dynamically on test splits.
