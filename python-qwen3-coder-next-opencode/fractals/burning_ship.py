"""Burning Ship fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("burning_ship")
class BurningShip(FractalBase):
    """Burning Ship fractal using absolute values."""
    
    name = "Burning Ship"
    description = "Uses absolute values for ship-like shapes"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 1.5, 'ymin': -2.5, 'ymax': 0.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Burning Ship iteration for a point."""
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                nu = np.log(np.log(abs(z))) / np.log(2)
                return i + 1 - nu
            
            z = (abs(z.real) + abs(z.imag) * 1j) ** 2 + c
        
        return float(max_iter)
