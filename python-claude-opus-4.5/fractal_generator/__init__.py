"""
Fractal Generator - An interactive fractal explorer.

This package provides a modular fractal rendering application with:
- Multiple fractal types (Mandelbrot, Julia, Multibrot, Burning Ship, Phoenix)
- Customizable color palettes
- Interactive zoom functionality
- Sequential and parallel rendering support
- Session state preservation
"""

from .fractals import FractalType, FractalFactory
from .palettes import PaletteFactory
from .renderer import FractalRenderer
from .state import SessionState, FractalState, ViewState, ZoomHistory
from .app import FractalApp, main

__all__ = [
    'FractalType',
    'FractalFactory',
    'PaletteFactory',
    'FractalRenderer',
    'SessionState',
    'FractalState',
    'ViewState',
    'ZoomHistory',
    'FractalApp',
    'main',
]

__version__ = '1.0.0'
