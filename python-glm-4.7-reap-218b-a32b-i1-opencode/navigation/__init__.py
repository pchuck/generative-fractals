"""Navigation and zoom controller."""

from typing import Dict, Any, Optional


class ZoomController:
    """Manages coordinate transformations for zooming and panning."""
    
    def __init__(self, width: int = 800, height: int = 600):
        """Initialize the zoom controller.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.width = width
        self.height = height
        self.reset()
    
    def reset(self) -> None:
        """Reset to default bounds."""
        self.bounds = {"xmin": -2.0, "xmax": 1.5, "ymin": -1.25, "ymax": 1.25}
    
    def set_bounds(self, xmin: float, xmax: float, ymin: float, ymax: float) -> None:
        """Set custom coordinate bounds.
        
        Args:
            xmin: Minimum x value
            xmax: Maximum x value
            ymin: Minimum y value
            ymax: Maximum y value
        """
        self.bounds = {"xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax}
    
    def get_bounds(self) -> Dict[str, float]:
        """Get current bounds."""
        return self.bounds.copy()
    
    def pixel_to_complex(self, px: int, py: int) -> tuple:
        """Convert pixel coordinates to complex plane coordinates.
        
        Args:
            px: Pixel x coordinate
            py: Pixel y coordinate
            
        Returns:
            Tuple of (x, y) in complex plane
        """
        width = self.bounds["xmax"] - self.bounds["xmin"]
        height = self.bounds["ymax"] - self.bounds["ymin"]
        
        x = self.bounds["xmin"] + (px / self.width) * width
        y = self.bounds["ymax"] - (py / self.height) * height
        
        return (x, y)
    
    def complex_to_pixel(self, x: float, y: float) -> tuple:
        """Convert complex plane coordinates to pixel coordinates.
        
        Args:
            x: X coordinate in complex plane
            y: Y coordinate in complex plane
            
        Returns:
            Tuple of (px, py) pixel coordinates
        """
        width = self.bounds["xmax"] - self.bounds["xmin"]
        height = self.bounds["ymax"] - self.bounds["ymin"]
        
        px = int((x - self.bounds["xmin"]) / width * self.width)
        py = int((self.bounds["ymax"] - y) / height * self.height)
        
        return (px, py)
    
    def zoom(self, factor: float, center_x: Optional[float] = None, center_y: Optional[float] = None) -> None:
        """Zoom in or out by a factor.
        
        Args:
            factor: Zoom factor (>1 to zoom out, <1 to zoom in)
            center_x: X coordinate of zoom center (None for center of view)
            center_y: Y coordinate of zoom center (None for center of view)
        """
        if center_x is None or center_y is None:
            center_x = (self.bounds["xmin"] + self.bounds["xmax"]) / 2
            center_y = (self.bounds["ymin"] + self.bounds["ymax"]) / 2
        
        width = self.bounds["xmax"] - self.bounds["xmin"]
        height = self.bounds["ymax"] - self.bounds["ymin"]
        
        new_width = width * factor
        new_height = height * factor
        
        self.bounds["xmin"] = center_x - (center_x - self.bounds["xmin"]) / width * new_width
        self.bounds["xmax"] = center_x + (self.bounds["xmax"] - center_x) / width * new_width
        self.bounds["ymin"] = center_y - (center_y - self.bounds["ymin"]) / height * new_height
        self.bounds["ymax"] = center_y + (self.bounds["ymax"] - center_y) / height * new_height
    
    def select_area(self, px1: int, py1: int, px2: int, py2: int,
                    width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Zoom to a selected rectangular area.

        Args:
            px1: First pixel x coordinate
            py1: First pixel y coordinate
            px2: Second pixel x coordinate
            py2: Second pixel y coordinate
            width: Canvas width (uses self.width if not provided)
            height: Canvas height (uses self.height if not provided)
        """
        w = width if width is not None else self.width
        h = height if height is not None else self.height

        x1, y1 = self._pixel_to_complex_with_size(px1, py1, w, h)
        x2, y2 = self._pixel_to_complex_with_size(px2, py2, w, h)

        self.bounds["xmin"] = min(x1, x2)
        self.bounds["xmax"] = max(x1, x2)
        self.bounds["ymin"] = min(y1, y2)
        self.bounds["ymax"] = max(y1, y2)

    def _pixel_to_complex_with_size(self, px: int, py: int, width: int, height: int) -> tuple:
        """Convert pixel coordinates to complex plane with explicit size.

        Args:
            px: Pixel x coordinate
            py: Pixel y coordinate
            width: Canvas width
            height: Canvas height

        Returns:
            Tuple of (x, y) in complex plane
        """
        bounds_width = self.bounds["xmax"] - self.bounds["xmin"]
        bounds_height = self.bounds["ymax"] - self.bounds["ymin"]

        x = self.bounds["xmin"] + (px / width) * bounds_width
        y = self.bounds["ymax"] - (py / height) * bounds_height

        return (x, y)