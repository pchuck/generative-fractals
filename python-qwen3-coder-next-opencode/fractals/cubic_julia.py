"""Cubic Julia set implementation."""

import numpy as np
from typing import Dict, Any

from . import FractalBase, register_fractal


@register_fractal("cubic_julia")
class CubicJulia(FractalBase):
    """Cubic Julia set with z³ iteration."""
    
    name = "Cubic Julia"
    description = "Julia set with z³ iteration"
    parameters: Dict[str, Any] = {
        'c': {'type': 'complex', 'default': (0.3, 0.5)}
    }
    
    def __init__(self):
        self.c = complex(0.3, 0.5)
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -1.5, 'xmax': 1.5, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Cubic Julia iteration for a point."""
        z = complex(x, y)
        c = self.c
        
        for i in range(max_iter):
            if abs(z) > 2:
                nu = np.log(np.log(abs(z))) / np.log(3)
                return i + 1 - nu
            
            z = z ** 3 + c
        
        return float(max_iter)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set c parameter."""
        if 'c' in params:
            c_val = params['c']
            if isinstance(c_val, str):
                self.c = complex(c_val)
            else:
                self.c = complex(c_val[0], c_val[1])
        super().set_parameters(params)
