from __future__ import annotations

from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from core.models import AnalysisResult, Track
from analysis.metrics import interpolate_speed_at_distance

_DARK_BG = "#1a1a2e"
_DARK_PANEL = "#0f0f23"
_TICK_COLOR = "#aaaaaa"
_COLOR_ACTUAL = "#ef5350"
_COLOR_REF = "#4fc3f7"


def plot_comparison(
    result: AnalysisResult,
    track: Track,
    title: str = "Driver Comparison",
    show: bool = True,
    save_path: Optional[str] = None,
) -> matplotlib.figure.Figure:
    """
    4-panel comparison figure:
    1 — Track overlay (actual vs reference lines)
    2 — Speed traces with speed-loss fill
    3 — Cumulative delta time (red = slower, green = faster)
    4 — Lateral deviation from reference line
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), facecolor=_DARK_BG)
    fig.suptitle(
        f"{result.run.driver_name} vs {result.reference_run.driver_name}",
        color="white", fontsize=14, y=0.99,
    )

    for ax in axes.ravel():
        ax.set_facecolor(_DARK_PANEL)
        ax.tick_params(colors=_TICK_COLOR)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333355")

    dist = track.distance_array
    actual_spd = interpolate_speed_at_distance(result.run.points, dist)
    ref_spd = interpolate_speed_at_distance(result.reference_run.points, dist)

    # ── Panel 1: track overlay ─────────────────────────────────────────────
    ax1 = axes[0, 0]
    ref_coords = np.array([[p.x, p.y] for p in result.reference_run.points])
    run_coords = np.array([[p.x, p.y] for p in result.run.points])

    ax1.plot(ref_coords[:, 0], ref_coords[:, 1],
             color=_COLOR_REF, linewidth=2.0, alpha=0.85,
             label=result.reference_run.driver_name)
    ax1.plot(run_coords[:, 0], run_coords[:, 1],
             color=_COLOR_ACTUAL, linewidth=1.5, alpha=0.75,
             linestyle="--", label=result.run.driver_name)
    ax1.set_title("Track Lines", color="white")
    ax1.set_aspect("equal")
    ax1.legend(facecolor="#2d2d44", labelcolor="white", fontsize=8)

    # ── Panel 2: speed traces ──────────────────────────────────────────────
    ax2 = axes[0, 1]
    ax2.plot(dist, ref_spd, color=_COLOR_REF, linewidth=1.5, label="Reference")
    ax2.plot(dist, actual_spd, color=_COLOR_ACTUAL, linewidth=1.5, label="Run")
    ax2.fill_between(dist, actual_spd, ref_spd,
                     where=(actual_spd < ref_spd),
                     alpha=0.35, color=_COLOR_ACTUAL, label="Speed loss")
    ax2.fill_between(dist, actual_spd, ref_spd,
                     where=(actual_spd >= ref_spd),
                     alpha=0.25, color="#66bb6a", label="Speed gain")
    ax2.set_title("Speed Trace (m/s)", color="white")
    ax2.set_xlabel("Distance (m)", color=_TICK_COLOR)
    ax2.legend(facecolor="#2d2d44", labelcolor="white", fontsize=8)

    # ── Panel 3: cumulative delta time ─────────────────────────────────────
    ax3 = axes[1, 0]
    dt = result.delta_time_cumulative
    ax3.plot(dist, dt, color="#ffd700", linewidth=2.0)
    ax3.axhline(0, color="#555577", linestyle="--", linewidth=1)
    ax3.fill_between(dist, dt, 0,
                     where=(dt > 0), alpha=0.4, color=_COLOR_ACTUAL, label="Losing time")
    ax3.fill_between(dist, dt, 0,
                     where=(dt <= 0), alpha=0.4, color="#66bb6a", label="Gaining time")
    final = float(dt[-1]) if len(dt) else 0.0
    ax3.text(0.98, 0.05, f"Final Δt: {final:+.3f}s",
             transform=ax3.transAxes, ha="right", color="white", fontsize=9)
    ax3.set_title("Cumulative Delta Time (s)", color="white")
    ax3.set_xlabel("Distance (m)", color=_TICK_COLOR)
    ax3.legend(facecolor="#2d2d44", labelcolor="white", fontsize=8)

    # ── Panel 4: lateral deviation ─────────────────────────────────────────
    ax4 = axes[1, 1]
    ld = result.lateral_deviation
    ax4.plot(dist, ld, color="#3498db", linewidth=1.5)
    ax4.axhline(0, color="#555577", linestyle="--", linewidth=1)
    ax4.fill_between(dist, ld, 0,
                     where=(ld > 0), alpha=0.35, color="#3498db", label="Left of ref")
    ax4.fill_between(dist, ld, 0,
                     where=(ld <= 0), alpha=0.35, color="#ffa726", label="Right of ref")
    ax4.set_title("Lateral Deviation from Reference (m)", color="white")
    ax4.set_xlabel("Distance (m)", color=_TICK_COLOR)
    ax4.legend(facecolor="#2d2d44", labelcolor="white", fontsize=8)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_DARK_BG)
    if show:
        plt.show()
    return fig
