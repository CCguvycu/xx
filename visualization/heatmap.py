from __future__ import annotations

from typing import List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize

from core.models import TelemetryPoint

_DARK_BG = "#1a1a2e"
_DARK_PANEL = "#0f0f23"
_TICK_COLOR = "#aaaaaa"


def plot_speed_heatmap(
    points: List[TelemetryPoint],
    title: str = "Speed Heatmap",
    show: bool = True,
    save_path: Optional[str] = None,
) -> matplotlib.figure.Figure:
    """Colour-coded speed trace on a 2D track map using LineCollection."""
    coords = np.array([[p.x, p.y] for p in points])
    speeds = np.array([p.speed for p in points])

    # Build (N-1, 2, 2) segment array for LineCollection.
    segments = np.stack([coords[:-1], coords[1:]], axis=1)
    seg_speeds = (speeds[:-1] + speeds[1:]) * 0.5

    norm = Normalize(vmin=speeds.min(), vmax=speeds.max())
    lc = LineCollection(segments, cmap="RdYlGn", norm=norm, linewidth=3, alpha=0.9)
    lc.set_array(seg_speeds)

    fig, ax = plt.subplots(figsize=(12, 8), facecolor=_DARK_BG)
    ax.set_facecolor(_DARK_PANEL)
    ax.add_collection(lc)

    pad = 10
    ax.set_xlim(coords[:, 0].min() - pad, coords[:, 0].max() + pad)
    ax.set_ylim(coords[:, 1].min() - pad, coords[:, 1].max() + pad)

    cbar = fig.colorbar(lc, ax=ax, pad=0.02)
    cbar.set_label("Speed (m/s)", color="white")
    cbar.ax.yaxis.set_tick_params(color=_TICK_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

    _style_ax(ax, title)
    ax.set_aspect("equal")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_DARK_BG)
    if show:
        plt.show()
    return fig


def plot_braking_zones(
    points: List[TelemetryPoint],
    threshold: float = 0.1,
    title: str = "Braking Zones",
    show: bool = True,
    save_path: Optional[str] = None,
) -> matplotlib.figure.Figure:
    """Scatter of points where brake > threshold, coloured by intensity."""
    coords = np.array([[p.x, p.y] for p in points])
    brakes = np.array([p.brake for p in points])
    mask = brakes > threshold

    fig, ax = plt.subplots(figsize=(12, 8), facecolor=_DARK_BG)
    ax.set_facecolor(_DARK_PANEL)

    # Full track outline.
    ax.plot(coords[:, 0], coords[:, 1], color="#444466", linewidth=1.5, alpha=0.5)

    if mask.any():
        sc = ax.scatter(
            coords[mask, 0], coords[mask, 1],
            c=brakes[mask], cmap="Reds",
            vmin=threshold, vmax=1.0,
            s=brakes[mask] * 60, zorder=4, alpha=0.85,
        )
        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        cbar.set_label("Brake Pressure", color="white")
        cbar.ax.yaxis.set_tick_params(color=_TICK_COLOR)
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

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
