from __future__ import annotations

from typing import List

import numpy as np

from core.models import DriverRun
from core.schema import clamp
from track.geometry import compute_distances


def consistency_score(runs: List[DriverRun]) -> float:
    """
    Lap-time consistency score [0, 1].
    1.0 = all laps identical. Based on coefficient of variation (CV).
    score = max(0, 1 − CV * 10); CV of 0.1 maps to 0.
    """
    if len(runs) < 2:
        return 1.0
    times = np.array([r.lap_time for r in runs], dtype=float)
    mean = np.mean(times)
    if mean == 0:
        return 1.0
    cv = np.std(times) / mean
    return float(clamp(1.0 - cv * 10.0, 0.0, 1.0))


def speed_trace_consistency(
    runs: List[DriverRun],
    n_points: int = 500,
) -> np.ndarray:
    """
    Per-position speed standard deviation across runs (shape: (n_points,)).
    Lower values = more consistent through that section.
    """
    if not runs:
        return np.zeros(n_points)

    traces = []
    for run in runs:
        coords = np.array([[p.x, p.y] for p in run.points])
        dist = compute_distances(coords)
        speeds = np.array([p.speed for p in run.points])
        # Resample to n_points uniformly in distance.
        query = np.linspace(0, dist[-1], n_points)
        resampled = np.interp(query, dist, speeds)
        traces.append(resampled)

    matrix = np.array(traces)   # (n_runs, n_points)
    return np.std(matrix, axis=0)
