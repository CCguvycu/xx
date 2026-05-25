from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter


def compute_distances(coords: np.ndarray) -> np.ndarray:
    """
    Cumulative arc-length for an (N, 2) coordinate array.
    Returns (N,) array with distances[0] == 0.
    """
    diffs = np.diff(coords, axis=0)
    seg_lengths = np.hypot(diffs[:, 0], diffs[:, 1])
    return np.concatenate([[0.0], np.cumsum(seg_lengths)])


def compute_curvature(coords: np.ndarray) -> np.ndarray:
    """
    Signed curvature κ = (x'y'' − y'x'') / (x'² + y'²)^1.5.
    Positive = left turn, negative = right turn.
    Uses central finite differences via np.gradient.
    """
    x_p = np.gradient(coords[:, 0])
    y_p = np.gradient(coords[:, 1])
    x_pp = np.gradient(x_p)
    y_pp = np.gradient(y_p)

    denom = (x_p ** 2 + y_p ** 2) ** 1.5
    # Clip denominator to avoid division by zero on straight sections.
    denom = np.where(denom < 1e-10, 1e-10, denom)

    return (x_p * y_pp - y_p * x_pp) / denom


def smooth_polyline(
    coords: np.ndarray,
    window: int = 11,
    poly: int = 3,
) -> np.ndarray:
    """
    Savitzky-Golay smoothing applied independently to x and y.
    Automatically adjusts window to fit array length and ensures it is odd.
    """
    n = len(coords)
    if n < poly + 2:
        return coords.copy()

    # window must be odd and <= n.
    w = min(window, n)
    if w % 2 == 0:
        w -= 1
    w = max(w, poly + 1 if (poly + 1) % 2 == 1 else poly + 2)

    sx = savgol_filter(coords[:, 0], window_length=w, polyorder=poly)
    sy = savgol_filter(coords[:, 1], window_length=w, polyorder=poly)
    return np.column_stack([sx, sy])


def resample_polyline(
    coords: np.ndarray,
    spacing: float = 1.0,
) -> np.ndarray:
    """
    Resample polyline to uniform arc-length spacing (metres).
    Returns (M, 2) array where M = floor(total_length / spacing).
    """
    d = compute_distances(coords)
    total = d[-1]
    if total < spacing:
        return coords.copy()

    query = np.arange(0.0, total, spacing)
    xs = np.interp(query, d, coords[:, 0])
    ys = np.interp(query, d, coords[:, 1])
    return np.column_stack([xs, ys])


def heading_angle(coords: np.ndarray) -> np.ndarray:
    """
    Heading in radians at each point (central differences).
    Returns (N,) array.
    """
    dx = np.gradient(coords[:, 0])
    dy = np.gradient(coords[:, 1])
    return np.arctan2(dy, dx)
