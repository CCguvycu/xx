from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any

from core.models import TelemetryPoint
from core.schema import (
    FIELD_ALIASES,
    SPEED_COLUMN_UNITS,
    clamp,
    gps_to_xy,
    normalize_speed,
)


class TelemetryNormalizer:
    """
    Converts raw CSV rows (list of dicts) into TelemetryPoints.

    Handles:
    - Case-insensitive column name aliasing
    - GPS lat/lon → local XY via equirectangular projection (centroid reference)
    - Speed unit detection from column name or value range
    - Throttle/brake normalisation from percent to fraction
    """

    def normalize_batch(
        self,
        rows: List[Dict[str, str]],
        speed_unit: Optional[str] = None,
    ) -> List[TelemetryPoint]:
        if not rows:
            raise ValueError("Cannot normalise an empty telemetry batch.")

        # Build lowercase key mapping once.
        lower_rows = [{k.lower().strip(): v for k, v in r.items()} for r in rows]

        has_gps, has_xy = self._detect_coordinate_type(lower_rows[0])
        if not has_gps and not has_xy:
            raise ValueError(
                "Telemetry rows must contain either (lat/lon) or (x/y) columns."
            )

        lat_ref = lon_ref = None
        if has_gps:
            lat_ref, lon_ref = self._compute_gps_centroid(lower_rows)

        unit = speed_unit or self._detect_speed_unit(lower_rows[0])

        return [
            self._normalise_row(r, unit, has_gps, lat_ref, lon_ref)
            for r in lower_rows
        ]

    # ── coordinate detection ──────────────────────────────────────────────────

    def _detect_coordinate_type(
        self, row: Dict[str, str]
    ) -> Tuple[bool, bool]:
        resolved = self._resolve_aliases(row)
        has_gps = "lat" in resolved and "lon" in resolved
        has_xy = "x" in resolved and "y" in resolved
        return has_gps, has_xy

    def _compute_gps_centroid(
        self, rows: List[Dict[str, str]]
    ) -> Tuple[float, float]:
        lats, lons = [], []
        for r in rows:
            resolved = self._resolve_aliases(r)
            lat_str = resolved.get("lat")
            lon_str = resolved.get("lon")
            if lat_str and lon_str:
                lats.append(float(lat_str))
                lons.append(float(lon_str))
        if not lats:
            raise ValueError("No valid GPS coordinates found in batch.")
        return sum(lats) / len(lats), sum(lons) / len(lons)

    # ── speed unit detection ──────────────────────────────────────────────────

    def _detect_speed_unit(self, row: Dict[str, str]) -> str:
        for col_name, unit in SPEED_COLUMN_UNITS.items():
            if col_name in row:
                return unit
        # Fallback: try to detect from value magnitude.
        speed_val = self._get_raw_speed(row)
        if speed_val is not None and float(speed_val) > 60:
            return "kmh"
        return "ms"

    def _get_raw_speed(self, row: Dict[str, str]) -> Optional[str]:
        for col in ("speed_kmh", "speed_mph", "speed_ms", "speed", "v", "vel", "velocity"):
            if col in row:
                return row[col]
        return None

    # ── per-row normalisation ─────────────────────────────────────────────────

    def _normalise_row(
        self,
        row: Dict[str, str],
        unit: str,
        has_gps: bool,
        lat_ref: Optional[float],
        lon_ref: Optional[float],
    ) -> TelemetryPoint:
        r = self._resolve_aliases(row)

        timestamp = float(r.get("timestamp", 0.0))

        # Position
        if has_gps:
            lat = float(r.get("lat", 0.0))
            lon = float(r.get("lon", 0.0))
            x, y = gps_to_xy(lat, lon, lat_ref, lon_ref)
        else:
            lat = lon = None
            x = float(r.get("x", 0.0))
            y = float(r.get("y", 0.0))

        # Speed – check explicit unit columns first, then fall back.
        if "speed_kmh" in row:
            speed = normalize_speed(float(row["speed_kmh"]), "kmh")
        elif "speed_mph" in row:
            speed = normalize_speed(float(row["speed_mph"]), "mph")
        elif "speed_ms" in row:
            speed = normalize_speed(float(row["speed_ms"]), "ms")
        else:
            raw = float(r.get("speed", 0.0))
            speed = normalize_speed(raw, unit)

        accel = float(r.get("acceleration", 0.0))

        # Throttle/brake: normalise from percent if > 1.
        raw_thr = float(r.get("throttle", 0.0))
        throttle = clamp(raw_thr / 100.0 if raw_thr > 1.0 else raw_thr, 0.0, 1.0)

        raw_brk = float(r.get("brake", 0.0))
        brake = clamp(raw_brk / 100.0 if raw_brk > 1.0 else raw_brk, 0.0, 1.0)

        steer = float(r.get("steering_angle", 0.0))
        gear = int(float(r.get("gear", 0)))

        return TelemetryPoint(
            timestamp=timestamp,
            x=x,
            y=y,
            speed=speed,
            acceleration=accel,
            throttle=throttle,
            brake=brake,
            steering_angle=steer,
            gear=gear,
            lat=lat if has_gps else None,
            lon=lon if has_gps else None,
        )

    # ── alias resolution ──────────────────────────────────────────────────────

    def _resolve_aliases(self, row: Dict[str, str]) -> Dict[str, str]:
        """Return a new dict with columns renamed to canonical names."""
        resolved: Dict[str, str] = {}
        for k, v in row.items():
            canonical = FIELD_ALIASES.get(k, k)
            # Don't overwrite an already-canonical key.
            if canonical not in resolved:
                resolved[canonical] = v
            # Also keep original key so speed_kmh etc. are accessible.
            if k not in resolved:
                resolved[k] = v
        return resolved
