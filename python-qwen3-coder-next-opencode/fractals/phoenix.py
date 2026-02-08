"""Phoenix fractal implementation."""

import numpy as np
from typing import Dict, Any

from . import FractalBase, register_fractal


@register_fractal("phoenix")
class Phoenix(FractalBase):
    """Phoenix fractal using previous z value."""
    
    name = "Phoenix"
    description = "Uses previous z value in iteration"
    parameters: Dict[str, Any] = {
        'p': {'type': 'complex', 'default': complex(-0.70176, 0.3842)}
    }
    
    def __init__(self):
        self.p = complex(-0.70176, 0.3842)
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -2.0, 'ymax': 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Phoenix iteration for a point."""
        c = complex(x, y)
        z = 0j
        z_prev = 0j
        p = self.p
        
        for i in range(max_iter):
            if abs(z) > 2:
                nu = np.log(np.log(abs(z))) / np.log(2)
                return i + 1 - nu
            
            z_prev, z = z, z ** 2 + c + p * z_prev
        
        return float(max_iter)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set p parameter."""
        if 'p' in params:
            p_val = params['p']
            if isinstance(p_val, str):
                self.p = complex(p_val)
            else:
                self.p = complex(p_val[0], p_val[1])
        super().set_parameters(params)
