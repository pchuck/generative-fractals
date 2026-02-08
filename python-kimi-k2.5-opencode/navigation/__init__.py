"""Zoom controller for fractal navigation."""

from typing import Tuple, Optional
from PIL import ImageTk

# Constants
MIN_DRAG_THRESHOLD: int = 5  # Pixels
ZOOM_IN_FACTOR: float = 0.5
ZOOM_OUT_FACTOR: float = 2.0
WHEEL_ZOOM_IN_FACTOR: float = 0.8
WHEEL_ZOOM_OUT_FACTOR: float = 1.25


class ZoomController:
    """Handles zoom operations, mouse events, and preview rendering."""
    
    def __init__(self, app) -> None:
        """
        Initialize zoom controller.
        
        Args:
            app: The FractalExplorer instance (provides canvas, image, width, height, etc.)
        """
        self.app = app
        self.drag_start: Optional[Tuple[int, int]] = None
        self.drag_current: Optional[Tuple[int, int]] = None
        self.selection_rect: Optional[int] = None
        
    def setup_bindings(self) -> None:
        """Setup mouse event bindings on the canvas."""
        canvas = self.app.canvas
        canvas.bind("<Button-1>", self._on_mouse_down)
        canvas.bind("<B1-Motion>", self._on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux scroll up
        canvas.bind("<Button-5>", self._on_mouse_wheel)  # Linux scroll down
        
    def _on_mouse_down(self, event) -> None:
        """Start selection/zoom."""
        if self.app.render_engine.is_busy():
            return
        self.drag_start = (event.x, event.y)
        self.drag_current = (event.x, event.y)
    
    def _on_mouse_drag(self, event) -> None:
        """Draw selection rectangle."""
        if not self.drag_start or self.app.render_engine.is_busy():
            return
        self.drag_current = (event.x, event.y)
        
        x1, y1 = self.drag_start
        x2, y2 = self.drag_current
        
        if self.selection_rect:
            self.app.canvas.coords(self.selection_rect, x1, y1, x2, y2)
        else:
            self.selection_rect = self.app.canvas.create_rectangle(
                x1, y1, x2, y2, outline="white", width=2, dash=(5, 5)
            )
    
    def _on_mouse_up(self, event) -> None:
        """Complete selection/zoom operation."""
        if not self.drag_start:
            return
        
        x1, y1 = self.drag_start
        x2, y2 = event.x, event.y
        
        # Remove selection rectangle
        if self.selection_rect:
            self.app.canvas.delete(self.selection_rect)
            self.selection_rect = None
        
        # Calculate drag distance
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        if dx < MIN_DRAG_THRESHOLD and dy < MIN_DRAG_THRESHOLD:
            # Click without significant drag - zoom in at point
            self.zoom(x2, y2, ZOOM_IN_FACTOR)
        else:
            # Selection zoom - calculate new bounds from selection
            self._selection_zoom(x1, y1, x2, y2)
        
        self.drag_start = None
        self.drag_current = None
    
    def _on_mouse_wheel(self, event) -> None:
        """Handle mouse wheel for zooming."""
        if self.app.render_engine.is_busy():
            return
        
        # Determine zoom direction
        if event.num == 4 or event.delta > 0:
            factor = WHEEL_ZOOM_IN_FACTOR  # Zoom in
        else:
            factor = WHEEL_ZOOM_OUT_FACTOR  # Zoom out
        
        self.zoom(event.x, event.y, factor)
    
    def zoom(self, x: int, y: int, factor: float) -> None:
        """
        Zoom at specific point.
        
        Args:
            x, y: Pixel coordinates to zoom towards
            factor: Zoom factor (< 1 zoom in, > 1 zoom out)
        """
        # Convert pixel to complex coordinates
        c = self.screen_to_complex(x, y)
        
        # Get current bounds
        bounds = self.app.get_bounds()
        x_min, x_max = bounds["xmin"], bounds["xmax"]
        y_min, y_max = bounds["ymin"], bounds["ymax"]
        
        # Calculate new ranges
        x_range = (x_max - x_min) * factor
        y_range = (y_max - y_min) * factor
        
        # Calculate new bounds centered on zoom point
        new_x_min = c.real - x_range * (x / self.app.width)
        new_x_max = new_x_min + x_range
        new_y_max = c.imag + y_range * ((self.app.height - y) / self.app.height)
        new_y_min = new_y_max - y_range
        
        # Update bounds
        bounds["xmin"] = new_x_min
        bounds["xmax"] = new_x_max
        bounds["ymin"] = new_y_min
        bounds["ymax"] = new_y_max
        
        self.app.set_bounds(bounds)
        self.app._push_current_state()
        self.app.render()
    
    def _selection_zoom(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Zoom to selected rectangle."""
        # Ensure proper ordering
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # Convert corners to complex coordinates
        c1 = self.screen_to_complex(x1, y1)
        c2 = self.screen_to_complex(x2, y2)
        
        # Set new bounds
        bounds = self.app.get_bounds()
        bounds["xmin"] = min(c1.real, c2.real)
        bounds["xmax"] = max(c1.real, c2.real)
        bounds["ymin"] = min(c1.imag, c2.imag)
        bounds["ymax"] = max(c1.imag, c2.imag)
        
        self.app.set_bounds(bounds)
        self.app._push_current_state()
        self.app.render()
    
    def screen_to_complex(self, x: int, y: int) -> complex:
        """
        Convert screen coordinates to complex plane coordinates.
        
        Args:
            x, y: Screen pixel coordinates
            
        Returns:
            Complex number corresponding to screen position
        """
        bounds = self.app.get_bounds()
        x_min, x_max = bounds["xmin"], bounds["xmax"]
        y_min, y_max = bounds["ymin"], bounds["ymax"]
        
        # Map pixel coordinates to complex plane
        real = x_min + (x / self.app.width) * (x_max - x_min)
        imag = y_max - (y / self.app.height) * (y_max - y_min)
        
        return complex(real, imag)
    
    def _display_zoom_preview(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Display preview of zoomed region using subsampled image."""
        try:
            if not hasattr(self.app, 'image') or self.app.image is None:
                return
            
            # Calculate selection rectangle in image coordinates
            img_width, img_height = self.app.image.size
            
            # Convert canvas coordinates to image coordinates
            px1 = int((x1 / self.app.width) * img_width)
            py1 = int((y1 / self.app.height) * img_height)
            px2 = int((x2 / self.app.width) * img_width)
            py2 = int((y2 / self.app.height) * img_height)
            
            # Ensure proper ordering
            px1, px2 = max(0, min(px1, px2)), min(img_width, max(px1, px2))
            py1, py2 = max(0, min(py1, py2)), min(img_height, max(py1, py2))
            
            # Check if selection is large enough
            if px2 - px1 < MIN_DRAG_THRESHOLD or py2 - py1 < MIN_DRAG_THRESHOLD:
                return
            
            # Crop and resize the selected region
            cropped = self.app.image.crop((px1, py1, px2, py2))
            preview = cropped.resize((self.app.width, self.app.height), 0)  # 0 = NEAREST
            
            # Display preview
            self.app.preview_photo = ImageTk.PhotoImage(preview)
            self.app.canvas.delete("all")
            self.app.canvas.create_image(0, 0, anchor="nw", image=self.app.preview_photo)
            
            # Redraw selection rectangle
            self.selection_rect = self.app.canvas.create_rectangle(
                x1, y1, x2, y2, outline="white", width=2, dash=(5, 5)
            )
            
        except Exception:
            # Silently fail if preview can't be created
            pass
    
    def _clear_zoom_preview(self) -> None:
        """Clear preview and restore original image."""
        try:
            if hasattr(self.app, 'photo') and self.app.photo:
                self.app.canvas.delete("all")
                self.app.canvas.create_image(0, 0, anchor="nw", image=self.app.photo)
        except Exception:
            pass
