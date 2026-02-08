"""Quick test script for Fractal Explorer."""

import tkinter as tk
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

from palettes.standard import *

import fractals
import palettes

from navigation import ZoomController
from rendering import RenderEngine
from ui import UIManager


def main():
    """Run a quick test of the application."""
    root = tk.Tk()
    root.title("Fractal Explorer Test")
    
    width, height = 600, 450
    
    zoom_controller = ZoomController(width, height)
    render_engine = RenderEngine(workers=1)
    ui_manager = UIManager(root, width, height)
    
    fractal_id = list(fractals.list_fractals().keys())[0]
    palette_id = list(palettes.list_palettes().keys())[0]
    
    print(f"Testing: {fractal_id} with {palette_id}")
    
    fractal = fractals.get_fractal(fractal_id)
    palette = palettes.get_palette(palette_id)
    
    # Render preview
    preview = render_engine.render_preview(
        fractal=fractal,
        palette=palette,
        zoom_controller=zoom_controller,
        preview_scale=15
    )
    
    print(f"Preview size: {len(preview)}x{len(preview[0])}")
    
    # Display it
    ui_manager.display_image(preview)
    ui_manager.show_status("Test complete!")
    
    print("Application test successful!")
    print("Close the window to exit...")
    
    root.mainloop()


if __name__ == "__main__":
    main()