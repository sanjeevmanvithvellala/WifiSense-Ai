"""
Dataset Adapter Registry and Factory.
Enables dynamic discovery, inspection, and instantiation of dataset adapters.
"""

from typing import Dict, List, Type, Optional, Any
from ml.adapters.base import CSIAdapter, CSIInputSource, DatasetSource, FileSource
from ml.adapters.synthetic_adapter import SyntheticDemoAdapter
from ml.adapters.esp_fi_adapter import ESPFiAdapter
from ml.adapters.csi_bench_adapter import CSIBenchAdapter
from ml.adapters.eighty_mhz_adapter import EightyMHzAdapter
from ml.adapters.wallhack_adapter import WallhackAdapter
from ml.adapters.generic_csv_adapter import GenericCSVAdapter


class AdapterRegistry:
    """Registry maintaining available CSI adapters."""

    def __init__(self):
        self._adapters: Dict[str, CSIAdapter] = {}
        # Register built-in adapters
        self.register(SyntheticDemoAdapter())
        self.register(ESPFiAdapter())
        self.register(CSIBenchAdapter())
        self.register(EightyMHzAdapter())
        self.register(WallhackAdapter())
        self.register(GenericCSVAdapter())

    def register(self, adapter: CSIAdapter):
        """Registers an adapter instance."""
        self._adapters[adapter.adapter_id] = adapter

    def get_adapter(self, adapter_id: str) -> Optional[CSIAdapter]:
        """Retrieves adapter by ID."""
        return self._adapters.get(adapter_id)

    def list_adapters(self) -> List[Dict[str, Any]]:
        """Lists metadata for all registered adapters."""
        res = []
        for a_id, adapter in self._adapters.items():
            res.append({
                "adapter_id": a_id,
                "dataset_name": adapter.dataset_name,
                "is_synthetic": adapter.is_synthetic,
            })
        return res

    def detect_adapter(self, source_path_or_metadata: Any) -> CSIAdapter:
        """Auto-detects the best matching adapter for a given input."""
        for adapter in self._adapters.values():
            if adapter.can_handle(source_path_or_metadata):
                return adapter
        # Fallback to generic CSV adapter
        return self._adapters["generic_csv"]


# Singleton registry instance
default_adapter_registry = AdapterRegistry()
