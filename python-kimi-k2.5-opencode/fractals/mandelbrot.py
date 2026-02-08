"""Mandelbrot set implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("mandelbrot")
class MandelbrotFractal(FractalBase):
    """The classic Mandelbrot set with smooth coloring."""
    
    name = "Mandelbrot Set"
    description = "z = z² + c, the classic Mandelbrot set"
    parameters = {}
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.25, "ymax": 1.25}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Mandelbrot iteration with smooth coloring."""
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                log_zn = np.log(abs(z))
                nu = np.log(log_zn / np.log(2)) / np.log(2)
                return i + 1 - nu
            z = z * z + c
        
        return max_iter
