"""Tricorn (Mandelbar) fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("tricorn")
class TricornFractal(FractalBase):
    """The Tricorn (Mandelbar) fractal - conjugates z."""
    
    name = "Tricorn"
    description = "z = conj(z)² + c"
    parameters = {}
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.5, "ymin": -1.5, "ymax": 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Tricorn iteration with smooth coloring."""
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                log_zn = np.log(abs(z))
                nu = np.log(log_zn / np.log(2)) / np.log(2)
                return i + 1 - nu
            z = z.conjugate() ** 2 + c
        
        return max_iter
