"""Exterior distance estimation for Mandelbrot set."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("mandelbrot_exterior")
class MandelbrotExteriorFractal(FractalBase):
    """Mandelbrot with exterior distance estimation coloring."""
    
    name = "Mandelbrot Exterior Distance"
    description = "Estimates distance from exterior points to the Mandelbrot boundary using analytic distance estimate"
    parameters = {
        "power": {
            "type": "float",
            "default": 0.5,
            "min": 0.1,
            "max": 2.0,
            "description": "Distance scaling power"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.power = float(self.params.get("power", 0.5))
        except (ValueError, TypeError):
            self.power = 0.5
        self.power = max(0.1, min(2.0, self.power))
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.25, "ymax": 1.25}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Mandelbrot with exterior distance estimation.
        
        Uses the analytic distance estimate formula:
        distance ≈ |z| * log|z| / |dz/dc|
        """
        c = complex(x, y)
        z = 0
        dz = 0  # Derivative of z with respect to c
        
        for i in range(max_iter):
            if abs(z) > 2:
                # Compute exterior distance estimate
                # Formula: distance ≈ |z| * log|z| / |dz/dc|
                abs_z = abs(z)
                abs_dz = abs(dz)
                
                if abs_dz > 1e-10:
                    # Distance estimate
                    distance = abs_z * np.log(abs_z) / abs_dz
                    
                    # Normalize for coloring
                    # Scale distance and apply power for contrast adjustment
                    normalized = distance ** self.power
                    
                    # Clamp and convert to iteration-like value
                    # Very close to boundary = high value
                    val = max(0, min(max_iter, normalized * max_iter))
                    return val
                else:
                    # Fallback to regular iteration count
                    log_zn = np.log(abs_z)
                    nu = np.log(log_zn / np.log(2)) / np.log(2)
                    return i + 1 - nu
            
            # Update z and dz
            # dz = 2*z*dz + 1
            dz = 2 * z * dz + 1
            z = z * z + c
        
        # Did not escape - inside the set
        return max_iter
