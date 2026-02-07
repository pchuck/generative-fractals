"""Default fractal renderer implementation."""

from typing import Tuple, List
from PIL import Image


class FractalRenderer:
    """Standard fractal renderer using a single process."""
    
    def __init__(self, fractal, palette, max_iter: int, bounds: Tuple[float, float, float, float]):
        """Initialize renderer.
        
        Args:
            fractal: Fractal to render
            palette: Color palette
            max_iter: Maximum iterations
            bounds: (xmin, xmax, ymin, ymax) view bounds
        """
        self.fractal = fractal
        self.palette = palette
        self.max_iter = max_iter
        self.bounds = bounds
    
    def render(self, width: int, height: int) -> bytes:
        """Render fractal to raw bytes."""
        pixels = []
        
        for y in range(height):
            for x in range(width):
                real = self.bounds[0] + (x / width) * (self.bounds[1] - self.bounds[0])
                imag = self.bounds[2] + ((height - y) / height) * (self.bounds[3] - self.bounds[2])
                
                z = complex(real, imag)
                value = self.fractal.compute_pixel(z.real, z.imag, self.max_iter)
                color = self.palette.get_color(value, float(self.max_iter))
                pixels.append(color)
        
        img = Image.new('RGB', (width, height))
        pixel_data = []
        for color in pixels:
            pixel_data.extend(color)
        
        img.putdata(pixel_data)
        
        return img


__all__ = ['FractalRenderer']
