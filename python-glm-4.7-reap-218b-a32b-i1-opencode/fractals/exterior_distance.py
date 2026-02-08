"""Exterior distance Mandelbrot variant."""

from . import FractalBase, register_fractal


@register_fractal("exterior_distance")
class ExteriorDistance(FractalBase):
    """Exterior distance - analytic distance estimation."""
    
    name = "Exterior Distance"
    description = "Analytic distance estimation for exterior points"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.375, "ymax": 1.375}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                dist = (abs(z) * cmath.log(abs(z))) / abs(2 * z)
                return float(i) + min(1.0, max(0, dist.real))
            
            z = z * z + c
        
        return float(max_iter)


import cmath