from __future__ import annotations

from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from core.models import SegmentType, Track

_DARK_BG = "#1a1a2e"
_DARK_PANEL = "#0f0f23"
_TICK_COLOR = "#aaaaaa"

SEGMENT_COLORS = {
    SegmentType.STRAIGHT: "#4fc3f7",
    SegmentType.BRAKING: "#ef5350",
    SegmentType.CORNER_ENTRY: "#ffa726",
    SegmentType.APEX: "#ab47bc",
    SegmentType.CORNER_EXIT: "#66bb6a",
    SegmentType.CHICANE: "#ff7043",
}


def plot_track(
    track: Track,
    title: str = "Track Map",
    show: bool = True,
    save_path: Optional[str] = None,
) -> matplotlib.figure.Figure:
    """2D top-down track map coloured by segment type."""
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=_DARK_BG)
    ax.set_facecolor(_DARK_PANEL)

    poly = track.polyline

    for seg in track.segments:
        s = seg.start_idx
        e = min(seg.end_idx + 1, len(poly))
        pts = poly[s:e]
        if len(pts) < 2:
            continue
        color = SEGMENT_COLORS.get(seg.segment_type, "#ffffff")
        ax.plot(pts[:, 0], pts[:, 1], color=color, linewidth=2.5, alpha=0.9)

    # Start/finish marker.
    ax.scatter(
        poly[0, 0], poly[0, 1],
        s=200, color="#ffd700", zorder=6, marker="*", label="Start / Finish",
    )

    legend_handles = [
        plt.Line2D([0], [0], color=c, linewidth=2,
                   label=t.value.replace("_", " ").title())
        for t, c in SEGMENT_COLORS.items()
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper right",
        facecolor="#2d2d44",
        labelcolor="white",
        fontsize=8,
        framealpha=0.8,
    )

    _style_ax(ax, title)
    ax.set_aspect("equal")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_DARK_BG)
    if show:
        plt.show()
    return fig


def _style_ax(ax, title: str) -> None:
    ax.set_title(title, color="white", fontsize=14, pad=10)
    ax.set_xlabel("X (m)", color=_TICK_COLOR)
    ax.set_ylabel("Y (m)", color=_TICK_COLOR)
    ax.tick_params(colors=_TICK_COLOR)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333355")
