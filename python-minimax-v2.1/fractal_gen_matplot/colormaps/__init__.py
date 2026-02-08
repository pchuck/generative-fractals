"""
Colormap package - contains various color mapping strategies.

Each colormap is a callable that takes normalized values and returns RGB colors,
making them easy to swap and extend.
"""

from .base import ColorMap
from .grayscale import GrayscaleMap
from .fire import FireMap
from .cool import CoolMap, NebulaMap
from .rainbow import RainbowMap
from .classic import ClassicMandelbrot

__all__ = [
    'ColorMap',
    'GrayscaleMap',
    'FireMap',
    'CoolMap',
    'NebulaMap',
    'RainbowMap',
    'ClassicMandelbrot',
]