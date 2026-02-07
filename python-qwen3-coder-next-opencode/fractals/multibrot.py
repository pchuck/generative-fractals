"""Multibrot fractal with configurable power."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("multibrot")
class Multibrot(FractalBase):
    """Multibrot with configurable power z^n + c."""
    
    name = "Multibrot"
    description = "Configurable power (z^n + c, where n = 2-10)"
    parameters: Dict[str, Any] = {
        'power': {'type': 'int', 'min': 2, 'max': 10, 'default': 3}
    }
    
    def __init__(self):
        self.power = 3
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -2.0, 'ymax': 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Multibrot iteration for a point."""
        c = complex(x, y)
        z = 0j
        power = self.power
        
        for i in range(max_iter):
            if abs(z) > 2:
                try:
                    nu = np.log(np.log(abs(z)) / np.log(power)) / np.log(power)
                except (ValueError, ZeroDivisionError):
                    nu = 0
                return i + 1 - nu
            
            z = z ** power + c
        
        return float(max_iter)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set power parameter."""
        if 'power' in params:
            self.power = int(params['power'])
        super().set_parameters(params)
