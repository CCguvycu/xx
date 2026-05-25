from __future__ import annotations

from typing import List

import numpy as np
from scipy.spatial import cKDTree

from core.models import TelemetryPoint
from track.geometry import compute_distances


def interpolate_speed_at_distance(
    points: List[TelemetryPoint],
    query_distances: np.ndarray,
) -> np.ndarray:
    """
    Interpolate TelemetryPoint speeds onto a common distance axis.
    Points are assumed to be ordered; distances computed from their (x, y) positions.
    """
    coords = np.array([[p.x, p.y] for p in points])
    dist = compute_distances(coords)
    speeds = np.array([p.speed for p in points])
    return np.interp(query_distances, dist, speeds)


def compute_delta_time(
    actual_speeds: np.ndarray,
    ref_speeds: np.ndarray,
    distances: np.ndarray,
) -> np.ndarray:
    """
    Cumulative time delta: Σ (1/v_actual − 1/v_ref) · ds.
    Positive = actual is slower; negative = faster.
    Denominators clipped to 0.1 m/s to avoid singularity at standstill.
    Returns (N,) array starting at 0.
    """
    ds = np.diff(distances)
    v_a = np.maximum(actual_speeds[:-1], 0.1)
    v_r = np.maximum(ref_speeds[:-1], 0.1)
    dt = (1.0 / v_a - 1.0 / v_r) * ds
    return np.concatenate([[0.0], np.cumsum(dt)])


def compute_lateral_deviation(
    run_coords: np.ndarray,
    reference_polyline: np.ndarray,
) -> np.ndarray:
    """
    Signed lateral deviation of run points from the reference line.
    Positive = left of reference direction of travel.

    For each run point:
    1. Find nearest reference index via cKDTree.
    2. Compute tangent at that index (central difference).
    3. Left-hand normal = [-tangent_y, tangent_x].
    4. deviation = dot(run_point − ref_point, normal).
    """
    tree = cKDTree(reference_polyline)
    _, indices = tree.query(run_coords)
    n_ref = len(reference_polyline)

    deviations = np.empty(len(run_coords))
    for i, (pt, k) in enumerate(zip(run_coords, indices)):
        k = int(k)
        # Central difference for tangent.
        k_prev = max(k - 1, 0)
        k_next = min(k + 1, n_ref - 1)
        tangent = reference_polyline[k_next] - reference_polyline[k_prev]
        norm = np.linalg.norm(tangent)
        if norm < 1e-10:
            deviations[i] = 0.0
            continue
        tangent /= norm
        normal = np.array([-tangent[1], tangent[0]])
        deviations[i] = float(np.dot(pt - reference_polyline[k], normal))

    return deviations


def performance_score(
    actual_lap_time: float,
    reference_lap_time: float,
) -> float:
    """
    0–100 score relative to reference. Identical times → 100.0.
    Faster than reference is capped at 100.
    """
    if actual_lap_time <= 0 or reference_lap_time <= 0:
        return 0.0
    ratio = reference_lap_time / actual_lap_time
    return float(np.clip(ratio * 100.0, 0.0, 100.0))
