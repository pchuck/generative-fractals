"""Cubic Julia fractal implementation."""

from . import FractalBase, register_fractal, smooth_coloring


@register_fractal("cubic_julia")
class CubicJulia(FractalBase):
    """Julia set with z³ iteration."""
    
    name = "Cubic Julia"
    description = "z = z³ + c"
    parameters = {"c": -0.5j}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -1.75, "xmax": 1.75, "ymin": -1.75, "ymax": 1.75}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        c = self.get_parameter("c", -0.5j)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 3.0)
            z = z ** 3 + c
        
        return float(max_iter)