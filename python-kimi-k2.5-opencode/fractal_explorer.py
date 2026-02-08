#!/usr/bin/env python3
"""
Interactive Fractal Explorer using Tkinter
Supports pluggable fractal types and color palettes with zoom, pan, and customization.
"""

import tkinter as tk
from tkinter import messagebox
import multiprocessing as mp
import os
from typing import Dict, Any, Optional, TYPE_CHECKING

# Import modular components
from fractals import FractalRegistry
from fractals.mandelbrot import *   # Mandelbrot
from fractals.julia import *        # Julia variants
from fractals.burning_ship import * # Burning Ship
from fractals.tricorn import *      # Tricorn
from fractals.multibrot import *    # Multibrot (z³, z⁴, z⁵)
from fractals.phoenix import *      # Phoenix
from fractals.newton import *       # Newton
from fractals.cubic_julia import *  # Cubic Julia
from fractals.feather import *      # Feather
from fractals.spider import *       # Spider
from fractals.orbit_trap import *   # Orbit Trap Mandelbrot
from fractals.pickover_stalks import *    # Pickover Stalks
from fractals.interior_distance import *  # Interior Distance
from fractals.exterior_distance import *  # Exterior Distance
from fractals.deribail import *     # Derivative Bailout
from fractals.nova import *         # Nova (Newton's method variant)
from fractals.barnsley_fern import * # Barnsley Fern IFS
from fractals.ifs_fractals import *  # Sierpinski Triangle, Carpet, Dragon Curve, Maple Leaf
from palettes import PaletteRegistry
from palettes.standard import *     # Standard palettes
from navigation import ZoomController
from ui import UIManager
from rendering import RenderEngine

# Constants
DEFAULT_WINDOW_SIZE: str = "950x750"
DEFAULT_CANVAS_WIDTH: int = 800
DEFAULT_CANVAS_HEIGHT: int = 600
DEFAULT_ITERATIONS: int = 100
MAX_HISTORY_SIZE: int = 50
RESIZE_DEBOUNCE_MS: int = 200
RESIZE_REENABLE_DELAY_MS: int = 300
MIN_VALID_DIMENSION: int = 1

# Type checking imports for forward references
if TYPE_CHECKING:
    from tkinter import ttk
    from PIL import Image as PILImage


class FractalExplorer:
    """Main fractal explorer application."""
    
    # UI components (created dynamically by UIManager)
    fractal_var: tk.StringVar
    iter_var: tk.IntVar
    iter_label: 'ttk.Label'
    palette_var: tk.StringVar
    param_vars: Dict[str, Any]
    canvas: tk.Canvas
    status_var: tk.StringVar
    progress_var: tk.DoubleVar
    
    # Image storage
    image: Optional['PILImage.Image']
    photo: Optional[Any]
    preview_photo: Optional[Any]
    
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Interactive Fractal Explorer")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        
        # Canvas settings - initial size, will adjust to window
        self.width = DEFAULT_CANVAS_WIDTH
        self.height = DEFAULT_CANVAS_HEIGHT
        self.max_iter = DEFAULT_ITERATIONS
        self._resize_after_id = None  # For debouncing resize events
        self._disable_resize = False  # Flag to disable resize during fractal switches
        
        # Current fractal and palette
        self.fractal_name = "mandelbrot"
        self.fractal_params = {}
        self.palette_name = "smooth"
        self.palette_params = {"hue": 0.0, "saturation": 0.8, "value": 0.9}
        
        # Per-fractal storage for bounds, iteration limits, and palette selection
        self.bounds_storage = {}
        self.iter_storage = {}
        self.palette_storage = {}
        
        # Per-fractal history for undo/redo (back/forward navigation)
        self.fractal_histories = {}  # fractal_name -> list of states
        self.fractal_history_indices = {}  # fractal_name -> current index
        self.max_history_size = MAX_HISTORY_SIZE
        
        # Parallel processing
        self.num_workers = max(1, mp.cpu_count() - 1)
        
        # Controllers
        self.ui_manager = UIManager(self)
        self.zoom_controller = ZoomController(self)
        self.render_engine = RenderEngine(self)
        
        # Initialize UI
        self.ui_manager.create_ui()
        self.zoom_controller.setup_bindings()
        self._setup_keyboard_shortcuts()
        self._setup_mouse_tracking()
        self._update_window_title()
        self._load_initial_bounds()
        self._initialize_fractal_history()
        self.render()
    
    def _initialize_fractal_history(self) -> None:
        """Initialize history for the current fractal."""
        if self.fractal_name not in self.fractal_histories:
            self.fractal_histories[self.fractal_name] = []
            self.fractal_history_indices[self.fractal_name] = -1
            self._push_current_state()
    
    def _get_fractal_history(self) -> list:
        """Get history list for current fractal."""
        return self.fractal_histories.get(self.fractal_name, [])
    
    def _get_fractal_history_index(self) -> int:
        """Get history index for current fractal."""
        return self.fractal_history_indices.get(self.fractal_name, -1)
    
    def _set_fractal_history_index(self, index: int) -> None:
        """Set history index for current fractal."""
        self.fractal_history_indices[self.fractal_name] = index
    
    def _load_initial_bounds(self) -> None:
        """Load initial bounds for current fractal."""
        if self.fractal_name not in self.bounds_storage:
            fractal = FractalRegistry.create(self.fractal_name)
            self.bounds_storage[self.fractal_name] = fractal.get_default_bounds()
    
    def get_bounds(self) -> Dict[str, float]:
        """Get current viewport bounds."""
        return self.bounds_storage.get(self.fractal_name, 
                                       FractalRegistry.create(self.fractal_name).get_default_bounds())
    
    def set_bounds(self, bounds: Dict[str, float]) -> None:
        """Set viewport bounds."""
        self.bounds_storage[self.fractal_name] = bounds.copy()
    
    def render(self) -> None:
        """Render the fractal."""
        self.render_engine.render()
    
    def reset_view(self) -> None:
        """Reset to default view."""
        fractal = FractalRegistry.create(self.fractal_name)
        self.bounds_storage[self.fractal_name] = fractal.get_default_bounds()
        self.max_iter = DEFAULT_ITERATIONS
        self.iter_storage[self.fractal_name] = DEFAULT_ITERATIONS
        self.iter_var.set(DEFAULT_ITERATIONS)
        self.iter_label.configure(text=str(DEFAULT_ITERATIONS))
        self._push_current_state()
        self.render()
    
    def save_image(self) -> None:
        """Save the current image with validation and overwrite confirmation."""
        # Validate we have an image to save
        if not hasattr(self, 'image') or self.image is None:
            messagebox.showerror("Save Failed", "No image available to save. Please render a fractal first.")
            return
        
        # Create images directory if it doesn't exist
        images_dir = "images"
        try:
            os.makedirs(images_dir, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Save Failed", f"Cannot create images directory: {str(e)}")
            return
        
        # Sanitize filename (remove any problematic characters)
        safe_name = "".join(c for c in self.fractal_name if c.isalnum() or c in ('-', '_')).rstrip()
        
        # Handle edge case where filename becomes empty after sanitization
        if not safe_name:
            safe_name = "unnamed_fractal"
        
        filename = os.path.join(images_dir, f"fractal_{safe_name}_{self.max_iter}iter.png")
        
        try:
            # Check if file already exists
            if os.path.exists(filename):
                response = messagebox.askyesno("File Exists", 
                                               f"'{filename}' already exists.\nDo you want to overwrite it?")
                if not response:
                    return
            
            # Save the image
            self.image.save(filename)
            messagebox.showinfo("Save Successful", f"Image saved as {filename}")
        except PermissionError:
            messagebox.showerror("Save Failed", f"Permission denied. Cannot write to '{filename}'.\nTry a different location or check file permissions.")
        except Exception as e:
            messagebox.showerror("Save Failed", f"Failed to save image: {str(e)}")
    
    def _push_current_state(self) -> None:
        """Save current state to the current fractal's history."""
        # Initialize history for this fractal if needed
        if self.fractal_name not in self.fractal_histories:
            self.fractal_histories[self.fractal_name] = []
            self.fractal_history_indices[self.fractal_name] = -1
        
        history = self.fractal_histories[self.fractal_name]
        history_index = self.fractal_history_indices[self.fractal_name]
        
        state = {
            'bounds': self.get_bounds().copy(),
            'fractal_params': self.fractal_params.copy(),
            'palette_name': self.palette_name,
            'max_iter': self.max_iter
        }
        
        # Check if this state is identical to the current state in history
        if history and history_index >= 0 and history_index < len(history):
            current_state = history[history_index]
            if (current_state['bounds'] == state['bounds'] and
                current_state['fractal_params'] == state['fractal_params'] and
                current_state['palette_name'] == state['palette_name'] and
                current_state['max_iter'] == state['max_iter']):
                # State hasn't changed, don't push duplicate
                return
        
        # Remove any future states if we're not at the end
        if history_index < len(history) - 1:
            history[:] = history[:history_index + 1]
        
        # Add new state
        history.append(state)
        
        # Limit history size
        if len(history) > self.max_history_size:
            history.pop(0)
            self.fractal_history_indices[self.fractal_name] = len(history) - 1
        else:
            self.fractal_history_indices[self.fractal_name] += 1
        
        self._update_history_buttons()
    
    def go_back(self) -> None:
        """Navigate to previous state (undo) for current fractal."""
        history_index = self._get_fractal_history_index()
        if history_index > 0:
            self._set_fractal_history_index(history_index - 1)
            history = self._get_fractal_history()
            self._restore_state(history[self._get_fractal_history_index()])
            self._update_history_buttons()
    
    def go_forward(self) -> None:
        """Navigate to next state (redo) for current fractal."""
        history_index = self._get_fractal_history_index()
        history = self._get_fractal_history()
        if history_index < len(history) - 1:
            self._set_fractal_history_index(history_index + 1)
            self._restore_state(history[self._get_fractal_history_index()])
            self._update_history_buttons()
    
    def _update_history_buttons(self) -> None:
        """Update back/forward button states for current fractal."""
        # Check if UI manager has the buttons
        if hasattr(self, 'ui_manager') and hasattr(self.ui_manager, 'back_btn'):
            history_index = self._get_fractal_history_index()
            history = self._get_fractal_history()
            
            # Enable back button if we can go back
            if history_index > 0:
                self.ui_manager.back_btn.config(state='normal')
            else:
                self.ui_manager.back_btn.config(state='disabled')
            
            # Enable forward button if we can go forward
            if history_index < len(history) - 1:
                self.ui_manager.forward_btn.config(state='normal')
            else:
                self.ui_manager.forward_btn.config(state='disabled')
    
    def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restore application state from a history entry (same fractal only)."""
        # Restore fractal parameters
        if state.get('fractal_params'):
            self.fractal_params = state['fractal_params'].copy()
            self.ui_manager.create_fractal_params_ui()
        
        # Restore palette
        if state.get('palette_name'):
            self.palette_name = state['palette_name']
            self.palette_var.set(self.palette_name)
            self.palette_storage[self.fractal_name] = self.palette_name
        
        # Restore iteration limit
        if state.get('max_iter'):
            self.max_iter = state['max_iter']
            self.iter_storage[self.fractal_name] = self.max_iter
            self.iter_var.set(self.max_iter)
            self.iter_label.configure(text=str(self.max_iter))
        
        # Restore bounds
        self.bounds_storage[self.fractal_name] = state['bounds'].copy()
        
        # Render
        self.render()
    
    def _on_fractal_change(self, event=None) -> None:
        """Handle fractal type change."""
        # Disable resize handling during fractal switch to prevent unwanted zoom
        self._disable_resize = True
        
        # Save current bounds, iteration limit, and palette for old fractal
        self.bounds_storage[self.fractal_name] = self.get_bounds().copy()
        self.iter_storage[self.fractal_name] = self.max_iter
        self.palette_storage[self.fractal_name] = self.palette_name
        
        # Push final state to old fractal's history
        self._push_current_state()
        
        # Switch to new fractal
        self.fractal_name = self.fractal_var.get()
        self.fractal_params = {}
        
        # Initialize history for new fractal if needed
        if self.fractal_name not in self.fractal_histories:
            self.fractal_histories[self.fractal_name] = []
            self.fractal_history_indices[self.fractal_name] = -1
        
        # Update parameters UI
        self.ui_manager.create_fractal_params_ui()
        
        # Load saved bounds or use defaults
        self._load_initial_bounds()
        
        # Update window title with new fractal name
        self._update_window_title()
        
        # Load saved iteration limit or use default
        self.max_iter = self.iter_storage.get(self.fractal_name, DEFAULT_ITERATIONS)
        self.iter_var.set(self.max_iter)
        self.iter_label.configure(text=f"{self.max_iter}")
        
        # Load saved palette or use default
        saved_palette = self.palette_storage.get(self.fractal_name)
        if saved_palette and saved_palette in PaletteRegistry.list_palettes():
            self.palette_name = saved_palette
            self.palette_var.set(saved_palette)
        else:
            # Use default palette if no saved preference
            self.palette_name = "smooth"
            self.palette_var.set("smooth")
        self.palette_params = {}
        
        # Push initial state for new fractal
        self._push_current_state()
        
        # Update button states for new fractal's history
        self._update_history_buttons()
        
        # Re-enable resize handling after a short delay to let any pending resize events settle
        self.root.after(RESIZE_REENABLE_DELAY_MS, self._enable_resize)
        
        self.render()
    
    def _enable_resize(self) -> None:
        """Re-enable resize handling after fractal switch."""
        self._disable_resize = False
        # Cancel any pending resize that might have accumulated during the switch
        if self._resize_after_id:
            self.root.after_cancel(self._resize_after_id)
            self._resize_after_id = None
    
    def _on_palette_change(self, event=None) -> None:
        """Handle palette change."""
        self.palette_name = self.palette_var.get()
        self.palette_params = {}
        # Save palette preference for current fractal
        self.palette_storage[self.fractal_name] = self.palette_name
        self._push_current_state()
        self.render()
    
    def _on_param_change(self, event=None) -> None:
        """Handle fractal parameter change."""
        for param_name, var in self.param_vars.items():
            self.fractal_params[param_name] = var.get()
        self._push_current_state()
        self.render()
    
    def _on_slider_motion(self, event=None) -> None:
        """Update label while dragging."""
        self.iter_label.configure(text=f"{int(self.iter_var.get())}")
    
    def _on_slider_release(self, event=None) -> None:
        """Render on slider release."""
        self.max_iter = int(self.iter_var.get())
        self.iter_storage[self.fractal_name] = self.max_iter
        self._push_current_state()
        self.render()
    
    def _on_canvas_resize(self, event=None) -> None:
        """Handle canvas resize with debouncing."""
        # Skip resize handling during fractal switches
        if self._disable_resize:
            return
        
        if self._resize_after_id:
            self.root.after_cancel(self._resize_after_id)
        
        # Debounce resize - wait after resize ends before re-rendering
        self._resize_after_id = self.root.after(RESIZE_DEBOUNCE_MS, self._do_resize)
    
    def _do_resize(self) -> None:
        """Actually perform the resize and re-render."""
        self._resize_after_id = None
        
        # Get actual canvas size
        new_width = self.canvas.winfo_width()
        new_height = self.canvas.winfo_height()
        
        # Only update if size actually changed and is valid
        if new_width > MIN_VALID_DIMENSION and new_height > MIN_VALID_DIMENSION and (new_width != self.width or new_height != self.height):
            # Adjust bounds to maintain the center point and aspect ratio
            old_width, old_height = self.width, self.height
            self.width = new_width
            self.height = new_height
            
            # Update bounds to maintain the visible area while adjusting for new aspect ratio
            bounds = self.get_bounds()
            old_x_range = bounds["xmax"] - bounds["xmin"]
            old_y_range = bounds["ymax"] - bounds["ymin"]
            old_aspect = old_width / old_height
            new_aspect = self.width / self.height
            
            center_x = (bounds["xmin"] + bounds["xmax"]) / 2
            center_y = (bounds["ymin"] + bounds["ymax"]) / 2
            
            if new_aspect > old_aspect:
                # Window got wider - expand x range
                new_y_range = old_y_range
                new_x_range = new_y_range * new_aspect
            else:
                # Window got taller - expand y range
                new_x_range = old_x_range
                new_y_range = new_x_range / new_aspect
            
            bounds["xmin"] = center_x - new_x_range / 2
            bounds["xmax"] = center_x + new_x_range / 2
            bounds["ymin"] = center_y - new_y_range / 2
            bounds["ymax"] = center_y + new_y_range / 2
            
            self.set_bounds(bounds)
            self.render()
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for common actions."""
        # R - Reset view
        self.root.bind('<Key-r>', lambda e: self.reset_view())
        self.root.bind('<Key-R>', lambda e: self.reset_view())
        
        # B - Go back
        self.root.bind('<Key-b>', lambda e: self.go_back())
        self.root.bind('<Key-B>', lambda e: self.go_back())
        
        # F - Go forward
        self.root.bind('<Key-f>', lambda e: self.go_forward())
        self.root.bind('<Key-F>', lambda e: self.go_forward())
        
        # Ctrl+S - Save image
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-S>', lambda e: self.save_image())
        
        # F1 - About/Help
        self.root.bind('<Key-F1>', lambda e: self.show_about())
    
    def _setup_mouse_tracking(self) -> None:
        """Setup mouse motion tracking to show coordinates."""
        self.canvas.bind('<Motion>', self._on_mouse_move)
    
    def _on_mouse_move(self, event) -> None:
        """Update status bar with mouse coordinates."""
        try:
            # Convert screen coordinates to complex plane
            bounds = self.get_bounds()
            x_range = bounds['xmax'] - bounds['xmin']
            y_range = bounds['ymax'] - bounds['ymin']
            
            x = bounds['xmin'] + (event.x / self.width) * x_range
            y = bounds['ymax'] - (event.y / self.height) * y_range
            
            # Update status with coordinates
            self.status_var.set(f"Mouse: ({x:.6f}, {y:.6f})")
        except Exception:
            pass  # Silently fail if bounds not available
    
    def _update_window_title(self) -> None:
        """Update window title to show current fractal."""
        self.root.title(f"Fractal Explorer - {self.fractal_name}")
    
    def show_about(self) -> None:
        """Show About dialog with version and credits."""
        about_text = """Fractal Explorer v2.0

An interactive fractal visualization application built with Python and Tkinter.

Features:
• 27 Fractal Types (IFS and Escape-time)
• 8 Color Palettes (HSV, Fire, Ocean, etc.)
• Parallel Rendering (Multi-core support)
• Interactive Zoom and Pan
• History Navigation (Undo/Redo)
• Per-Fractal State Persistence

Keyboard Shortcuts:
  R - Reset view
  B - Go back
  F - Go forward
  Ctrl+S - Save image
  F1 - This help

Created with Python 3, NumPy, PIL, and Tkinter.
License: MIT

© 2024 Fractal Explorer Team"""
        
        messagebox.showinfo("About Fractal Explorer", about_text)


def main() -> None:
    root = tk.Tk()
    app = FractalExplorer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
