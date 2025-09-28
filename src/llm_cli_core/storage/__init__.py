"""Storage backends."""

from .base import StorageBackend, TelemetryRecord
from .local import LocalStorage

__all__ = ["StorageBackend", "TelemetryRecord", "LocalStorage"]

