"""Tests for main_refactored.py utilities.

Run with: python -m pytest tests/ -v
"""

import pytest
from main_refactored import _camel_to_snake


class TestCamelToSnake:
    """Tests for the CamelCase to snake_case converter."""
    
    def test_mandelbrot(self):
        assert _camel_to_snake("Mandelbrot") == "mandelbrot"
    
    def test_julia3(self):
        assert _camel_to_snake("Julia3") == "julia3"
    
    def test_burning_ship(self):
        assert _camel_to_snake("BurningShip") == "burning_ship"
    
    def test_collatz(self):
        assert _camel_to_snake("Collatz") == "collatz"
    
    def test_multibrot(self):
        assert _camel_to_snake("Multibrot") == "multibrot"
    
    def test_phoenix(self):
        assert _camel_to_snake("Phoenix") == "phoenix"


class TestDefaultBounds:
    """Tests for DEFAULT_BOUNDS lookup."""
    
    @pytest.fixture
    def app_class(self):
        """Import FractalApp to access DEFAULT_BOUNDS."""
        from main_refactored import FractalApp
        return FractalApp
    
    def test_all_fractals_have_bounds(self, app_class):
        """All registered fractal types should have bounds defined."""
        from fractals import (
            Mandelbrot, Julia, Julia3, BurningShip,
            Collatz, Multibrot, Phoenix
        )
        
        for cls in [Mandelbrot, Julia, Julia3, BurningShip, Collatz, Multibrot, Phoenix]:
            key = _camel_to_snake(cls.__name__)
            assert key in app_class.DEFAULT_BOUNDS, f"{cls.__name__} missing bounds"
    
    def test_bounds_lookup_returns_tuple(self, app_class):
        """DEFAULT_BOUNDS values should be 4-tuples of floats."""
        for bounds in app_class.DEFAULT_BOUNDS.values():
            assert isinstance(bounds, tuple)
            assert len(bounds) == 4
            x_min, x_max, y_min, y_max = bounds
            assert isinstance(x_min, (int, float))
            assert isinstance(x_max, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])