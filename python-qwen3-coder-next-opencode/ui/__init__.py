"""UI manager for fractal explorer."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Dict, Any, Optional

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class UIManager:
    """Manages the user interface for fractal explorer."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Interactive Fractal Explorer")
        
        self.fractal_registry = None
        self.palette_registry = None
        
        self.current_fractal_name = "mandelbrot"
        self.current_palette_name = "smooth"
        self.iterations = 200
        
        self.zoom_state = {
            'drag_start': None,
            'drag_rect': None
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        sidebar = ttk.Frame(main_frame, width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self._setup_sidebar(sidebar)
        self._setup_canvas(canvas_frame)
        self._setup_toolbar(sidebar)
    
    def _setup_sidebar(self, parent: ttk.Frame):
        """Setup the fractal and palette selection sidebar."""
        ttk.Label(parent, text="Fractal:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.fractal_combo = ttk.Combobox(parent, state='readonly', width=25)
        self.fractal_combo.pack(fill=tk.X, pady=(0, 10))
        self.fractal_combo.bind('<<ComboboxSelected>>', lambda e: self.on_fractal_change())
        
        ttk.Label(parent, text="Color Palette:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.palette_combo = ttk.Combobox(parent, state='readonly', width=25)
        self.palette_combo.pack(fill=tk.X, pady=(0, 10))
        self.palette_combo.bind('<<ComboboxSelected>>', lambda e: self.on_palette_change())
        
        ttk.Label(parent, text="Iterations:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.iteration_scale = ttk.Scale(parent, from_=50, to=2000, 
                                         orient=tk.HORIZONTAL)
        self.iteration_scale.pack(fill=tk.X, pady=(0, 10))
        self.iteration_scale.set(200)
        self.iteration_scale.bind('<ButtonRelease-1>', lambda e: self.on_iteration_change())
        
        self.iteration_label = ttk.Label(parent, text="200 iterations")
        self.iteration_label.pack(anchor=tk.W, pady=(0, 20))
        
        self.param_frame = ttk.LabelFrame(parent, text="Parameters")
        self.param_frame.pack(fill=tk.X)
        
        self.param_widgets: Dict[str, Any] = {}
    
    def _setup_canvas(self, parent: ttk.Frame):
        """Setup the fractal canvas."""
        self.canvas = tk.Canvas(parent, bg='black', cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.image = None
        self.photo = None
        
        self.canvas.bind('<Configure>', lambda e: self.on_resize())
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<MouseWheel>', self.on_wheel)
        
        parent.bind('<Configure>', lambda e: self.on_resize())
    
    def _setup_toolbar(self, parent: ttk.Frame):
        """Setup toolbar buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Reset View", 
                  command=self.on_reset_view).pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame, text="Save Image", 
                  command=self.on_save_image).pack(fill=tk.X, pady=2)
    
    def set_registries(self, fractal_registry: dict, palette_registry: dict):
        """Set the registries for fractals and palettes."""
        self.fractal_registry = fractal_registry
        self.palette_registry = palette_registry
        
        fractal_names = [f[1].name for f in sorted(fractal_registry.items(), key=lambda x: x[1].name)]
        self.fractal_combo['values'] = fractal_names
        
        palette_names = [p[1].name for p in sorted(palette_registry.items(), key=lambda x: x[1].name)]
        self.palette_combo['values'] = palette_names
        
        if fractal_names:
            self.fractal_combo.current(0)
            self.on_fractal_change()
        
        if palette_names:
            self.palette_combo.current(0)
    
    def on_fractal_change(self):
        """Handle fractal change."""
        selected = self.fractal_combo.get()
        self.current_fractal_name = selected
        self.show_fractal_parameters()
    
    def on_palette_change(self):
        """Handle palette change."""
        selected = self.palette_combo.get()
        self.current_palette_name = selected
    
    def on_iteration_change(self):
        """Handle iteration slider change."""
        val = int(self.iteration_scale.get())
        self.iteration_label.config(text=f"{val} iterations")
    
    def show_fractal_parameters(self):
        """Show fractal-specific parameters."""
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        self.param_widgets.clear()
    
    def on_resize(self):
        """Handle canvas resize."""
        if hasattr(self, 'current_fractal') and self.current_fractal:
            self.render()
    
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        self.zoom_state['drag_start'] = (event.x, event.y)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag."""
        if self.zoom_state['drag_start']:
            start_x, start_y = self.zoom_state['drag_start']
            
            if hasattr(self, 'zoom_rect_id'):
                self.canvas.delete(self.zoom_rect_id)
            
            self.zoom_rect_id = self.canvas.create_rectangle(
                start_x, start_y, event.x, event.y,
                outline='red', width=2, dash=(4, 4)
            )
    
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        if self.zoom_state['drag_start']:
            start_x, start_y = self.zoom_state['drag_start']
            
            if hasattr(self, 'zoom_rect_id'):
                self.canvas.delete(self.zoom_rect_id)
                delattr(self, 'zoom_rect_id')
            
            if abs(event.x - start_x) > 10 or abs(event.y - start_y) > 10:
                self.zoom_to_rect(start_x, start_y, event.x, event.y)
            
            self.zoom_state['drag_start'] = None
    
    def on_wheel(self, event):
        """Handle mouse wheel zoom."""
        zoom_factor = 1.1 if event.delta < 0 else 0.9
        self.zoom_at_cursor(event.x, event.y, zoom_factor)
    
    def zoom_to_rect(self, x1: int, y1: int, x2: int, y2: int):
        """Zoom to a rectangular region."""
        if hasattr(self, 'zoom_controller'):
            result = self.zoom_controller.zoom_rect(x1, y1, x2, y2)
            if result:
                self.render()
    
    def zoom_at_cursor(self, px: int, py: int, factor: float):
        """Zoom in/out at cursor position."""
        if hasattr(self, 'zoom_controller'):
            self.zoom_controller.zoom_at(px, py, factor)
            self.render()
    
    def on_reset_view(self):
        """Reset to default view."""
        if hasattr(self, 'zoom_controller') and hasattr(self, 'current_fractal'):
            self.zoom_controller.set_fractional_view(0.0, 1.0, 0.0, 1.0)
        self.render()
    
    def on_save_image(self):
        """Save the current fractal as PNG."""
        if not hasattr(self, 'current_fractal'):
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.save_image(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
    
    def set_zoom_controller(self, zoom_controller):
        """Set the zoom controller."""
        self.zoom_controller = zoom_controller
    
    def set_fractal(self, fractal):
        """Set the current fractal."""
        self.current_fractal = fractal
    
    def set_palette(self, palette):
        """Set the current palette."""
        self.current_palette = palette
    
    def set_max_iterations(self, iterations: int):
        """Set the maximum iterations."""
        self.iterations = iterations
    
    def render(self):
        """Trigger a render (should be implemented by subclass)."""
        pass
    
    def save_image(self, file_path: str):
        """Save image to file (should be implemented by subclass)."""
        pass


__all__ = ['UIManager']
