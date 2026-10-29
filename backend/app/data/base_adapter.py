"""
Canonical internal data representations and abstract adapter interface.
Ensures uniform ingestion across Tobii Pro hardware recordings, webcam streams, and synthetic fixtures.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..schemas.canonical import TrialData, GazeSample, DatasetAuditReport


class BaseDatasetAdapter(ABC):
    """Abstract base class for all eye-tracking dataset adapters."""

    @abstractmethod
    def audit_dataset(self, data_directory: str) -> DatasetAuditReport:
        """Inspects directory, validates schemas, checks for corruption and returns an audit report."""
        pass

    @abstractmethod
    def load_participant_trials(self, data_directory: str, participant_id: str) -> List[TrialData]:
        """Loads all trials for a single participant into canonical TrialData format."""
        pass

    @abstractmethod
    def list_available_participants(self, data_directory: str) -> List[str]:
        """Returns list of all available participant identifiers."""
        pass
