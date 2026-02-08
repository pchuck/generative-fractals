"""Multibrot fractal implementation with configurable power."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("multibrot")
class MultibrotFractal(FractalBase):
    """Multibrot set with configurable power (z^n + c)."""
    
    name = "Multibrot"
    description = "z = z^n + c, configurable power"
    parameters = {
        "power": {
            "type": "int",
            "default": 2,
            "min": 2,
            "max": 10,
            "description": "Power n (2=Mandelbrot, 3, 4, 5, etc.)"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.power = int(self.params.get("power", 2))
        except (ValueError, TypeError):
            self.power = 2
        # Clamp to valid range
        self.power = max(2, min(10, self.power))
    
    def get_default_bounds(self):
        # Center on zero with bounds to fit all powers
        return {"xmin": -2.5, "xmax": 2.5, "ymin": -2.5, "ymax": 2.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Multibrot iteration with smooth coloring."""
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                # Smooth coloring based on power
                log_zn = np.log(abs(z))
                nu = np.log(log_zn / np.log(self.power)) / np.log(self.power)
                return i + 1 - nu
            z = z ** self.power + c
        
        return max_iter
