"""Barnsley Fern fractal implementation using IFS base class."""

import numpy as np
from . import register_fractal
from .ifs_base import IFSFractalBase


@register_fractal("barnsley_fern")
class BarnsleyFernFractal(IFSFractalBase):
    """Barnsley Fern - iterated function system generating a realistic fern shape."""
    
    name = "Barnsley Fern"
    description = "IFS fractal: affine transformations creating a natural fern"
    parameters = {
        "points": {
            "type": "int",
            "default": 100000,
            "min": 10000,
            "max": 500000,
            "description": "Number of points to generate"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.num_points = int(self.params.get("points", 100000))
        except (ValueError, TypeError):
            self.num_points = 100000
        self.num_points = max(10000, min(500000, self.num_points))
        self._current_point = (0.0, 0.0)
    
    def get_default_bounds(self):
        return {"xmin": -3.0, "xmax": 3.0, "ymin": -1.0, "ymax": 11.0}
    
    def iterate_point(self, x: float, y: float) -> tuple:
        """Apply one iteration of Barnsley fern IFS."""
        r = np.random.random()
        
        if r < 0.01:
            # Stem (1%)
            return (0.0, 0.16 * y)
        elif r < 0.86:
            # Leaflets (85%)
            return (0.85 * x + 0.04 * y,
                   -0.04 * x + 0.85 * y + 1.6)
        elif r < 0.93:
            # Left leaflet (7%)
            return (0.2 * x - 0.26 * y,
                   0.23 * x + 0.22 * y + 1.6)
        else:
            # Right leaflet (7%)
            return (-0.15 * x + 0.28 * y,
                   0.26 * x + 0.24 * y + 0.44)
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Not used for IFS - render_to_image is used instead."""
        return 0.0


@register_fractal("barnsley_fern_variant")
class BarnsleyFernVariantFractal(IFSFractalBase):
    """Barnsley Fern Variant - modified IFS parameters."""
    
    name = "Barnsley Fern (Variant)"
    description = "Modified IFS with different transformation parameters"
    parameters = {
        "points": {
            "type": "int",
            "default": 100000,
            "min": 10000,
            "max": 500000,
            "description": "Number of points to generate"
        },
        "variant": {
            "type": "choice",
            "default": "tree",
            "choices": ["tree", "spiral", "crystal"],
            "description": "Variant type"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        try:
            self.num_points = int(self.params.get("points", 100000))
        except (ValueError, TypeError):
            self.num_points = 100000
        self.num_points = max(10000, min(500000, self.num_points))
        self.variant = self.params.get("variant", "tree")
    
    def get_default_bounds(self):
        return {"xmin": -5.0, "xmax": 5.0, "ymin": -2.0, "ymax": 12.0}
    
    def iterate_point(self, x: float, y: float) -> tuple:
        """Apply variant IFS transformation."""
        r = np.random.random()
        
        if self.variant == "tree":
            # Tree-like
            if r < 0.05:
                return (0.0, 0.5 * y)
            elif r < 0.5:
                return (0.6 * x, 0.6 * y + 2.0)
            elif r < 0.75:
                return (0.4 * x + 0.3 * y - 1.0, -0.3 * x + 0.4 * y + 1.0)
            else:
                return (0.4 * x - 0.3 * y + 1.0, 0.3 * x + 0.4 * y + 1.0)
        
        elif self.variant == "spiral":
            # Spiral fern
            if r < 0.01:
                return (0.0, 0.16 * y)
            elif r < 0.86:
                return (0.85 * x + 0.02 * y,
                       -0.02 * x + 0.85 * y + 1.6)
            elif r < 0.93:
                return (0.09 * x - 0.28 * y,
                       0.3 * x + 0.11 * y + 1.6)
            else:
                return (-0.09 * x + 0.28 * y,
                       0.3 * x + 0.09 * y + 0.44)
        
        else:  # crystal
            if r < 0.02:
                return (0.0, 0.25 * y - 0.4)
            elif r < 0.86:
                return (0.95 * x + 0.005 * y - 0.002,
                       -0.005 * x + 0.93 * y + 0.5)
            elif r < 0.93:
                return (0.035 * x - 0.2 * y - 0.09,
                       0.16 * x + 0.04 * y + 0.02)
            else:
                return (-0.04 * x + 0.2 * y + 0.083,
                       0.16 * x + 0.04 * y + 0.12)
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Not used for IFS - render_to_image is used instead."""
        return 0.0
