"""Render engine for fractal computation and display."""

import numpy as np
from PIL import Image, ImageTk
import threading
from typing import Optional, Any, TYPE_CHECKING

# Import at module level to avoid repeated imports in render method
from fractals import FractalRegistry
from fractals.ifs_base import IFSFractalBase

from .parallel import compute_fractal_parallel

if TYPE_CHECKING:
    pass  # Avoid circular imports

# Constants
THREAD_JOIN_TIMEOUT: float = 1.0
DEFAULT_IFS_POINTS: int = 100000
IFS_GAMMA: float = 0.5
IFS_COLOR_TINT: tuple = (0.3, 0.9, 0.2)  # RGB multipliers
IFS_PROGRESS_INTERVAL: int = 10000  # Update progress every N points

# Re-export for convenience
__all__ = ['RenderEngine', 'compute_fractal_parallel']


class RenderEngine:
    """Handles fractal rendering, threading, and image display."""
    
    def __init__(self, app: Any) -> None:
        """
        Initialize render engine.
        
        Args:
            app: The FractalExplorer instance
        """
        self.app = app
        self.is_rendering: bool = False
        self.render_thread: Optional[threading.Thread] = None
        self._cancel_render: bool = False
        
    def render(self) -> None:
        """Render the fractal using parallel processing."""
        if self.is_rendering:
            self._cancel_render = True
            if self.render_thread:
                self.render_thread.join(timeout=THREAD_JOIN_TIMEOUT)
                # Check if thread is still alive after timeout
                if self.render_thread.is_alive():
                    self.app.status_var.set("Warning: Render thread did not terminate in time")
            self._cancel_render = False
        
        self.is_rendering = True
        self.app.status_var.set(f"Rendering {self.app.fractal_name}...")
        self.app.progress_var.set(0)
        
        # Check if this is an IFS fractal
        try:
            fractal_class = FractalRegistry.get(self.app.fractal_name)
            if fractal_class is None:
                raise ValueError(f"Unknown fractal: {self.app.fractal_name}")
            is_ifs = issubclass(fractal_class, IFSFractalBase)
        except Exception as e:
            self.app.status_var.set(f"Error checking fractal type: {str(e)}")
            self.is_rendering = False
            return
        
        if is_ifs:
            self._render_ifs()
        else:
            self._render_escape_time()
    
    def _render_escape_time(self) -> None:
        """Render escape-time fractal using parallel processing."""
        def render_thread() -> None:
            try:
                bounds = self.app.get_bounds()
                
                img_array = compute_fractal_parallel(
                    width=self.app.width,
                    height=self.app.height,
                    bounds=bounds,
                    fractal_name=self.app.fractal_name,
                    fractal_params=self.app.fractal_params,
                    max_iter=self.app.max_iter,
                    palette_name=self.app.palette_name,
                    palette_params=self.app.palette_params,
                    num_workers=self.app.num_workers,
                    progress_callback=self._progress_callback,
                    cancel_check=self._cancel_check
                )
                
                if img_array is not None and not self._cancel_render:
                    self.app.root.after(0, lambda: self.display_image(img_array))
            except Exception as e:
                self.app.root.after(0, lambda: self.app.status_var.set(f"Error: {str(e)}"))
            finally:
                self.is_rendering = False
        
        self.render_thread = threading.Thread(target=render_thread, daemon=True)
        self.render_thread.start()
    
    def _render_ifs(self) -> None:
        """Render IFS fractal using point generation with incremental progress."""
        def render_thread() -> None:
            try:
                fractal_class = FractalRegistry.get(self.app.fractal_name)
                if fractal_class is None:
                    raise ValueError(f"Unknown fractal: {self.app.fractal_name}")
                
                # Create IFS fractal instance
                ifs_fractal = fractal_class(**self.app.fractal_params)
                
                # Get number of points to generate
                num_points = getattr(ifs_fractal, 'num_points', DEFAULT_IFS_POINTS)
                
                # Generate points with progress updates
                points = ifs_fractal.generate_points(num_points)
                progress = 10  # Start at 10%
                self.app.root.after(0, lambda p=progress: self.app.progress_var.set(p))
                
                # Create histogram/image buffer
                bounds = self.app.get_bounds()
                width, height = self.app.width, self.app.height
                img_buffer = np.zeros((height, width), dtype=np.float64)
                
                # Map points to pixel coordinates with incremental progress
                x_min, x_max = bounds['xmin'], bounds['xmax']
                y_min, y_max = bounds['ymin'], bounds['ymax']
                
                x_scale = width / (x_max - x_min)
                y_scale = height / (y_max - y_min)
                
                # Vectorized coordinate transformation
                px = ((points[:, 0] - x_min) * x_scale).astype(np.int32)
                py = ((y_max - points[:, 1]) * y_scale).astype(np.int32)
                
                # Filter points within bounds
                mask = (px >= 0) & (px < width) & (py >= 0) & (py < height)
                px_valid = px[mask]
                py_valid = py[mask]
                
                # Accumulate points
                np.add.at(img_buffer, (py_valid, px_valid), 1)
                
                # Update progress during accumulation (if many points)
                if num_points > 50000:
                    progress = 40
                    self.app.root.after(0, lambda p=progress: self.app.progress_var.set(p))
                
                # Normalize
                max_val = img_buffer.max()
                if max_val > 0:
                    img_buffer = img_buffer / max_val
                
                if num_points > 50000:
                    progress = 60
                    self.app.root.after(0, lambda p=progress: self.app.progress_var.set(p))
                
                # Vectorized RGB conversion
                intensity = (255 * img_buffer ** IFS_GAMMA).astype(np.uint8)
                
                # Create RGB image with color tint
                rgb_img = np.zeros((height, width, 3), dtype=np.uint8)
                rgb_img[:, :, 0] = (intensity * IFS_COLOR_TINT[0]).astype(np.uint8)
                rgb_img[:, :, 1] = (intensity * IFS_COLOR_TINT[1]).astype(np.uint8)
                rgb_img[:, :, 2] = (intensity * IFS_COLOR_TINT[2]).astype(np.uint8)
                
                progress = 90
                self.app.root.after(0, lambda p=progress: self.app.progress_var.set(p))
                
                if rgb_img is not None and not self._cancel_render:
                    self.app.root.after(0, lambda: self.display_image(rgb_img))
            except Exception as e:
                self.app.root.after(0, lambda: self.app.status_var.set(f"Error: {str(e)}"))
            finally:
                self.is_rendering = False
        
        self.render_thread = threading.Thread(target=render_thread, daemon=True)
        self.render_thread.start()
    
    def _cancel_check(self) -> bool:
        """Check if rendering should be cancelled."""
        return self._cancel_render
    
    def _progress_callback(self, progress: float) -> None:
        """Update progress bar."""
        self.app.root.after(0, lambda: self.app.progress_var.set(progress))
    
    def display_image(self, img_array: np.ndarray) -> None:
        """Display the rendered image."""
        try:
            # Validate the image array
            if img_array is None:
                self.app.status_var.set("Error: No image data to display")
                return
            
            if not isinstance(img_array, np.ndarray):
                self.app.status_var.set("Error: Invalid image data type")
                return
            
            # Check for NaN or Inf values in the array
            if np.isnan(img_array).any() or np.isinf(img_array).any():
                self.app.status_var.set("Error: Image contains invalid values (NaN/Inf)")
                return
            
            self.app.image = Image.fromarray(img_array)
            self.app.photo = ImageTk.PhotoImage(self.app.image)
            
            self.app.canvas.delete("all")
            self.app.canvas.create_image(0, 0, anchor="nw", image=self.app.photo)
            
            bounds = self.app.get_bounds()
            info = (f"{self.app.fractal_name}: x=[{bounds['xmin']:.6f}, {bounds['xmax']:.6f}], "
                    f"y=[{bounds['ymin']:.6f}, {bounds['ymax']:.6f}]")
            self.app.status_var.set(info)
            self.app.progress_var.set(100)
        except Exception as e:
            self.app.status_var.set(f"Error displaying image: {str(e)}")
    
    def request_cancel(self) -> None:
        """Request cancellation of current render."""
        self._cancel_render = True
        
    def is_busy(self) -> bool:
        """Check if currently rendering."""
        return self.is_rendering
