#!/usr/bin/env python3
"""Integration tests for the fractal explorer UI components."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import to trigger registration
from fractals import FractalRegistry
from fractals.mandelbrot import *
from fractals.ifs_fractals import *
from palettes import PaletteRegistry
from palettes.standard import *


class TestFractalComputationCorrectness(unittest.TestCase):
    """Test mathematical correctness of fractal computations."""
    
    def test_mandelbrot_cardioid(self):
        """Test known points in Mandelbrot set."""
        fractal = FractalRegistry.create('mandelbrot')
        
        # Points known to be in the set
        in_set_points = [
            (0.0, 0.0),
            (-1.0, 0.0),
            (-0.5, 0.0),
        ]
        
        for x, y in in_set_points:
            result = fractal.compute_pixel(x, y, 100)
            self.assertEqual(result, 100, f"Point ({x}, {y}) should be in set")
    
    def test_mandelbrot_escape(self):
        """Test known points outside Mandelbrot set."""
        fractal = FractalRegistry.create('mandelbrot')
        
        # Points known to escape
        out_set_points = [
            (2.0, 0.0),
            (0.0, 2.0),
            (1.0, 1.0),
        ]
        
        for x, y in out_set_points:
            result = fractal.compute_pixel(x, y, 100)
            self.assertLess(result, 100, f"Point ({x}, {y}) should escape")


class TestPaletteConsistency(unittest.TestCase):
    """Test palette color consistency."""
    
    def test_smooth_palette_variation(self):
        """Test that smooth palette produces varied colors."""
        palette = PaletteRegistry.create('smooth')
        
        # Get colors for different values
        colors = []
        for i in range(0, 100, 20):
            color = palette.get_color(i, 100)
            colors.append(color)
        
        # Check that we have different colors (not all the same)
        unique_colors = set(colors)
        self.assertGreater(len(unique_colors), 1, "Smooth palette should produce varied colors")
    
    def test_banded_palette_discrete(self):
        """Test that banded palette has discrete bands."""
        palette = PaletteRegistry.create('banded', bands=4)
        
        # Get multiple colors
        colors = [palette.get_color(i, 100) for i in range(0, 100, 5)]
        
        # With 4 bands in 100 iterations, we should see some repetition
        unique_colors = set(colors)
        # Should have at most 5 unique colors (4 bands + black for max_iter)
        self.assertLessEqual(len(unique_colors), 5)


class TestIFSGeometry(unittest.TestCase):
    """Test IFS fractal geometric properties."""
    
    def test_sierpinski_triangle_area(self):
        """Test that Sierpinski triangle points fill expected area."""
        fractal = FractalRegistry.create('sierpinski_triangle')
        points = fractal.generate_points(10000)
        
        # Points should be distributed across the triangle
        x_min, x_max = points[:, 0].min(), points[:, 0].max()
        y_min, y_max = points[:, 1].min(), points[:, 1].max()
        
        # Check spread (should cover most of [0,1]x[0,1])
        self.assertGreater(x_max - x_min, 0.8)
        self.assertGreater(y_max - y_min, 0.8)
    
    def test_dragon_curve_bounds(self):
        """Test dragon curve stays within bounds."""
        fractal = FractalRegistry.create('dragon_curve')
        points = fractal.generate_points(5000)
        
        # Get bounds
        bounds = fractal.get_default_bounds()
        
        # All points should be within bounds
        self.assertTrue(np.all(points[:, 0] >= bounds['xmin']))
        self.assertTrue(np.all(points[:, 0] <= bounds['xmax']))
        self.assertTrue(np.all(points[:, 1] >= bounds['ymin']))
        self.assertTrue(np.all(points[:, 1] <= bounds['ymax']))


class TestRegistry(unittest.TestCase):
    """Test registry functionality."""
    
    def test_fractal_registry_singleton(self):
        """Test that registry maintains single instance."""
        # Get list twice
        list1 = FractalRegistry.list_fractals()
        list2 = FractalRegistry.list_fractals()
        
        self.assertEqual(list1, list2)
    
    def test_palette_registry_singleton(self):
        """Test that palette registry maintains single instance."""
        list1 = PaletteRegistry.list_palettes()
        list2 = PaletteRegistry.list_palettes()
        
        self.assertEqual(list1, list2)
    
    def test_fractal_unknown(self):
        """Test handling of unknown fractal."""
        with self.assertRaises(ValueError):
            FractalRegistry.create('nonexistent_fractal')
    
    def test_palette_unknown(self):
        """Test handling of unknown palette."""
        with self.assertRaises(ValueError):
            PaletteRegistry.create('nonexistent_palette')


if __name__ == '__main__':
    import numpy as np
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestFractalComputationCorrectness))
    suite.addTests(loader.loadTestsFromTestCase(TestPaletteConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestIFSGeometry))
    suite.addTests(loader.loadTestsFromTestCase(TestRegistry))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)
