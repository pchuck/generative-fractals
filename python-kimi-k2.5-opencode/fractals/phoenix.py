"""Phoenix fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal, parse_complex_string


@register_fractal("phoenix")
class PhoenixFractal(FractalBase):
    """The Phoenix fractal - uses previous z value."""
    
    name = "Phoenix"
    description = "z = z² + c + p*z_prev"
    parameters = {
        "p": {
            "type": "complex",
            "default": "0.5667",
            "description": "Phoenix constant p"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        p_str = self.params.get("p", "0.5667")
        self.p = parse_complex_string(p_str)
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.5, "ymin": -1.5, "ymax": 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        z_prev = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)
            z_new = z * z + c + self.p * z_prev
            z_prev = z
            z = z_new
        
        return float(max_iter)
