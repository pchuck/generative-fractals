"""
Base class for color maps.

This module defines the abstract interface that all colormap implementations
must follow, ensuring consistent behavior and easy extensibility.
"""

from abc import ABC, abstractmethod
import numpy as np


class ColorMap(ABC):
    """
    Abstract base class for fractal color maps.

    Color maps convert normalized fractal values (typically 0 to max_iterations)
    into RGB colors. Subclasses can implement specific coloring algorithms.

    The colormap should handle:
    - Normalized input in [0, 1] range
    - Interpolation between colors or algorithmic generation
    - Return values as float arrays in [0, 1] range for each RGB channel
    """

    @abstractmethod
    def __call__(self, values: np.ndarray) -> np.ndarray:
        """
        Convert normalized fractal values to RGB colors.

        Args:
            values: 2D array of normalized values (typically from 0 to 1).

        Returns:
            3D array of shape (height, width, 3) with RGB values in [0, 1].
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of this colormap."""
        pass


class ContinuousColorMap(ColorMap):
    """
    Base class for continuous color maps using linear interpolation.

    Subclasses define a list of control points (colors at specific positions),
    and this class handles smooth interpolation between them.
    """

    def __init__(self, colors: list, n_colors: int = 256):
        """
        Initialize with a list of RGB color tuples.

        Args:
            colors: List of (r, g, b) tuples in [0, 1].
            n_colors: Number of discrete colors to interpolate between control points.
        """
        self.colors = np.array(colors)
        self.n_colors = n_colors
        # Pre-compute the color lookup table
        self._lut = self._build_lookup_table()

    def _build_lookup_table(self) -> np.ndarray:
        """Build a linear interpolation table from control colors."""
        n_control = len(self.colors)

        if n_control < 2:
            raise ValueError("At least 2 colors required for interpolation")

        # Create evenly spaced indices and interpolate
        indices = np.linspace(0, n_control - 1, self.n_colors)
        lower_idx = np.floor(indices).astype(int)
        upper_idx = np.ceil(indices).astype(int)

        t = indices - lower_idx

        lut = (1 - t)[:, None] * self.colors[lower_idx] + t[:, None] * self.colors[upper_idx]

        return lut

    def __call__(self, values: np.ndarray) -> np.ndarray:
        """
        Apply the colormap to normalized values.

        Args:
            values: 2D array of floats in [0, max_iterations].

        Returns:
            RGB image as (height, width, 3) float array.
        """
        # Handle edge cases
        max_val = values.max()
        if np.isnan(max_val) or max_val <= 0:
            # Return black for invalid input
            return np.zeros((*values.shape, 3))

        # Normalize values to [0, n_colors-1]
        normalized = np.clip(values / max_val, 0, 1)
        indices = (normalized * (self.n_colors - 1)).astype(np.int64)

        # Clip indices to valid range
        indices = np.clip(indices, 0, self.n_colors - 1)

        # Look up colors
        result = self._lut[indices]

        return result

    @property
    def name(self) -> str:
        """Return class name by default."""
        return type(self).__name__


class ProceduralColorMap(ColorMap):
    """
    Base class for programmatically generated color maps.

    Subclasses implement a method to generate colors algorithmically,
    useful for mathematical or procedural patterns.
    """

    def __init__(self, n_colors: int = 256):
        """Initialize with desired number of output colors."""
        self.n_colors = n_colors
        self._lut = None

    @abstractmethod
    def _generate_lut(self) -> np.ndarray:
        """
        Generate the color lookup table.

        Returns:
            Array of shape (n_colors, 3) with RGB values.
        """
        pass

    def __call__(self, values: np.ndarray) -> np.ndarray:
        """Apply procedural coloring to normalized values."""
        if self._lut is None:
            self._lut = self._generate_lut()

        # Normalize and look up
        max_val = values.max() if values.max() > 0 else 1
        normalized = np.clip(values / max_val, 0, 1)
        indices = (normalized * (self.n_colors - 1)).astype(int)

        return self._lut[indices]

    @property
    def name(self) -> str:
        return type(self).__name__