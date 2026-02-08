"""Pickover stalks Mandelbrot variant."""

from . import FractalBase, register_fractal


@register_fractal("pickover_stalks")
class PickoverStalks(FractalBase):
    """Pickover stalks - colors based on closest approach to axes."""
    
    name = "Pickover Stalks"
    description = "Colors based on minimum distance to x and y axes during iteration"
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.375, "ymax": 1.375}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        
        min_real_dist = float('inf')
        min_imag_dist = float('inf')
        
        for i in range(max_iter):
            real_dist = abs(z.real)
            imag_dist = abs(z.imag)
            
            if real_dist < min_real_dist:
                min_real_dist = real_dist
            if imag_dist < min_imag_dist:
                min_imag_dist = imag_dist
            
            if abs(z) > 2:
                stalk_val = int((min(min_real_dist, min_imag_dist)) * 1000)
                return max_iter - stalk_val
            
            z = z * z + c
        
        return float(max_iter)