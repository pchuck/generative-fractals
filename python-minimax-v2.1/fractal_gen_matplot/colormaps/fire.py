"""
Fire and warm color palettes for dramatic fractal visualization.
"""

import numpy as np
from .base import ContinuousColorMap


class FireMap(ContinuousColorMap):
    """
    Classic fire palette: black -> red -> orange -> yellow -> white.

    Creates a dramatic, fiery appearance with bright hot regions.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.0, 0.0, 0.0),       # Black
                (0.5, 0.0, 0.1),       # Dark red
                (0.9, 0.2, 0.0),       # Orange-red
                (1.0, 0.7, 0.0),       # Yellow-orange
                (1.0, 0.95, 0.8),      # White-yellow
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Fire"


class MagmaMap(ContinuousColorMap):
    """
    Magma/inferno palette inspired by popular scientific visualization.

    Transitions from black through purple, red, orange to yellow-white.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.0, 0.0, 0.1),       # Near black
                (0.2, 0.0, 0.3),       # Deep purple
                (0.8, 0.2, 0.2),       # Red
                (1.0, 0.6, 0.1),       # Orange-gold
                (1.0, 1.0, 1.0),       # White
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Magma"


class InfernoMap(ContinuousColorMap):
    """
    Deep inferno palette: black to purple to bright yellow.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.0, 0.0, 0.0),       # Black
                (0.1, 0.0, 0.2),       # Very dark purple
                (0.3, 0.0, 0.4),       # Purple
                (0.9, 0.5, 0.0),       # Orange
                (1.0, 0.9, 0.1),       # Yellow-white
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Inferno"