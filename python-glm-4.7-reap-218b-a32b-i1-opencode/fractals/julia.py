"""Julia set implementations with presets."""

from . import FractalBase, register_fractal, smooth_coloring


@register_fractal("julia")
class Julia(FractalBase):
    """Julia set with customizable complex constant c."""
    
    name = "Julia Set"
    description = "z = z² + c (c fixed)"
    parameters = {"c": -0.75 + 0.1j}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        c = self.get_parameter("c", -0.75 + 0.1j)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 2.0)
            z = z * z + c
        
        return float(max_iter)


@register_fractal("julia_dendrite")
class JuliaDendrite(FractalBase):
    """Julia set dendrite variant."""
    
    name = "Julia Dendrite"
    description = "z = z² - 1 (dendrite)"
    parameters = {"c": -1.0 + 0j}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 2.0)
            z = z * z - 1
        
        return float(max_iter)


@register_fractal("julia_dragon")
class JuliaDragon(FractalBase):
    """Julia set dragon variant."""
    
    name = "Julia Dragon"
    description = "z = z² + c (dragon)"
    parameters = {"c": 0.36 + 0.1j}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 2.0)
            z = z * z + (0.36 + 0.1j)
        
        return float(max_iter)


@register_fractal("julia_spiral")
class JuliaSpiral(FractalBase):
    """Julia set spiral variant."""
    
    name = "Julia Spiral"
    description = "z = z² + c (spiral)"
    parameters = {"c": -0.7269 + 0.1889j}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        z = complex(x, y)
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 2.0)
            z = z * z + (-0.7269 + 0.1889j)
        
        return float(max_iter)