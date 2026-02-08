"""Unit tests for UI panels.

Run with: python -m pytest tests/ -v
"""

import tkinter as tk
import pytest
from fractals import Mandelbrot, Julia, Multibrot, Phoenix, FractalFactory


class TestJuliaPanel:
    """Tests for Julia parameter panel."""
    
    @pytest.fixture
    def root(self):
        """Create a temporary root window for testing."""
        root = tk.Tk()
        yield root
        root.destroy()
    
    @pytest.fixture
    def julia_fractal(self):
        return Julia(c_real=-0.7, c_imag=0.27)
    
    def test_panel_creation(self, root, julia_fractal):
        """Panel should be created successfully."""
        from ui.julia_panel import JuliaPanel
        
        panel = JuliaPanel(root, julia_fractal, lambda: None)
        assert panel is not None
    
    def test_c_real_variable_exists(self, root, julia_fractal):
        """c_real_var should exist and have correct initial value."""
        from ui.julia_panel import JuliaPanel
        
        panel = JuliaPanel(root, julia_fractal, lambda: None)
        assert hasattr(panel, 'c_real_var')
        assert abs(panel.c_real_var.get() - (-0.7)) < 0.01
    
    def test_c_imag_variable_exists(self, root, julia_fractal):
        """c_imag_var should exist."""
        from ui.julia_panel import JuliaPanel
        
        panel = JuliaPanel(root, julia_fractal, lambda: None)
        assert hasattr(panel, 'c_imag_var')
    
    def test_update_from_fractal(self, root):
        """update_from_fractal should sync UI with fractal state."""
        from ui.julia_panel import JuliaPanel
        
        # Create panel with default values
        panel = JuliaPanel(root, Julia(c_real=0.5, c_imag=-0.3), lambda: None)
        
        # Update from different fractal
        new_fractal = Julia(c_real=1.2, c_imag=0.8)
        panel.fractal = new_fractal
        panel.update_from_fractal()
        
        assert abs(panel.c_real_var.get() - 1.2) < 0.01
        assert abs(panel.c_imag_var.get() - 0.8) < 0.01


class TestMultibrotPanel:
    """Tests for Multibrot parameter panel."""
    
    @pytest.fixture
    def root(self):
        root = tk.Tk()
        yield root
        root.destroy()
    
    def test_panel_creation(self, root):
        """Panel should be created successfully."""
        from ui.multibrot_panel import MultibrotPanel
        
        panel = MultibrotPanel(root, Multibrot(power=4.0), lambda: None)
        assert panel is not None
    
    def test_power_variable_exists(self, root):
        """power_var should exist and have correct initial value."""
        from ui.multibrot_panel import MultibrotPanel
        
        panel = MultibrotPanel(root, Multibrot(power=3.5), lambda: None)
        assert hasattr(panel, 'power_var')
        assert abs(panel.power_var.get() - 3.5) < 0.01
    
    def test_update_from_fractal(self, root):
        """update_from_fractal should sync UI with fractal state."""
        from ui.multibrot_panel import MultibrotPanel
        
        panel = MultibrotPanel(root, Multibrot(power=2.0), lambda: None)
        
        # Update from different fractal
        new_fractal = Multibrot(power=5.0)
        panel.fractal = new_fractal
        panel.update_from_fractal()
        
        assert abs(panel.power_var.get() - 5.0) < 0.01


class TestPhoenixPanel:
    """Tests for Phoenix parameter panel."""
    
    @pytest.fixture
    def root(self):
        root = tk.Tk()
        yield root
        root.destroy()
    
    def test_panel_creation(self, root):
        """Panel should be created successfully."""
        from ui.phoenix_panel import PhoenixPanel
        
        panel = PhoenixPanel(root, Phoenix(), lambda: None)
        assert panel is not None
    
    def test_c_real_variable_exists(self, root):
        """c_real_var should exist and have correct initial value."""
        from ui.phoenix_panel import PhoenixPanel
        
        panel = PhoenixPanel(root, Phoenix(real=-1.0, imag=0.2), lambda: None)
        assert hasattr(panel, 'c_real_var')
        assert abs(panel.c_real_var.get() - (-1.0)) < 0.01
    
    def test_p_variable_exists(self, root):
        """p_var should exist."""
        from ui.phoenix_panel import PhoenixPanel
        
        panel = PhoenixPanel(root, Phoenix(p=1.5), lambda: None)
        assert hasattr(panel, 'p_var')
    
    def test_update_from_fractal(self, root):
        """update_from_fractal should sync UI with fractal state."""
        from ui.phoenix_panel import PhoenixPanel
        
        panel = PhoenixPanel(root, Phoenix(real=-0.5, imag=0.1), lambda: None)
        
        # Update from different fractal
        new_fractal = Phoenix(real=2.0, imag=-1.0, p=0.8)
        panel.fractal = new_fractal
        panel.update_from_fractal()
        
        assert abs(panel.c_real_var.get() - 2.0) < 0.01
        assert abs(panel.p_var.get() - 0.8) < 0.01


class TestCreateParamPanel:
    """Tests for the _create_param_panel factory function."""
    
    @pytest.fixture
    def root(self):
        root = tk.Tk()
        yield root
        root.destroy()
    
    def test_julia_returns_panel(self, root):
        """Julia type should return JuliaPanel."""
        from main_refactored import _create_param_panel
        
        panel = _create_param_panel("Julia", root, Julia(), lambda: None)
        assert panel is not None
    
    def test_multibrot_returns_panel(self, root):
        """Multibrot type should return MultibrotPanel."""
        from main_refactored import _create_param_panel
        
        panel = _create_param_panel("Multibrot", root, Multibrot(), lambda: None)
        assert panel is not None
    
    def test_phoenix_returns_panel(self, root):
        """Phoenix type should return PhoenixPanel."""
        from main_refactored import _create_param_panel
        
        panel = _create_param_panel("Phoenix", root, Phoenix(), lambda: None)
        assert panel is not None
    
    def test_mandelbrot_returns_none(self, root):
        """Mandelbrot (no params) should return None."""
        from main_refactored import _create_param_panel
        
        panel = _create_param_panel("Mandelbrot", root, Mandelbrot(), lambda: None)
        assert panel is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])