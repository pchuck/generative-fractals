"""
Grayscale and simple color maps.
"""

import numpy as np
from .base import ContinuousColorMap


class GrayscaleMap(ContinuousColorMap):
    """
    Simple grayscale gradient from black to white.

    Useful for pure iteration count visualization without color bias.
    """

    def __init__(self, n_colors: int = 256):
        """Initialize with black to white gradient."""
        super().__init__([(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)], n_colors)

    @property
    def name(self) -> str:
        return "Grayscale"


class InvertedGrayscaleMap(ContinuousColorMap):
    """
    Inverted grayscale gradient from white to black.

    Useful for dark backgrounds with bright fractal interiors.
    """

    def __init__(self, n_colors: int = 256):
        """Initialize with white to black gradient."""
        super().__init__([(1.0, 1.0, 1.0), (0.0, 0.0, 0.0)], n_colors)

    @property
    def name(self) -> str:
        return "Inverted Grayscale"


class SepiaMap(ContinuousColorMap):
    """
    Warm sepia tones for a classic look.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.1, 0.05, 0.03),   # Dark brown
                (0.8, 0.7, 0.5),     # Light tan
                (1.0, 0.95, 0.8),    # Cream white
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Sepia"