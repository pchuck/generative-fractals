"""Feather fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("feather")
class Feather(FractalBase):
    """Feather fractal with z² + z/c iteration pattern."""
    
    name = "Feather"
    description = "z² + z/c iteration pattern"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -2.0, 'ymax': 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Feather iteration for a point."""
        c = complex(x, y)
        z = 0.1 + 0.1j
        
        for i in range(max_iter):
            if abs(z) > 2:
                nu = np.log(np.log(abs(z))) / np.log(2)
                return i + 1 - nu
            
            if abs(c) < 1e-10:
                break
            z = z ** 2 + z / c
        
        return float(max_iter)
