"""Interior distance Mandelbrot variant."""

from . import FractalBase, register_fractal


@register_fractal("interior_distance")
class InteriorDistance(FractalBase):
    """Interior distance - estimates distance from interior to boundary."""
    
    name = "Interior Distance"
    description = "Estimates distance from points in the set to the boundary"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.375, "ymax": 1.375}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        dz_dc = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)
            
            dz_dc = 2 * z * dz_dc + 1
            z = z * z + c
        
        if abs(dz_dc) > 0:
            dist = (1 - abs(z)) / abs(dz_dc)
            return max_iter - min(max_iter, int(dist * 100))
        
        return float(max_iter)