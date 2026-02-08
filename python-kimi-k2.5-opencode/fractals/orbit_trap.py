"""Orbit trap Mandelbrot implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("mandelbrot_orbit_trap")
class MandelbrotOrbitTrapFractal(FractalBase):
    """Mandelbrot set with orbit trap coloring."""
    
    name = "Mandelbrot Orbit Trap"
    description = "Mandelbrot with orbit trap coloring (tracks distance to geometric shapes)"
    parameters = {
        "trap_type": {
            "type": "choice",
            "default": "cross",
            "choices": ["point", "cross", "circle", "x_axis", "y_axis"],
            "description": "Type of orbit trap"
        },
        "trap_size": {
            "type": "float",
            "default": 0.5,
            "min": 0.1,
            "max": 2.0,
            "description": "Size of the trap"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        self.trap_type = self.params.get("trap_type", "cross")
        try:
            self.trap_size = float(self.params.get("trap_size", 0.5))
        except (ValueError, TypeError):
            self.trap_size = 0.5
        self.trap_size = max(0.1, min(2.0, self.trap_size))
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.25, "ymax": 1.25}
    
    def _distance_to_trap(self, z: complex) -> float:
        """Calculate distance from point z to the trap."""
        if self.trap_type == "point":
            # Distance to origin
            return abs(z)
        
        elif self.trap_type == "cross":
            # Distance to cross (both axes)
            dist_x = abs(z.imag)
            dist_y = abs(z.real)
            return min(dist_x, dist_y)
        
        elif self.trap_type == "circle":
            # Distance to a circle centered at origin
            return abs(abs(z) - self.trap_size)
        
        elif self.trap_type == "x_axis":
            # Distance to x-axis (imaginary part is 0)
            return abs(z.imag)
        
        elif self.trap_type == "y_axis":
            # Distance to y-axis (real part is 0)
            return abs(z.real)
        
        return abs(z)
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Mandelbrot with orbit trap."""
        c = complex(x, y)
        z = 0
        
        min_distance = float('inf')
        
        for i in range(max_iter):
            if abs(z) > 2:
                # Return the minimum distance found
                # Scale and invert so closer = higher value
                dist_val = min_distance / self.trap_size
                # Clamp and invert: 0 distance = max_val, large distance = 0
                normalized = max(0, 1 - min(dist_val, 1))
                return normalized * max_iter
            
            # Track minimum distance to trap, but skip the first iteration
            # because z=0 is not meaningful for most trap types
            if i > 0:
                dist = self._distance_to_trap(z)
                if dist < min_distance:
                    min_distance = dist
            
            z = z * z + c
        
        # Inside set - return based on minimum distance
        # Skip first iteration in the check
        if min_distance == float('inf'):
            # If we never updated min_distance (happens for z that stays at 0)
            min_distance = self.trap_size  # Use max distance
        
        dist_val = min_distance / self.trap_size
        normalized = max(0, 1 - min(dist_val, 1))
        return normalized * max_iter
