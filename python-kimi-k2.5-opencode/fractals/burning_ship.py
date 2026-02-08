"""Burning Ship fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("burning_ship")
class BurningShipFractal(FractalBase):
    """The Burning Ship fractal - uses absolute values."""
    
    name = "Burning Ship"
    description = "z = (|Re(z)| + i|Im(z)|)² + c"
    parameters = {}
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.5, "ymin": -2.0, "ymax": 1.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Burning Ship iteration with smooth coloring."""
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                log_zn = np.log(abs(z))
                nu = np.log(log_zn / np.log(2)) / np.log(2)
                return i + 1 - nu
            z = (abs(z.real) + 1j * abs(z.imag)) ** 2 + c
        
        return max_iter
