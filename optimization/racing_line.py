from __future__ import annotations

import numpy as np

from core.models import Track
from track.geometry import compute_curvature, smooth_polyline


class RacingLineOptimizer:
    """
    Approximate the minimum-curvature racing line via iterative path smoothing.

    At each iteration:
    1. Pull each interior point toward the midpoint of its neighbours,
       weighted by local curvature magnitude (pull harder in corners).
    2. Project back so the point never moves more than track_half_width
       from the original centerline.
    3. Every 50 iterations apply a light Savitzky-Golay pass for stability.
    """

    def __init__(
        self,
        iterations: int = 200,
        smoothing_weight: float = 0.3,
        track_half_width: float = 4.0,   # metres from centre to edge
    ):
        self.iterations = iterations
        self.smoothing_weight = smoothing_weight
        self.track_half_width = track_half_width

    def compute(self, track: Track) -> np.ndarray:
        """Return optimised racing line as (N, 2) array."""
        centerline = track.polyline  # reference — never modified
        line = centerline.copy()
        n = len(line)

        for step in range(self.iterations):
            kappa = compute_curvature(line)
            new_line = line.copy()

            for i in range(1, n - 1):
                midpoint = 0.5 * (line[i - 1] + line[i + 1])
                # Increase pull strength in high-curvature zones.
                weight = self.smoothing_weight * (1.0 + abs(kappa[i]))
                candidate = line[i] + weight * (midpoint - line[i])

                # Project back within track_half_width of the static centerline.
                offset = candidate - centerline[i]
                dist = np.linalg.norm(offset)
                if dist > self.track_half_width:
                    candidate = centerline[i] + (offset / dist) * self.track_half_width

                new_line[i] = candidate

            line = new_line

            if (step + 1) % 50 == 0:
                line = smooth_polyline(line, window=5, poly=2)
                # Re-clamp after smoothing.
                for i in range(1, n - 1):
                    offset = line[i] - centerline[i]
                    dist = np.linalg.norm(offset)
                    if dist > self.track_half_width:
                        line[i] = centerline[i] + (offset / dist) * self.track_half_width

        return line
