from __future__ import annotations

import abc
from typing import List

from core.models import TelemetryPoint


class TelemetryLoader(abc.ABC):
    """Abstract base for all telemetry input sources."""

    @abc.abstractmethod
    def load(self, source: str) -> List[TelemetryPoint]:
        """Load telemetry from source and return normalised TelemetryPoints."""
        ...

    @abc.abstractmethod
    def can_load(self, source: str) -> bool:
        """Return True if this loader supports the given source."""
        ...
