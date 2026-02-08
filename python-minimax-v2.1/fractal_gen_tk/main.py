#!/usr/bin/env python3
"""Interactive Fractal Generator with Tkinter."""

import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

from fractals import FractalFactory, Phoenix
from palettes import PaletteFactory


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase class name to snake_case for factory lookup.
    
    Examples: 'Mandelbrot' → 'mandelbrot', 'Julia3' → 'julia3'
    """
    # Insert underscore before capital letters (except first char), then lowercase
    snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
    return snake.lower()

# Import UI panels for modularity
from ui import JuliaPanel, MultibrotPanel, PhoenixPanel


def _create_param_panel(fractal_type_name: str, parent, fractal, on_change):
    """Factory function to create the appropriate parameter panel for a fractal type.
    
    Returns:
        A panel instance, or None if no parameters needed
    """
    if "Julia" in fractal_type_name and hasattr(fractal, 'set_c'):
        return JuliaPanel(parent, fractal, on_change)
    elif fractal_type_name == "Multibrot":
        return MultibrotPanel(parent, fractal, on_change)
    elif fractal_type_name == "Phoenix":
        return PhoenixPanel(parent, fractal, on_change)
    return None


# Worker for parallel computation - must be at module level for pickling
def _compute_strip(args):
    """Compute a horizontal strip of the fractal."""
    from fractals import FractalFactory
    
    y_start, y_end = args[0], args[1]
    x_min, x_max = args[2], args[3]
    y_min_orig, y_max_orig = args[4], args[5]
    width, height = args[6], args[7]
    max_iter = args[8]
    fractal_name = args[9] if len(args) > 9 else None
    
    # Extract optional parameters (Phoenix marker + values, Julia/Multibrot params)
    extra_params = args[10] if len(args) > 10 else None
    
    fractal = FractalFactory.create(fractal_name)
    
    # Apply custom parameters
    if extra_params is not None:
        if isinstance(extra_params, tuple) and extra_params and extra_params[0] == 'phoenix':
            # Phoenix: marker + c_real, c_imag, p (for consistency with other checks)
            _, c_re, c_im, p_val = extra_params
            fractal.c = complex(c_re, c_im)
            fractal.p = p_val
        elif hasattr(fractal, 'set_c') and len(extra_params) == 4:
            # Julia types: c_real, c_imag, z0_real, z0_imag
            c_real, c_imag, z0_real, z0_imag = extra_params
            fractal.set_c(c_real, c_imag)
            if hasattr(fractal, 'set_z0'):
                fractal.set_z0(z0_real, z0_imag)
        elif hasattr(fractal, 'power') and not isinstance(fractal, Phoenix) and len(extra_params) == 1:
            # Multibrot: just power (exclude Phoenix which also has power attr)
            fractal.power = extra_params[0]
    
    # Exact y values for this strip (inverted: top of image = higher Y)
    y = np.linspace(
        y_max_orig - (y_start / height) * (y_max_orig - y_min_orig),
        y_max_orig - ((y_end - 1) / height) * (y_max_orig - y_min_orig),
        y_end - y_start
    )
    
    x = np.linspace(x_min, x_max, width)
    X_strip, Y_strip = np.meshgrid(x, y)
    iterations = fractal.calculate(X_strip, Y_strip, max_iter)
    
    return (y_start, y_end, iterations)


class FractalApp:
    """Main application for fractal rendering."""
    
    # Default view bounds per fractal type (x_min, x_max, y_min, y_max)
    # Keys are class names in snake_case format for consistent lookup via _camel_to_snake()
    DEFAULT_BOUNDS = {
        "mandelbrot": (-2.0, 0.7, -1.3, 1.3),
        "julia": (-1.5, 1.5, -1.2, 1.2),
        "julia3": (-1.5, 1.5, -1.2, 1.2),
        "burning_ship": (-2.0, 0.7, -2.0, 0.6),  # Shifted down for ship shape
        "collatz": (-5.0, 5.0, -5.0, 5.0),  # Extended range as Collatz is larger
        "multibrot": (-2.0, 1.5, -1.5, 1.5),  # Similar to Mandelbrot but slightly wider
        "phoenix": (-2.5, 1.5, -1.8, 1.8),  # Wide view for Phoenix symmetry
    }
    
    def __init__(self, root):
        self.root = root
        root.title("Fractal Generator")
        root.geometry("900x700")
        
        self.width, self.height = 800, 600
        self.max_iter = 250
        self.palette_name = "Rainbow"
        
        self.selection_start = None
        self.selection_end = None
        self.current_render = None
        self.photo_image = None
        
        self.is_processing = False
        self.pending_render_id = None
        self.resize_timer_id = None
        self.use_parallel = tk.BooleanVar(value=True)
        self.num_workers = max(2, multiprocessing.cpu_count())
        
        # Initialize fractal based on default selection (before UI setup)
        self.fractal_var = tk.StringVar(value="Mandelbrot")
        self._current_fractal_type = "Mandelbrot"
        self.fractal = FractalFactory.create(self.fractal_var.get())
        
        # Set appropriate initial bounds for the fractal type
        key = _camel_to_snake(type(self.fractal).__name__)
        init_bounds = self.DEFAULT_BOUNDS.get(key, (-2.0, 1.0, -1.5, 1.5))
        self.x_min, self.x_max, self.y_min, self.y_max = init_bounds

        self._setup_ui()
        
        # Create initial parameter panel
        self.active_panel = _create_param_panel(
            self.fractal_var.get(), 
            self.param_container, 
            self.fractal, 
            self.render
        )
        if self.active_panel:
            self.active_panel.grid()
    
    def _setup_ui(self):
        """Create UI elements."""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid weights for expansion
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Controls frame
        ctrl = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        ctrl.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Fractal type dropdown
        ttk.Label(ctrl, text="Type:").grid(row=0, column=0, padx=(0, 5))
        fractal_types = FractalFactory.list_types()
        cb1 = ttk.Combobox(ctrl, textvariable=self.fractal_var, values=fractal_types,
                           state="readonly", width=18)
        cb1.grid(row=0, column=1, padx=(0, 15))
        
        # Palette dropdown  
        ttk.Label(ctrl, text="Palette:").grid(row=0, column=2, padx=(0, 5))
        self.palette_var = tk.StringVar(value=self.palette_name)
        cb2 = ttk.Combobox(ctrl, textvariable=self.palette_var,
                           values=PaletteFactory.list_names(), state="readonly", width=12)
        cb2.grid(row=0, column=3, padx=(0, 15))
        
        # Iteration slider
        ttk.Label(ctrl, text="Iter:").grid(row=0, column=4)
        self.iter_var = tk.StringVar(value=str(self.max_iter))
        iter_scale = ttk.Scale(ctrl, from_=20, to=4096,
                               orient=tk.HORIZONTAL)
        iter_scale.grid(row=0, column=5, sticky=(tk.W, tk.E), padx=(5, 0))
        
        def on_iter_drag(value):
            self.max_iter = int(float(value))
            self.iter_var.set(str(self.max_iter))
        
        def on_iter_release(event):
            if not self.is_processing:
                self.render()
        
        iter_scale.configure(command=on_iter_drag)
        iter_scale.bind("<ButtonRelease-1>", on_iter_release)
        
        ttk.Label(ctrl, textvariable=self.iter_var, width=4).grid(row=0, column=6, padx=(5, 15))
        
        # Checkbox and buttons
        ttk.Checkbutton(ctrl, text="Parallel", variable=self.use_parallel,
                        command=lambda: self.render() if self.current_render else None).grid(row=0, column=7)
        ttk.Button(ctrl, text="Reset View", command=self._reset_view).grid(row=0, column=8, padx=(15, 0))
        ttk.Button(ctrl, text="Save JPG", command=self._on_save).grid(row=0, column=9, padx=(5, 0))
        
        # Bind combobox selection changes
        cb1.bind("<<ComboboxSelected>>", self._on_fractal_select)
        cb2.bind("<<ComboboxSelected>>", self._on_palette_select)
        
        # Parameter panel container row (grid at row 1, populated dynamically)
        self.param_container = ttk.Frame(ctrl)
        self.param_container.grid(row=1, column=0, columnspan=10, sticky=(tk.W, tk.E), pady=(8, 0))
        self.active_panel = None
        
        # Status bar
        self.status = ttk.Label(main_frame, text="Ready")
        self.status.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        
        # Canvas with proper expansion
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg="black", cursor="cross")
        self.canvas.grid(sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mouse events
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Configure>", self._on_configure)
    
    def _on_fractal_select(self, event):
        """Handle fractal type selection change."""
        new_type = self.fractal_var.get()
        current_type = getattr(self, '_current_fractal_type', None)
        
        # Initialize caches if needed
        if not hasattr(self, '_fractal_cache'):
            self._fractal_cache = {}
        if not hasattr(self, '_view_cache'):
            self._view_cache = {}  # Maps type name -> (x_min, x_max, y_min, y_max)
        if not hasattr(self, '_max_iter_cache'):
            self._max_iter_cache = {}  # Maps type name -> max_iter
        
        # Save current view and max_iter for the fractal we're leaving
        if current_type and current_type != new_type:
            self._view_cache[current_type] = (self.x_min, self.x_max, self.y_min, self.y_max)
            self._max_iter_cache[current_type] = self.max_iter
        
        # Get or create the fractal for this type (preserves parameters across switches)
        if new_type not in self._fractal_cache:
            self._fractal_cache[new_type] = FractalFactory.create(new_type)
        
        self.fractal = self._fractal_cache[new_type]
        self._current_fractal_type = new_type
        
        # Restore saved view and max_iter for this fractal, or use defaults
        if new_type in self._view_cache:
            self.x_min, self.x_max, self.y_min, self.y_max = self._view_cache[new_type]
        else:
            key = _camel_to_snake(type(self.fractal).__name__)
            bounds = self.DEFAULT_BOUNDS.get(key, (-2.0, 1.0, -1.5, 1.5))
            self.x_min, self.x_max, self.y_min, self.y_max = bounds
        
        # Restore saved max_iter for this fractal
        if new_type in self._max_iter_cache:
            self.max_iter = self._max_iter_cache[new_type]
            self.iter_var.set(str(self.max_iter))
        
        # Remove old panel if exists
        if self.active_panel:
            self.active_panel.grid_forget()
        
        # Create and show appropriate parameter panel (uses cached fractal instance)
        self.active_panel = _create_param_panel(
            new_type, 
            self.param_container, 
            self.fractal,
            self.render
        )
        if self.active_panel:
            self.active_panel.update_from_fractal()
            self.active_panel.grid()
        
        self.render()
    
    def _on_palette_select(self, event):
        """Handle palette selection change."""
        self.palette_name = self.palette_var.get()
        self.render()
    
    def _reset_view(self):
        """Reset to appropriate default view for current fractal type."""
        # Save current view and max_iter before resetting (so user can undo reset by switching away and back)
        if not hasattr(self, '_view_cache'):
            self._view_cache = {}
        if not hasattr(self, '_max_iter_cache'):
            self._max_iter_cache = {}
        self._view_cache[self._current_fractal_type] = (self.x_min, self.x_max, self.y_min, self.y_max)
        self._max_iter_cache[self._current_fractal_type] = self.max_iter
        
        key = _camel_to_snake(type(self.fractal).__name__)
        bounds = self.DEFAULT_BOUNDS.get(key, (-2.0, 1.0, -1.5, 1.5))
        self.x_min, self.x_max, self.y_min, self.y_max = bounds
        
        # Clear the cached view for this type so next reset goes to default
        if self._current_fractal_type in self._view_cache:
            del self._view_cache[self._current_fractal_type]
        
        self.current_render = None
        self.render()
    
    def _on_save(self):
        """Save current image as JPEG."""
        if not self.current_render:
            messagebox.showwarning("No Image", "Generate a fractal first.")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg;*.jpeg")],
            initialfile=f"{self.fractal_var.get()}_{self.palette_name}.jpg"
        )
        if not path:
            return
        
        try:
            self.current_render.save(path, "JPEG", quality=95)
            print(f"Saved: {path}")
            self.status.config(text=f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\n{e}")
    
    def _on_configure(self, event):
        """Handle window/canvas resize."""
        nw, nh = int(event.width), int(event.height)
        if abs(nw - self.width) < 10 and abs(nh - self.height) < 10:
            return
        
        if self.resize_timer_id:
            self.root.after_cancel(self.resize_timer_id)
        
        def do_resize():
            ox, oy = self.width, self.height
            sx, sy = nw / ox, nh / oy
            
            # Scale view bounds from center
            cx, cy = (self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2
            vx, vy = self.x_max - self.x_min, self.y_max - self.y_min
            
            self.x_min, self.x_max = cx - vx * sx / 2, cx + vx * sx / 2
            self.y_min, self.y_max = cy - vy * sy / 2, cy + vy * sy / 2
            
            # Save the resized view for this fractal type
            if not hasattr(self, '_view_cache'):
                self._view_cache = {}
            if not hasattr(self, '_max_iter_cache'):
                self._max_iter_cache = {}
            self._view_cache[self._current_fractal_type] = (self.x_min, self.x_max, self.y_min, self.y_max)
            self._max_iter_cache[self._current_fractal_type] = self.max_iter
            
            self.width, self.height = nw, nh
            self.current_render = None
            self.render()
            self.resize_timer_id = None
        
        self.resize_timer_id = self.root.after(100, do_resize)
    
    def _compute_fractal(self):
        """Compute fractal using sequential or parallel mode."""
        if not hasattr(self, 'fractal') or self.fractal is None:
            return np.zeros((self.height, self.width), dtype=np.int32)
        
        # Note: Y axis is inverted - image row 0 (top) should be max Y, row -1 (bottom) should be min Y
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_max, self.y_min, self.height)
        X, Y = np.meshgrid(x, y)
        
        if not self.use_parallel.get():
            return self.fractal.calculate(X, Y, self.max_iter)
        
        # Parallel mode - limit workers to avoid overhead on small canvases
        # Ensure workers >= 1 and at least 2 rows per worker for efficiency
        workers = max(1, min(self.num_workers, max(1, self.height // 2)))
        strip_h = max(1, self.height // workers)
        
        # Get fractal-specific parameters (consistent type checking)
        extra_params = None
        if isinstance(self.fractal, Phoenix):
            # Phoenix: pass marker and c, p values
            extra_params = ('phoenix', self.fractal.c.real, self.fractal.c.imag, self.fractal.p)
        elif hasattr(self.fractal, 'power'):
            # Multibrot: just power (Phoenix also has power attr, so check after isinstance)
            if not isinstance(self.fractal, Phoenix):
                extra_params = (self.fractal.power,)
        elif hasattr(self.fractal, 'c') and hasattr(self.fractal, 'set_c'):
            # Julia types: pass c and z0 values
            c_real = getattr(self.fractal.c, 'real', 0.0)
            c_imag = getattr(self.fractal.c, 'imag', 0.0)
            z0 = getattr(self.fractal, 'z0', complex(0, 0))
            extra_params = (c_real, c_imag, z0.real, z0.imag)
        
        strips = []
        for ys in range(0, self.height, strip_h):
            ye = min(ys + strip_h, self.height)
            fractal_name = _camel_to_snake(type(self.fractal).__name__)
            args = (ys, ye, self.x_min, self.x_max, self.y_min, self.y_max,
                    self.width, self.height, self.max_iter, fractal_name,
                    extra_params)
            strips.append(args)
        
        result = np.zeros((self.height, self.width), dtype=np.int32)
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(_compute_strip, s) for s in strips]
            for f in futures:
                ys, ye, data = f.result()
                result[ys:ye] = data
        
        return result
    
    def _iterations_to_image(self, iterations):
        """Convert iteration counts to RGB image using vectorized operations."""
        palette_func = PaletteFactory.get(self.palette_name)
        max_i = self.max_iter
        
        # Build lookup table: for each possible iteration count (0 to max_iter), get the color
        colors = np.array([palette_func(i, max_i)[:3] for i in range(max_i + 1)], dtype=np.uint8)
        
        indices = np.clip(iterations, 0, len(colors) - 1).astype(np.int32)
        return Image.fromarray(colors[indices], mode='RGB')
    
    def _show(self, image):
        """Display image on canvas."""
        self.photo_image = ImageTk.PhotoImage(image)
        if hasattr(self, '_display_rect'):
            self.canvas.delete(self._display_rect)
        self._display_rect = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
    
    def _do_render(self):
        """Main render method with timing and diagnostics."""
        start = time.perf_counter()
        
        try:
            iterations = self._compute_fractal()
            img = self._iterations_to_image(iterations)
            self.current_render = img
            self._show(img)
            
            elapsed = int((time.perf_counter() - start) * 1000)
            mode = "par" if self.use_parallel.get() else "seq"
            
            print(f"[{mode.upper()}] {type(self.fractal).__name__}, {self.palette_name}, "
                  f"{self.width}x{self.height}x{self.max_iter}, ({self.x_min:.0f},{self.y_max:.0f})-({self.x_max:.0f},{self.y_min:.0f}), {elapsed}ms")
            
            prefix = "Parallel " if self.use_parallel.get() else ""
            self.status.config(text=f"{prefix}View: ({self.x_min:.6f},{self.y_max:.6f}) to "
                                    f"({self.x_max:.6f},{self.y_min:.6f})")
        except Exception as e:
            self.status.config(text=f"Error: {e}")
        finally:
            self.is_processing = False
            self.pending_render_id = None
    
    def render(self):
        """Public render entry point."""
        if self.is_processing:
            return
        
        if self.pending_render_id:
            self.root.after_cancel(self.pending_render_id)
        
        self.is_processing = True
        prefix = "Parallel calculating..." if self.use_parallel.get() else "Calculating..."
        self.status.config(text=prefix)
        self._do_render()
    
    def _on_mouse_down(self, event):
        """Start selection."""
        # Don't delete the image - just store start position
        self.selection_start = (event.x, event.y)
        self.selection_end = None
    
    def _on_mouse_drag(self, event):
        """Update selection rectangle with fixed aspect ratio."""
        if not self.selection_start or self.is_processing:
            return
        
        x1, y1 = self.selection_start
        ar = self.width / max(1, self.height)
        
        dx, dy = abs(event.x - x1), abs(event.y - y1)
        
        if dx > dy:  # Width-driven
            h = int(dx / ar)
            x2_adj, y2_adj = event.x, (y1 + h) if event.y >= y1 else (y1 - h)
        else:  # Height-driven
            w = int(dy * ar)
            x2_adj, y2_adj = (x1 + w) if event.x >= x1 else (x1 - w), event.y
        
        x2_adj = max(0, min(self.width, x2_adj))
        y2_adj = max(0, min(self.height, y2_adj))
        
        self.selection_end = (x2_adj, y2_adj)
        
        if hasattr(self, '_sel_rect'):
            self.canvas.delete(self._sel_rect)
        self._sel_rect = self.canvas.create_rectangle(x1, y1, x2_adj, y2_adj,
                                                       outline="white", width=2, dash=(5, 3))
    
    def _on_mouse_up(self, event):
        """Apply zoom from selection."""
        if not self.selection_start or self.is_processing:
            return
        
        x1, y1 = self.selection_start
        x2, y2 = self.selection_end or (event.x, event.y)
        
        if hasattr(self, '_sel_rect'):
            self.canvas.delete(self._sel_rect)
        
        sel_x1, sel_x2 = sorted((x1, x2))
        sel_y1, sel_y2 = sorted((y1, y2))
        
        if sel_x2 - sel_x1 < 5 or sel_y2 - sel_y1 < 5:
            self.selection_start = None
            return
        
        # Convert to complex plane coordinates
        re1 = self.x_min + (sel_x1 / self.width) * (self.x_max - self.x_min)
        im1 = self.y_max - (sel_y1 / self.height) * (self.y_max - self.y_min)
        re2 = self.x_min + (sel_x2 / self.width) * (self.x_max - self.x_min)
        im2 = self.y_max - (sel_y2 / self.height) * (self.y_max - self.y_min)
        
        self.x_min, self.x_max = min(re1, re2), max(re1, re2)
        self.y_min, self.y_max = min(im1, im2), max(im1, im2)
        
        # Save the zoomed view for this fractal type
        if not hasattr(self, '_view_cache'):
            self._view_cache = {}
        self._view_cache[self._current_fractal_type] = (self.x_min, self.x_max, self.y_min, self.y_max)
        
        # Also save max_iter
        if not hasattr(self, '_max_iter_cache'):
            self._max_iter_cache = {}
        self._max_iter_cache[self._current_fractal_type] = self.max_iter
        
        # Show preview
        if self.current_render:
            # Crop from current render and resize to fill canvas
            cropped = self.current_render.crop((
                int(sel_x1),      # left
                int(sel_y1),      # upper (top of selection)
                int(sel_x2 + 1),  # right
                int(sel_y2 + 1)   # lower (bottom of selection)
            ))
            self._show(cropped.resize((self.width, self.height), Image.Resampling.NEAREST))
        
        prefix = "Parallel calculating..." if self.use_parallel.get() else "Calculating..."
        self.status.config(text=prefix)
        self.root.update()
        self.is_processing = True
        self.pending_render_id = self.root.after(50, self._do_render)


if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(600, 500)
    app = FractalApp(root)
    
    # Initial render after UI settles
    root.update_idletasks()
    app.render()
    
    root.mainloop()
