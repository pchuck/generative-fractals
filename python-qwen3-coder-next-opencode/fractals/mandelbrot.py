"""Mandelbrot fractal implementation."""

import numpy as np
from typing import Dict, Any

from . import FractalBase, register_fractal


@register_fractal("mandelbrot")
class Mandelbrot(FractalBase):
    """Classic Mandelbrot set with smooth coloring."""
    
    name = "Mandelbrot Set"
    description = "The classic fractal with smooth coloring"
    
    def __init__(self):
        self.power = 2
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.5, 'xmax': 1.5, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Mandelbrot iteration for a point."""
        c = complex(x, y)
        z = 0j
        power = self.power
        
        for i in range(max_iter):
            if abs(z) > 2:
                if power == 2:
                    nu = np.log(np.log(abs(z))) / np.log(2)
                else:
                    try:
                        nu = np.log(np.log(abs(z)) / np.log(power)) / np.log(power)
                    except (ValueError, ZeroDivisionError):
                        nu = 0
                return i + 1 - nu
            
            z = z ** power + c
        
        return float(max_iter)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set parameters including power."""
        if 'power' in params:
            self.power = int(params['power'])
        super().set_parameters(params)
