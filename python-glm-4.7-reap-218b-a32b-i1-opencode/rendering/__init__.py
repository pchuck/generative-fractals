"""RenderEngine class."""

from typing import Callable, Optional


class RenderEngine:
    """Main rendering engine for fractals."""
    
    def __init__(self, workers: int = None):
        """Initialize the render engine.
        
        Args:
            workers: Number of worker processes (None to auto-detect)
        """
        if workers is None:
            import multiprocessing
            self.workers = max(1, multiprocessing.cpu_count() - 1)
        else:
            self.workers = max(1, workers)
    
    def render(self, fractal, palette, zoom_controller, width: int, height: int,
               max_iter: int, progress_callback: Optional[Callable[[int, int], None]] = None):
        """Render a fractal image.
        
        Args:
            fractal: Fractal instance to render
            palette: Palette instance for coloring
            zoom_controller: ZoomController instance for coordinate mapping
            width: Image width in pixels
            height: Image height in pixels
            max_iter: Maximum iterations per pixel
            progress_callback: Optional callback function (completed_rows, total_rows)
            
        Returns:
            2D numpy array of RGB values
        """
        from .parallel import ParallelRenderer
        
        renderer = ParallelRenderer(self.workers)
        
        bounds = zoom_controller.get_bounds()
        
        return renderer.render(
            fractal=fractal,
            palette=palette,
            bounds=bounds,
            width=width,
            height=height,
            max_iter=max_iter,
            progress_callback=progress_callback
        )
    
    def render_preview(self, fractal, palette, zoom_controller, 
                       preview_scale: int = 10) -> list:
        """Render a quick blocky preview of the fractal.
        
        Args:
            fractal: Fractal instance to render
            palette: Palette instance for coloring
            zoom_controller: ZoomController instance for coordinate mapping
            preview_scale: Scale factor for preview (higher = more blocky)
            
        Returns:
            2D list of RGB values scaled down
        """
        width = zoom_controller.width // preview_scale
        height = zoom_controller.height // preview_scale
        
        result = []
        bounds = zoom_controller.get_bounds()
        
        dx = (bounds["xmax"] - bounds["xmin"]) / width
        dy = (bounds["ymax"] - bounds["ymin"]) / height
        
        for py in range(height):
            row = []
            y = bounds["ymax"] - (py + 0.5) * dy
            
            for px in range(width):
                x = bounds["xmin"] + (px + 0.5) * dx
                
                value = fractal.compute_pixel(x, y, max_iter=50)
                color = palette.get_color(value, 50)
                row.append(color)
            
            result.append(row)
        
        return result