"""Interactive Fractal Explorer - Main Application."""

import tkinter as tk
from datetime import datetime
import multiprocessing

# Import all fractal implementations to register them
from fractals.mandelbrot import *
from fractals.julia import *
from fractals.multibrot import *
from fractals.burning_ship import *
from fractals.tricorn import *
from fractals.phoenix import *
from fractals.newton import *
from fractals.cubic_julia import *
from fractals.feather import *
from fractals.spider import *
from fractals.orbit_trap import *
from fractals.pickover_stalks import *
from fractals.interior_distance import *
from fractals.exterior_distance import *
from fractals.deribail import *

# Import palette implementations
from palettes.standard import *

# Import navigation, rendering, and UI components
from navigation import ZoomController
from rendering import RenderEngine
from ui import UIManager

# Import registry functions
import fractals
import palettes


class FractalExplorer:
    """Main application controller."""
    
    def __init__(self):
        """Initialize the fractal explorer app."""
        self.root = tk.Tk()
        
        # Create tkinter variables first
        from tkinter import ttk
        self.fractal_var = tk.StringVar()
        self.palette_var = tk.StringVar()
        self.iterations_var = tk.IntVar(value=200)
        
        # Track previous state to detect if only iterations changed
        self.last_bounds = None
        
        # Initialize UI manager with window size and pass variables
        self.ui_manager = UIManager(self.root)
        self.ui_manager.fractal_var = self.fractal_var
        self.ui_manager.palette_var = self.palette_var  
        self.ui_manager.iterations_var = self.iterations_var
        
        self.root.title("Interactive Fractal Explorer")

        # Use canvas dimensions from UI manager
        self.width = self.ui_manager.width
        self.height = self.ui_manager.height

        # Get registered fractals and palettes first
        self.fractals = fractals.list_fractals()
        self.palettes = palettes.list_palettes()

        # Per-fractal state storage - create first so zoom_controller can reference it
        self.fractal_states = {}
        default_palette_id = list(self.palettes.keys())[0]
        for fid in self.fractals.keys():
            fractal_instance = fractals.get_fractal(fid)
            zoom = ZoomController(self.width, self.height)
            if fractal_instance:
                bounds = fractal_instance.get_default_bounds()
                zoom.set_bounds(bounds['xmin'], bounds['xmax'],
                               bounds['ymin'], bounds['ymax'])
            self.fractal_states[fid] = {
                'zoom': zoom,
                'iterations': 200,
                'palette_id': default_palette_id
            }

        # Initialize components - use first fractal's zoom controller
        first_fractal_id = list(self.fractals.keys())[0]
        self.zoom_controller = self.fractal_states[first_fractal_id]['zoom']
        self.render_engine = RenderEngine()
        
        # Current state
        self.current_fractal = None
        self.current_palette = None
        
        # Setup UI
        self.ui_manager.add_click_handler(self.on_click)
        self.ui_manager.setup_ui(
            fractals=self.fractals,
            palettes=self.palettes,
            render_callback=self.render,
            reset_view_callback=self.reset_view,
            save_image_callback=self.save_image,
            fractal_change_callback=self.on_fractal_change
        )
        
        # Worker count display
        workers = max(1, multiprocessing.cpu_count() - 1)
        self.ui_manager.show_status(f"Using {workers} worker(s)")
        
        # Initial render
        self.render()
    
    def get_current_fractal_instance(self):
        """Get the current fractal instance based on UI selection."""
        fid = self.fractal_var.get()
        return fractals.get_fractal(fid)
    
    def get_current_palette_instance(self):
        """Get the current palette instance based on UI selection."""
        pid = self.palette_var.get()
        return palettes.get_palette(pid)
    
    def render(self):
        """Render the fractal with current settings."""
        
        import time
        start_time = time.time()
        
        fractal = self.get_current_fractal_instance()
        palette = self.get_current_palette_instance()
        
        if not fractal or not palette:
            return
        
        # Update dimensions from UI manager (may have changed on resize)
        self.width = self.ui_manager.width
        self.height = self.ui_manager.height
        
        # Update zoom controller size
        self.zoom_controller.width = self.width
        self.zoom_controller.height = self.height
        
        max_iter = self.iterations_var.get()
        
        # Check if only iterations changed (compare bounds)
        current_bounds = self.zoom_controller.get_bounds()
        only_iterations_changed = (
            self.last_bounds is not None and 
            current_bounds == self.last_bounds
        )
        self.last_bounds = current_bounds.copy()
        
        def progress_callback(completed, total):
            percent = int(100 * completed / total)
            workers = max(1, multiprocessing.cpu_count() - 1)
            self.ui_manager.show_status(f"Rendering: {percent}% ({workers} workers)")
        
        # Skip preview - render directly to detailed version
        
        # Render detailed version
        image_data = self.render_engine.render(
            fractal=fractal,
            palette=palette,
            zoom_controller=self.zoom_controller,
            width=self.width,
            height=self.height,
            max_iter=max_iter,
            progress_callback=progress_callback
        )
        
        self.ui_manager.display_image(image_data)
        
        # Calculate render time and print diagnostics
        end_time = time.time()
        render_time_ms = (end_time - start_time) * 1000
        
        workers = max(1, multiprocessing.cpu_count() - 1)
        self.ui_manager.show_status(f"Complete ({workers} workers)")
        
        # Print diagnostic output to console
        print(f"Render: {fractal.name} | Palette: {palette.name} | "
              f"{self.width}x{self.height}x{max_iter} | "
              f"xmin={current_bounds['xmin']:.4f}, xmax={current_bounds['xmax']:.4f}, "
              f"ymin={current_bounds['ymin']:.4f}, ymax={current_bounds['ymax']:.4f} | "
              f"{render_time_ms:.1f}ms")
    
    def on_click(self, x, y, zoom=None, x2=None, y2=None):
        """Handle click events for zooming.

        Args:
            x: X pixel coordinate
            y: Y pixel coordinate
            zoom: Zoom factor (for single point zoom)
            x2: Second X coordinate (for area selection)
            y2: Second Y coordinate (for area selection)
        """
        if x2 is not None and y2 is not None:
            # Area selection - pass current canvas dimensions to ensure correct conversion
            self.zoom_controller.select_area(x, y, x2, y2,
                                            width=self.ui_manager.width,
                                            height=self.ui_manager.height)
                
        elif zoom is not None:
            # Single point zoom
            cx, cy = self.zoom_controller.pixel_to_complex(x, y)
            self.zoom_controller.zoom(zoom, cx, cy)
        
        self.render()

    def on_fractal_change(self, new_fractal_id: str):
        """Save current fractal state and restore new fractal's state.

        Args:
            new_fractal_id: The ID of the fractal being switched to
        """
        # Save current fractal state
        current_fractal_id = self.fractal_var.get()
        if current_fractal_id and current_fractal_id in self.fractal_states:
            self.fractal_states[current_fractal_id] = {
                'zoom': self.zoom_controller,
                'iterations': self.iterations_var.get(),
                'palette_id': self.palette_var.get()
            }

        # Restore new fractal's state if it exists
        if new_fractal_id in self.fractal_states:
            state = self.fractal_states[new_fractal_id]
            self.zoom_controller = state['zoom']
            # Update zoom controller dimensions in case window was resized
            self.zoom_controller.width = self.ui_manager.width
            self.zoom_controller.height = self.ui_manager.height
            self.iterations_var.set(state['iterations'])
            self.palette_var.set(state['palette_id'])
            # Update UI to reflect restored palette
            self.ui_manager.update_palette_dropdown(state['palette_id'], self.palettes)
        else:
            # Initialize new state for fractal with default bounds
            new_fractal = fractals.get_fractal(new_fractal_id)
            if new_fractal:
                bounds = new_fractal.get_default_bounds()
                new_zoom = ZoomController(self.width, self.height)
                new_zoom.set_bounds(bounds['xmin'], bounds['xmax'],
                                   bounds['ymin'], bounds['ymax'])
                self.fractal_states[new_fractal_id] = {
                    'zoom': new_zoom,
                    'iterations': 200,
                    'palette_id': list(self.palettes.keys())[0]
                }
                # Restore the new state
                state = self.fractal_states[new_fractal_id]
                self.zoom_controller = state['zoom']
                # Update zoom controller dimensions in case window was resized
                self.zoom_controller.width = self.ui_manager.width
                self.zoom_controller.height = self.ui_manager.height
                self.iterations_var.set(state['iterations'])
                self.palette_var.set(state['palette_id'])
                self.ui_manager.update_palette_dropdown(state['palette_id'], self.palettes)

    def reset_view(self):
        """Reset the view to current fractal's default bounds."""
        current_fractal = self.get_current_fractal_instance()
        if current_fractal:
            bounds = current_fractal.get_default_bounds()
            self.zoom_controller.set_bounds(
                bounds['xmin'], bounds['xmax'],
                bounds['ymin'], bounds['ymax']
            )
        else:
            self.zoom_controller.reset()
    
    def save_image(self):
        """Save the current fractal image as PNG."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fractal_{timestamp}.png"
        
        try:
            from PIL import Image
            
            fractal = self.get_current_fractal_instance()
            palette = self.get_current_palette_instance()
            
            if not fractal or not palette:
                return
            
            max_iter = self.iterations_var.get()
            
            image_data = self.render_engine.render(
                fractal=fractal,
                palette=palette,
                zoom_controller=self.zoom_controller,
                width=self.width,
                height=self.height,
                max_iter=max_iter
            )
            
            img = Image.fromarray(image_data, 'RGB')
            img.save(filename)
            
            self.ui_manager.show_status(f"Saved to {filename}")
        except ImportError:
            self.ui_manager.show_status("PIL not available - cannot save image")
    
    def run(self):
        """Start the main event loop."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = FractalExplorer()
    app.run()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()