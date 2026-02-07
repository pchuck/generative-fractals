"""Tricorn (Mandelbar) fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("tricorn")
class Tricorn(FractalBase):
    """Tricorn or Mandelbar fractal."""
    
    name = "Tricorn"
    description = "Conjugates z before squaring"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 1.5, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Tricorn iteration for a point."""
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                nu = np.log(np.log(abs(z))) / np.log(2)
                return i + 1 - nu
            
            z = (z.real - z.imag * 1j) ** 2 + c
        
        return float(max_iter)
