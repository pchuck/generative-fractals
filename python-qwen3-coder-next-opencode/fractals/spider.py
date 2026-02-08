"""Spider fractal implementation."""

import numpy as np
from typing import Dict, Any

from . import FractalBase, register_fractal


@register_fractal("spider")
class Spider(FractalBase):
    """Spider fractal with dynamic c parameter."""
    
    name = "Spider"
    description = "Dynamic c parameter updating each iteration"
    parameters: Dict[str, Any] = {
        'speed': {'type': 'float', 'min': 0.01, 'max': 0.5, 'default': 0.5}
    }
    
    def __init__(self):
        self.speed = 0.5
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Spider iteration for a point."""
        z = 0j
        c = complex(x, y)
        speed = self.speed
        
        for i in range(max_iter):
            if abs(z) > 2:
                nu = np.log(np.log(abs(z))) / np.log(2)
                return i + 1 - nu
            
            z = z ** 2 + c
            c = complex(c.real + speed * np.sin(z.imag), c.imag + speed * np.cos(z.real))
        
        return float(max_iter)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set speed parameter."""
        if 'speed' in params:
            self.speed = float(params['speed'])
        super().set_parameters(params)
