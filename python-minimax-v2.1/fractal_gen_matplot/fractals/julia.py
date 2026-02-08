"""
Julia set implementation - demonstrates adding new fractal types.

To add the JuliaSet, import it in colormaps/__init__.py and fractals/__init__.py:

    from .julia import JuliaSet

Then use it like any other fractal:
    
    explorer = FractalExplorer(fractal_set=JuliaSet(c=-0.7+0.27015j))
"""

import numpy as np
from typing import Tuple, Optional
from .base import FractalSet


class JuliaSet(FractalSet):
    """
    The Julia set for a given constant c in the complex plane.

    For each point z₀ in the grid, we iterate z_{n+1} = z_n² + c and check
    if it escapes to infinity. Different values of c produce different shapes.
    
    Common interesting values:
    - c = -0.7 + 0.27015j: The "Douady's rabbit" fractal
    - c = -0.7269 + 0.1889j: Another classic shape  
    - c = -0.835 - 0.2321j: "Dendrite"
    - c = -0.8 + 0.156j: Interesting connected set
    """

    def __init__(
        self,
        c: complex = None,
        max_iterations: int = 256,
        escape_radius: float = 2.0
    ):
        """
        Initialize the Julia set calculator.

        Args:
            c: Complex constant defining the Julia set (default -0.7+0.27015j).
            max_iterations: Maximum iterations for escape time.
            escape_radius: Radius for divergence detection.
        """
        super().__init__(max_iterations, escape_radius)
        # Default to Douady's rabbit
        self.c = c if c is not None else -0.7 + 0.27015j

    @property
    def name(self) -> str:
        return f"Julia Set (c={self.c})"

    def compute_fractal(
        self,
        x_min: float, x_max: float,
        y_min: float, y_max: float,
        width: int, height: int
    ) -> np.ndarray:
        """
        Compute Julia set iteration counts for a grid of starting points z₀.

        Args:
            x_min, x_max: Real part bounds (z₀.real).
            y_min, y_max: Imaginary part bounds (z₀.imag).
            width, height: Resolution.

        Returns:
            2D array where each value is the iteration count at escape.
        """
        # Create coordinate grid
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        X, Y = np.meshgrid(x, y)
        z = X + 1j * Y

        iterations = np.zeros(z.shape, dtype=np.uint16)
        mask = np.ones(z.shape, dtype=bool)

        for i in range(self.max_iterations):
            if not np.any(mask):
                break

            # z = z² + c
            z[mask] = z[mask] * z[mask] + self.c

            escaped_now = mask & (np.abs(z) > self.escape_radius)
            iterations[escaped_now] = i + 1
            mask &= ~escaped_now

        iterations[mask] = self.max_iterations

        return iterations

    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Default bounds showing the main structure."""
        # Julia sets are typically viewed in a smaller region
        return -1.8, 1.8, -1.4, 1.4


class BurningShipJuliaSet(JuliaSet):
    """
    A variant combining the Burning Ship with Julia set iterations.

    Uses absolute value (abs(z)² + c), creating dramatic "ship" shapes.
    """

    def __init__(
        self,
        c: complex = None,
        max_iterations: int = 256,
        escape_radius: float = 2.0
    ):
        # Default to an interesting shape
        super().__init__(c or -0.4 + 0.6j, max_iterations, escape_radius)

    @property
    def name(self) -> str:
        return f"Burning Ship Julia (c={self.c})"

    def compute_fractal(
        self,
        x_min: float, x_max: float,
        y_min: float, y_max: float,
        width: int, height: int
    ) -> np.ndarray:
        """Compute with absolute value applied."""
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        X, Y = np.meshgrid(x, y)
        z = X + 1j * Y

        iterations = np.zeros(z.shape, dtype=np.uint16)
        mask = np.ones(z.shape, dtype=bool)

        for i in range(self.max_iterations):
            if not np.any(mask):
                break

            # Use absolute value of real and imaginary parts (Burning Ship twist)
            z_real = np.abs(np.real(z[mask]))
            z_imag = np.imag(z[mask])
            combined = z_real + 1j * z_imag
            z[mask] = combined * combined + self.c

            escaped_now = mask & (np.abs(z) > self.escape_radius)
            iterations[escaped_now] = i + 1
            mask &= ~escaped_now

        iterations[mask] = self.max_iterations

        return iterations