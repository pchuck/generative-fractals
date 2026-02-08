"""Mandelbrot set implementation."""

from . import FractalBase, register_fractal, smooth_coloring


@register_fractal("mandelbrot")
class Mandelbrot(FractalBase):
    """Classic Mandelbrot set with smooth coloring."""
    
    name = "Mandelbrot Set"
    description = "z = z² + c"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.375, "ymax": 1.375}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 2.0)
            z = z * z + c
        
        return float(max_iter)