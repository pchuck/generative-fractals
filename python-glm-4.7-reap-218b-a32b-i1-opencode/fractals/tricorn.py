"""Tricorn (Mandelbar) fractal implementation."""

from . import FractalBase, register_fractal


@register_fractal("tricorn")
class Tricorn(FractalBase):
    """Tricorn/Mandelbar fractal - conjugates z before squaring."""
    
    name = "Tricorn"
    description = "z = conj(z)² + c"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -1.5, "xmax": 0.75, "ymin": -1.125, "ymax": 1.125}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)
            z = (z.conjugate()) ** 2 + c
        
        return float(max_iter)