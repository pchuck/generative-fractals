"""
Helper utilities for creating and managing color maps.

This module provides convenient functions for quickly adding new colormap styles.
"""

import numpy as np

from colormaps.base import ContinuousColorMap, ProceduralColorMap


def simple_gradient(
    colors: list,
    n_colors: int = 256
) -> ContinuousColorMap:
    """
    Create a simple gradient colormap from a list of RGB colors.

    Args:
        colors: List of (r, g, b) tuples in [0, 1].
        n_colors: Number of discrete color steps.

    Returns:
        A ContinuousColorMap instance ready to use.

    Example:
        >>> cmap = simple_gradient([(0, 0, 0), (1, 0.5, 0), (1, 1, 1)])
        >>> image = cmap(fractal_values)
    """
    return ContinuousColorMap(colors, n_colors)


def cyclic_rainbow(n_colors: int = 360) -> ProceduralColorMap:
    """Create a rainbow colormap that wraps around smoothly."""

    class CyclicRainbow(ProceduralColorMap):
        def _generate_lut(self):
            lut = np.zeros((self.n_colors, 3))
            for i in range(self.n_colors):
                hue = (i / self.n_colors) * 6.28318530718
                # Convert HSV to RGB (simplified)
                r = abs(np.sin(hue)) ** 0.5
                g = abs(np.sin(hue + 2.094)) ** 0.5
                b = abs(np.sin(hue + 4.188)) ** 0.5
                lut[i] = [r, g, b]
            return lut

        @property
        def name(self):
            return "Cyclic Rainbow"

    return CyclicRainbow(n_colors)


def plasma_like(n_colors: int = 256) -> ProceduralColorMap:
    """Create a colormap similar to matplotlib's 'plasma'."""

    class PlasmaLike(ProceduralColorMap):
        def _generate_lut(self):
            lut = np.zeros((self.n_colors, 3))
            for i in range(self.n_colors):
                t = i / (self.n_colors - 1)
                # Approximate plasma colors
                if t < 0.33:
                    r = 0.2 + 1.5 * t / 0.33
                    g = 0.1
                    b = 0.8 - 0.6 * t / 0.33
                elif t < 0.66:
                    t_adj = (t - 0.33) / 0.33
                    r = 1.7 - 0.9 * t_adj
                    g = 0.2 + 0.8 * t_adj
                    b = 0.2 + 0.4 * t_adj
                else:
                    t_adj = (t - 0.66) / 0.34
                    r = 0.8 - 0.6 * t_adj
                    g = 1.0 - 0.3 * t_adj
                    b = 0.6 + 0.4 * t_adj

                lut[i] = [r, g, b]
            return lut

        @property
        def name(self):
            return "Plasma-like"

    return PlasmaLike(n_colors)


# Pre-made popular color schemes for quick use
POPULAR_MAPS = {
    'electric': lambda: simple_gradient([
        (0.0, 0.0, 0.1),
        (0.0, 0.2, 0.8),
        (0.0, 0.8, 1.0),
        (1.0, 1.0, 1.0)
    ]),
    'sunset': lambda: simple_gradient([
        (0.1, 0.05, 0.2),
        (0.6, 0.1, 0.3),
        (0.9, 0.4, 0.2),
        (1.0, 0.8, 0.4)
    ]),
    'matrix': lambda: simple_gradient([
        (0.0, 0.15, 0.05),
        (0.0, 0.35, 0.1),
        (0.2, 0.7, 0.3),
        (0.8, 1.0, 0.6)
    ]),
}


def register_custom_map(name: str, colormap):
    """Register a custom colormap globally."""
    global POPULAR_MAPS
    POPULAR_MAPS[name] = colormap


# Example of adding a new colormap to the application:
#
# from app import FractalExplorer
# from utils.colormaps import electric
#
# explorer = FractalExplorer()
# explorer.colormaps['Electric'] = (electric(), True)
# # Need to also update the radio button - see app.py for details