from __future__ import annotations

from typing import List

import numpy as np

from core.models import AnalysisResult, DriverRun, SegmentAnalysis, Track
from analysis.metrics import (
    compute_delta_time,
    compute_lateral_deviation,
    interpolate_speed_at_distance,
    performance_score,
)
from analysis.consistency import consistency_score
from track.geometry import compute_distances


class RunComparator:
    """Compare a driver run against a reference run on a shared track."""

    def compare(
        self,
        run: DriverRun,
        reference: DriverRun,
        track: Track,
    ) -> AnalysisResult:
        dist = track.distance_array

        actual_speeds = interpolate_speed_at_distance(run.points, dist)
        ref_speeds = interpolate_speed_at_distance(reference.points, dist)

        delta_time = compute_delta_time(actual_speeds, ref_speeds, dist)
        speed_delta = actual_speeds - ref_speeds

        # Interpolate run coords onto the track distance grid for deviation calc.
        run_raw = np.array([[p.x, p.y] for p in run.points])
        run_raw_dist = compute_distances(run_raw)
        run_xs = np.interp(dist, run_raw_dist, run_raw[:, 0])
        run_ys = np.interp(dist, run_raw_dist, run_raw[:, 1])
        run_interp = np.column_stack([run_xs, run_ys])

        lateral_dev = compute_lateral_deviation(run_interp, track.polyline)

        seg_analyses = self._analyse_segments(
            track, run, reference, actual_speeds, ref_speeds, dist, delta_time
        )

        score = performance_score(run.lap_time, reference.lap_time)
        c_score = consistency_score([run, reference])

        return AnalysisResult(
            run=run,
            reference_run=reference,
            delta_time_cumulative=delta_time,
            speed_delta=speed_delta,
            lateral_deviation=lateral_dev,
            performance_score=score,
            segment_analyses=seg_analyses,
            consistency_score=c_score,
        )

    def _analyse_segments(
        self,
        track: Track,
        run: DriverRun,
        reference: DriverRun,
        actual_speeds: np.ndarray,
        ref_speeds: np.ndarray,
        distances: np.ndarray,
        delta_time: np.ndarray,
    ) -> List[SegmentAnalysis]:
        n = len(actual_speeds)
        analyses = []

        for seg in track.segments:
            s = seg.start_idx
            e = min(seg.end_idx + 1, n)
            if s >= e:
                continue

            a_spd = actual_speeds[s:e]
            r_spd = ref_speeds[s:e]

            a_min = float(np.min(a_spd))
            r_min = float(np.min(r_spd))
            exit_delta = float(a_spd[-1] - r_spd[-1]) if len(a_spd) else 0.0

            # Time delta over this segment.
            seg_dist = distances[s:e]
            seg_dt = compute_delta_time(a_spd, r_spd, seg_dist)
            time_delta = float(seg_dt[-1]) if len(seg_dt) else 0.0

            # Braking point: distance to first brake application in this segment.
            bp_delta = self._braking_point_delta(run, reference, s, e, distances)

            analyses.append(
                SegmentAnalysis(
                    segment_index=seg.index,
                    actual_min_speed=a_min,
                    reference_min_speed=r_min,
                    speed_delta=a_min - r_min,
                    braking_point_delta=bp_delta,
                    exit_speed_delta=exit_delta,
                    time_delta=time_delta,
                )
            )

        return analyses

    def _braking_point_delta(
        self,
        run: DriverRun,
        reference: DriverRun,
        start: int,
        end: int,
        distances: np.ndarray,
    ) -> float:
        """
        Positive = actual braked later than reference (better), negative = earlier.
        Returns 0 if no brake event found in either run for this segment.
        """
        def first_brake_distance(pts, s, e):
            for i in range(s, min(e, len(pts))):
                if pts[i].brake > 0.1:
                    return distances[i] if i < len(distances) else None
            return None

        actual_bd = first_brake_distance(run.points, start, end)
        ref_bd = first_brake_distance(reference.points, start, end)

        if actual_bd is None or ref_bd is None:
            return 0.0
        return float(actual_bd - ref_bd)
