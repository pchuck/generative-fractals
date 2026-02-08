"""Julia set implementation."""

import numpy as np
from . import FractalBase, register_fractal, parse_complex_string


@register_fractal("julia")
class JuliaFractal(FractalBase):
    """Julia set with configurable c parameter."""
    
    name = "Julia Set"
    description = "z = z² + c, where c is constant"
    parameters = {
        "c": {
            "type": "complex",
            "default": "-0.7+0.27015j",
            "description": "Complex constant c (format: a+bj)"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        c_str = self.params.get("c", "-0.7+0.27015j")
        self.c = parse_complex_string(c_str)
    
    def get_default_bounds(self):
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Julia iteration with smooth coloring."""
        z = complex(x, y)
        
        for i in range(max_iter):
            if abs(z) > 2:
                log_zn = np.log(abs(z))
                nu = np.log(log_zn / np.log(2)) / np.log(2)
                return i + 1 - nu
            z = z * z + self.c
        
        return max_iter


@register_fractal("julia_dendrite")
class JuliaDendriteFractal(JuliaFractal):
    """Julia set with dendrite structure."""
    
    name = "Julia Dendrite"
    description = "Julia set c = 0.0 + 1.0i (dendrite structure)"
    
    def __init__(self, **params):
        super().__init__(c="0+1j", **params)


@register_fractal("julia_dragon")
class JuliaDragonFractal(JuliaFractal):
    """Julia set with dragon-like structure."""
    
    name = "Julia Dragon"
    description = "Julia set c = 0.0 + 0.8i (dragon shape)"
    
    def __init__(self, **params):
        super().__init__(c="0+0.8j", **params)


@register_fractal("julia_spiral")
class JuliaSpiralFractal(JuliaFractal):
    """Julia set with spiral structure."""
    
    name = "Julia Spiral"
    description = "Julia set c = -0.75 + 0.11i (spiral)"
    
    def __init__(self, **params):
        super().__init__(c="-0.75+0.11j", **params)
