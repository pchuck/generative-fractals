# Fractal Explorer

A high-performance, interactive fractal visualization application built with Python and Tkinter. Explore 27 different fractal types with real-time zoom, pan, and customizable color palettes.

**[Quick Start](#installation)** | **[Features](#features)** | **[Fractal Catalog](#fractal-catalog)** | **[Architecture](ARCHITECTURE.md)**

## Quick Start

```bash
pip install numpy pillow
python3 fractal_explorer.py
```

## Features

### **27 Fractal Types**
- **Mandelbrot Set** - The classic boundary of the Mandelbrot set
- **Julia Sets** - Multiple variants including dendrite, dragon, and spiral
- **IFS Fractals** - Barnsley fern, Sierpinski triangle/carpet, dragon curve, maple leaf
- **Special Variants** - Burning Ship, Tricorn, Phoenix, Newton, Nova, Multibrot, and more
- **Advanced Variants** - Distance estimation, orbit traps, Pickover stalks

### **8 Color Palettes**
- **Smooth** - Continuous HSV color cycling with customizable hue/saturation
- **Banded** - Discrete color bands for structured visualization
- **Rainbow** - Full spectrum colors
- **Grayscale** - Black and white with optional inversion
- **Fire** - Red, orange, and yellow gradient
- **Ocean** - Blues and greens
- **Electric** - Electric blue and cyan
- **Neon** - Neon pink and green

### **Performance**
- **Parallel Rendering** - Uses all available CPU cores for escape-time fractals
- **Vectorized IFS** - NumPy-optimized point generation and rendering
- **Debounced Resize** - Efficient window resizing with 200ms debounce
- **Async Rendering** - Non-blocking UI during computation

### **Interactive Controls**
- **Mouse Wheel** - Zoom in/out with smooth scaling
- **Click** - Zoom in at specific point
- **Drag** - Selection zoom to specific region
- **Real-time Preview** - Live zoom preview during selection
- **Mouse Tracking** - Status bar shows coordinates in complex plane

### **Keyboard Shortcuts**
| Key | Action |
|-----|--------|
| `R` | Reset view to defaults |
| `B` | Go back (undo) |
| `F` | Go forward (redo) |
| `Ctrl+S` | Save image to file |
| `F1` | Show About/Help dialog |

### **History & State**
- **Per-Fractal History** - Each fractal maintains its own undo/redo stack (50 states)
- **State Persistence** - Bounds, iterations, and palette preferences saved per fractal
- **Smart History** - Automatically removes duplicate consecutive states

## Installation

### Requirements
- Python 3.8+
- NumPy
- Pillow (PIL)
- Tkinter (usually included with Python)

### Install Dependencies
```bash
pip install numpy pillow
```

### Run the Application
```bash
python3 fractal_explorer.py
```

## Usage Guide

### Getting Started
1. Launch the application
2. Select a fractal from the dropdown menu
3. Adjust iterations for detail level (50-2000)
4. Choose a color palette
5. Use mouse to zoom and explore

### Zooming
- **Mouse wheel** - Zoom in/out at cursor position
- **Click** - Zoom in 2x at click location
- **Drag** - Draw a selection rectangle to zoom to that region
- **R key** - Reset to default view

### Navigation
- **◀ (Back)** - Return to previous view
- **▶ (Forward)** - Go to next view
- Each fractal maintains its own history

### Saving Images
- Click **Save Image** button or press `Ctrl+S`
- Images saved to `images/` directory as PNG
- Filenames include fractal name and iteration count

### Customizing Colors
1. Select palette from dropdown
2. Some palettes have adjustable parameters (hue, saturation, bands)
3. Changes apply immediately

### Parameter Sliders
Some fractals have adjustable parameters:
- **Julia sets** - Complex constant `c`
- **Multibrot** - Power (z³, z⁴, z⁵, etc.)
- **IFS fractals** - Point count (affects density)

## Fractal Catalog

### Escape-Time Fractals
| Name | Description |
|------|-------------|
| mandelbrot | The classic z² + c Mandelbrot set |
| julia | z² + c with configurable constant |
| burning_ship | Mandelbrot variant with absolute values |
| tricorn | Conjugate Mandelbrot (z*² + c) |
| phoenix | z² + c + p·z_prev |
| multibrot | z^n + c with configurable power |
| newton | Newton's method for z³ - 1 = 0 |
| nova | Relaxed Newton's method |
| spider | z² + c with c = c/2 + z |
| feather | z² + z/c |

### IFS (Iterated Function System) Fractals
| Name | Description |
|------|-------------|
| barnsley_fern | Classic fern attractor with 4 transformations |
| sierpinski_triangle | Triangle subdivision with 3 contractions |
| sierpinski_carpet | Square holes with 8 contractions |
| dragon_curve | Heighway dragon with 2 rotations |
| maple_leaf | Natural leaf pattern |

### Advanced Variants
| Name | Description |
|------|-------------|
| mandelbrot_orbit_trap | Orbit trap coloring |
| mandelbrot_stalks | Pickover stalks (closest approach) |
| mandelbrot_interior | Interior distance estimation |
| mandelbrot_exterior | Exterior distance estimation |
| mandelbrot_deribail | Derivative-based bailout |

## Performance Tips

### Speed Up Rendering
- **Reduce iterations** - Lower max_iter for faster preview
- **Smaller window** - Resize window smaller for quicker updates
- **IFS point count** - Lower points parameter for IFS fractals

### Quality Improvements
- **Increase iterations** - 500-1000 for smooth coloring
- **Zoom deep** - Use selection zoom for precision
- **High point count** - 200k+ points for dense IFS images

## Development

### Running Tests
```bash
python3 tests/run_tests.py
```

### Adding a New Fractal
1. Create file in `fractals/` directory
2. Inherit from `FractalBase` or `IFSFractalBase`
3. Implement `compute_pixel()` or `iterate_point()`
4. Use `@register_fractal("name")` decorator
5. Import in `fractal_explorer.py`

### Adding a New Palette
1. Add class to `palettes/standard.py`
2. Inherit from `PaletteBase`
3. Implement `get_color()` method
4. Use `@register_palette("name")` decorator

For more details on the architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install numpy pillow`
- Check Tkinter is available: `python3 -c "import tkinter"`

### Slow rendering
- Reduce iteration count
- Close other CPU-intensive applications
- For IFS fractals, reduce point count parameter

### Images not saving
- Check write permissions in application directory
- Ensure `images/` directory can be created
- Try running with elevated permissions if needed

### UI not responding
- Large renders run in background threads
- Wait for render to complete or press any key to cancel

## License

MIT License - Feel free to use, modify, and distribute.

## Credits

Built with:
- Python 3
- Tkinter (GUI)
- NumPy (numerical computing)
- Pillow (image processing)

## Version History

### v2.0 (Current)
- Added 6 new IFS fractals
- Vectorized IFS rendering (10x faster)
- Added keyboard shortcuts
- Added mouse coordinate tracking
- Added incremental IFS progress
- Added About dialog
- Comprehensive type hints
- Unit tests (29 tests)

### v1.0
- Initial release
- 21 escape-time fractals
- 8 color palettes
- Basic zoom and pan
- History navigation

---

**Happy Exploring!**
