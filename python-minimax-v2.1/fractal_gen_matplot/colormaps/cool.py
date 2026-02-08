"""
Cool color palettes: blues, greens, and nebula-like colors.
"""

import numpy as np
from .base import ContinuousColorMap


class CoolMap(ContinuousColorMap):
    """
    Cool blue-green palette: black -> cyan -> blue.

    Creates an icy, cold appearance.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.0, 0.0, 0.0),       # Black
                (0.0, 0.3, 0.4),       # Teal
                (0.0, 0.6, 0.8),       # Sky blue
                (0.5, 0.8, 1.0),       # Light blue
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Cool Blue"


class NebulaMap(ContinuousColorMap):
    """
    Nebula palette inspired by deep space imagery.

    Transitions from black through purple to pink to cyan.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.02, 0.02, 0.05),    # Deep space dark
                (0.2, 0.0, 0.3),       # Dark purple
                (0.6, 0.1, 0.4),       # Purple-pink
                (0.9, 0.5, 0.7),       # Pink
                (0.5, 0.8, 0.9),       # Cyan highlight
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Nebula"


class OceanMap(ContinuousColorMap):
    """
    Deep ocean colors: midnight blue to teal to foam white.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.0, 0.02, 0.1),      # Midnight
                (0.0, 0.2, 0.4),       # Deep blue
                (0.0, 0.5, 0.6),       # Teal
                (0.4, 0.8, 0.9),       # Foam
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Ocean"


class ForestMap(ContinuousColorMap):
    """
    Natural greens and earth tones.
    """

    def __init__(self, n_colors: int = 256):
        super().__init__(
            [
                (0.05, 0.1, 0.02),     # Dark forest
                (0.1, 0.3, 0.05),      # Forest green
                (0.4, 0.6, 0.2),       # Light green
                (0.9, 0.85, 0.5),      # Sunlight
            ],
            n_colors
        )

    @property
    def name(self) -> str:
        return "Forest"