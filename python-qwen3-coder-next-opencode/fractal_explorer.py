#!/usr/bin/env python3
"""Main entry point for the fractal explorer."""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Error: Pillow is required. Install with: pip install pillow")
    sys.exit(1)

from typing import Union

from fractals.mandelbrot import Mandelbrot
from fractals.julia import Julia, JULIA_PRESETS
from fractals import FractalBase
from palettes.standard import (
    SmoothPalette, BandedPalette, GrayscalePalette,
    FirePalette, OceanPalette, RainbowPalette,
    ElectricPalette, NeonPalette
)
from navigation import ZoomController


class FractalApp:
    """Main application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Fractal Explorer")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        self.fractal = None
        self.palette = None
        self.zoom_controller: ZoomController | None = None
        
        self.current_fractal_name = "mandelbrot"
        self.current_palette_name = "smooth"
        self.iterations = 200
        
        # Zoom history for each fractal type
        self.zoom_history = {"mandelbrot": [], "julia": []}
        self.zoom_history_pos = {"mandelbrot": -1, "julia": -1}
        
        # Store fractal state per type: {fractal_name: {'zoom_bounds': ..., 'palette': ..., 'iterations': ...}}
        self.fractal_states = {"mandelbrot": {}, "julia": {}}
        
        self.setup_ui()
        self.load_fractal("mandelbrot")
        self.load_palette("smooth")

    def setup_ui(self):
        """Setup the UI layout."""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        sidebar = tk.Frame(main_frame, width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.setup_sidebar(sidebar)
        self.setup_canvas(main_frame)
        self.setup_toolbar(sidebar)

        # Progress bar for rendering
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(sidebar, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)

        try:
            from rendering.parallel import ParallelRenderEngine
            self.renderer = ParallelRenderEngine()
            worker_count = getattr(self.renderer, 'num_workers', 1)
            self.worker_label = tk.Label(sidebar, text=f"Workers: {worker_count}")
            self.worker_label.pack(anchor=tk.W, pady=5)
        except ImportError:
            self.renderer = None

        self.image_label = tk.Label(main_frame, text="")
        self.image_label.pack(side=tk.BOTTOM, anchor=tk.W)

    def setup_sidebar(self, parent):
        """Setup sidebar controls."""
        tk.Label(parent, text="Fractal:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        self.fractal_combo = ttk.Combobox(parent, state='readonly', width=25)
        self.fractal_combo.pack(fill=tk.X, pady=(0, 10))

        fractals = ["Mandelbrot Set", "Julia Set", "Burning Ship", 
                   "Tricorn", "Multibrot", "Phoenix", "Newton", 
                   "Cubic Julia", "Feather", "Spider"]
        self.fractal_combo['values'] = fractals
        self.fractal_combo.current(0)
        self.fractal_combo.bind('<<ComboboxSelected>>', lambda e: self.on_fractal_change())

        tk.Label(parent, text="Color Palette:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        self.palette_combo = ttk.Combobox(parent, state='readonly', width=25)
        self.palette_combo.pack(fill=tk.X, pady=(0, 10))

        palettes = ["Smooth", "Banded", "Grayscale", "Fire", 
                   "Ocean", "Rainbow", "Electric", "Neon"]
        self.palette_combo['values'] = palettes
        self.palette_combo.current(0)
        self.palette_combo.bind('<<ComboboxSelected>>', lambda e: self.on_palette_change())

        tk.Label(parent, text="Iterations:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        self.iteration_scale = ttk.Scale(parent, from_=50, to=2000, 
                                         orient=tk.HORIZONTAL)
        self.iteration_scale.bind("<B1-Motion>", lambda e: self.on_iteration_change(update_label_only=True))
        self.iteration_scale.bind("<ButtonRelease-1>", lambda e: self.on_iteration_change())
        self.iteration_scale.pack(fill=tk.X, pady=(0, 10))
        self.iteration_scale.set(200)

        self.iteration_label = tk.Label(parent, text="200 iterations")
        self.iteration_label.pack(anchor=tk.W, pady=(0, 20))

    def setup_canvas(self, parent):
        """Setup the fractal canvas."""
        self.canvas = tk.Canvas(parent, bg='black', cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind('<Configure>', lambda e: self.on_resize())
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<MouseWheel>', self.on_wheel)

    def setup_toolbar(self, parent):
        """Setup toolbar buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        # Back/Forward navigation
        nav_frame = ttk.Frame(button_frame)
        nav_frame.pack(fill=tk.X, pady=2)

        self.back_button = ttk.Button(nav_frame, text="← Back", 
                      command=self.on_navigate_back)
        self.back_button.pack(side=tk.LEFT, expand=True, padx=2)

        self.forward_button = ttk.Button(nav_frame, text="Forward →", 
                      command=self.on_navigate_forward)
        self.forward_button.pack(side=tk.LEFT, expand=True, padx=2)

        ttk.Button(button_frame, text="Reset View", 
                   command=self.on_reset_view).pack(fill=tk.X, pady=2)

        ttk.Button(button_frame, text="Save Image", 
                   command=self.on_save_image).pack(fill=tk.X, pady=2)

        self.update_nav_buttons()

    def on_fractal_change(self):
        """Handle fractal change."""
        # Save current state before switching
        if self.current_fractal_name and hasattr(self, 'zoom_controller'):
            try:
                current_bounds = self.zoom_controller.get_bounds()
                if current_bounds:
                    self.fractal_states[self.current_fractal_name] = {
                        'zoom_bounds': current_bounds,
                        'palette': getattr(self, 'current_palette_name', 'smooth'),
                        'iterations': int(self.iteration_scale.get()),
                        'zoom_history': list(self.zoom_history.get(self.current_fractal_name, [])),
                        'zoom_history_pos': self.zoom_history_pos.get(self.current_fractal_name, -1)
                    }
            except Exception:
                pass

        selected = self.fractal_combo.get()
        fractal_map = {
            "Mandelbrot Set": "mandelbrot",
            "Julia Set": "julia",
        }
        self.load_fractal(fractal_map.get(selected, "mandelbrot"))

    def on_palette_change(self):
        """Handle palette change."""
        selected = self.palette_combo.get()
        palette_map = {
            "Smooth": "smooth",
            "Banded": "banded",
            "Grayscale": "grayscale",
            "Fire": "fire",
            "Ocean": "ocean",
            "Rainbow": "rainbow",
            "Electric": "electric",
            "Neon": "neon"
        }
        self.load_palette(palette_map.get(selected, "smooth"))

    def on_iteration_change(self, update_label_only=False):
        """Handle iteration slider change."""
        val = int(self.iteration_scale.get())
        self.iteration_label.config(text=f"{val} iterations")
        if not update_label_only:
            self.render()

    def load_fractal(self, name: str):
        """Load a fractal by name."""
        from fractals.mandelbrot import Mandelbrot
        from fractals.julia import Julia

        fractal_classes = {
            "mandelbrot": Mandelbrot,
            "julia": Julia
        }

        self.current_fractal_name = name
        self.fractal = fractal_classes[name]()

        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 10 or height < 10:
            width, height = 800, 600

        self.zoom_controller = ZoomController(width, height)

        # Restore saved state for this fractal type
        has_zoom_bounds_saved = 'zoom_bounds' in self.fractal_states.get(name, {})
        if name in self.fractal_states:
            state = self.fractal_states[name]
            if 'zoom_bounds' in state:
                self.zoom_controller.set_bounds(*state['zoom_bounds'])
            if 'palette' in state:
                self.load_palette(state['palette'], render=False)
                palette_internal_names = ["smooth", "banded", "grayscale", "fire",
                                           "ocean", "rainbow", "electric", "neon"]
                try:
                    idx = palette_internal_names.index(state['palette'])
                    self.palette_combo.current(idx)
                except ValueError:
                    pass
            if 'iterations' in state:
                self.iteration_scale.set(state['iterations'])
                val = int(self.iteration_scale.get())
                self.iteration_label.config(text=f"{val} iterations")

        # Restore zoom history for this fractal type
        if name not in self.zoom_history:
            self.zoom_history[name] = []
            self.zoom_history_pos[name] = -1
        if name in self.fractal_states and 'zoom_history' in self.fractal_states[name]:
            self.zoom_history[name] = list(self.fractal_states[name]['zoom_history'])
            self.zoom_history_pos[name] = self.fractal_states[name].get('zoom_history_pos', -1)

        # Load default bounds only if no saved zoom state
        if not has_zoom_bounds_saved:
            if hasattr(self.fractal, 'get_default_bounds'):
                bounds = self.fractal.get_default_bounds()
                self.zoom_controller.scale_to_fractal(bounds)
            else:
                self.zoom_controller.set_fractional_view(0.0, 1.0, 0.0, 1.0)

        self.update_nav_buttons()
        self.render()

    def load_palette(self, name: str, render: bool = True):
        """Load a palette by name."""
        from palettes.standard import (
            SmoothPalette, BandedPalette, GrayscalePalette,
            FirePalette, OceanPalette, RainbowPalette,
            ElectricPalette, NeonPalette
        )

        palette_map = {
            "smooth": SmoothPalette,
            "banded": BandedPalette,
            "grayscale": GrayscalePalette,
            "fire": FirePalette,
            "ocean": OceanPalette,
            "rainbow": RainbowPalette,
            "electric": ElectricPalette,
            "neon": NeonPalette
        }

        self.palette = palette_map.get(name, SmoothPalette)()
        self.current_palette_name = name
        if render:
            self.render()

    def on_resize(self, event=None):
        """Handle window resize."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width > 10 and height > 10:
            if hasattr(self, 'zoom_controller') and self.zoom_controller:
                self.zoom_controller.width = width
                self.zoom_controller.height = height
            self.render()

    def update_nav_buttons(self):
        """Update navigation button states."""
        name = self.current_fractal_name
        
        print(f"\n[DEBUG] update_nav_buttons for '{name}':")
        print(f"  zoom_history['{name}'] length: {len(self.zoom_history.get(name, []))}")
        print(f"  zoom_history_pos['{name}']: {self.zoom_history_pos.get(name, -1)}")

        can_back = False
        pos = self.zoom_history_pos.get(name, -1)
        history = self.zoom_history.get(name, [])
        if pos > 0 and len(history) > 0:
            can_back = True

        print(f"  pos={pos}, len(history)={len(history)}, can_back={can_back}")
        self.back_button.config(state='normal' if can_back else 'disabled')

        can_forward = False
        pos = self.zoom_history_pos.get(name, -1)
        history = self.zoom_history.get(name, [])
        if pos < len(history) - 1 and len(history) > 0:
            can_forward = True

        print(f"  pos={pos}, len(history)={len(history)}, can_forward={can_forward} (checking: {pos} < {len(history)} - 1)")
        self.forward_button.config(state='normal' if can_forward else 'disabled')

    def on_navigate_back(self):
        """Navigate to previous zoom state."""
        name = self.current_fractal_name
        if name not in self.zoom_history or name not in self.zoom_history_pos:
            return

        pos = self.zoom_history_pos[name]
        history = self.zoom_history[name]

        print(f"\n[DEBUG] on_navigate_back: name={name}, pos={pos}, len(history)={len(history)}")
        
        if pos > 0 and len(history) > 0:
            self.zoom_history_pos[name] = pos - 1
            bounds = history[self.zoom_history_pos[name]]
            print(f"  Moving back to position {self.zoom_history_pos[name]}, bounds={bounds}")
            if hasattr(self, 'zoom_controller') and self.zoom_controller:
                self.zoom_controller.set_bounds(*bounds)
            self.render_with_bounds(bounds)
            self.update_nav_buttons()
        else:
            print(f"  Cannot navigate back: pos={pos}, len(history)={len(history)}")
            self.update_nav_buttons()

    def render_with_bounds(self, bounds: tuple):
        """Render fractal with specific bounds without adding to history."""
        if not hasattr(self, 'zoom_controller') or not self.zoom_controller:
            return

        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 10 or height < 10:
            return

        try:
            from rendering.parallel import ParallelRenderEngine
            if hasattr(self, 'renderer') and self.renderer:
                progress = [0]
                def update_progress(current, total):
                    if total > 0:
                        progress[0] = (current / total) * 100
                        self.progress_var.set(progress[0])
                        self.root.update_idletasks()

                img = self.renderer.render_with_bounds(
                    width, height,
                    self.fractal, self.palette,
                    int(self.iteration_scale.get()),
                    bounds, update_progress
                )
            else:
                from rendering.fractal import FractalRenderer
                renderer = FractalRenderer(self.fractal, self.palette,
                                         int(self.iteration_scale.get()),
                                         (bounds[0], bounds[1], bounds[2], bounds[3]))
                img = renderer.render(width, height)
        except ImportError:
            from rendering.fractal import FractalRenderer
            renderer = FractalRenderer(self.fractal, self.palette,
                                     int(self.iteration_scale.get()),
                                     (bounds[0], bounds[1], bounds[2], bounds[3]))
            img = renderer.render(width, height)

        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo
        self.progress_var.set(0)

    def on_navigate_forward(self):
        """Navigate to next zoom state."""
        name = self.current_fractal_name
        if name not in self.zoom_history or name not in self.zoom_history_pos:
            return

        pos = self.zoom_history_pos[name]
        history = self.zoom_history[name]

        print(f"\n[DEBUG] on_navigate_forward: name={name}, pos={pos}, len(history)={len(history)}")
        
        if pos < len(history) - 1 and len(history) > 0:
            self.zoom_history_pos[name] = pos + 1
            bounds = history[self.zoom_history_pos[name]]
            print(f"  Moving forward to position {self.zoom_history_pos[name]}, bounds={bounds}")
            if hasattr(self, 'zoom_controller') and self.zoom_controller:
                self.zoom_controller.set_bounds(*bounds)
            self.render_with_bounds(bounds)
            self.update_nav_buttons()
        else:
            print(f"  Cannot navigate forward: pos={pos}, len(history)={len(history)} (checking {pos} < {len(history)} - 1)")
            self.update_nav_buttons()

    def on_reset_view(self):
        """Reset to default view."""
        print(f"\n[DEBUG] on_reset_view called")
        
        if hasattr(self.fractal, 'get_default_bounds'):
            bounds = self.fractal.get_default_bounds()
            if hasattr(self, 'zoom_controller') and self.zoom_controller:
                self.zoom_controller.set_bounds(bounds['xmin'], bounds['xmax'],
                                                bounds['ymin'], bounds['ymax'])
        else:
            if hasattr(self, 'zoom_controller') and self.zoom_controller:
                self.zoom_controller.reset()

        name = self.current_fractal_name
        print(f"  Resetting history for '{name}': was {len(self.zoom_history.get(name, []))} items, pos={self.zoom_history_pos.get(name, -1)}")
        self.zoom_history[name] = []
        self.zoom_history_pos[name] = -1

        # Clear forward history from saved state too
        if name in self.fractal_states:
            self.fractal_states[name]['zoom_history'] = []
            self.fractal_states[name]['zoom_history_pos'] = -1

        self.update_nav_buttons()
        self.render()

    def on_save_image(self):
        """Save current fractal image."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("Save Image", f"Saving to {filename}")
            # TODO: Implement actual image saving

    def render(self):
        """Render the fractal."""
        self.progress_var.set(0)

        if not hasattr(self, 'zoom_controller') or not self.zoom_controller:
            return

        # Save current zoom state before rendering
        name = self.current_fractal_name
        bounds = self.zoom_controller.get_bounds()
        
        print(f"\n[DEBUG] render: name={name}, pos before={self.zoom_history_pos.get(name, -1)}")

        # If this is a new state, truncate forward history
        if name in self.zoom_history and name in self.zoom_history_pos:
            pos = self.zoom_history_pos[name]
            history = self.zoom_history[name]
            print(f"  Truncation check: pos={pos}, len(history)={len(history)}")
            if pos < len(history) - 1:
                print(f"  Truncating forward history from {len(history)} to {pos + 1} items")
                self.zoom_history[name] = history[:pos + 1]

        # Add current bounds to history (don't add duplicates)
        should_add = True
        if name in self.zoom_history and len(self.zoom_history[name]) > 0:
            last_bounds = self.zoom_history[name][-1]
            print(f"  Checking duplicate: last={last_bounds}, curr={bounds}")
            if last_bounds == bounds:
                should_add = False
        
        print(f"  Should add to history: {should_add}")

        if should_add:
            if name not in self.zoom_history:
                self.zoom_history[name] = []
            self.zoom_history[name].append(bounds)
            new_pos = len(self.zoom_history[name]) - 1
            print(f"  Added bounds to history at index {new_pos}")
            self.zoom_history_pos[name] = new_pos
        else:
            print(f"  Skipping duplicate, keeping pos={self.zoom_history_pos.get(name, -1)}")

        # Render
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width < 10 or height < 10:
            return

        try:
            from rendering.parallel import ParallelRenderEngine
            if hasattr(self, 'renderer') and self.renderer:
                # Use parallel renderer
                progress = [0]
                def update_progress(current, total):
                    if total > 0:
                        progress[0] = (current / total) * 100
                        self.progress_var.set(progress[0])
                        self.root.update_idletasks()

                img = self.renderer.render_with_bounds(
                    width, height,
                    self.fractal, self.palette,
                    int(self.iteration_scale.get()),
                    bounds, update_progress
                )
            else:
                # Use basic renderer
                from rendering.fractal import FractalRenderer
                renderer = FractalRenderer(self.fractal, self.palette,
                                         int(self.iteration_scale.get()),
                                         (bounds[0], bounds[1], bounds[2], bounds[3]))
                img = renderer.render(width, height)
        except ImportError:
            from rendering.fractal import FractalRenderer
            renderer = FractalRenderer(self.fractal, self.palette,
                                     int(self.iteration_scale.get()),
                                     (bounds[0], bounds[1], bounds[2], bounds[3]))
            img = renderer.render(width, height)

        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo
        self.progress_var.set(0)

    def on_mouse_down(self, event):
        """Handle mouse button press."""
        if not hasattr(self, 'zoom_state'):
            self.zoom_state = {}
        self.zoom_state['drag_start'] = (event.x, event.y)
        self.zoom_state['drag_rect'] = None

    def on_mouse_drag(self, event):
        """Handle mouse drag."""
        if not hasattr(self, 'zoom_state') or not self.zoom_state.get('drag_start'):
            return

        x1, y1 = self.zoom_state['drag_start']

        if self.zoom_state['drag_rect']:
            self.canvas.delete(self.zoom_state['drag_rect'])

        self.zoom_state['drag_rect'] = self.canvas.create_rectangle(
            x1, y1, event.x, event.y, outline='red', width=2
        )

    def on_mouse_up(self, event):
        """Handle mouse button release."""
        if not hasattr(self, 'zoom_state'):
            return

        print(f"\n[DEBUG] on_mouse_up: before zoom pos={self.zoom_history_pos.get(self.current_fractal_name, -1)}")

        if (self.zoom_state.get('drag_start') and 
            self.zoom_state.get('drag_rect')):
            x1, y1 = self.zoom_state['drag_start']

            self.canvas.delete(self.zoom_state['drag_rect'])

            if abs(event.x - x1) > 5 and abs(event.y - y1) > 5:
                if hasattr(self, 'zoom_controller') and self.zoom_controller:
                    print(f"  Performing rect zoom from ({x1}, {y1}) to ({event.x}, {event.y})")
                    self.zoom_controller.zoom_rect(x1, y1, event.x, event.y)
                    self.render()
                    print(f"[DEBUG] on_mouse_up: after render pos={self.zoom_history_pos.get(self.current_fractal_name, -1)}")
                    self.update_nav_buttons()

        self.zoom_state = {'drag_start': None, 'drag_rect': None}

    def on_wheel(self, event):
        """Handle mouse wheel zoom."""
        if not hasattr(self, 'zoom_controller') or not self.zoom_controller:
            return

        print(f"\n[DEBUG] on_wheel: before zoom pos={self.zoom_history_pos.get(self.current_fractal_name, -1)}")

        zoom_factor = 0.9 if event.delta > 0 else 1.1

        px, py = event.x, event.y
        self.zoom_controller.zoom_at(px, py, zoom_factor)
        self.render()
        print(f"[DEBUG] on_wheel: after render pos={self.zoom_history_pos.get(self.current_fractal_name, -1)}")
        self.update_nav_buttons()

    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = FractalApp()
    app.run()
