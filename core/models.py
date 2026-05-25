from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

import numpy as np


class SegmentType(Enum):
    STRAIGHT = "straight"
    BRAKING = "braking"
    CORNER_ENTRY = "corner_entry"
    APEX = "apex"
    CORNER_EXIT = "corner_exit"
    CHICANE = "chicane"

    @property
    def is_corner(self) -> bool:
        return self in {
            SegmentType.CORNER_ENTRY,
            SegmentType.APEX,
            SegmentType.CORNER_EXIT,
            SegmentType.CHICANE,
        }


@dataclass
class TelemetryPoint:
    timestamp: float
    x: float
    y: float
    speed: float              # m/s
    acceleration: float = 0.0
    throttle: float = 0.0     # 0.0 – 1.0
    brake: float = 0.0        # 0.0 – 1.0
    steering_angle: float = 0.0
    gear: int = 0
    lat: Optional[float] = None
    lon: Optional[float] = None

    def as_xy(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class TrackSegment:
    index: int
    start_idx: int
    end_idx: int
    segment_type: SegmentType
    curvature: float    # 1/m, signed
    length: float       # metres
    avg_speed: float = 0.0
    min_speed: float = 0.0


@dataclass
class Track:
    name: str
    points: List[TelemetryPoint]
    segments: List[TrackSegment]
    polyline: np.ndarray        # (N, 2)
    curvature_array: np.ndarray # (N,)
    distance_array: np.ndarray  # (N,) cumulative arc-length
    total_length: float


@dataclass
class DriverRun:
    run_id: str
    driver_name: str
    points: List[TelemetryPoint]
    lap_time: float
    track: Optional[Track] = None


@dataclass
class SegmentAnalysis:
    segment_index: int
    actual_min_speed: float
    reference_min_speed: float
    speed_delta: float          # actual - reference, m/s
    braking_point_delta: float  # metres, positive = later braking
    exit_speed_delta: float     # m/s
    time_delta: float           # seconds, positive = slower


@dataclass
class AnalysisResult:
    run: DriverRun
    reference_run: DriverRun
    delta_time_cumulative: np.ndarray   # (N,)
    speed_delta: np.ndarray             # (N,)
    lateral_deviation: np.ndarray       # (N,) signed metres
    performance_score: float            # 0 – 100
    segment_analyses: List[SegmentAnalysis]
    consistency_score: float = 1.0      # 0 – 1
