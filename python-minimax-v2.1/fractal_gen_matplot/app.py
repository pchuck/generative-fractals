"""
Interactive Fractal Explorer Application.

This is the main entry point for the fractal visualization tool. It provides
an interactive matplotlib-based interface for exploring fractal sets with:
- Zoom-to-rectangle selection
- Pan and zoom navigation
- Multiple color maps
- Easy switching between fractal types

Usage:
    python app.py [--width WIDTH] [--height HEIGHT]
"""

import sys
from pathlib import Path
from typing import Optional, Dict
import argparse
from dataclasses import dataclass
from time import perf_counter

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fractals.mandelbrot import MandelbrotSet


@dataclass
class ViewState:
    """Stores the current view bounds and zoom history."""
    x_min: float = -2.1
    x_max: float = 0.8
    y_min: float = -1.3
    y_max: float = 1.3

    def __iter__(self):
        return iter((self.x_min, self.x_max, self.y_min, self.y_max))

    def copy(self) -> 'ViewState':
        """Create a deep copy of this state."""
        return ViewState(
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max
        )


class FractalExplorer:
    """
    Interactive fractal explorer using matplotlib.

    Features:
    - Rectangle zoom: click and drag to select area
    - Pan with navigation toolbar or arrow keys
    - Zoom in/out with mouse wheel (if available)
    - Multiple color maps via radio buttons
    - Reset button to return to initial view
    """

    def __init__(
        self,
        fractal_set=None,
        width: int = 800,
        height: int = 600,
        max_iterations: int = 256
    ):
        """
        Initialize the explorer.

        Args:
            fractal_set: FractalSet instance (defaults to Mandelbrot).
            width, height: Image resolution in pixels.
            max_iterations: Iteration count for fractal calculation.
        """
        # Set up fractal
        self.fractal = fractal_set or MandelbrotSet(max_iterations=max_iterations)
        self.max_iterations = max_iterations

        # Set up view state and history
        self.view_history: list[ViewState] = []
        self.history_index: int = -1

        x_min, x_max, y_min, y_max = self.fractal.get_default_bounds()
        self.initial_view = ViewState(x_min, x_max, y_min, y_max)
        self.current_view = self.initial_view.copy()

        # Set up image dimensions
        self.width = width
        self.height = height

        # Colormap registry - maps names to (colormap_instance, use_smoothing)
        self.colormaps: Dict[str, tuple] = {}
        self._register_default_colormaps()

        # Current colormap name
        self.current_colormap_name = "Fire"

        # Set up the figure and axes
        self.fig = plt.figure(figsize=(12, 9))
        self.ax = self.fig.add_axes([0.05, 0.15, 0.65, 0.8])  # Leave room for controls

        # Image display
        self.image_data: Optional[np.ndarray] = None
        self.image_object = None

        # Selection rectangle (for zoom-to-rectangle)
        self.rect_selector = None
        self._setup_rectangle_selector()

        # UI elements
        self.colormap_radio: Optional[RadioButtons] = None
        self.reset_button: Optional[Button] = None
        self.info_text = None

        # Set up the interface
        self._setup_ui()
        self._connect_events()

        # Initial render
        self.render_fractal()

    def _register_default_colormaps(self):
        """Register all available colormaps."""
        from colormaps.fire import FireMap, MagmaMap, InfernoMap
        from colormaps.cool import CoolMap, NebulaMap, OceanMap, ForestMap
        from colormaps.rainbow import RainbowMap, TurboMap, PastelMap
        from colormaps.grayscale import GrayscaleMap, InvertedGrayscaleMap
        from colormaps.classic import ClassicMandelbrot

        # Register maps: name -> (instance, use_smooth_coloring)
        self.colormaps = {
            "Fire": (FireMap(), True),
            "Magma": (MagmaMap(), True),
            "Inferno": (InfernoMap(), True),
            "Cool Blue": (CoolMap(), True),
            "Nebula": (NebulaMap(), True),
            "Ocean": (OceanMap(), True),
            "Forest": (ForestMap(), True),
            "Rainbow": (RainbowMap(), True),
            "Turbo": (TurboMap(), True),
            "Pastel": (PastelMap(), True),
            "Grayscale": (GrayscaleMap(), False),
            "Inv. Grayscale": (InvertedGrayscaleMap(), False),
            "Classic": (ClassicMandelbrot(), False),
        }

    def _setup_rectangle_selector(self):
        """Set up the zoom-to-rectangle functionality."""
        self.rect_selector = RectangleSelector(
            self.ax,
            self._on_zoom_select,
            useblit=True,
            button=[1],  # Left click only
            minspanx=10, minspany=10,  # Minimum selection size
            spancoords='pixels',
            interactive=False,
        )
        self.rect_selector.set_active(True)

    def _setup_ui(self):
        """Set up the user interface controls."""
        # Colormap selector panel
        ax_radio = self.fig.add_axes([0.72, 0.35, 0.25, 0.5])
        ax_radio.set_facecolor('#f0f0f0')
        self.colormap_radio = RadioButtons(
            ax_radio,
            list(self.colormaps.keys()),
            active=list(self.colormaps.keys()).index(self.current_colormap_name)
        )
        self.colormap_radio.on_clicked(self._on_colormap_change)

        # Add colormap label
        self.fig.text(0.85, 0.86, 'Color Map', ha='center', fontsize=11, fontweight='bold')

        # Reset button
        ax_reset = self.fig.add_axes([0.72, 0.08, 0.22, 0.06])
        self.reset_button = Button(ax_reset, 'Reset View', color='#e0e0e0')
        self.reset_button.on_clicked(self._on_reset)

        # Title
        self.ax.set_title(f"{self.fractal.name} - Drag to zoom", fontsize=12)
        self.fig.suptitle("Interactive Fractal Explorer", fontsize=14, fontweight='bold')

    def _connect_events(self):
        """Connect keyboard and mouse events."""
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)

    def render_fractal(self):
        """
        Render the fractal image for current view bounds.

        This is the main rendering function that computes the fractal
        values and applies the selected colormap.
        """
        # Get current view bounds
        x_min, x_max, y_min, y_max = self.current_view

        # Compute fractal with timing
        compute_start = perf_counter()
        fractal_values = self.fractal.compute_fractal(
            x_min, x_max,
            y_min, y_max,
            self.width, self.height
        )
        compute_time = perf_counter() - compute_start

        # Get colormap and smoothing preference
        cmap_obj, use_smoothing = self.colormaps[self.current_colormap_name]

        # Apply colormap with timing if using smoothing
        colorize_start = perf_counter()
        if use_smoothing:
            smooth_values = self.fractal.compute_smooth_color(
                fractal_values, x_min, x_max, y_min, y_max
            )
            colored_image = cmap_obj(smooth_values)
        else:
            colored_image = cmap_obj(fractal_values)
        colorize_time = perf_counter() - colorize_start

        # Display the image
        if self.image_object is None:
            self.image_object = self.ax.imshow(
                colored_image,
                extent=[x_min, x_max, y_min, y_max],
                origin='lower',
                aspect='equal'
            )
        else:
            self.image_object.set_data(colored_image)
            self.image_object.set_extent([x_min, x_max, y_min, y_max])

        # Update axis limits
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        # Compute diagnostics
        total_pixels = self.width * self.height
        max_iter_used = int(fractal_values.max())
        min_iter_used = int(fractal_values.min())

        # Center point info and span
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        span_x = abs(x_max - x_min)
        total_time_ms = (compute_time + colorize_time) * 1000

        # Print compact diagnostic summary
        print(f"{self.fractal.name[:15]:>15} | "
              f"{self.width}x{self.height} | "
              f"{self.current_colormap_name:12} | "
              f"[{x_min:.4f},{y_min:.4f}]..[{x_max:.4f},{y_max:.4f}] | "
              f"iter={self.max_iterations} [{min_iter_used}-{max_iter_used}] | "
              f"{compute_time*1000:5.1f}+{colorize_time*1000:5.1f}={total_time_ms:6.1f}ms")

        # Update info text on plot
        if self.info_text:
            self.info_text.remove()
        
        zoom_level = int(3.5 / span_x) if span_x > 0 else 0
        info_str = (
            f"Fractal: {self.fractal.name}\n"
            f"Res:     {self.width} x {self.height}\n"
            f"Colormap: {self.current_colormap_name}\n"
            f"Iter:    {self.max_iterations}\n"
            f"Center:  ({center_x:.6f}, {center_y:.6f})\n"
            f"Zoom:    1:{zoom_level:,}\n"
            f"Time:    {total_time_ms:.0f}ms"
        )
        self.info_text = self.fig.text(0.05, 0.02, info_str, fontsize=9,
                                        family='monospace', transform=self.fig.transFigure)

        # Redraw
        self.fig.canvas.draw()

    def _on_zoom_select(self, event_click, event_release):
        """Handle rectangle zoom selection."""
        x1 = min(event_click.xdata, event_release.xdata)
        x2 = max(event_click.xdata, event_release.xdata)
        y1 = min(event_click.ydata, event_release.ydata)
        y2 = max(event_click.ydata, event_release.ydata)

        # Only zoom if selection is large enough
        span_x = abs(x2 - x1)
        span_y = abs(y2 - y1)

        current_span = (self.current_view.x_max - self.current_view.x_min,
                       self.current_view.y_max - self.current_view.y_min)

        # Use 1/50 of current dimension as minimum (allows ~7x zoom per selection)
        min_span_x = max(current_span[0] / 50, 1e-14)
        min_span_y = max(current_span[1] / 50, 1e-14)

        if span_x < min_span_x or span_y < min_span_y:
            print(f"Selection too small (min: {min_span_x:.2e} x {min_span_y:.2e})")
            return

        # Save current view to history before changing
        self._save_view_state()

        # Update current view with new bounds
        self.current_view.x_min = x1
        self.current_view.x_max = x2
        self.current_view.y_min = y1
        self.current_view.y_max = y2

        self.render_fractal()

    def _on_colormap_change(self, label: str):
        """Handle colormap selection change."""
        self.current_colormap_name = label
        print(f"Changed to {label} colormap")
        self.render_fractal()

    def _on_reset(self, event=None):
        """Reset view to initial state."""
        self._save_view_state()
        self.current_view = self.initial_view.copy()
        self.render_fractal()

    def _on_key_press(self, event):
        """Handle keyboard navigation."""
        x_span = self.current_view.x_max - self.current_view.x_min
        y_span = self.current_view.y_max - self.current_view.y_min

        dx = x_span * 0.1
        dy = y_span * 0.1

        moved = False

        if event.key == 'left':
            self._save_view_state()
            self.current_view.x_min -= dx
            self.current_view.x_max -= dx
            moved = True
        elif event.key == 'right':
            self._save_view_state()
            self.current_view.x_min += dx
            self.current_view.x_max += dx
            moved = True
        elif event.key == 'up':
            self._save_view_state()
            self.current_view.y_min += dy
            self.current_view.y_max += dy
            moved = True
        elif event.key == 'down':
            self._save_view_state()
            self.current_view.y_min -= dy
            self.current_view.y_max -= dy
            moved = True
        elif event.key in ('+', '=', 'page-up'):
            # Zoom in
            self._zoom(0.5)
            moved = True
        elif event.key in ('-', 'page-down'):
            # Zoom out
            self._zoom(2.0)
            moved = True
        elif event.key == 'home':
            # Reset to initial view
            self._save_view_state()
            self.current_view = self.initial_view.copy()
            moved = True

        if moved:
            self.render_fractal()

    def _zoom(self, factor: float):
        """Zoom in or out by the given factor."""
        center_x = (self.current_view.x_min + self.current_view.x_max) / 2
        center_y = (self.current_view.y_min + self.current_view.y_max) / 2

        half_width = (self.current_view.x_max - self.current_view.x_min) / 2 * factor
        half_height = (self.current_view.y_max - self.current_view.y_min) / 2 * factor

        # Limit zoom to prevent numerical precision issues (double precision limit)
        if abs(center_x) + half_width < 1e-13 and abs(center_y) + half_height < 1e-13:
            print("Maximum zoom reached (approaching double precision limit)")
            return
        if half_width < 1e-15 or half_height < 1e-15:
            # Still allow zooming to very small regions, but warn on next attempt
            pass

        self._save_view_state()

        self.current_view.x_min = center_x - half_width
        self.current_view.x_max = center_x + half_width
        self.current_view.y_min = center_y - half_height
        self.current_view.y_max = center_y + half_height

    def _save_view_state(self):
        """Save current view to history, removing any future states."""
        # Remove any states after current index (in case we went back)
        if self.history_index < len(self.view_history) - 1:
            self.view_history = self.view_history[:self.history_index + 1]

        # Save current state
        self.view_history.append(self.current_view.copy())
        self.history_index += 1

    def zoom_out(self):
        """Go back to previous view (undo)."""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_view = self.view_history[self.history_index].copy()
            self.render_fractal()

    def show(self):
        """Display the explorer window."""
        plt.show()


# Import RectangleSelector at module level to avoid issues
from matplotlib.widgets import RectangleSelector


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactive Fractal Explorer"
    )
    parser.add_argument(
        '--width', type=int, default=800,
        help='Image width in pixels (default: 800)'
    )
    parser.add_argument(
        '--height', type=int, default=600,
        help='Image height in pixels (default: 600)'
    )
    parser.add_argument(
        '--iterations', type=int, default=256,
        help='Maximum iterations for fractal calculation (default: 256)'
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    print("=" * 50)
    print("Interactive Fractal Explorer")
    print("=" * 50)
    print()
    print("Controls:")
    print("  Click and drag to zoom into a region")
    print("  Arrow keys: Pan around the image")
    print("  +/- or Page Up/Down: Zoom in/out")
    print("  Home key: Reset to initial view")
    print("  Select colormaps from the panel on the right")
    print()
    print(f"Resolution: {args.width} x {args.height}")
    print(f"Iterations: {args.iterations}")
    print()

    explorer = FractalExplorer(
        width=args.width,
        height=args.height,
        max_iterations=args.iterations
    )
    explorer.show()


if __name__ == "__main__":
    main()