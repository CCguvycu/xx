from __future__ import annotations

from typing import List

import numpy as np

from core.models import SegmentType, TrackSegment

CURVATURE_STRAIGHT_THRESHOLD = 0.005   # |κ| below this → straight (R > 200 m)
CURVATURE_APEX_THRESHOLD = 0.02        # |κ| above this → apex zone (R < 50 m)
BRAKING_DECEL_THRESHOLD = -3.0         # m/s² — sustained decel marks braking zone
MIN_SEGMENT_LENGTH = 5.0               # metres — merge shorter segments


def classify_segments(
    curvature: np.ndarray,
    distances: np.ndarray,
    speeds: np.ndarray,
    accelerations: np.ndarray,
) -> List[TrackSegment]:
    """
    1. Label each point.
    2. Run-length encode into segments.
    3. Merge segments shorter than MIN_SEGMENT_LENGTH.
    """
    labels = _label_points(curvature, speeds, accelerations)
    segments = _encode_segments(labels, curvature, distances, speeds)
    return _merge_short(segments, curvature, distances, speeds)


# ── point labelling ───────────────────────────────────────────────────────────

def _label_points(
    curvature: np.ndarray,
    speeds: np.ndarray,
    accelerations: np.ndarray,
) -> List[SegmentType]:
    abs_k = np.abs(curvature)
    speed_grad = np.gradient(speeds)
    labels = []

    for i in range(len(curvature)):
        k = abs_k[i]
        a = accelerations[i]

        if k < CURVATURE_STRAIGHT_THRESHOLD:
            if a < BRAKING_DECEL_THRESHOLD:
                labels.append(SegmentType.BRAKING)
            else:
                labels.append(SegmentType.STRAIGHT)
        elif k >= CURVATURE_APEX_THRESHOLD:
            labels.append(SegmentType.APEX)
        else:
            # Transition zone: classify by whether speed is falling or rising.
            if speed_grad[i] < 0:
                labels.append(SegmentType.CORNER_ENTRY)
            else:
                labels.append(SegmentType.CORNER_EXIT)

    return labels


# ── run-length encoding ───────────────────────────────────────────────────────

def _encode_segments(
    labels: List[SegmentType],
    curvature: np.ndarray,
    distances: np.ndarray,
    speeds: np.ndarray,
) -> List[TrackSegment]:
    if not labels:
        return []

    segments: List[TrackSegment] = []
    start = 0
    current = labels[0]

    for i in range(1, len(labels)):
        if labels[i] != current:
            segments.append(
                _make_segment(len(segments), start, i - 1, current,
                              curvature, distances, speeds)
            )
            start = i
            current = labels[i]

    segments.append(
        _make_segment(len(segments), start, len(labels) - 1, current,
                      curvature, distances, speeds)
    )
    return segments


def _make_segment(
    index: int,
    start_idx: int,
    end_idx: int,
    seg_type: SegmentType,
    curvature: np.ndarray,
    distances: np.ndarray,
    speeds: np.ndarray,
) -> TrackSegment:
    k_slice = curvature[start_idx: end_idx + 1]
    s_slice = speeds[start_idx: end_idx + 1]
    length = float(distances[end_idx] - distances[start_idx])

    return TrackSegment(
        index=index,
        start_idx=start_idx,
        end_idx=end_idx,
        segment_type=seg_type,
        curvature=float(np.mean(k_slice)),
        length=max(length, 0.01),
        avg_speed=float(np.mean(s_slice)) if len(s_slice) else 0.0,
        min_speed=float(np.min(s_slice)) if len(s_slice) else 0.0,
    )


# ── merge short segments ──────────────────────────────────────────────────────

def _merge_short(
    segments: List[TrackSegment],
    curvature: np.ndarray,
    distances: np.ndarray,
    speeds: np.ndarray,
) -> List[TrackSegment]:
    """Absorb segments shorter than MIN_SEGMENT_LENGTH into their neighbour."""
    if len(segments) <= 1:
        return segments

    changed = True
    while changed:
        changed = False
        merged: List[TrackSegment] = []
        i = 0
        while i < len(segments):
            seg = segments[i]
            if seg.length < MIN_SEGMENT_LENGTH and len(segments) > 1:
                # Absorb into previous if possible, else next.
                if merged:
                    prev = merged[-1]
                    merged[-1] = _make_segment(
                        prev.index, prev.start_idx, seg.end_idx,
                        prev.segment_type, curvature, distances, speeds,
                    )
                elif i + 1 < len(segments):
                    nxt = segments[i + 1]
                    merged.append(_make_segment(
                        0, seg.start_idx, nxt.end_idx,
                        nxt.segment_type, curvature, distances, speeds,
                    ))
                    i += 1  # skip next
                else:
                    merged.append(seg)
                changed = True
            else:
                merged.append(seg)
            i += 1
        segments = merged

    # Re-index.
    for idx, seg in enumerate(segments):
        seg.index = idx

    return segments
