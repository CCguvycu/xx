import numpy as np
import pytest

from core.models import (
    AnalysisResult,
    DriverRun,
    SegmentAnalysis,
    SegmentType,
    TelemetryPoint,
    Track,
    TrackSegment,
)


def _pt(t=0.0, x=0.0, y=0.0, speed=10.0):
    return TelemetryPoint(timestamp=t, x=x, y=y, speed=speed)


# ── TelemetryPoint ────────────────────────────────────────────────────────────

def test_telemetry_point_defaults():
    p = _pt()
    assert p.acceleration == 0.0
    assert p.throttle == 0.0
    assert p.brake == 0.0
    assert p.steering_angle == 0.0
    assert p.gear == 0
    assert p.lat is None
    assert p.lon is None


def test_telemetry_point_as_xy():
    p = _pt(x=3.0, y=4.0)
    assert p.as_xy() == (3.0, 4.0)


def test_telemetry_point_stores_speed_ms():
    p = TelemetryPoint(timestamp=0, x=0, y=0, speed=27.78)
    assert p.speed == pytest.approx(27.78)


# ── SegmentType ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("st", [
    SegmentType.CORNER_ENTRY,
    SegmentType.APEX,
    SegmentType.CORNER_EXIT,
    SegmentType.CHICANE,
])
def test_segment_type_is_corner_true(st):
    assert st.is_corner


@pytest.mark.parametrize("st", [
    SegmentType.STRAIGHT,
    SegmentType.BRAKING,
])
def test_segment_type_is_corner_false(st):
    assert not st.is_corner


# ── DriverRun ─────────────────────────────────────────────────────────────────

def test_driver_run_track_defaults_none():
    run = DriverRun("r1", "driver", [], 60.0)
    assert run.track is None


def test_driver_run_stores_points():
    pts = [_pt(i * 0.1) for i in range(5)]
    run = DriverRun("r1", "driver", pts, 60.0)
    assert len(run.points) == 5


# ── AnalysisResult ────────────────────────────────────────────────────────────

def test_analysis_result_consistency_score_default():
    dummy_run = DriverRun("r1", "A", [], 60.0)
    arr = np.zeros(10)
    result = AnalysisResult(
        run=dummy_run,
        reference_run=dummy_run,
        delta_time_cumulative=arr,
        speed_delta=arr,
        lateral_deviation=arr,
        performance_score=95.0,
        segment_analyses=[],
    )
    assert result.consistency_score == 1.0
