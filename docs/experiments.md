# Experiment Engine & Scientific Evaluation

## 1. Automated Benchmark Evaluation

WiFiSense AI includes a scientific evaluation engine that dynamically computes performance metrics on test splits:

- **Accuracy**: Overall classification accuracy across all activity classes.
- **Macro F1-Score**: Unweighted mean of per-class F1-scores, penalizing models that perform poorly on minority classes like falls.
- **Weighted F1-Score**: Class-balanced F1 metric weighted by class frequency.
- **Per-Class Precision & Recall**: Detailed breakdown for each human activity.
- **Confusion Matrix**: Full N x N matrix visualizing inter-class confusions (e.g., distinguishing Sitting vs. Standing vs. Lying).
- **Latency & Resource Profile**: Inference latency (ms per window), memory consumption, and parameter count.

## 2. Experiment Types

### 1. Same-Environment Benchmark
Trains and evaluates models within the same physical environment using stratified train/test splits. Establishes the performance upper bound in stationary surroundings.

### 2. Cross-Environment Generalization Benchmark
Trains on Environment A (e.g., Residential) and tests on unseen Environment B (e.g., Office) without fine-tuning. Measures cross-domain performance decay caused by multipath variations.

### 3. Domain-Adapted Evaluation (CORAL + Ambient Calibration)
Applies covariance alignment (CORAL) and ambient subtraction to bridge domain gaps between environments, demonstrating quantitative metric recovery.

### 4. Multi-Environment Composite Benchmark
Trains on pooled data from multiple environments to evaluate generalized, environment-invariant representations.
