# Unified CSI Data Model Specification

## Overview

The Unified CSI Data Model provides an immutable, standardized internal schema across diverse hardware capture sources (Intel 5300, Atheros AR9580, ESP32 CSI tool, Nexmon Broadcom, and Physics Simulation).

## Schema Definitions

### CSIMetadata
Contains contextual parameters and RF hardware capture characteristics:

```python
@dataclass
class CSIMetadata:
    source_format: str                    # "esp_fi", "csi_bench", "eighty_mhz", "wallhack", "synthetic", "generic_csv"
    carrier_freq_ghz: float = 5.0        # RF Carrier Frequency (2.4 GHz or 5.0 GHz)
    bandwidth_mhz: float = 40.0          # Channel Bandwidth (20.0, 40.0, 80.0, 160.0 MHz)
    num_subcarriers: int = 64            # Active subcarrier channels (e.g., 30, 52, 64, 114)
    num_rx: int = 3                      # Receiver antennas (N_rx)
    num_tx: int = 1                      # Transmitter antennas (N_tx)
    sampling_rate_hz: float = 100.0      # Packet capture rate (Hz)
    environment_id: str = "default_env"  # Associated physical room/zone
    environment_type: EnvironmentType = EnvironmentType.LIVING_ROOM
    activity: ActivityLabel = ActivityLabel.UNKNOWN
    subject_id: Optional[str] = None
    is_synthetic: bool = False           # Distinguishes simulated physics from hardware
```

### CSISample
Encapsulates multichannel raw and processed Wi-Fi Channel State Information matrices:

```python
@dataclass
class CSISample:
    sample_id: str
    metadata: CSIMetadata
    amplitude: np.ndarray      # Shape: (T, N_sub, N_rx, N_tx) - Float32 CSI Amplitude
    phase: np.ndarray          # Shape: (T, N_sub, N_rx, N_tx) - Float32 CSI Phase (radians)
    timestamps: np.ndarray     # Shape: (T,) - Relative timestamps in seconds (Float64)
```

### Supported Activities
- `empty` (Ambient room baseline / Presence: Absent)
- `walking`
- `sitting`
- `standing`
- `running`
- `lying`
- `waving`
- `falling` (Critical sudden impact event)
- `unknown`
