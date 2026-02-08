"""Sierpinski Triangle IFS fractal implementation."""

import numpy as np
from . import register_fractal
from .ifs_base import IFSFractalBase


@register_fractal("sierpinski_triangle")
class SierpinskiTriangleFractal(IFSFractalBase):
    """Sierpinski Triangle - classic IFS fractal with infinite detail."""
    
    name = "Sierpinski Triangle"
    description = "Classic IFS: three contractions creating triangular holes"
    parameters = {
        "points": {
            "type": "int",
            "default": 150000,
            "min": 50000,
            "max": 500000,
            "description": "Number of points to generate"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.num_points = int(self.params.get("points", 150000))
        except (ValueError, TypeError):
            self.num_points = 150000
        self.num_points = max(50000, min(500000, self.num_points))
    
    def get_default_bounds(self):
        return {"xmin": -0.1, "xmax": 1.1, "ymin": -0.1, "ymax": 1.1}
    
    def iterate_point(self, x: float, y: float) -> tuple:
        """Apply Sierpinski triangle IFS transformation."""
        r = np.random.random()
        
        if r < 0.333:
            # Contract toward bottom-left vertex (0, 0)
            return (0.5 * x, 0.5 * y)
        elif r < 0.667:
            # Contract toward bottom-right vertex (1, 0)
            return (0.5 * x + 0.5, 0.5 * y)
        else:
            # Contract toward top vertex (0.5, 1)
            return (0.5 * x + 0.25, 0.5 * y + 0.5)


@register_fractal("sierpinski_carpet")
class SierpinskiCarpetFractal(IFSFractalBase):
    """Sierpinski Carpet - square version with holes."""
    
    name = "Sierpinski Carpet"
    description = "IFS with 8 contractions creating square holes"
    parameters = {
        "points": {
            "type": "int",
            "default": 200000,
            "min": 50000,
            "max": 500000,
            "description": "Number of points to generate"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.num_points = int(self.params.get("points", 200000))
        except (ValueError, TypeError):
            self.num_points = 200000
        self.num_points = max(50000, min(500000, self.num_points))
    
    def get_default_bounds(self):
        return {"xmin": -0.1, "xmax": 1.1, "ymin": -0.1, "ymax": 1.1}
    
    def iterate_point(self, x: float, y: float) -> tuple:
        """Apply Sierpinski carpet IFS (8 transformations, skipping center)."""
        r = np.random.random()
        
        # 8 squares around the center (each 1/3 size)
        if r < 0.125:
            # Top-left
            return (x / 3, y / 3 + 2/3)
        elif r < 0.25:
            # Top-center
            return (x / 3 + 1/3, y / 3 + 2/3)
        elif r < 0.375:
            # Top-right
            return (x / 3 + 2/3, y / 3 + 2/3)
        elif r < 0.5:
            # Middle-left
            return (x / 3, y / 3 + 1/3)
        elif r < 0.625:
            # Middle-right
            return (x / 3 + 2/3, y / 3 + 1/3)
        elif r < 0.75:
            # Bottom-left
            return (x / 3, y / 3)
        elif r < 0.875:
            # Bottom-center
            return (x / 3 + 1/3, y / 3)
        else:
            # Bottom-right
            return (x / 3 + 2/3, y / 3)


@register_fractal("dragon_curve")
class DragonCurveFractal(IFSFractalBase):
    """Dragon Curve - complex boundary IFS fractal."""
    
    name = "Dragon Curve"
    description = "Heighway dragon: two rotations creating intricate boundary"
    parameters = {
        "points": {
            "type": "int",
            "default": 150000,
            "min": 50000,
            "max": 500000,
            "description": "Number of points to generate"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.num_points = int(self.params.get("points", 150000))
        except (ValueError, TypeError):
            self.num_points = 150000
        self.num_points = max(50000, min(500000, self.num_points))
    
    def get_default_bounds(self):
        return {"xmin": -0.5, "xmax": 1.3, "ymin": -0.5, "ymax": 0.9}
    
    def iterate_point(self, x: float, y: float) -> tuple:
        """Apply Heighway dragon IFS."""
        r = np.random.random()
        
        if r < 0.5:
            # First transformation: rotate 45°, scale by 1/sqrt(2)
            return (0.5 * x - 0.5 * y, 0.5 * x + 0.5 * y)
        else:
            # Second transformation: rotate 135°, scale by 1/sqrt(2), translate
            return (-0.5 * x - 0.5 * y + 1, 0.5 * x - 0.5 * y)


@register_fractal("maple_leaf")
class MapleLeafFractal(IFSFractalBase):
    """Maple Leaf - natural-looking leaf pattern IFS."""
    
    name = "Maple Leaf"
    description = "IFS generating a realistic maple leaf pattern"
    parameters = {
        "points": {
            "type": "int",
            "default": 150000,
            "min": 50000,
            "max": 500000,
            "description": "Number of points to generate"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.num_points = int(self.params.get("points", 150000))
        except (ValueError, TypeError):
            self.num_points = 150000
        self.num_points = max(50000, min(500000, self.num_points))
    
    def get_default_bounds(self):
        return {"xmin": -3.8, "xmax": 3.8, "ymin": -1.0, "ymax": 6.0}
    
    def iterate_point(self, x: float, y: float) -> tuple:
        """Apply maple leaf IFS."""
        r = np.random.random()
        
        if r < 0.35:
            # Main stem and center
            return (0.6 * x + 0.01 * y, -0.01 * x + 0.6 * y + 1.5)
        elif r < 0.55:
            # Left leaflets
            return (0.4 * x - 0.3 * y - 1.5, 0.3 * x + 0.4 * y + 0.8)
        elif r < 0.75:
            # Right leaflets  
            return (0.4 * x + 0.3 * y + 1.5, -0.3 * x + 0.4 * y + 0.8)
        elif r < 0.90:
            # Top details
            return (0.3 * x + 0.02 * y, -0.02 * x + 0.3 * y + 3.5)
        else:
            # Fine details
            return (0.5 * x + 0.05 * y, -0.05 * x + 0.5 * y + 2.0)
