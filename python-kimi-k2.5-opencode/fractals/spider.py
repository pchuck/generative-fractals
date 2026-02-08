"""Spider fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("spider")
class SpiderFractal(FractalBase):
    """Spider fractal."""
    
    name = "Spider"
    description = "z = z² + c, c = c/2 + z"
    parameters = {}
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.5, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)
            z = z * z + c
            c = c / 2 + z
        
        return float(max_iter)
