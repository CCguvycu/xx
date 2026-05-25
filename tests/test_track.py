import numpy as np
import pytest

from core.models import TelemetryPoint
from track.geometry import (
    compute_curvature,
    compute_distances,
    heading_angle,
    resample_polyline,
    smooth_polyline,
)
from track.reconstruction import TrackReconstructor


# ── helpers ───────────────────────────────────────────────────────────────────

def _circle_coords(radius: float, n: int = 300) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([radius * np.cos(t), radius * np.sin(t)])


def _circle_points(radius: float = 50.0, n: int = 120) -> list:
    t = np.linspace(0, 2 * np.pi * 0.95, n)
    return [
        TelemetryPoint(
            timestamp=float(i) * 0.1,
            x=radius * np.cos(a),
            y=radius * np.sin(a),
            speed=10.0,
            acceleration=0.0,
        )
        for i, a in enumerate(t)
    ]


def _straight_points(n: int = 20) -> list:
    return [
        TelemetryPoint(timestamp=float(i) * 0.1, x=float(i) * 5.0, y=0.0, speed=20.0)
        for i in range(n)
    ]


# ── compute_distances ─────────────────────────────────────────────────────────

def test_distances_starts_at_zero():
    coords = np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0]])
    d = compute_distances(coords)
    assert d[0] == pytest.approx(0.0)


def test_distances_l_shape():
    coords = np.array([[0.0, 0.0], [3.0, 0.0], [3.0, 4.0]])
    d = compute_distances(coords)
    assert d[1] == pytest.approx(3.0)
    assert d[2] == pytest.approx(7.0)


def test_distances_length_matches_input():
    coords = np.random.default_rng(0).random((50, 2))
    assert len(compute_distances(coords)) == 50


# ── compute_curvature ─────────────────────────────────────────────────────────

def test_curvature_of_circle_magnitude():
    radius = 50.0
    coords = _circle_coords(radius, n=500)
    kappa = compute_curvature(coords)
    # Ignore endpoints (boundary effect of np.gradient).
    interior = np.abs(kappa[20:-20])
    assert np.mean(interior) == pytest.approx(1.0 / radius, rel=0.15)


def test_curvature_of_straight_near_zero():
    coords = np.column_stack([np.linspace(0, 100, 200), np.zeros(200)])
    kappa = compute_curvature(coords)
    assert np.max(np.abs(kappa[5:-5])) < 0.001


def test_curvature_sign_left_turn():
    coords = _circle_coords(radius=30.0, n=200)
    kappa = compute_curvature(coords)
    # A counter-clockwise circle should have predominantly positive curvature.
    assert np.mean(kappa[10:-10]) > 0


# ── smooth_polyline ───────────────────────────────────────────────────────────

def test_smooth_reduces_noise():
    rng = np.random.default_rng(42)
    t = np.linspace(0, 4 * np.pi, 200)
    clean = np.column_stack([t, np.sin(t)])
    noisy = clean + rng.normal(0, 0.3, clean.shape)
    smoothed = smooth_polyline(noisy, window=15)
    # Smoothed should be closer to the clean signal.
    mse_smooth = float(np.mean((smoothed - clean) ** 2))
    mse_noisy = float(np.mean((noisy - clean) ** 2))
    assert mse_smooth < mse_noisy


def test_smooth_output_shape():
    coords = np.random.default_rng(0).random((100, 2))
    out = smooth_polyline(coords)
    assert out.shape == coords.shape


def test_smooth_short_array():
    coords = np.random.default_rng(0).random((5, 2))
    out = smooth_polyline(coords, window=11)
    assert out.shape == coords.shape


# ── resample_polyline ─────────────────────────────────────────────────────────

def test_resample_uniform_spacing():
    coords = np.column_stack([np.linspace(0, 100, 500), np.zeros(500)])
    spacing = 5.0
    resampled = resample_polyline(coords, spacing=spacing)
    diffs = np.hypot(np.diff(resampled[:, 0]), np.diff(resampled[:, 1]))
    assert np.allclose(diffs, spacing, atol=spacing * 0.05)


def test_resample_output_within_original_bounds():
    coords = np.column_stack([np.linspace(0, 50, 100), np.zeros(100)])
    resampled = resample_polyline(coords, spacing=2.0)
    assert resampled[:, 0].min() >= -0.01
    assert resampled[:, 0].max() <= 50.01


# ── heading_angle ─────────────────────────────────────────────────────────────

def test_heading_rightward_line():
    coords = np.column_stack([np.linspace(0, 10, 50), np.zeros(50)])
    h = heading_angle(coords)
    assert np.allclose(h, 0.0, atol=1e-6)


# ── TrackReconstructor ────────────────────────────────────────────────────────

def test_reconstruct_circle_total_length():
    pts = _circle_points(radius=50.0, n=200)
    track = TrackReconstructor(smooth_window=11, resample_spacing=2.0).reconstruct(pts)
    # 95% of circle circumference = 0.95 * 2π * 50 ≈ 298 m
    expected = 0.95 * 2 * np.pi * 50
    assert track.total_length == pytest.approx(expected, rel=0.15)


def test_reconstruct_has_segments():
    pts = _circle_points(n=120)
    track = TrackReconstructor(smooth_window=11, resample_spacing=2.0).reconstruct(pts)
    assert len(track.segments) >= 1


def test_reconstruct_polyline_shape():
    pts = _circle_points(n=120)
    track = TrackReconstructor(smooth_window=11, resample_spacing=2.0).reconstruct(pts)
    assert track.polyline.ndim == 2
    assert track.polyline.shape[1] == 2


def test_reconstruct_arrays_same_length():
    pts = _circle_points(n=120)
    track = TrackReconstructor(smooth_window=11, resample_spacing=2.0).reconstruct(pts)
    assert len(track.curvature_array) == len(track.polyline)
    assert len(track.distance_array) == len(track.polyline)


def test_reconstruct_raises_too_few_points():
    pts = _straight_points(n=5)
    with pytest.raises(ValueError, match="at least"):
        TrackReconstructor().reconstruct(pts)


def test_reconstruct_straight_low_curvature():
    pts = _straight_points(n=50)
    track = TrackReconstructor(smooth_window=9, resample_spacing=2.0).reconstruct(pts)
    assert np.max(np.abs(track.curvature_array)) < 0.01
