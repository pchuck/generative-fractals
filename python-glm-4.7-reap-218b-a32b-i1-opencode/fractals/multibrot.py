"""Multibrot set implementation."""

from . import FractalBase, register_fractal, smooth_coloring


@register_fractal("multibrot")
class Multibrot(FractalBase):
    """Configurable power multibrot set."""
    
    name = "Multibrot"
    description = "z = z^n + c (n configurable)"
    parameters = {"power": 3.0}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -1.75, "xmax": 1.25, "ymin": -1.5, "ymax": 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        power = self.get_parameter("power", 3.0)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, power)
            z = z ** power + c
        
        return float(max_iter)