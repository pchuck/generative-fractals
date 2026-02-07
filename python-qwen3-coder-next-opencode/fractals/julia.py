"""Julia sets implementation."""

import numpy as np
from typing import Dict, Any

from . import FractalBase, register_fractal


JULIA_PRESETS = {
    'dendrite': complex(0, -1),
    'dragon': complex(-0.123, 0.745),
    'spiral': complex(-0.726, 0.189),
}


@register_fractal("julia")
class Julia(FractalBase):
    """Julia set with customizable complex constant c."""
    
    name = "Julia Set"
    description = "Julia sets with customizable complex constant c"
    
    def __init__(self):
        self.c = complex(-0.7, 0.27)
        self.power = 2
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -1.5, 'xmax': 1.5, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Julia iteration for a point."""
        z = complex(x, y)
        c = self.c
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
        """Set parameters including c and power."""
        if 'c' in params:
            c_val = params['c']
            if isinstance(c_val, str):
                self.c = complex(c_val)
            else:
                self.c = complex(c_val[0], c_val[1])
        if 'power' in params:
            self.power = int(params['power'])
        super().set_parameters(params)
    
    def apply_preset(self, preset_name: str):
        """Apply a Julia preset."""
        if preset_name in JULIA_PRESETS:
            self.c = JULIA_PRESETS[preset_name]
