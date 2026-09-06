# Environment Adaptation & Calibration

## The Cross-Environment Generalization Challenge

Wi-Fi CSI reflects the unique multipath reflections of physical surroundings (walls, furniture, room dimensions, router positioning). A model trained in Room A frequently experiences severe performance degradation (domain shift) when evaluated in Room B.

## Adaptation Strategies in WiFiSense AI

### 1. Ambient Baseline Calibration (`AmbientBaselineCalibrator`)
- Captures static CSI when the target room is vacant.
- Calculates per-subcarrier static amplitude vectors $\mathbf{\mu}_{\text{ambient}}$ and variance matrices $\mathbf{\sigma}^2_{\text{ambient}}$.
- Applies differential ambient cancellation:
  $$\mathbf{H}_{\text{calibrated}}(t) = \frac{\mathbf{H}(t) - \mathbf{\mu}_{\text{ambient}}}{\mathbf{\sigma}_{\text{ambient}} + \epsilon}$$
- Eliminates static multipath clutter, isolating dynamic reflections caused exclusively by human movement.

### 2. CORAL (Correlation Alignment) Domain Adaptation (`CORALDomainAdapter`)
- Minimizes distance between source domain covariance $C_S$ and target domain covariance $C_T$:
  $$\min_{\mathbf{A}} \| \mathbf{A}^\top C_S \mathbf{A} - C_T \|_F^2$$
- Computes whitening and recoloring transformation:
  $$\mathbf{X}_{\text{adapted}} = \mathbf{X}_S C_S^{-1/2} C_T^{1/2}$$
- Allows activity recognition models trained on Room A datasets to generalize accurately to Room B without requiring labeled activity samples in Room B.

## Cross-Environment Benchmarks

The Experiment Engine (`ml/experiments/engine.py`) provides automated benchmarking to evaluate:
- **Same-Environment Benchmark**: Train and test on Room A.
- **Direct Cross-Environment Benchmark**: Train on Room A, evaluate on Room B (measures domain drop).
- **Adaptation Benchmark**: Train on Room A with CORAL/Baseline adaptation applied, evaluate on Room B (measures accuracy recovery).
- **Multi-Environment Combined Benchmark**: Train across diverse environments for domain-invariant feature learning.
