"""
Classic Mandelbrot-style color maps.

These provide the traditional coloring often seen in fractal visualizations.
"""

import numpy as np
from .base import ContinuousColorMap


class ClassicMandelbrot(ContinuousColorMap):
    """
    The classic black-to-white gradient with smooth transitions.

    Often used for scientific visualization of iteration counts.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.0, 0.0, 0.0),       # Black inside set
                (0.1, 0.0, 0.2),       # Dark border
                (0.3, 0.1, 0.4),       # Purple mid
                (0.6, 0.3, 0.5),       # Pink-purple
                (1.0, 1.0, 1.0),       # White exterior
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Classic"


class StripedMap(ContinuousColorMap):
    """
    Banded color map for viewing iteration bands clearly.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.1, 0.05, 0.2),      # Dark purple
                (0.5, 0.3, 0.7),       # Light purple
                (0.9, 0.6, 0.4),       # Tan
                (0.95, 0.8, 0.2),      # Gold
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Banded"