"""Feather fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("feather")
class FeatherFractal(FractalBase):
    """Feather fractal (z² + z/c)."""
    
    name = "Feather"
    description = "z = z² + z/c"
    parameters = {}
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 2.5, "ymin": -2.5, "ymax": 2.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        if abs(c) < 1e-10:
            return float(max_iter)
        
        # Start with z = c instead of z = 0 to avoid staying at 0
        z = c
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)
            z = z * z + z / c
        
        return float(max_iter)
