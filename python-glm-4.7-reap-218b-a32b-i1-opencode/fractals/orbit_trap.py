"""Orbit trap Mandelbrot variant."""

from . import FractalBase, register_fractal


@register_fractal("orbit_trap")
class OrbitTrap(FractalBase):
    """Mandelbrot with orbit trap coloring - tracks distance to geometric shapes."""
    
    name = "Orbit Trap"
    description = "Colors based on minimum distance to trap shape during iteration"
    parameters = {"trap_type": "circle", "trap_radius": 0.5}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.375, "ymax": 1.375}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        trap_type = self.get_parameter("trap_type", "circle")
        trap_radius = self.get_parameter("trap_radius", 0.5)

        min_dist = float('inf')
        
        for i in range(max_iter):
            if trap_type == "point":
                dist = abs(z)
            elif trap_type == "cross":
                dist = min(abs(z.real), abs(z.imag))
            else:
                dist = abs(abs(z) - trap_radius)
            
            if dist < min_dist:
                min_dist = dist
            
            if abs(z) > 2:
                trapped_val = int(min_dist * 500)
                return max_iter - min(max_iter, trapped_val)
            
            z = z * z + c
        
        return float(max_iter)