"""Pytest configuration and shared fixtures.

Note: Run tests with targeted paths to avoid collection conflicts:
    python -m pytest fractal_gen_tk/tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pytest
from fractals import (
    Mandelbrot, Julia, Julia3, BurningShip, Collatz, Multibrot, Phoenix,
    FractalFactory
)


@pytest.fixture(params=[
    "Mandelbrot", "Julia", "Julia³", "Burning Ship", "Collatz", "Multibrot", "Phoenix"
])
def fractal_type(request):
    """Parametrize all fractal types."""
    return request.param


@pytest.fixture
def standard_meshgrid():
    """Standard meshgrid for testing."""
    x = np.linspace(-2, 1.5, 50)
    y = np.linspace(-1.5, 1.5, 40)
    return np.meshgrid(x, y)


@pytest.fixture
def all_fractals():
    """All fractal instances."""
    return {
        'mandelbrot': Mandelbrot(),
        'julia': Julia(),
        'julia3': Julia3(),
        'burning_ship': BurningShip(),
        'collatz': Collatz(),
        'multibrot': Multibrot(),
        'phoenix': Phoenix(),
    }