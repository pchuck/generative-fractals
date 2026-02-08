"""
Rainbow and multi-color palettes.
"""

import numpy as np
from .base import ContinuousColorMap


class RainbowMap(ContinuousColorMap):
    """
    Classic rainbow spectrum.

    Cycles through the visible spectrum for maximum color variety.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (1.0, 0.0, 0.0),       # Red
                (1.0, 1.0, 0.0),       # Yellow
                (0.0, 1.0, 0.0),       # Green
                (0.0, 1.0, 1.0),       # Cyan
                (0.0, 0.0, 1.0),       # Blue
                (1.0, 0.0, 1.0),       # Magenta
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Rainbow"


class TurboMap(ContinuousColorMap):
    """
    Turbo rainbow - a perceptually-uniform rainbow colormap.

    Based on the "Turbo" colormap designed for better perceptual uniformity.
    """

    def __init__(self, n_colors: int = 256):
        # Approximate turbo palette
        super().__init__(
            [
                (0.1, 0.05, 0.3),      # Dark blue-purple
                (0.2, 0.5, 1.0),       # Blue-cyan
                (0.4, 0.9, 0.6),       # Green
                (0.9, 0.9, 0.0),       # Yellow
                (1.0, 0.4, 0.0),       # Orange
                (0.5, 0.05, 0.2),      # Red-purple
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Turbo Rainbow"


class PastelMap(ContinuousColorMap):
    """
    Soft pastel rainbow for gentle visualization.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.6, 0.2, 0.4),       # Muted red
                (0.9, 0.5, 0.3),       # Peach
                (0.7, 0.8, 0.4),       # Yellow-green
                (0.4, 0.7, 0.7),       # Teal
                (0.5, 0.4, 0.7),       # Lavender
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Pastel"