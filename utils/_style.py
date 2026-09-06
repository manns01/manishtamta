"""Shared plotting style so both research animations read as one set.

Palette matches the website (navy / teal / burgundy on a warm off-white).
"""

import matplotlib as mpl

NAVY = "#1a3a52"
TEAL = "#2c7a7b"
BURGUNDY = "#8b3a3a"
INK = "#2d3748"
PAPER = "#fbfaf8"
GRID = "#e2ddd4"
MUTED = "#8a8175"

FPS = 30
DPI = 160
FIGSIZE = (8.0, 4.5)  # -> 1280 x 720 px at DPI = 160


def apply():
    mpl.rcParams.update(
        {
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
            "font.size": 11,
            "text.color": INK,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "axes.titlecolor": NAVY,
            "axes.linewidth": 1.0,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK,
            "ytick.labelcolor": INK,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "legend.frameon": False,
            "mathtext.fontset": "cm",
        }
    )
