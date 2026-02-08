"""Feather fractal implementation."""

from . import FractalBase, register_fractal, smooth_coloring


@register_fractal("feather")
class Feather(FractalBase):
    """Feather fractal - z² + z/c iteration pattern."""
    
    name = "Feather"
    description = "z = z² + z/c"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -1.5, "xmax": 0.75, "ymin": -1.125, "ymax": 1.125}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        
        if abs(c) < 0.05:
            return float(max_iter)
        
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2 or abs(c) < 1e-10:
                return smooth_coloring(z, i, max_iter, 2.0)
            z = z * z + z / c
        
        return float(max_iter)