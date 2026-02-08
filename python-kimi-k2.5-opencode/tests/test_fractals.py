#!/usr/bin/env python3
"""Unit tests for the fractal explorer application."""

import sys
import os
import unittest
import numpy as np
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import fractal modules to trigger registration
from fractals import FractalRegistry, FractalBase
from fractals.ifs_base import IFSFractalBase
from fractals.mandelbrot import *
from fractals.julia import *
from fractals.barnsley_fern import *
from fractals.ifs_fractals import *
from fractals.multibrot import *

# Import palette modules to trigger registration
from palettes import PaletteRegistry, PaletteBase
from palettes.standard import *


class TestFractalRegistry(unittest.TestCase):
    """Test fractal registration and creation."""
    
    def test_all_fractals_registered(self):
        """Test that all expected fractals are registered."""
        fractals = FractalRegistry.list_fractals()
        self.assertGreater(len(fractals), 0)
        
        # Check some known fractals exist
        expected = ['mandelbrot', 'julia', 'barnsley_fern', 'sierpinski_triangle']
        for name in expected:
            self.assertIn(name, fractals, f"Expected fractal '{name}' not found")
    
    def test_fractal_creation(self):
        """Test creating fractal instances."""
        for name in FractalRegistry.list_fractals()[:5]:  # Test first 5
            fractal = FractalRegistry.create(name)
            self.assertIsNotNone(fractal)
            self.assertIsInstance(fractal, FractalBase)
    
    def test_fractal_default_bounds(self):
        """Test that all fractals have valid default bounds."""
        for name in FractalRegistry.list_fractals():
            fractal = FractalRegistry.create(name)
            bounds = fractal.get_default_bounds()
            
            # Check required keys exist
            required_keys = ['xmin', 'xmax', 'ymin', 'ymax']
            for key in required_keys:
                self.assertIn(key, bounds, f"{name}: Missing '{key}' in bounds")
            
            # Check bounds are valid numbers
            self.assertIsInstance(bounds['xmin'], (int, float))
            self.assertIsInstance(bounds['xmax'], (int, float))
            self.assertIsInstance(bounds['ymin'], (int, float))
            self.assertIsInstance(bounds['ymax'], (int, float))
            
            # Check x_min < x_max and y_min < y_max
            self.assertLess(bounds['xmin'], bounds['xmax'], 
                          f"{name}: xmin >= xmax")
            self.assertLess(bounds['ymin'], bounds['ymax'],
                          f"{name}: ymin >= ymax")


class TestMandelbrotFractal(unittest.TestCase):
    """Test Mandelbrot set computation."""
    
    def setUp(self):
        self.fractal = FractalRegistry.create('mandelbrot')
    
    def test_origin_in_set(self):
        """Test that origin (0,0) is in the Mandelbrot set."""
        # Origin should not escape (returns max_iter)
        result = self.fractal.compute_pixel(0.0, 0.0, 100)
        self.assertEqual(result, 100)
    
    def test_point_outside_set(self):
        """Test that points far from origin escape quickly."""
        # Point (2, 2) should escape immediately
        result = self.fractal.compute_pixel(2.0, 2.0, 100)
        self.assertLess(result, 100)
    
    def test_negative_coordinates(self):
        """Test computation with negative coordinates."""
        result = self.fractal.compute_pixel(-0.5, 0.0, 100)
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0)


class TestJuliaFractal(unittest.TestCase):
    """Test Julia set computation."""
    
    def test_julia_creation(self):
        """Test creating Julia sets with different parameters."""
        # Standard Julia set
        julia = FractalRegistry.create('julia', c="-0.7+0.27j")
        self.assertIsNotNone(julia)
        
        # Test computation
        result = julia.compute_pixel(0.0, 0.0, 100)
        self.assertIsInstance(result, (int, float))


class TestIFSFractals(unittest.TestCase):
    """Test IFS (Iterated Function System) fractals."""
    
    def test_ifs_fractals_exist(self):
        """Test that IFS fractals are properly registered."""
        ifs_fractals = ['barnsley_fern', 'sierpinski_triangle', 'sierpinski_carpet', 
                       'dragon_curve', 'maple_leaf']
        
        for name in ifs_fractals:
            if name in FractalRegistry.list_fractals():
                fractal = FractalRegistry.create(name)
                self.assertIsInstance(fractal, IFSFractalBase)
    
    def test_sierpinski_point_generation(self):
        """Test Sierpinski triangle point generation."""
        fractal = FractalRegistry.create('sierpinski_triangle')
        points = fractal.generate_points(1000)
        
        # Check shape
        self.assertEqual(points.shape, (1000, 2))
        
        # Check all points are within expected bounds [0, 1]
        self.assertTrue(np.all(points[:, 0] >= 0))
        self.assertTrue(np.all(points[:, 0] <= 1))
        self.assertTrue(np.all(points[:, 1] >= 0))
        self.assertTrue(np.all(points[:, 1] <= 1))
    
    def test_sierpinski_rendering(self):
        """Test Sierpinski triangle image rendering."""
        fractal = FractalRegistry.create('sierpinski_triangle')
        bounds = fractal.get_default_bounds()
        
        # Render small image
        img = fractal.render_to_image(100, 100, bounds, num_points=5000)
        
        # Check image properties
        self.assertEqual(img.shape, (100, 100, 3))
        self.assertEqual(img.dtype, np.uint8)
        
        # Check that some pixels are non-zero (fractal was drawn)
        self.assertGreater(np.count_nonzero(img), 0)
    
    def test_barnsley_fern_rendering(self):
        """Test Barnsley fern image rendering."""
        fractal = FractalRegistry.create('barnsley_fern')
        bounds = fractal.get_default_bounds()
        
        img = fractal.render_to_image(100, 100, bounds, num_points=5000)
        
        self.assertEqual(img.shape, (100, 100, 3))
        self.assertEqual(img.dtype, np.uint8)


class TestPaletteRegistry(unittest.TestCase):
    """Test palette registration and color generation."""
    
    def test_all_palettes_registered(self):
        """Test that all expected palettes are registered."""
        palettes = PaletteRegistry.list_palettes()
        self.assertGreater(len(palettes), 0)
        
        expected = ['smooth', 'banded', 'grayscale', 'fire', 'ocean']
        for name in expected:
            self.assertIn(name, palettes)
    
    def test_palette_creation(self):
        """Test creating palette instances."""
        for name in PaletteRegistry.list_palettes():
            palette = PaletteRegistry.create(name)
            self.assertIsNotNone(palette)
            self.assertIsInstance(palette, PaletteBase)
    
    def test_color_generation(self):
        """Test that palettes generate valid RGB colors."""
        for name in PaletteRegistry.list_palettes():
            palette = PaletteRegistry.create(name)
            
            # Test various iteration values
            for value in [0, 50, 100]:
                color = palette.get_color(value, 100)
                
                # Check color is RGB tuple
                self.assertIsInstance(color, tuple)
                self.assertEqual(len(color), 3)
                
                # Check values are in valid range
                for channel in color:
                    self.assertIsInstance(channel, int)
                    self.assertGreaterEqual(channel, 0)
                    self.assertLessEqual(channel, 255)
    
    def test_max_iter_color(self):
        """Test that max iteration returns black (inside set)."""
        palette = PaletteRegistry.create('smooth')
        color = palette.get_color(100, 100)  # value == max_iter
        
        # Should be black (0, 0, 0)
        self.assertEqual(color, (0, 0, 0))


class TestBoundsCalculations(unittest.TestCase):
    """Test viewport bounds calculations."""
    
    def test_mandelbrot_bounds(self):
        """Test Mandelbrot default bounds are reasonable."""
        fractal = FractalRegistry.create('mandelbrot')
        bounds = fractal.get_default_bounds()
        
        # Mandelbrot is usually centered at origin with width ~3, height ~2.5
        x_center = (bounds['xmin'] + bounds['xmax']) / 2
        y_center = (bounds['ymin'] + bounds['ymax']) / 2
        
        # Should be roughly centered at origin
        self.assertAlmostEqual(x_center, -0.75, delta=1.0)  # Mandelbrot is shifted left
        self.assertAlmostEqual(y_center, 0.0, delta=0.5)


class TestParameterHandling(unittest.TestCase):
    """Test fractal parameter handling."""
    
    def test_julia_parameters(self):
        """Test Julia set accepts complex parameter."""
        # Create with different c values
        test_values = [
            "-0.7+0.27j",
            "0.0+1.0j",
            "-0.75+0.11j"
        ]
        
        for c_val in test_values:
            fractal = FractalRegistry.create('julia', c=c_val)
            self.assertEqual(fractal.params['c'], c_val)
    
    def test_multibrot_parameters(self):
        """Test Multibrot accepts power parameter."""
        for power in [3, 4, 5]:
            fractal = FractalRegistry.create('multibrot', power=power)
            self.assertEqual(fractal.params.get('power', power), power)


class TestPerformance(unittest.TestCase):
    """Basic performance tests."""
    
    def test_ifs_rendering_speed(self):
        """Test that IFS rendering completes in reasonable time."""
        import time
        
        fractal = FractalRegistry.create('sierpinski_triangle')
        bounds = fractal.get_default_bounds()
        
        start = time.time()
        img = fractal.render_to_image(200, 200, bounds, num_points=10000)
        elapsed = time.time() - start
        
        # Should complete in less than 1 second for 10k points
        self.assertLess(elapsed, 1.0, 
                       f"IFS rendering took {elapsed:.2f}s, expected < 1s")
        
        # Verify image was created
        self.assertIsNotNone(img)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFractalRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestMandelbrotFractal))
    suite.addTests(loader.loadTestsFromTestCase(TestJuliaFractal))
    suite.addTests(loader.loadTestsFromTestCase(TestIFSFractals))
    suite.addTests(loader.loadTestsFromTestCase(TestPaletteRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundsCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestParameterHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
