"""Burning ship fractal implementation."""

from . import FractalBase, register_fractal


@register_fractal("burning_ship")
class BurningShip(FractalBase):
    """Burning ship fractal using absolute values."""
    
    name = "Burning Ship"
    description = "z = (|Re(z)| + i|Im(z)|)² + c"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.0, "xmax": 1.5, "ymin": -1.75, "ymax": 1.75}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)
            z = (abs(z.real) + 1j * abs(z.imag)) ** 2 + c
        
        return float(max_iter)