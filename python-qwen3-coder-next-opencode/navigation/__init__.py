"""Navigation and zoom controller."""

import numpy as np


class ZoomController:
    """Handles zoom, pan, and viewport transformations."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.xmin, self.xmax = -2.5, 1.5
        self.ymin, self.ymax = -1.5, 1.5
    
    def set_bounds(self, xmin: float, xmax: float, ymin: float, ymax: float):
        """Set the viewport bounds."""
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    
    def get_bounds(self) -> tuple:
        """Get current bounds."""
        return self.xmin, self.xmax, self.ymin, self.ymax
    
    def pixel_to_complex(self, px: int, py: int) -> complex:
        """Convert pixel coordinates to complex plane."""
        x = self.xmin + (px / self.width) * (self.xmax - self.xmin)
        y = self.ymin + ((self.height - py) / self.height) * (self.ymax - self.ymin)
        return complex(x, y)
    
    def complex_to_pixel(self, z: complex) -> tuple:
        """Convert complex plane to pixel coordinates."""
        px = int((z.real - self.xmin) / (self.xmax - self.xmin) * self.width)
        py = int(self.height - (z.imag - self.ymin) / (self.ymax - self.ymin) * self.height)
        return px, py
    
    def zoom_at(self, px: int, py: int, factor: float):
        """Zoom in/out at a specific pixel location."""
        center = self.pixel_to_complex(px, py)
        
        new_width = (self.xmax - self.xmin) * factor
        new_height = (self.ymax - self.ymin) * factor
        
        half_width = new_width / 2
        half_height = new_height / 2
        
        self.xmin = center.real - half_width
        self.xmax = center.real + half_width
        self.ymin = center.imag - half_height
        self.ymax = center.imag + half_height
    
    def zoom_rect(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Zoom to a rectangular region."""
        if x1 == x2 or y1 == y2:
            return False
        
        px_min = min(x1, x2)
        px_max = max(x1, x2)
        py_min = min(y1, y2)
        py_max = max(y1, y2)
        
        xmin = self.xmin + (px_min / self.width) * (self.xmax - self.xmin)
        xmax = self.xmin + (px_max / self.width) * (self.xmax - self.xmin)
        ymin = self.ymin + ((self.height - py_max) / self.height) * (self.ymax - self.ymin)
        ymax = self.ymin + ((self.height - py_min) / self.height) * (self.ymax - self.ymin)
        
        self.xmin, self.xmax = xmin, xmax
        self.ymin, self.ymax = ymin, ymax
        return True
    
    def pan(self, dx: int, dy: int):
        """Pan by pixel deltas."""
        width = self.xmax - self.xmin
        height = self.ymax - self.ymin
        
        self.xmin -= (dx / self.width) * width
        self.xmax -= (dx / self.width) * width
        self.ymin += (dy / self.height) * height
        self.ymax += (dy / self.height) * height
    
    def reset(self):
        """Reset to default bounds."""
        self.xmin, self.xmax = -2.5, 1.5
        self.ymin, self.ymax = -1.5, 1.5
    
    def set_fractional_view(self, xmin_f: float, xmax_f: float, ymin_f: float, ymax_f: float):
        """Set view as fractions of the original range."""
        orig_width = 4.0
        orig_height = 3.0
        
        self.xmin = -2.5 + xmin_f * orig_width
        self.xmax = self.xmin + xmax_f * orig_width
        self.ymin = -1.5 + ymin_f * orig_height
        self.ymax = self.ymin + ymax_f * orig_height
    
    def scale_to_fractal(self, fractal_bounds: dict):
        """Scale to fit a fractal's default bounds."""
        self.xmin = fractal_bounds['xmin']
        self.xmax = fractal_bounds['xmax']
        self.ymin = fractal_bounds['ymin']
        self.ymax = fractal_bounds['ymax']


__all__ = ['ZoomController']
