"""
Generate a synthetic circuit telemetry CSV for testing.

Circuit layout (parametric, curvature-driven integration):
  T0  Long straight            200 m
  T1  Hairpin  R=20 m  180°    ~63 m
  T2  Short straight            80 m
  T3  Medium corner R=50 m 90°  ~79 m (right)
  T4a Chicane left  R=30 m 60°  ~31 m
  T4b Chicane right R=30 m 60°  ~31 m
  T5  Sweeping left R=80 m 150° ~209 m
  T6  Short straight            50 m

Total ~ 743 m.  Simulated at 10 Hz.
"""

from __future__ import annotations

import csv
import math
import os
from typing import List, NamedTuple, Tuple

import numpy as np

_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "sample_telemetry.csv")
_WHEELBASE = 2.5   # metres (for Ackermann steering angle)
_SAMPLE_HZ = 10    # samples per second
_ARC_STEP = 0.5    # integration step in metres


# ── circuit definition ────────────────────────────────────────────────────────

class Segment(NamedTuple):
    name: str
    radius: float   # metres (None → straight)
    length: float   # arc length in metres
    direction: int  # +1 left, -1 right, 0 straight


CIRCUIT: List[Segment] = [
    Segment("T0_STRAIGHT",      0.0,  200.0,  0),
    Segment("T1_HAIRPIN",      20.0,   62.8, +1),
    Segment("T2_SHORT_STR",     0.0,   80.0,  0),
    Segment("T3_MEDIUM_CRN",   50.0,   78.5, -1),
    Segment("T4A_CHICANE_L",   30.0,   31.4, +1),
    Segment("T4B_CHICANE_R",   30.0,   31.4, -1),
    Segment("T5_SWEEPING",     80.0,  209.4, +1),
    Segment("T6_HOME_STR",      0.0,   50.0,  0),
]


# ── geometry integration ──────────────────────────────────────────────────────

def build_track_geometry() -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns:
        coords: (N, 2) array of (x, y) positions
        curvatures: (N,) array of curvature values (1/m)
    """
    xs, ys, ks = [0.0], [0.0], [0.0]
    heading = 0.0   # radians, 0 = east

    for seg in CIRCUIT:
        n_steps = max(1, int(seg.length / _ARC_STEP))
        step = seg.length / n_steps

        if seg.direction == 0 or seg.radius == 0:
            kappa = 0.0
        else:
            kappa = seg.direction / seg.radius

        for _ in range(n_steps):
            x_new = xs[-1] + math.cos(heading) * step
            y_new = ys[-1] + math.sin(heading) * step
            xs.append(x_new)
            ys.append(y_new)
            ks.append(kappa)
            heading += kappa * step

    return np.column_stack([xs, ys]), np.array(ks)


# ── speed profile ─────────────────────────────────────────────────────────────

def build_speed_profile(
    curvatures: np.ndarray,
    arc_steps: np.ndarray,
    a_lat: float = 15.0,
    a_accel: float = 5.0,
    a_brake: float = 12.0,
    v_max: float = 30.0,   # ~108 km/h — realistic for club circuit
    v_min: float = 3.0,
) -> np.ndarray:
    abs_k = np.abs(curvatures)
    # Corner-limited speed — clip denominator to avoid divide-by-zero on straights.
    v_limit = np.where(
        abs_k > 1e-4,
        np.sqrt(a_lat / np.maximum(abs_k, 1e-10)),
        v_max,
    )
    v_limit = np.clip(v_limit, v_min, v_max)

    ds = arc_steps

    # Backward pass (braking).
    v = v_limit.copy()
    for i in range(len(v) - 2, -1, -1):
        v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2.0 * a_brake * ds[i]))

    # Forward pass (acceleration).
    for i in range(len(v) - 1):
        v[i + 1] = min(v[i + 1], math.sqrt(v[i] ** 2 + 2.0 * a_accel * ds[i]))

    return np.clip(v, v_min, v_max)


# ── control assignment ────────────────────────────────────────────────────────

def assign_controls(
    speeds: np.ndarray,
    curvatures: np.ndarray,
    a_accel: float = 5.0,
    a_brake: float = 12.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = len(speeds)
    accel_arr = np.zeros(n)
    throttle = np.zeros(n)
    brake = np.zeros(n)
    steer = np.zeros(n)
    gear = np.ones(n, dtype=int)

    for i in range(1, n):
        dv = speeds[i] - speeds[i - 1]
        accel_arr[i] = dv * _SAMPLE_HZ  # approximate a = dv/dt

    for i in range(n):
        a = accel_arr[i]
        if a >= 0:
            throttle[i] = min(a / a_accel, 1.0)
            brake[i] = 0.0
        else:
            throttle[i] = 0.0
            brake[i] = min(-a / a_brake, 1.0)

        # Ackermann: steering = arctan(wheelbase * kappa)
        steer[i] = math.degrees(math.atan(_WHEELBASE * curvatures[i]))

        # Gear from speed bands (m/s).
        v = speeds[i]
        if v < 10:
            gear[i] = 1
        elif v < 20:
            gear[i] = 2
        elif v < 30:
            gear[i] = 3
        elif v < 42:
            gear[i] = 4
        else:
            gear[i] = 5

    return accel_arr, throttle, brake, steer, gear


# ── temporal resampling ───────────────────────────────────────────────────────

def resample_to_time(
    coords: np.ndarray,
    speeds: np.ndarray,
    curvatures: np.ndarray,
    accel: np.ndarray,
    throttle: np.ndarray,
    brake: np.ndarray,
    steer: np.ndarray,
    gear: np.ndarray,
    hz: int = _SAMPLE_HZ,
) -> List[dict]:
    """Convert space-domain data to uniform time-domain rows."""
    # Compute cumulative time for each spatial sample.
    n = len(speeds)
    t = [0.0]
    for i in range(1, n):
        v_avg = max((speeds[i - 1] + speeds[i]) * 0.5, 0.1)
        dt = _ARC_STEP / v_avg
        t.append(t[-1] + dt)

    t_arr = np.array(t)
    t_uniform = np.arange(0.0, t_arr[-1], 1.0 / hz)

    rows = []
    for ts in t_uniform:
        x = float(np.interp(ts, t_arr, coords[:, 0]))
        y = float(np.interp(ts, t_arr, coords[:, 1]))
        v = float(np.interp(ts, t_arr, speeds)) * 3.6  # m/s → km/h
        a = float(np.interp(ts, t_arr, accel))
        th = float(np.interp(ts, t_arr, throttle))
        br = float(np.interp(ts, t_arr, brake))
        st = float(np.interp(ts, t_arr, steer))
        g = int(round(float(np.interp(ts, t_arr, gear.astype(float)))))
        rows.append({
            "timestamp": round(ts, 3),
            "x": round(x, 4),
            "y": round(y, 4),
            "speed_kmh": round(v, 3),
            "acceleration": round(a, 4),
            "throttle": round(th, 4),
            "brake": round(br, 4),
            "steering_angle": round(st, 4),
            "gear": g,
        })
    return rows


# ── main ──────────────────────────────────────────────────────────────────────

def generate(output_path: str = _OUTPUT_PATH) -> str:
    coords, curvatures = build_track_geometry()
    n = len(coords)

    # Arc step array (uniform _ARC_STEP for each geometry sample).
    arc_steps = np.full(n, _ARC_STEP)

    speeds = build_speed_profile(curvatures, arc_steps)
    accel, throttle, brake, steer, gear = assign_controls(speeds, curvatures)

    rows = resample_to_time(coords, speeds, curvatures, accel,
                             throttle, brake, steer, gear)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fields = ["timestamp", "x", "y", "speed_kmh", "acceleration",
              "throttle", "brake", "steering_angle", "gear"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


if __name__ == "__main__":
    path = generate()
    print(f"Generated {path}")
