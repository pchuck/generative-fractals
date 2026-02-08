"""Nova fractal implementation (Newton's method applied to Mandelbrot)."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("nova")
class NovaFractal(FractalBase):
    """Nova fractal - Newton's method applied to z³ - 1 = 0 with perturbation."""
    
    name = "Nova"
    description = "Newton's method with relaxation: z = z - R*(z³-1)/(3z²) + c"
    parameters = {
        "relaxation": {
            "type": "float",
            "default": 1.0,
            "min": 0.1,
            "max": 2.0,
            "description": "Relaxation parameter R"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.relaxation = float(self.params.get("relaxation", 1.0))
        except (ValueError, TypeError):
            self.relaxation = 1.0
        self.relaxation = max(0.1, min(2.0, self.relaxation))
    
    def get_default_bounds(self):
        return {"xmin": -3.0, "xmax": 3.0, "ymin": -3.0, "ymax": 3.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Nova iteration with smooth coloring."""
        c = complex(x, y)
        z = 1.0  # Start at root 1
        
        for i in range(max_iter):
            if abs(z) < 1e-10:
                return float(max_iter)
            
            # Newton's method for z³ - 1 = 0 with relaxation and perturbation
            # z_new = z - R * (z³ - 1) / (3z²) + c
            z3 = z ** 3
            z2 = z ** 2
            
            if abs(z2) < 1e-10:
                return float(max_iter)
            
            z_new = z - self.relaxation * (z3 - 1) / (3 * z2) + c
            
            # Check for convergence to any root
            roots = [complex(1, 0), 
                     complex(-0.5, np.sqrt(3)/2), 
                     complex(-0.5, -np.sqrt(3)/2)]
            
            for j, root in enumerate(roots):
                if abs(z_new - root) < 1e-6:
                    # Return value based on which root and iteration count
                    return float(i + j * max_iter / 3)
            
            # Check for divergence
            if abs(z_new) > 100:
                log_zn = np.log(abs(z_new))
                nu = np.log(log_zn / np.log(10)) / np.log(3)
                return i + 1 - nu
            
            z = z_new
        
        return float(max_iter)
