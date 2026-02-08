"""Derivative bailout Mandelbrot variant."""

from . import FractalBase, register_fractal


@register_fractal("deribail")
class DeriBail(FractalBase):
    """Derivative bailout - uses |dz/dc| for bailout condition."""
    
    name = "Derivative Bailout"
    description = "Uses |dz/dc| instead of |z| for bailout condition"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.375, "ymax": 1.375}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        dz_dc = 0j
        
        for i in range(max_iter):
            if abs(dz_dc) > 10:
                return float(i)
            
            dz_dc = 2 * z * dz_dc + 1
            z = z * z + c
        
        return float(max_iter)