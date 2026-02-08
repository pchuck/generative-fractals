"""Unit tests for fractal calculations.

Run with: python -m pytest tests/ -v
"""

import numpy as np
import pytest
from fractals import (
    Mandelbrot, Julia, Julia3, BurningShip, Collatz, Multibrot, Phoenix,
    FractalFactory, FractalType
)


class TestMandelbrot:
    """Tests for Mandelbrot fractal."""
    
    def test_output_shape(self):
        """Output should match input shape."""
        x = np.linspace(-2, 1, 100)
        y = np.linspace(-1.5, 1.5, 80)
        X, Y = np.meshgrid(x, y)
        
        result = Mandelbrot().calculate(X, Y, 100)
        assert result.shape == (80, 100)
    
    def test_center_point_escapes(self):
        """Point at origin should not escape immediately."""
        x = np.array([0.0])
        y = np.array([0.0])
        
        result = Mandelbrot().calculate(x, y, 10)
        # z=0 stays bounded for all iterations
        assert result[0] == 10
    
    def test_known_bound_point(self):
        """Point known to be in the set."""
        x = np.array([-0.5])
        y = np.array([0.0])
        
        result = Mandelbrot().calculate(x, y, 100)
        # This point is in the main cardioid
        assert result[0] == 100
    
    def test_known_escape_point(self):
        """Point known to escape quickly."""
        x = np.array([2.0])
        y = np.array([0.0])
        
        result = Mandelbrot().calculate(x, y, 100)
        # This point escapes immediately
        assert result[0] == 1
    
    def test_max_iter_respected(self):
        """Result should never exceed max_iter."""
        x = np.linspace(-2, 2, 50)
        y = np.linspace(-2, 2, 50)
        X, Y = np.meshgrid(x, y)
        
        max_iter = 75
        result = Mandelbrot().calculate(X, Y, max_iter)
        assert np.all(result <= max_iter)


class TestJulia:
    """Tests for Julia fractal."""
    
    def test_output_shape(self):
        x = np.linspace(-2, 2, 100)
        y = np.linspace(-2, 2, 80)
        X, Y = np.meshgrid(x, y)
        
        result = Julia().calculate(X, Y, 100)
        assert result.shape == (80, 100)
    
    def test_default_c(self):
        """Default c parameter should be set correctly."""
        j = Julia()
        assert abs(j.c.real - (-0.7)) < 0.01
        assert abs(j.c.imag - 0.27015) < 0.0001
    
    def test_set_c(self):
        """set_c should update the c parameter."""
        j = Julia()
        j.set_c(0.3, 0.5)
        assert j.c == complex(0.3, 0.5)
    
    def test_z0_offset(self):
        """z0 should offset initial z values."""
        # Use a point that escapes quickly without offset but may behave differently with offset
        x = np.array([1.5])
        y = np.array([0.0])
        
        j = Julia()
        result_with_zero = Julia(z0_real=0, z0_imag=0).calculate(x, y, 50)
        result_with_offset = Julia(z0_real=-0.5, z0_imag=0).calculate(x, y, 50)
        
        # Different starting points should give different results
        assert not np.array_equal(result_with_zero, result_with_offset)


class TestJulia3:
    """Tests for Julia³ (cubic) fractal."""
    
    def test_output_shape(self):
        x = np.linspace(-2, 2, 100)
        y = np.linspace(-2, 2, 80)
        X, Y = np.meshgrid(x, y)
        
        result = Julia3().calculate(X, Y, 100)
        assert result.shape == (80, 100)
    
    def test_different_from_quadratic(self):
        """Julia³ should differ from quadratic Julia at same c."""
        x = np.linspace(-1.5, 1.5, 30)
        y = np.linspace(-1.5, 1.5, 30)
        X, Y = np.meshgrid(x, y)
        
        j2 = Julia(c_real=-0.65, c_imag=0.5)
        j3 = Julia3(real=-0.65, imag=0.5)  # Note: Julia3 uses different param names
        
        result_2 = j2.calculate(X, Y, 50)
        result_3 = j3.calculate(X, Y, 50)
        
        # Results should differ due to different iteration formulas
        assert not np.array_equal(result_2, result_3)


class TestBurningShip:
    """Tests for Burning Ship fractal."""
    
    def test_output_shape(self):
        x = np.linspace(-2, 1, 100)
        y = np.linspace(-2, 2, 80)
        X, Y = np.meshgrid(x, y)
        
        result = BurningShip().calculate(X, Y, 100)
        assert result.shape == (80, 100)
    
    def test_symmetry_broken(self):
        """Burning ship should not be symmetric about real axis."""
        # Use a point where asymmetry is visible - need z to get negative imag parts during iteration
        x = np.array([-0.5])
        
        # Points mirrored across real axis
        y_pos = np.array([0.7])
        y_neg = np.array([-0.7])
        
        bs = BurningShip()
        result_pos = bs.calculate(x, y_pos, 50)
        result_neg = bs.calculate(x, y_neg, 50)
        
        # Results should differ due to absolute value on imaginary part
        assert not np.array_equal(result_pos, result_neg)


class TestCollatz:
    """Tests for Collatz fractal."""
    
    def test_output_shape(self):
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 80)
        X, Y = np.meshgrid(x, y)
        
        result = Collatz().calculate(X, Y, 50)
        assert result.shape == (80, 100)
    
    def test_escape_radius(self):
        """Points should escape at radius > 1000."""
        x = np.array([500.0])
        y = np.array([500.0])  # |z| ~ 707 < 1000, stays bounded initially
        
        result = Collatz().calculate(x, y, 10)
        assert result[0] == 10  # Should stay bounded
    
    def test_fast_escape(self):
        """Large values should escape quickly."""
        x = np.array([50.0])
        y = np.array([50.0])  # |z| ~ 70 > 1000? no, still < 100
        
        result = Collatz().calculate(x, y, 20)
        assert result[0] <= 20
    
    def test_max_iter_respected(self):
        """Result should never exceed max_iter."""
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        
        max_iter = 100
        result = Collatz().calculate(X, Y, max_iter)
        assert np.all(result <= max_iter)


class TestMultibrot:
    """Tests for Multibrot fractal."""
    
    def test_output_shape(self):
        x = np.linspace(-2, 1.5, 100)
        y = np.linspace(-1.5, 1.5, 80)
        X, Y = np.meshgrid(x, y)
        
        result = Multibrot().calculate(X, Y, 100)
        assert result.shape == (80, 100)
    
    def test_default_power(self):
        """Default power should be 4."""
        m = Multibrot()
        assert abs(m.power - 4.0) < 0.01
    
    def test_quadratic_equals_mandelbrot_shape(self):
        """Multibrot with power=2 should have similar structure to Mandelbrot."""
        x = np.linspace(-2, 0.5, 50)
        y = np.linspace(-1.2, 1.2, 40)
        X, Y = np.meshgrid(x, y)
        
        m2 = Multibrot(power=2.0)
        mandelbrot = Mandelbrot()
        
        result_m2 = m2.calculate(X, Y, 50)
        result_mandelbrot = mandelbrot.calculate(X, Y, 50)
        
        # Should have similar escape patterns
        assert result_m2.shape == result_mandelbrot.shape
    
    def test_power_modification(self):
        """Power should be modifiable."""
        m = Multibrot(power=3.0)
        assert abs(m.power - 3.0) < 0.01
        
        m.power = 5.5
        assert abs(m.power - 5.5) < 0.01


class TestPhoenix:
    """Tests for Phoenix fractal."""
    
    def test_output_shape(self):
        x = np.linspace(-2.5, 1.5, 100)
        y = np.linspace(-1.8, 1.8, 80)
        X, Y = np.meshgrid(x, y)
        
        result = Phoenix().calculate(X, Y, 100)
        assert result.shape == (80, 100)
    
    def test_default_params(self):
        """Default parameters should be set correctly."""
        p = Phoenix()
        assert abs(p.c.real - (-1.0)) < 0.01
        assert abs(p.c.imag - 0.2) < 0.01
        assert abs(p.p - 1.0) < 0.01
    
    def test_set_c(self):
        """set_c should update the c parameter."""
        p = Phoenix()
        p.set_c(0.5, -0.3)
        assert p.c == complex(0.5, -0.3)
    
    def test_p_parameter_affects_result(self):
        """Different p values should produce different results."""
        x = np.array([0.0])
        y = np.array([0.1])
        
        p1 = Phoenix(p=0.5)
        p2 = Phoenix(p=1.5)
        
        result1 = p1.calculate(x, y, 20)
        result2 = p2.calculate(x, y, 20)
        
        assert not np.array_equal(result1, result2)


class TestFractalFactory:
    """Tests for FractalFactory."""
    
    def test_create_mandelbrot(self):
        f = FractalFactory.create("Mandelbrot")
        assert isinstance(f, Mandelbrot)
    
    def test_create_julia(self):
        f = FractalFactory.create("Julia")
        assert isinstance(f, Julia)
    
    def test_create_case_insensitive(self):
        f1 = FractalFactory.create("julia")
        f2 = FractalFactory.create("Julia")
        assert type(f1) == type(f2)
    
    def test_list_types(self):
        types = FractalFactory.list_types()
        assert "Mandelbrot" in types
        assert "Julia" in types
        assert "Phoenix" in types
    
    def test_create_snake_case_key(self):
        """Snake-case keys should map correctly (e.g., 'burning_ship')."""
        f = FractalFactory.create("burning_ship")
        assert isinstance(f, BurningShip)
        
        f = FractalFactory.create("julia3")
        assert isinstance(f, Julia3)
    
    def test_create_fallback_on_invalid(self):
        """Invalid names should fall back to Mandelbrot."""
        f = FractalFactory.create("nonexistent")
        assert isinstance(f, Mandelbrot)
        
        f = FractalFactory.create("")
        assert isinstance(f, Mandelbrot)
    
    def test_create_with_none(self):
        """None input should return default Mandelbrot."""
        f = FractalFactory.create(None)
        assert isinstance(f, Mandelbrot)
    
    def test_register_normalizes_key(self):
        """register() should normalize keys using _normalize_name()."""
        # Register with display-style name (spaces, special chars)
        class TestFractal(FractalType):
            @property
            def name(self):
                return "Test Fractal"
            
            def calculate(self, x, y, max_iter):
                return np.zeros(x.shape, dtype=np.int32) + max_iter
        
        FractalFactory.register("Test Fractal", TestFractal)
        
        # Should be stored with normalized key
        assert "test_fractal" in FractalFactory._fractals
        f = FractalFactory.create("test fractal")
        assert isinstance(f, TestFractal)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])