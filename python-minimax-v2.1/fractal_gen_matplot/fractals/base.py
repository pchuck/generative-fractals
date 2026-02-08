"""
Base class for fractal sets.

This module defines the abstract base class that all fractal set implementations
must inherit from. It provides a common interface for computing fractal values
and ensures consistent behavior across different fractal types.
"""

from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np


class FractalSet(ABC):
    """
    Abstract base class for fractal sets.

    Subclasses must implement the compute_fractal method to define how
    the fractal values are computed for each point in a grid.

    Attributes:
        max_iterations: Maximum number of iterations for escape time algorithms.
        escape_radius: Radius at which points are considered to have escaped.
    """

    def __init__(self, max_iterations: int = 256, escape_radius: float = 2.0):
        """
        Initialize the fractal set.

        Args:
            max_iterations: Maximum iterations for escape time (default 256).
            escape_radius: Escape radius for determining divergence (default 2.0).
        """
        self.max_iterations = max_iterations
        self.escape_radius = escape_radius

    @abstractmethod
    def compute_fractal(
        self,
        x_min: float, x_max: float,
        y_min: float, y_max: float,
        width: int, height: int
    ) -> np.ndarray:
        """
        Compute fractal values over a 2D grid.

        Args:
            x_min, x_max: X-axis bounds (real part for complex numbers).
            y_min, y_max: Y-axis bounds (imaginary part for complex numbers).
            width: Number of pixels horizontally.
            height: Number of pixels vertically.

        Returns:
            2D array of shape (height, width) containing fractal values
            (typically iteration counts at escape or max iterations).
        """
        pass

    def compute_smooth_color(
        self,
        fractal_values: np.ndarray,
        x_min: float = None, x_max: float = None,
        y_min: float = None, y_max: float = None
    ) -> np.ndarray:
        """
        Compute smooth coloring values for better visual representation.

        Uses the formula: iterations + 1 - log(log(|z|)) / log(2)
        to create smooth transitions between iteration counts.

        Args:
            fractal_values: Array of raw iteration counts from compute_fractal.
            x_min, x_max, y_min, y_max: Unused in default implementation,
                included for potential subclass overrides.

        Returns:
            Smoothed values normalized for colormap application.
        """
        import warnings
        # Get the actual iteration count (non-escaped points have max_iterations)
        escaped = fractal_values < self.max_iterations

        if not np.any(escaped):
            return fractal_values.astype(float)

        smooth = np.zeros_like(fractal_values, dtype=float)

        # For non-escaped points
        mask_escaped = escaped & (fractal_values > 0)
        if np.any(mask_escaped):
            z_magnitudes = self._get_z_magnitudes(
                x_min, x_max, y_min, y_max,
                fractal_values.shape[1], fractal_values.shape[0]
            )
            # Add small epsilon to avoid log(1) = 0 and log(<=0)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                smooth_vals = (
                    fractal_values[mask_escaped]
                    - np.log2(np.log(z_magnitudes[mask_escaped] + 1e-10))
                )
                # Clamp to valid range
                smooth_vals = np.clip(smooth_vals, 0.5, self.max_iterations)
            smooth[mask_escaped] = smooth_vals

        # Points that didn't escape get max value (slightly below for visual effect)
        smooth[~escaped] = self.max_iterations - 0.1

        return smooth

    def _get_z_magnitudes(
        self,
        x_min: float, x_max: float,
        y_min: float, y_max: float,
        width: int, height: int
    ) -> np.ndarray:
        """
        Get the magnitude of z at escape for each pixel.

        Subclasses can override this if they track magnitudes during computation.
        Default returns zeros (subclasses should implement proper tracking).
        """
        return np.zeros((height, width))

    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Return default bounds for initial view. Override in subclasses."""
        return -2.0, 2.0, -1.5, 1.5

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of this fractal set."""
        pass