"""IFS (Iterated Function System) fractal base and renderer."""

import numpy as np
from abc import abstractmethod
from typing import Dict, Tuple
from . import FractalBase

# Constants
IFS_SKIP_ITERATIONS: int = 20
DEFAULT_IFS_POINTS: int = 100000
IFS_GAMMA: float = 0.5
IFS_COLOR_TINT: Tuple[float, float, float] = (0.3, 0.9, 0.2)  # RGB multipliers


class IFSFractalBase(FractalBase):
    """Base class for IFS fractals that generate points rather than escape-time."""
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """
        Not used for IFS fractals - they use iterate_point() and render_to_image().
        This is required by the base class but should not be called.
        """
        raise NotImplementedError("IFS fractals use render_to_image() instead of compute_pixel()")
    
    @abstractmethod
    def iterate_point(self, x: float, y: float) -> Tuple[float, float]:
        """
        Apply one iteration of the IFS to a point.
        
        Args:
            x, y: Current point coordinates
            
        Returns:
            (new_x, new_y) after applying transformation
        """
        pass
    
    def get_initial_point(self) -> Tuple[float, float]:
        """Get starting point for IFS iteration."""
        return (0.0, 0.0)
    
    def generate_points(self, num_points: int = DEFAULT_IFS_POINTS) -> np.ndarray:
        """
        Generate points using the IFS.
        
        Args:
            num_points: Number of points to generate
            
        Returns:
            Numpy array of shape (num_points, 2) with (x, y) coordinates
        """
        points = np.zeros((num_points, 2), dtype=np.float64)
        x, y = self.get_initial_point()
        
        # Skip first few iterations to reach attractor
        for _ in range(IFS_SKIP_ITERATIONS):
            x, y = self.iterate_point(x, y)
        
        # Generate points
        for i in range(num_points):
            x, y = self.iterate_point(x, y)
            points[i] = [x, y]
        
        return points
    
    def render_to_image(self, width: int, height: int, bounds: Dict[str, float], 
                       num_points: int = DEFAULT_IFS_POINTS) -> np.ndarray:
        """
        Render IFS to an image array.
        
        Args:
            width, height: Image dimensions
            bounds: Viewport bounds dict with keys 'xmin', 'xmax', 'ymin', 'ymax'
            num_points: Number of points to generate
            
        Returns:
            RGB image array of shape (height, width, 3)
        """
        # Generate points
        points = self.generate_points(num_points)
        
        # Create histogram/image buffer
        img_buffer = np.zeros((height, width), dtype=np.float64)
        
        # Map points to pixel coordinates (vectorized)
        x_min, x_max = bounds['xmin'], bounds['xmax']
        y_min, y_max = bounds['ymin'], bounds['ymax']
        
        x_scale = width / (x_max - x_min)
        y_scale = height / (y_max - y_min)
        
        # Vectorized coordinate transformation
        px = ((points[:, 0] - x_min) * x_scale).astype(np.int32)
        py = ((y_max - points[:, 1]) * y_scale).astype(np.int32)  # Flip y
        
        # Filter points within bounds
        mask = (px >= 0) & (px < width) & (py >= 0) & (py < height)
        px_valid = px[mask]
        py_valid = py[mask]
        
        # Accumulate using numpy (faster than Python loop)
        np.add.at(img_buffer, (py_valid, px_valid), 1)
        
        # Normalize
        max_val = img_buffer.max()
        if max_val > 0:
            img_buffer = img_buffer / max_val
        
        # Vectorized RGB conversion
        # Apply gamma correction and scale to 0-255
        intensity = (255 * img_buffer ** IFS_GAMMA).astype(np.uint8)
        
        # Create RGB image with color tint (vectorized)
        rgb_img = np.zeros((height, width, 3), dtype=np.uint8)
        rgb_img[:, :, 0] = (intensity * IFS_COLOR_TINT[0]).astype(np.uint8)  # R
        rgb_img[:, :, 1] = (intensity * IFS_COLOR_TINT[1]).astype(np.uint8)  # G
        rgb_img[:, :, 2] = (intensity * IFS_COLOR_TINT[2]).astype(np.uint8)  # B
        
        return rgb_img
