"""Storage backend interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class TelemetryRecord:
    """Structured telemetry payload ready for persistence."""

    timestamp: datetime
    agent_name: str
    operation: str
    model: str
    session_id: str
    user_id: str
    duration_ms: int
    total_tokens: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    success: bool
    prompt_hash: Optional[str]
    response_hash: Optional[str]
    metadata: Dict[str, Any]
    prompt_text: Optional[str] = None
    response_text: Optional[str] = None


class StorageBackend(ABC):
    """Abstract base class for telemetry storage backends."""

    @abstractmethod
    def record(self, record: TelemetryRecord) -> None:
        """Persist a telemetry record."""

