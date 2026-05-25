import numpy as np
import pytest

from core.models import DriverRun, TelemetryPoint
from track.reconstruction import TrackReconstructor
from analysis.comparator import RunComparator
from analysis.metrics import (
    compute_delta_time,
    compute_lateral_deviation,
    interpolate_speed_at_distance,
    performance_score,
)
from analysis.consistency import consistency_score, speed_trace_consistency


# ── helpers ───────────────────────────────────────────────────────────────────

def _arc_points(speed: float, n: int = 80, radius: float = 50.0) -> list:
    t = np.linspace(0, np.pi * 1.5, n)
    return [
        TelemetryPoint(
            timestamp=float(i) * 0.1,
            x=radius * np.cos(a),
            y=radius * np.sin(a),
            speed=speed,
            acceleration=0.0,
        )
        for i, a in enumerate(t)
    ]


def _run(speed: float, lap_time: float, name: str = "driver", n: int = 80) -> DriverRun:
    return DriverRun(
        run_id="r",
        driver_name=name,
        points=_arc_points(speed, n=n),
        lap_time=lap_time,
    )


# ── compute_delta_time ────────────────────────────────────────────────────────

def test_delta_time_identical_speeds_is_zero():
    dist = np.linspace(0, 100, 50)
    v = np.full(50, 15.0)
    delta = compute_delta_time(v, v, dist)
    assert np.allclose(delta, 0.0, atol=1e-10)


def test_delta_time_slower_run_positive():
    dist = np.linspace(0, 100, 50)
    ref = np.full(50, 20.0)
    actual = np.full(50, 10.0)
    delta = compute_delta_time(actual, ref, dist)
    assert delta[-1] > 0


def test_delta_time_faster_run_negative():
    dist = np.linspace(0, 100, 50)
    ref = np.full(50, 10.0)
    actual = np.full(50, 20.0)
    delta = compute_delta_time(actual, ref, dist)
    assert delta[-1] < 0


def test_delta_time_starts_at_zero():
    dist = np.linspace(0, 100, 50)
    v = np.full(50, 10.0)
    delta = compute_delta_time(v, v * 0.8, dist)
    assert delta[0] == pytest.approx(0.0)


def test_delta_time_shape():
    dist = np.linspace(0, 100, 30)
    v = np.ones(30) * 10
    assert compute_delta_time(v, v, dist).shape == (30,)


# ── performance_score ─────────────────────────────────────────────────────────

def test_performance_score_equal_times():
    assert performance_score(60.0, 60.0) == pytest.approx(100.0)


def test_performance_score_slower_below_100():
    assert performance_score(70.0, 60.0) < 100.0


def test_performance_score_faster_capped_at_100():
    assert performance_score(50.0, 60.0) == pytest.approx(100.0)


def test_performance_score_zero_time_returns_zero():
    assert performance_score(0.0, 60.0) == pytest.approx(0.0)


# ── compute_lateral_deviation ─────────────────────────────────────────────────

def test_lateral_deviation_on_reference_near_zero():
    coords = np.column_stack([np.linspace(0, 100, 50), np.zeros(50)])
    dev = compute_lateral_deviation(coords, coords)
    assert np.max(np.abs(dev)) < 0.1


def test_lateral_deviation_shape():
    ref = np.column_stack([np.linspace(0, 100, 100), np.zeros(100)])
    run = ref + np.array([0.0, 2.0])  # 2 m to the left
    dev = compute_lateral_deviation(run, ref)
    assert dev.shape == (100,)


# ── consistency_score ─────────────────────────────────────────────────────────

def test_consistency_score_single_run():
    runs = [DriverRun("r1", "A", [], 60.0)]
    assert consistency_score(runs) == pytest.approx(1.0)


def test_consistency_score_identical_times():
    runs = [DriverRun("r1", "A", [], 60.0), DriverRun("r2", "A", [], 60.0)]
    assert consistency_score(runs) == pytest.approx(1.0)


def test_consistency_score_varies_with_spread():
    tight = [DriverRun("r1", "A", [], 60.0), DriverRun("r2", "A", [], 60.5)]
    wide = [DriverRun("r1", "A", [], 60.0), DriverRun("r2", "A", [], 80.0)]
    assert consistency_score(tight) > consistency_score(wide)


def test_consistency_score_bounded():
    runs = [DriverRun(f"r{i}", "A", [], t) for i, t in enumerate([55, 62, 70, 45, 90])]
    score = consistency_score(runs)
    assert 0.0 <= score <= 1.0


# ── speed_trace_consistency ───────────────────────────────────────────────────

def test_speed_trace_consistency_shape():
    runs = [_run(10.0, 60.0), _run(11.0, 58.0)]
    out = speed_trace_consistency(runs, n_points=100)
    assert out.shape == (100,)


def test_speed_trace_consistency_identical_runs_near_zero():
    runs = [_run(10.0, 60.0), _run(10.0, 60.0)]
    out = speed_trace_consistency(runs, n_points=50)
    assert np.max(out) < 1e-6


# ── RunComparator end-to-end ──────────────────────────────────────────────────

def test_run_comparator_output_shape():
    ref = _run(15.0, 60.0, name="ref", n=80)
    act = _run(12.0, 75.0, name="driver", n=80)
    track = TrackReconstructor(smooth_window=9, resample_spacing=2.0).reconstruct(ref.points)
    result = RunComparator().compare(act, ref, track)
    n = len(track.distance_array)
    assert result.delta_time_cumulative.shape == (n,)
    assert result.speed_delta.shape == (n,)
    assert result.lateral_deviation.shape == (n,)


def test_run_comparator_slower_run_loses_time():
    ref = _run(15.0, 60.0, name="ref", n=80)
    act = _run(10.0, 80.0, name="driver", n=80)
    track = TrackReconstructor(smooth_window=9, resample_spacing=2.0).reconstruct(ref.points)
    result = RunComparator().compare(act, ref, track)
    assert result.delta_time_cumulative[-1] > 0


def test_run_comparator_performance_score_range():
    ref = _run(15.0, 60.0, name="ref", n=80)
    act = _run(12.0, 75.0, name="driver", n=80)
    track = TrackReconstructor(smooth_window=9, resample_spacing=2.0).reconstruct(ref.points)
    result = RunComparator().compare(act, ref, track)
    assert 0.0 <= result.performance_score <= 100.0


def test_run_comparator_segment_analyses_present():
    ref = _run(15.0, 60.0, n=100)
    track = TrackReconstructor(smooth_window=9, resample_spacing=2.0).reconstruct(ref.points)
    result = RunComparator().compare(ref, ref, track)
    assert isinstance(result.segment_analyses, list)
