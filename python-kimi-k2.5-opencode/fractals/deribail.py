"""Derivative bailout (deribail) Mandelbrot implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("mandelbrot_deribail")
class MandelbrotDeribailFractal(FractalBase):
    """Mandelbrot with derivative bailout - uses derivative magnitude for escape condition."""
    
    name = "Mandelbrot Derivative Bailout"
    description = "Uses |dz/dc| as bailout condition instead of |z|, creating different exterior patterns"
    parameters = {
        "bailout": {
            "type": "float",
            "default": 100.0,
            "min": 10.0,
            "max": 1000.0,
            "description": "Derivative magnitude bailout threshold"
        },
        "blend": {
            "type": "float",
            "default": 0.5,
            "min": 0.0,
            "max": 1.0,
            "description": "Blend between standard (0) and derivative (1) bailout"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.bailout = float(self.params.get("bailout", 100.0))
        except (ValueError, TypeError):
            self.bailout = 100.0
        self.bailout = max(10.0, min(1000.0, self.bailout))
        
        try:
            self.blend = float(self.params.get("blend", 0.5))
        except (ValueError, TypeError):
            self.blend = 0.5
        self.blend = max(0.0, min(1.0, self.blend))
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.25, "ymax": 1.25}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Mandelbrot with derivative bailout."""
        c = complex(x, y)
        z = 0
        dz = 0  # Derivative dz/dc
        
        for i in range(max_iter):
            # Standard bailout condition
            z_mag = abs(z)
            
            # Derivative bailout condition
            dz_mag = abs(dz)
            
            # Check for NaN or infinity
            if np.isnan(z_mag) or np.isinf(z_mag) or np.isnan(dz_mag) or np.isinf(dz_mag):
                return float(i)
            
            # Cap values to prevent overflow
            if z_mag > 1e10 or dz_mag > 1e10:
                return float(i)
            
            # Blended bailout: combination of both
            if self.blend < 0.01:
                # Pure standard bailout
                bail = z_mag > 2
            elif self.blend > 0.99:
                # Pure derivative bailout
                bail = dz_mag > self.bailout
            else:
                # Blended condition
                z_factor = z_mag / 2.0
                dz_factor = dz_mag / self.bailout
                bail = (1 - self.blend) * z_factor + self.blend * dz_factor > 1
            
            if bail:
                # For smooth coloring, we need |z| > 2
                # If bailed due to derivative, we might have |z| < 2
                # In that case, just return the iteration count
                if z_mag <= 2:
                    return float(i)
                
                # Standard smooth iteration
                log_zn = np.log(z_mag)
                nu = np.log(log_zn / np.log(2)) / np.log(2)
                
                # Mix in derivative information for coloring
                if dz_mag > 0:
                    dz_contrib = np.log(dz_mag + 1) / np.log(self.bailout + 1)
                else:
                    dz_contrib = 0
                
                # Return blended value
                result = (i + 1 - nu) * (1 + self.blend * dz_contrib)
                # Ensure we return a valid float
                if np.isnan(result) or np.isinf(result):
                    return float(i)
                return float(result)
            
            # Update z and dz
            dz = 2 * z * dz + 1
            z = z * z + c
        
        # Did not escape
        return float(max_iter)
