import numpy as np
import pytest

from core.models import TelemetryPoint
from track.reconstruction import TrackReconstructor
from optimization.speed_profile import SpeedProfileOptimizer
from optimization.racing_line import RacingLineOptimizer


# ── helpers ───────────────────────────────────────────────────────────────────

def _circle_track(radius: float = 50.0, n: int = 150):
    t = np.linspace(0, 2 * np.pi * 0.9, n)
    pts = [
        TelemetryPoint(
            timestamp=float(i) * 0.1,
            x=radius * np.cos(a),
            y=radius * np.sin(a),
            speed=15.0,
            acceleration=0.0,
        )
        for i, a in enumerate(t)
    ]
    return TrackReconstructor(smooth_window=11, resample_spacing=2.0).reconstruct(pts)


# ── SpeedProfileOptimizer ─────────────────────────────────────────────────────

def test_speed_profile_output_shape():
    track = _circle_track()
    opt = SpeedProfileOptimizer()
    v = opt.compute(track)
    assert v.shape == track.curvature_array.shape


def test_speed_profile_all_positive():
    track = _circle_track()
    v = SpeedProfileOptimizer(v_min=1.0).compute(track)
    assert np.all(v > 0)


def test_speed_profile_respects_v_max():
    track = _circle_track(radius=1000.0)  # near-straight → speed could hit cap
    v_max = 30.0
    v = SpeedProfileOptimizer(v_max=v_max).compute(track)
    assert np.all(v <= v_max + 1e-6)


def test_speed_profile_respects_corner_limit():
    # Tight circle R=20 m, a_lat=15 → v_corner = sqrt(15*20) ≈ 17.3 m/s
    # Check interior points only — endpoints are unconstrained by braking/accel
    # limits because the track is open (no wrap-around), so they can be higher.
    track = _circle_track(radius=20.0)
    opt = SpeedProfileOptimizer(a_lat_max=15.0, v_max=50.0)
    v = opt.compute(track)
    v_corner_expected = np.sqrt(15.0 * 20.0)
    interior = v[5:-5]  # exclude edge points
    assert np.max(interior) <= v_corner_expected + 0.5


def test_speed_profile_no_sudden_jumps():
    track = _circle_track()
    opt = SpeedProfileOptimizer()
    v = opt.compute(track)
    ds = np.diff(track.distance_array)
    # Max possible speed change between adjacent points via acceleration/braking.
    max_dv = np.sqrt(2 * opt.a_lon_max * np.max(ds)) * 1.5  # generous tolerance
    dv = np.abs(np.diff(v))
    assert np.all(dv <= max_dv)


# ── RacingLineOptimizer ───────────────────────────────────────────────────────

def test_racing_line_output_shape():
    track = _circle_track()
    opt = RacingLineOptimizer(iterations=10)
    line = opt.compute(track)
    assert line.shape == track.polyline.shape


def test_racing_line_stays_within_bounds():
    half_width = 4.0
    track = _circle_track(radius=50.0)
    opt = RacingLineOptimizer(iterations=50, track_half_width=half_width)
    line = opt.compute(track)
    delta = line - track.polyline
    dist = np.linalg.norm(delta, axis=1)
    assert np.all(dist <= half_width + 0.05)


def test_racing_line_differs_from_centerline_in_corners():
    track = _circle_track(radius=30.0)  # all corners
    opt = RacingLineOptimizer(iterations=100, smoothing_weight=0.3, track_half_width=4.0)
    line = opt.compute(track)
    # At least some points should differ from the centerline.
    delta = np.linalg.norm(line - track.polyline, axis=1)
    assert np.max(delta) > 0.01


def test_racing_line_endpoints_unchanged():
    track = _circle_track()
    opt = RacingLineOptimizer(iterations=20)
    line = opt.compute(track)
    # First and last points should match centerline (not moved by interior loop).
    assert np.allclose(line[0], track.polyline[0], atol=0.01)
    assert np.allclose(line[-1], track.polyline[-1], atol=0.01)
