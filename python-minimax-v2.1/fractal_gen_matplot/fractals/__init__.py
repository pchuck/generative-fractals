"""
Fractal package - contains fractal set implementations.
"""

from .base import FractalSet
from .mandelbrot import MandelbrotSet
from .julia import JuliaSet, BurningShipJuliaSet

__all__ = ['FractalSet', 'MandelbrotSet', 'JuliaSet', 'BurningShipJuliaSet']