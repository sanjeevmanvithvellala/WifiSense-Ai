"""
Base interfaces and classes for CSI Data Sources and Adapters.
Follows pluggable adapter pattern to ingest various public/private datasets into Unified CSI representation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator
import os
import numpy as np
from ml.unified_model import CSISample, CSIMetadata


class CSIInputSource(ABC):
    """Abstract base class for any source of Wi-Fi CSI data."""

    @abstractmethod
    def get_source_type(self) -> str:
        """Returns the source identifier (e.g. 'dataset', 'file', 'replay')."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks whether the underlying source data exists and is readable."""
        pass


class DatasetSource(CSIInputSource):
    """Source referencing an entire dataset directory on disk or in memory."""

    def __init__(self, dataset_id: str, root_path: Optional[str] = None):
        self.dataset_id = dataset_id
        self.root_path = root_path

    def get_source_type(self) -> str:
        return "dataset"

    def is_available(self) -> bool:
        if self.root_path is None:
            return False
        return os.path.exists(self.root_path) and os.path.isdir(self.root_path)


class FileSource(CSIInputSource):
    """Source referencing a single uploaded or local CSI data file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_source_type(self) -> str:
        return "file"

    def is_available(self) -> bool:
        return os.path.exists(self.file_path) and os.path.isfile(self.file_path)


class ReplaySource(CSIInputSource):
    """Source streaming or iterating recorded CSI frames for replay simulation."""

    def __init__(self, samples: List[CSISample], loop: bool = True):
        self.samples = samples
        self.loop = loop
        self._current_index = 0

    def get_source_type(self) -> str:
        return "replay"

    def is_available(self) -> bool:
        return len(self.samples) > 0

    def next_sample(self) -> Optional[CSISample]:
        if not self.samples:
            return None
        sample = self.samples[self._current_index]
        self._current_index += 1
        if self._current_index >= len(self.samples):
            if self.loop:
                self._current_index = 0
            else:
                self._current_index = len(self.samples) - 1
        return sample

    def reset(self):
        self._current_index = 0


class CSIAdapter(ABC):
    """
    Abstract adapter for parsing dataset-specific formats into standardized CSISample objects.
    """

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Unique ID for the adapter, e.g., 'esp_fi', 'csi_bench'."""
        pass

    @property
    @abstractmethod
    def dataset_name(self) -> str:
        """Human-readable name of the target dataset."""
        pass

    @property
    @abstractmethod
    def is_synthetic(self) -> bool:
        """Explicit flag indicating if data produced by this adapter is synthetic."""
        pass

    @abstractmethod
    def can_handle(self, source_path_or_metadata: Any) -> bool:
        """Inspects file/directory signatures to check if this adapter can parse the dataset."""
        pass

    @abstractmethod
    def get_dataset_metadata(self, source: Optional[CSIInputSource] = None) -> Dict[str, Any]:
        """Extracts summary statistics, activities, environments, sampling rate without loading everything."""
        pass

    @abstractmethod
    def load_samples(
        self,
        source: CSIInputSource,
        max_samples: Optional[int] = None,
        environment_filter: Optional[str] = None,
        activity_filter: Optional[str] = None
    ) -> List[CSISample]:
        """Loads and converts source data into a list of unified CSISample instances."""
        pass
