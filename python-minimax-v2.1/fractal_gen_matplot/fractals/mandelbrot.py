"""
Mandelbrot set implementation.

This module provides a concrete implementation of the Mandelbrot fractal set,
one of the most famous and visually striking mathematical objects.
"""

import numpy as np
from typing import Tuple

from .base import FractalSet


class MandelbrotSet(FractalSet):
    """
    The Mandelbrot set defined by z_{n+1} = z_n^2 + c.

    For each point c in the complex plane, we iterate starting from z_0 = 0
    and check if the sequence diverges to infinity.
    """

    def __init__(self, max_iterations: int = 256, escape_radius: float = 2.0):
        """
        Initialize the Mandelbrot set calculator.

        Args:
            max_iterations: Maximum iterations for escape time (default 256).
            escape_radius: Radius for divergence detection (default 2.0).
        """
        super().__init__(max_iterations, escape_radius)

    @property
    def name(self) -> str:
        return "Mandelbrot Set"

    def compute_fractal(
        self,
        x_min: float, x_max: float,
        y_min: float, y_max: float,
        width: int, height: int
    ) -> np.ndarray:
        """
        Compute Mandelbrot iteration counts for a grid of complex numbers.

        Args:
            x_min, x_max: Real part bounds (c.real).
            y_min, y_max: Imaginary part bounds (c.imag).
            width: Horizontal resolution.
            height: Vertical resolution.

        Returns:
            2D array where each value is the iteration count at which
            |z| exceeded escape_radius (or max_iterations if never escaped).
        """
        # Create coordinate grid in complex plane
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        # Use broadcasting to create meshgrid; transpose for correct orientation
        X, Y = np.meshgrid(x, y)
        c = X + 1j * Y

        # Initialize z at origin and iteration count array
        z = np.zeros_like(c)
        iterations = np.zeros(c.shape, dtype=np.uint16)

        # Track which points haven't escaped yet
        mask = np.ones(c.shape, dtype=bool)

        for i in range(self.max_iterations):
            # Only compute for points that haven't escaped
            if not np.any(mask):
                break

            # Update z: z = z^2 + c (vectorized)
            z[mask] = z[mask] * z[mask] + c[mask]

            # Check which have escaped this iteration
            escaped_now = mask & (np.abs(z) > self.escape_radius)

            if np.any(escaped_now):
                iterations[escaped_now] = i + 1

            # Update mask to exclude escaped points
            mask &= ~escaped_now

        # Points that never escaped get max_iterations
        iterations[mask] = self.max_iterations

        return iterations

    def _get_z_magnitudes(
        self,
        x_min: float, x_max: float,
        y_min: float, y_max: float,
        width: int, height: int
    ) -> np.ndarray:
        """
        Get the magnitude of z at escape for smooth coloring.

        For Mandelbrot, we need to recompute to track |z| values.
        This is a simplified version - a full implementation would cache these.
        """
        # Use default bounds if not provided
        if x_min is None or x_max is None:
            x_min, x_max, y_min, y_max = self.get_default_bounds()

        # Create coordinate grid
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        X, Y = np.meshgrid(x, y)
        c = X + 1j * Y

        z = np.zeros_like(c)
        magnitudes = np.ones(c.shape) * self.escape_radius
        mask = np.ones(c.shape, dtype=bool)

        for i in range(self.max_iterations):
            if not np.any(mask):
                break

            z[mask] = z[mask] * z[mask] + c[mask]
            mags = np.abs(z)
            escaped_now = mask & (mags > self.escape_radius)

            magnitudes[escaped_now] = mags[escaped_now]
            mask &= ~escaped_now

        return magnitudes

    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """
        Return sensible default bounds that show the full Mandelbrot set.

        The Mandelbrot set is contained within |c| <= 2, and typically
        centered around (-0.5, 0).
        """
        return -2.1, 0.8, -1.3, 1.3