"""Newton's method fractal for z^3 - 1 = 0."""

import numpy as np
from typing import Dict, Any

from . import FractalBase, register_fractal


def newton_update(z):
    """Newton's method update for z^3 - 1 = 0."""
    z_sq = z * z
    z_cubed = z_sq * z
    denom = 3 * z_sq
    if abs(denom) < 1e-10:
        return z
    return z - (z_cubed - 1) / denom


def get_root_index(z, tolerance=1e-6):
    """Determine which root z converged to."""
    roots = [
        complex(1, 0),
        complex(-0.5, np.sqrt(3)/2),
        complex(-0.5, -np.sqrt(3)/2)
    ]
    
    for i, root in enumerate(roots):
        if abs(z - root) < tolerance:
            return float(i + 1)
    
    return -1.0


@register_fractal("newton")
class Newton(FractalBase):
    """Newton's method visualization for z^3 - 1 = 0."""
    
    name = "Newton"
    description = "Newton's method visualization for z³ - 1 = 0"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -2.0, 'ymax': 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Newton fractal for a point."""
        z = complex(x, y)
        
        for i in range(max_iter):
            new_z = newton_update(z)
            if abs(new_z - z) < 1e-6:
                root = get_root_index(new_z)
                if root >= 0:
                    return (root / 3.0) * max_iter
            z = new_z
        
        return float(max_iter * 2)
