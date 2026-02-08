"""Newton fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("newton")
class NewtonFractal(FractalBase):
    """Newton fractal for z³ - 1 = 0."""
    
    name = "Newton"
    description = "Newton's method for z³ - 1 = 0"
    parameters = {}
    
    def get_default_bounds(self):
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        
        roots = [
            complex(1, 0),
            complex(-0.5, np.sqrt(3)/2),
            complex(-0.5, -np.sqrt(3)/2)
        ]
        
        for i in range(max_iter):
            if abs(z) < 1e-10:
                return float(max_iter)
            
            z_new = z - (z**3 - 1) / (3 * z**2)
            
            for j, root in enumerate(roots):
                if abs(z_new - root) < 1e-6:
                    return float(i + j * max_iter / 3)
            
            z = z_new
        
        return float(max_iter)
