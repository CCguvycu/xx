from __future__ import annotations

import numpy as np

from core.models import Track


class SpeedProfileOptimizer:
    """
    Compute the theoretically optimal speed profile for a given track.

    Three-phase algorithm:
    1. Corner speed limit: v_c = sqrt(a_lat / |κ|)
    2. Forward integration (acceleration limited)
    3. Backward integration (braking limited)
    """

    def __init__(
        self,
        a_lat_max: float = 20.0,    # m/s² lateral grip
        a_lon_max: float = 8.0,     # m/s² peak acceleration
        a_brake_max: float = 15.0,  # m/s² peak braking
        v_max: float = 80.0,        # m/s absolute cap
        v_min: float = 1.0,         # m/s floor (avoids singularity)
    ):
        self.a_lat_max = a_lat_max
        self.a_lon_max = a_lon_max
        self.a_brake_max = a_brake_max
        self.v_max = v_max
        self.v_min = v_min

    def compute(self, track: Track) -> np.ndarray:
        """Return optimal speed (m/s) at each point in track.polyline."""
        abs_k = np.maximum(np.abs(track.curvature_array), 1e-6)
        dist = track.distance_array
        ds = np.diff(dist)
        n = len(abs_k)

        # Phase 1 — corner speed limit.
        v_corner = np.sqrt(self.a_lat_max / abs_k)
        v_corner = np.clip(v_corner, self.v_min, self.v_max)

        # Phase 2 — forward integration (acceleration limited).
        v_fwd = v_corner.copy()
        for i in range(n - 1):
            v_accel = np.sqrt(v_fwd[i] ** 2 + 2.0 * self.a_lon_max * ds[i])
            v_fwd[i + 1] = min(v_accel, v_corner[i + 1])

        # Phase 3 — backward integration (braking limited).
        v_opt = v_fwd.copy()
        for i in range(n - 2, -1, -1):
            v_brake = np.sqrt(v_opt[i + 1] ** 2 + 2.0 * self.a_brake_max * ds[i])
            v_opt[i] = min(v_brake, v_fwd[i])

        return v_opt
