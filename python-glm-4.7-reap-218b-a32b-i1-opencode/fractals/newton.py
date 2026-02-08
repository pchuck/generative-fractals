"""Newton's method fractal implementation."""

from . import FractalBase, register_fractal


@register_fractal("newton")
class Newton(FractalBase):
    """Newton's method visualization for z³ - 1 = 0."""
    
    name = "Newton"
    description = "z = (2z + c/z²) / 3 for finding roots of z³-1=0"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.5, "xmax": 2.5, "ymin": -2.5, "ymax": 2.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        
        # Define the three roots of unity
        roots = [1+0j, -0.5 + 0.866j, -0.5 - 0.866j]
        
        for i in range(max_iter):
            for r in roots:
                if abs(z - r) < 0.001:
                    return float(i)
            
            if abs(z) > 10 or abs(z * z) < 1e-10:
                return float(i + 100)
            
            # Newton iteration for z³ - 1 = 0
            z = (2 * z + 1 / (z * z)) / 3
        
        return float(max_iter)