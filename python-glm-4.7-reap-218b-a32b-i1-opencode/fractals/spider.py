"""Spider fractal implementation."""

from . import FractalBase, register_fractal, smooth_coloring


@register_fractal("spider")
class Spider(FractalBase):
    """Spider fractal - dynamic c parameter updating each iteration."""
    
    name = "Spider"
    description = "z = z² + c, where c varies with iteration"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -1.5, "xmax": 1.5, "ymin": -1.5, "ymax": 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        c_initial = complex(x, y)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 2.0)
            
            angle = (i % 360) * 3.14159 / 180
            c_factor = 0.05 + 0.02j
            
            z = z * z + c_initial + c_factor * complex(angle, angle).real
        
        return float(max_iter)