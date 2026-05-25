from __future__ import annotations

from typing import List

import numpy as np

from core.models import TelemetryPoint, Track
from track.geometry import (
    compute_distances,
    compute_curvature,
    smooth_polyline,
    resample_polyline,
)
from track.classifier import classify_segments


class TrackReconstructor:
    """
    Build a Track from a raw sequence of TelemetryPoints.

    Pipeline:
        raw coords → smooth → resample (uniform spacing)
        → distances → curvature
        → interpolate speed/accel onto resampled grid
        → classify segments
        → return Track
    """

    MIN_POINTS = 10

    def __init__(
        self,
        smooth_window: int = 15,
        resample_spacing: float = 2.0,
    ):
        self.smooth_window = smooth_window
        self.resample_spacing = resample_spacing

    def reconstruct(
        self,
        points: List[TelemetryPoint],
        name: str = "unnamed",
    ) -> Track:
        if len(points) < self.MIN_POINTS:
            raise ValueError(
                f"Need at least {self.MIN_POINTS} TelemetryPoints to reconstruct a track; "
                f"got {len(points)}."
            )

        raw = np.array([[p.x, p.y] for p in points])
        raw_speeds = np.array([p.speed for p in points])
        raw_accels = np.array([p.acceleration for p in points])

        smoothed = smooth_polyline(raw, window=self.smooth_window, poly=3)
        resampled = resample_polyline(smoothed, spacing=self.resample_spacing)

        dist_arr = compute_distances(resampled)
        curv_arr = compute_curvature(resampled)

        # Interpolate original speed/accel onto the resampled distance axis.
        raw_dist = compute_distances(raw)
        speeds_r = np.interp(dist_arr, raw_dist, raw_speeds)
        accels_r = np.interp(dist_arr, raw_dist, raw_accels)

        segments = classify_segments(curv_arr, dist_arr, speeds_r, accels_r)

        return Track(
            name=name,
            points=points,
            segments=segments,
            polyline=resampled,
            curvature_array=curv_arr,
            distance_array=dist_arr,
            total_length=float(dist_arr[-1]),
        )
