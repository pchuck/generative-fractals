"""Cubic Julia set implementation."""

import numpy as np
from . import FractalBase, register_fractal, parse_complex_string


@register_fractal("cubic_julia")
class CubicJuliaFractal(FractalBase):
    """Cubic Julia set (z³ + c)."""
    
    name = "Cubic Julia"
    description = "z = z³ + c"
    parameters = {
        "c": {
            "type": "complex",
            "default": "0.4+0.0j",
            "description": "Complex constant c"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        c_str = self.params.get("c", "0.4+0.0j")
        self.c = parse_complex_string(c_str)
    
    def get_default_bounds(self):
        return {"xmin": -1.5, "xmax": 1.5, "ymin": -1.5, "ymax": 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        
        for i in range(max_iter):
            if abs(z) > 2:
                log_zn = np.log(abs(z))
                nu = np.log(log_zn / np.log(3)) / np.log(3)
                return i + 1 - nu
            z = z ** 3 + self.c
        
        return max_iter
