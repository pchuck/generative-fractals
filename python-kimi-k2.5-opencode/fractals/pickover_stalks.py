"""Pickover stalks fractal implementation."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("mandelbrot_stalks")
class MandelbrotStalksFractal(FractalBase):
    """Pickover stalks - tracks orbit closest approach to axes."""
    
    name = "Mandelbrot Stalks (Pickover)"
    description = "Pickover stalks - colors based on closest approach to x/y axes during orbit"
    parameters = {
        "stalk_type": {
            "type": "choice",
            "default": "both",
            "choices": ["real", "imag", "both", "diagonal"],
            "description": "Which component to track"
        },
        "scale": {
            "type": "float",
            "default": 1.0,
            "min": 0.1,
            "max": 5.0,
            "description": "Stalk intensity scale"
        }
    }
    
    def __init__(self, **params):
        super().__init__(**params)
        self.stalk_type = self.params.get("stalk_type", "both")
        try:
            self.scale = float(self.params.get("scale", 1.0))
        except (ValueError, TypeError):
            self.scale = 1.0
        self.scale = max(0.1, min(5.0, self.scale))
    
    def get_default_bounds(self):
        return {"xmin": -2.5, "xmax": 1.0, "ymin": -1.25, "ymax": 1.25}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Mandelbrot with Pickover stalks coloring."""
        c = complex(x, y)
        z = 0
        
        min_real = float('inf')
        min_imag = float('inf')
        min_diagonal = float('inf')
        
        for i in range(max_iter):
            if abs(z) > 2:
                # Calculate stalk value based on type
                if self.stalk_type == "real":
                    # Track closest to y-axis (min |Re(z)|)
                    dist_val = min_real * 10 * self.scale
                elif self.stalk_type == "imag":
                    # Track closest to x-axis (min |Im(z)|)
                    dist_val = min_imag * 10 * self.scale
                elif self.stalk_type == "diagonal":
                    # Track closest to diagonal (|Re(z)| + |Im(z)|)
                    dist_val = min_diagonal * 10 * self.scale
                else:  # both
                    # Combine both axes
                    dist_val = (min_real + min_imag) * 5 * self.scale
                
                # Normalize and return
                # Smaller distance = higher value (brighter)
                normalized = max(0, min(1, 1 - dist_val))
                return normalized * max_iter
            
            # Track minimum distances, skip first iteration
            if i > 0:
                real_abs = abs(z.real)
                imag_abs = abs(z.imag)
                
                if real_abs < min_real:
                    min_real = real_abs
                if imag_abs < min_imag:
                    min_imag = imag_abs
                
                # Diagonal: distance from |Re| + |Im| = 0 line
                diagonal_dist = real_abs + imag_abs
                if diagonal_dist < min_diagonal:
                    min_diagonal = diagonal_dist
            
            z = z * z + c
        
        # Inside set
        if self.stalk_type == "real":
            dist_val = min_real * 10 * self.scale
        elif self.stalk_type == "imag":
            dist_val = min_imag * 10 * self.scale
        elif self.stalk_type == "diagonal":
            dist_val = min_diagonal * 10 * self.scale
        else:  # both
            dist_val = (min_real + min_imag) * 5 * self.scale
        
        normalized = max(0, min(1, 1 - dist_val))
        return normalized * max_iter
