# Datasets & Format Adapters

WiFiSense AI incorporates native dataset adapters allowing ingestion, standardization, and evaluation across leading academic CSI benchmarks and hardware formats.

## Supported Dataset Formats

| Format Identifier | Source Description | Hardware Architecture | Typical Subcarriers |
| :--- | :--- | :--- | :--- |
| `synthetic` | Physics-based Doppler/Multipath Generator | Simulated 2.4/5GHz | 30 / 64 / 114 |
| `esp_fi` | ESP32 CSI Tool Format (CSV/Binary) | Espressif ESP32 802.11n | 64 / 128 |
| `csi_bench` | Intel 5300 NIC CSI Benchmark Format | Intel 5300 802.11n | 30 |
| `eighty_mhz` | Atheros 802.11ac 80MHz Dataset (Widar/SignFi) | Qualcomm Atheros AR9580 | 114 / 242 |
| `wallhack` | WallHack Through-Wall RF Dataset | Multi-antenna transceiver | 52 / 64 |
| `generic_csv` | Standard Matrix Amplitude/Phase CSV | Generic Raw Capture | Configurable |

## Adapter Architecture

All adapters inherit from `BaseCSIAdapter` and implement:
1. `validate_format(source)`: Non-destructive header and schema verification.
2. `get_dataset_metadata(source)`: Extract channel configuration, frequency, and sample counts.
3. `load_dataset(source, max_samples)`: Convert raw capture structures into `List[CSISample]`.
4. `stream_samples(source)`: Memory-efficient Python generator for real-time live replay.

### Adding a Custom Adapter

```python
from ml.adapters.base import BaseCSIAdapter, CSIInputSource
from ml.adapters.registry import register_adapter
from ml.unified_model import CSISample

@register_adapter("my_hardware_format")
class MyCustomHardwareAdapter(BaseCSIAdapter):
    @property
    def format_name(self) -> str:
        return "my_hardware_format"

    def validate_format(self, source: Optional[CSIInputSource] = None) -> bool:
        # Validate file header or data structure
        return True

    def load_dataset(self, source: Optional[CSIInputSource] = None, max_samples: Optional[int] = None) -> List[CSISample]:
        # Return standard CSISample instances
        ...
```
