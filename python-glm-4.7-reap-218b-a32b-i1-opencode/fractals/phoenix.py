"""Phoenix fractal implementation."""

from . import FractalBase, register_fractal


@register_fractal("phoenix")
class Phoenix(FractalBase):
    """Phoenix fractal - uses previous z value in iteration."""
    
    name = "Phoenix"
    description = "z = z² + c + p*z_prev (p constant)"
    parameters = {"p": 0.5}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.0, "xmax": 1.5, "ymin": -1.75, "ymax": 1.75}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        z_prev = 0j
        p = self.get_parameter("p", 0.5)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)
            temp = z
            z = z * z + c + p * z_prev
            z_prev = temp
        
        return float(max_iter)