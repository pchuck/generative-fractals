"""Interior distance estimation for Mandelbrot set."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("mandelbrot_interior")
class MandelbrotInteriorFractal(FractalBase):
    """Mandelbrot with interior distance estimation coloring."""
    
    name = "Mandelbrot Interior Distance"
    description = "Estimates distance from interior points to the Mandelbrot boundary"
    parameters = {
        "smoothness": {
            "type": "float",
            "default": 1.0,
            "min": 0.1,
            "max": 5.0,
            "description": "Interior smoothness factor"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.smoothness = float(self.params.get("smoothness", 1.0))
        except (ValueError, TypeError):
            self.smoothness = 1.0
        self.smoothness = max(0.1, min(5.0, self.smoothness))
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.25, "ymax": 1.25}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Mandelbrot with interior distance estimation."""
        c = complex(x, y)
        z = 0
        dz = 0  # Derivative of z with respect to c
        
        # First check if point is in the main cardioid
        q = (x - 0.25) ** 2 + y ** 2
        if q * (q + (x - 0.25)) <= 0.25 * y ** 2:
            # In main cardioid - estimate distance
            # Distance estimation for cardioid
            dist = np.sqrt(q) * 2
            return max_iter * (1 - min(dist * self.smoothness, 1))
        
        # Check if in period-2 bulb
        if (x + 1) ** 2 + y ** 2 <= 0.0625:
            # In period-2 bulb
            dist = np.sqrt((x + 1) ** 2 + y ** 2) * 4
            return max_iter * (1 - min(dist * self.smoothness, 1))
        
        for i in range(max_iter):
            if abs(z) > 2:
                # Escaped - use standard smooth iteration
                log_zn = np.log(abs(z))
                nu = np.log(log_zn / np.log(2)) / np.log(2)
                return i + 1 - nu
            
            # Update derivative: dz = 2*z*dz + 1
            dz = 2 * z * dz + 1
            z = z * z + c
        
        # Did not escape - estimate interior distance
        # Using the derivative to estimate distance to boundary
        if abs(dz) > 1e-10:
            # Interior distance estimate: ~ 1/|dz|
            # Points closer to boundary have smaller |dz|
            dist_estimate = 1.0 / (abs(dz) * self.smoothness)
            
            # Normalize to [0, max_iter]
            # Smaller distance (closer to boundary) = higher value
            normalized = max(0, min(1, dist_estimate))
            return normalized * max_iter
        else:
            # Deep interior - return low value
            return 0
