from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional

from ingestion.base import TelemetryLoader
from ingestion.normalizer import TelemetryNormalizer
from core.models import TelemetryPoint


class CSVTelemetryLoader(TelemetryLoader):
    """Load telemetry from a CSV file into normalised TelemetryPoints."""

    def __init__(self, speed_unit: Optional[str] = None):
        self._speed_unit = speed_unit
        self._normalizer = TelemetryNormalizer()

    def can_load(self, source: str) -> bool:
        return isinstance(source, str) and Path(source).suffix.lower() in (".csv", ".txt")

    def load(self, source: str) -> List[TelemetryPoint]:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Telemetry file not found: {source}")

        rows = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))

        if not rows:
            raise ValueError(f"No data found in {source}")

        return self._normalizer.normalize_batch(rows, self._speed_unit)
