"""
Fractal Generator Package

A modular interactive fractal generator using Python Tkinter.

Modules:
- fractals: Fractal type implementations (Mandelbrot, Julia sets, etc.)
- palettes: Color palette definitions
- main: Main application with UI
"""

from .fractals import FractalFactory
from .palettes import PaletteFactory

__all__ = ['FractalFactory', 'PaletteFactory']