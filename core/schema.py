from __future__ import annotations

import math
from typing import Dict, Tuple

EARTH_RADIUS_M = 6_371_000.0

# Maps common CSV column name variants to canonical internal names.
FIELD_ALIASES: Dict[str, str] = {
    "ts": "timestamp",
    "time": "timestamp",
    "time_s": "timestamp",
    "t": "timestamp",
    "pos_x": "x",
    "pos_y": "y",
    "v": "speed",
    "vel": "speed",
    "velocity": "speed",
    "speed_ms": "speed",
    "accel": "acceleration",
    "acc": "acceleration",
    "accel_mss": "acceleration",
    "ax": "acceleration",
    "thr": "throttle",
    "throttle_pct": "throttle",
    "throttle_pos": "throttle",
    "gas": "throttle",
    "brk": "brake",
    "brake_pct": "brake",
    "brake_pos": "brake",
    "steer": "steering_angle",
    "steering": "steering_angle",
    "latitude": "lat",
    "longitude": "lon",
}

# Speed column names that carry unit information.
SPEED_COLUMN_UNITS: Dict[str, str] = {
    "speed_kmh": "kmh",
    "speed_mph": "mph",
    "speed_ms": "ms",
    "speed": "ms",  # assumed m/s unless overridden
}


def gps_to_xy(
    lat: float,
    lon: float,
    lat_ref: float,
    lon_ref: float,
) -> Tuple[float, float]:
    """Equirectangular projection: returns (x, y) in metres relative to reference."""
    lat_ref_rad = math.radians(lat_ref)
    x = EARTH_RADIUS_M * math.radians(lon - lon_ref) * math.cos(lat_ref_rad)
    y = EARTH_RADIUS_M * math.radians(lat - lat_ref)
    return x, y


def normalize_speed(value: float, unit: str) -> float:
    """Convert speed to m/s. unit in {'kmh', 'mph', 'ms'}."""
    if unit == "kmh":
        return value / 3.6
    if unit == "mph":
        return value * 0.44704
    return value  # already m/s


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
