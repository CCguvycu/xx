import os
import tempfile

import pytest

from core.models import TelemetryPoint
from ingestion.csv_loader import CSVTelemetryLoader
from ingestion.normalizer import TelemetryNormalizer


# ── helpers ───────────────────────────────────────────────────────────────────

def _write_csv(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                    encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


def _cleanup(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass


# ── CSV loader ────────────────────────────────────────────────────────────────

XY_CSV = """\
timestamp,x,y,speed_kmh,acceleration,throttle,brake,steering_angle,gear
0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1
0.1,1.0,0.5,36.0,2.0,0.8,0.0,-5.0,2
0.2,2.0,1.0,72.0,3.0,1.0,0.0,-3.0,3
"""

GPS_CSV = """\
timestamp,latitude,longitude,speed_kmh,gear
0.0,51.5000,-0.1000,0.0,1
0.1,51.5001,-0.1000,36.0,2
0.2,51.5002,-0.0999,72.0,3
"""

THROTTLE_PCT_CSV = """\
timestamp,x,y,speed_kmh,throttle,brake
0.0,0.0,0.0,0.0,75,50
"""

SPEED_MPH_CSV = """\
timestamp,x,y,speed_mph
0.0,0.0,0.0,60.0
"""


def test_csv_load_xy_row_count():
    path = _write_csv(XY_CSV)
    try:
        loader = CSVTelemetryLoader()
        pts = loader.load(path)
        assert len(pts) == 3
        assert all(isinstance(p, TelemetryPoint) for p in pts)
    finally:
        _cleanup(path)


def test_csv_load_xy_speed_conversion():
    path = _write_csv(XY_CSV)
    try:
        pts = CSVTelemetryLoader().load(path)
        assert pts[1].speed == pytest.approx(10.0, abs=0.05)   # 36 km/h
        assert pts[2].speed == pytest.approx(20.0, abs=0.05)   # 72 km/h
    finally:
        _cleanup(path)


def test_csv_load_xy_throttle_fraction():
    path = _write_csv(XY_CSV)
    try:
        pts = CSVTelemetryLoader().load(path)
        assert pts[1].throttle == pytest.approx(0.8, abs=0.01)
        assert 0.0 <= pts[1].throttle <= 1.0
    finally:
        _cleanup(path)


def test_csv_load_gps_projects_to_xy():
    path = _write_csv(GPS_CSV)
    try:
        pts = CSVTelemetryLoader().load(path)
        assert len(pts) == 3
        # First point is near centroid, so x,y should be small numbers.
        assert abs(pts[0].x) < 100
        assert abs(pts[0].y) < 100
        # GPS was stored.
        assert pts[0].lat is not None
        assert pts[0].lon is not None
    finally:
        _cleanup(path)


def test_csv_load_gps_northward_motion():
    """Increasing latitude → increasing y coordinate."""
    path = _write_csv(GPS_CSV)
    try:
        pts = CSVTelemetryLoader().load(path)
        assert pts[2].y > pts[0].y
    finally:
        _cleanup(path)


def test_csv_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        CSVTelemetryLoader().load("/does/not/exist.csv")


def test_can_load_csv_extension():
    loader = CSVTelemetryLoader()
    assert loader.can_load("telemetry.csv")
    assert loader.can_load("data.CSV")
    assert not loader.can_load("data.json")
    assert not loader.can_load("data.gpx")


def test_throttle_percent_normalised():
    path = _write_csv(THROTTLE_PCT_CSV)
    try:
        pts = CSVTelemetryLoader().load(path)
        assert pts[0].throttle == pytest.approx(0.75, abs=0.01)
        assert pts[0].brake == pytest.approx(0.50, abs=0.01)
    finally:
        _cleanup(path)


def test_speed_mph_conversion():
    path = _write_csv(SPEED_MPH_CSV)
    try:
        pts = CSVTelemetryLoader().load(path)
        # 60 mph = 26.82 m/s
        assert pts[0].speed == pytest.approx(26.82, abs=0.05)
    finally:
        _cleanup(path)


# ── normalizer edge cases ─────────────────────────────────────────────────────

def test_normalizer_empty_batch_raises():
    norm = TelemetryNormalizer()
    with pytest.raises(ValueError):
        norm.normalize_batch([])


def test_normalizer_no_coordinates_raises():
    norm = TelemetryNormalizer()
    with pytest.raises(ValueError):
        norm.normalize_batch([{"timestamp": "0", "speed_kmh": "0"}])
