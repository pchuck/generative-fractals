"""UI Manager for Tkinter interface."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional


class UIManager:
    """Manages the Tkinter user interface."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the UI manager.
        
        Args:
            root: Tkinter root widget
        """
        self.root = root
        
        # Set fixed window size
        self.window_width = 1024
        self.window_height = 768
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.update()
        
        self.width = 900
        self.height = 650
        
        # Variables that can be set from outside
        self.fractal_var = None
        self.palette_var = None  
        self.iterations_var = None
        
        self.click_handlers = []
        self.render_callback_ref = None
        
        # Track resize state to avoid continuous rendering
        self._resize_in_progress = False
        self._last_resize_time = 0
        self._pending_render = False
        
        # Track slider state for delayed render on release
        self._slider_change_time = 0
        self._slider_pending_render = False
        self._slider_timer_id = None
        self._last_trace_time = 0
        
        # Zoom selection rectangle visual feedback
        self.zoom_rect_tag = None
        
        # Create canvas later in setup_ui to ensure proper packing order
        self.canvas = None
    
    def setup_canvas(self):
        """Create and pack the canvas."""
        if not self.canvas:
            ui_frame_height = 60
            available_width = self.window_width
            available_height = self.window_height - ui_frame_height
            
            self.width = available_width
            self.height = available_height
            
            self.canvas = tk.Canvas(
                self.root, 
                width=self.width,
                height=self.height,
                highlightthickness=0
            )
            
            # Pack canvas to fill remaining space
            self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
    def setup_ui(self, fractals: Dict[str, str], palettes: Dict[str, str],
                 render_callback: Callable, reset_view_callback: Callable,
                 save_image_callback: Callable, fractal_change_callback: Optional[Callable] = None):
        """Setup the UI elements."""

        from tkinter import ttk

        if self.fractal_var is None:
            self.fractal_var = tk.StringVar()
        if self.palette_var is None:
            self.palette_var = tk.StringVar()
        if self.iterations_var is None:
            self.iterations_var = tk.IntVar(value=200)

        self.fractal_var.set(list(fractals.keys())[0])
        self.palette_var.set(list(palettes.keys())[0])
        self.render_callback_ref = render_callback

        # Store references for updating UI when restoring state
        self._fractal_dropdown = None
        self._palette_dropdown = None

        # Setup canvas first
        self.setup_canvas()

        # Create frames for UI elements at the top
        ui_frame = ttk.Frame(self.root, height=60)
        ui_frame.pack(side=tk.TOP, fill=tk.X)

        fractal_dropdown = ttk.Combobox(
            ui_frame,
            values=list(fractals.values()),
            state="readonly"
        )
        fractal_dropdown.set(list(fractals.values())[0])
        fractal_dropdown.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self._fractal_dropdown = fractal_dropdown

        def on_fractal_change(event):
            idx = fractal_dropdown.current()
            new_fractal_id = list(fractals.keys())[idx]
            # Call the change callback to save/restore state
            if fractal_change_callback:
                fractal_change_callback(new_fractal_id)
            self.fractal_var.set(new_fractal_id)
            render_callback()

        fractal_dropdown.bind("<<ComboboxSelected>>", on_fractal_change)
        
        palette_dropdown = ttk.Combobox(
            ui_frame,
            values=list(palettes.values()),
            state="readonly"
        )
        palette_dropdown.set(list(palettes.values())[0])
        palette_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        self._palette_dropdown = palette_dropdown

        def on_palette_change(event):
            idx = palette_dropdown.current()
            self.palette_var.set(list(palettes.keys())[idx])
            render_callback()

        palette_dropdown.bind("<<ComboboxSelected>>", on_palette_change)
        
        iterations_slider = ttk.Scale(
            ui_frame,
            from_=50,
            to=2000,
            variable=self.iterations_var,
            orient=tk.HORIZONTAL
        )
        iterations_slider.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        
        iter_text = tk.StringVar(value=str(self.iterations_var.get()))
        iterations_label = ttk.Label(
            ui_frame,
            textvariable=iter_text,
            font=("Arial", 10),
            foreground="#333399"
        )
        iterations_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        
        def update_iteration_label(*args):
            iter_text.set(str(self.iterations_var.get()))
        
        def on_iteration_release(event):
            render_callback()
        
        iterations_slider.bind("<<ButtonRelease-1>>", on_iteration_release)
        self.iterations_var.trace_add('write', update_iteration_label)
        
        reset_btn = ttk.Button(
            ui_frame,
            text="Reset View",
            command=lambda: (reset_view_callback(), render_callback())
        )
        reset_btn.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        save_btn = ttk.Button(
            ui_frame,
            text="Save Image",
            command=save_image_callback
        )
        save_btn.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
        
        # Bind canvas events for zoom/pan
        if self.canvas:
            self.canvas.bind("<ButtonPress-1>", self.on_click_start)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_click_end)
            
            def on_resize(event):
                if event.widget == self.root:
                    new_width = event.width
                    new_height = event.height - 60
                    
                    if new_width > 0 and new_height > 0:
                        self._resize_in_progress = True
                        self.width = new_width
                        self.height = new_height
                        self.canvas.config(width=new_width, height=new_height)
                        
                        import time as t
                        self._last_resize_time = t.time()
                        
                        def delayed_render():
                            if not self._resize_in_progress:
                                return
                            
                            if t.time() - self._last_resize_time > 0.3:
                                self._resize_in_progress = False
                                render_callback()
                        
                        self.root.after(500, delayed_render)
            
            self.root.bind("<Configure>", on_resize)
    
    def on_click_start(self, event):
        """Handle click start for zoom selection."""
        if event.widget != self.canvas:
            return
        self.drag_start = (event.x, event.y)
    
    def on_drag(self, event):
        """Handle drag for zoom selection - show selection rectangle."""
        if not hasattr(self, 'drag_start'):
            return
        
        x1, y1 = self.drag_start
        x2, y2 = event.x, event.y
        
        if self.zoom_rect_tag:
            self.canvas.delete(self.zoom_rect_tag)
        
        self.zoom_rect_tag = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="#4488ff"
        )
        self.root.update()
    
    def on_click_end(self, event):
        """Handle click end for zoom or single point zoom."""
        if event.widget != self.canvas:
            return
            
        rect_coords = None
        if self.zoom_rect_tag:
            try:
                rect_coords = self.canvas.coords(self.zoom_rect_tag)
                self.canvas.delete(self.zoom_rect_tag)
                self.zoom_rect_tag = None
            except:
                pass
        
        if not hasattr(self, 'drag_start'):
            return
        
        x1, y1 = self.drag_start
        x2, y2 = event.x, event.y
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        if dx < 10 and dy < 10:
            for handler in self.click_handlers:
                handler(event.x, event.y, zoom=2.0)
        else:
            # Pass rectangle coordinates to handlers (keyword arguments)
            if rect_coords:
                for handler in self.click_handlers:
                    handler(x=rect_coords[0], y=rect_coords[1],
                           x2=rect_coords[2], y2=rect_coords[3])
            else:
                for handler in self.click_handlers:
                    handler(x=x1, y=y1, x2=x2, y2=y2)
    
    def add_click_handler(self, handler: Callable):
        """Add a click handler callback."""
        self.click_handlers.append(handler)
    
    def display_image(self, image_data):
        """Display the rendered fractal image.
        
        Args:
            image_data: 2D numpy array of RGB values or list of lists
        """
        import numpy as np
        
        if isinstance(image_data, np.ndarray):
            height, width = image_data.shape[:2]
        else:
            height = len(image_data)
            width = len(image_data[0]) if height > 0 else 0
        
        # Remove any zoom selection rectangle
        if self.zoom_rect_tag:
            try:
                self.canvas.delete(self.zoom_rect_tag)
                self.zoom_rect_tag = None
            except:
                pass
        
        self.canvas.delete("all")
        
        preview_scale = max(1, min(self.width // width, self.height // height))
        
        display_width = min(width * preview_scale, self.width)
        display_height = min(height * preview_scale, self.height)
        
        block_size = max(1, min(
            (self.width + display_width - 1) // display_width,
            (self.height + display_height - 1) // display_height
        ))
        
        for py in range(0, height, block_size):
            for px in range(0, width, block_size):
                if isinstance(image_data, np.ndarray):
                    color = tuple(map(int, image_data[py, px]))
                else:
                    color = image_data[min(py, height - 1)][min(px, width - 1)]
                
                x1 = px * preview_scale
                y1 = py * preview_scale
                x2 = min((px + block_size) * preview_scale, self.width)
                y2 = min((py + block_size) * preview_scale, self.height)
                
                hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=hex_color,
                    outline=""
                )
        
        self.root.update()
    
    def display_zoom_preview(self, zoom_callback):
        """Display a preview of the selected zoom region using cached image."""
        return False
    
    def show_status(self, text: str):
        """Show status message."""
        self.root.title(f"Interactive Fractal Explorer - {text}")
        self.root.update()

    def update_fractal_dropdown(self, fractal_id: str, fractals: Dict[str, str]):
        """Update the fractal dropdown to show the given fractal ID.

        Args:
            fractal_id: The fractal ID to select
            fractals: Dictionary mapping fractal IDs to display names
        """
        if self._fractal_dropdown and fractal_id in fractals:
            self._fractal_dropdown.set(fractals[fractal_id])

    def update_palette_dropdown(self, palette_id: str, palettes: Dict[str, str]):
        """Update the palette dropdown to show the given palette ID.

        Args:
            palette_id: The palette ID to select
            palettes: Dictionary mapping palette IDs to display names
        """
        if self._palette_dropdown and palette_id in palettes:
            self._palette_dropdown.set(palettes[palette_id])