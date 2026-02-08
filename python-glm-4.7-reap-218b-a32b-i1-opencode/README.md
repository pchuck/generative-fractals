# Interactive Fractal Explorer

A high-performance, modular fractal visualization tool built with Python and Tkinter. Explore Mandelbrot, Julia sets, and many other fractal types with real-time zoom, pan, and customizable color palettes.

![Fractal Explorer Screenshot](screenshot.png)

## Features

### Fractal Types
- **Mandelbrot Set** - The classic fractal with smooth coloring
- **Julia Sets** - With customizable complex constant c, plus preset variants:
  - Julia Dendrite
  - Julia Dragon
  - Julia Spiral
- **Burning Ship** - Uses absolute values for ship-like shapes
- **Tricorn** - Conjugates z before squaring
- **Multibrot** - Configurable power (z^n + c, where n = 2-10)
- **Phoenix** - Uses previous z value in iteration
- **Newton** - Newton's method visualization for z³ - 1 = 0
- **Cubic Julia** - Julia set with z³ iteration
- **Feather** - z² + z/c iteration pattern
- **Spider** - Dynamic c parameter updating each iteration
- **Mandelbrot Variants**:
  - Orbit Trap - Tracks distance to geometric shapes
  - Pickover Stalks - Colors based on closest approach to axes
  - Interior Distance - Estimates distance from interior to boundary
  - Exterior Distance - Analytic distance estimation
  - Derivative Bailout - Uses |dz/dc| for bailout condition

### Color Palettes
- **Smooth** - Smooth HSV color cycling
- **Banded** - Discrete color bands
- **Grayscale** - Black and white gradient
- **Fire** - Red, orange, yellow gradients
- **Ocean** - Blues and greens
- **Rainbow** - Full spectrum
- **Electric** - Electric blue and cyan
- **Neon** - Neon pink and green

### Interactive Features
- **Zoom** - Mouse wheel or click to zoom in/out
- **Selection Zoom** - Click and drag to select zoom area
- **Pan** - Navigate through the fractal space
- **Real-time Preview** - Blocky preview appears instantly before detailed render
- **Parallel Rendering** - Uses all CPU cores for fast computation
- **Per-Fractal State** - Each fractal remembers its own zoom, iterations, and palette
- **Save Images** - Export fractals as PNG images

## Installation

### Requirements
- Python 3.8+
- Tkinter (usually included with Python)
- NumPy
- Pillow (PIL)

### Install Dependencies

```bash
pip install numpy pillow
```

### Run the Application

```bash
python fractal_explorer.py
```

## Usage Guide

### Basic Navigation

1. **Select a Fractal** - Choose from the dropdown menu
2. **Adjust Iterations** - Use the slider (50-2000) for detail level
3. **Choose a Palette** - Select from color scheme dropdown
4. **Zoom** - Use mouse wheel or click to zoom in
5. **Select Area** - Click and drag to zoom to a specific region
6. **Reset View** - Click "Reset View" to return to default
7. **Save Image** - Click "Save Image" to export as PNG

### Fractal-Specific Parameters

Some fractals have configurable parameters:
- **Julia Sets**: Edit the "c" parameter (format: `a+bj`)
- **Multibrot**: Adjust the power (2-10)
- **Phoenix**: Set the constant p
- **Orbit Trap**: Choose trap type (point, cross, circle, etc.)

### Performance Tips

- Lower iterations (100-200) for exploration
- Increase iterations (500-2000) for detailed final renders
- The application uses `cpu_count - 1` workers by default
- Status bar shows worker count and rendering progress

## Architecture

### Module Structure

```
fractal_explorer.py      # Main application controller
fractals/                # Fractal implementations
├── __init__.py          # Base classes and registry
├── mandelbrot.py        # Classic Mandelbrot
├── julia.py             # Julia sets
├── multibrot.py         # Configurable power
├── burning_ship.py      # Burning Ship fractal
├── tricorn.py           # Tricorn/Mandelbar
├── phoenix.py           # Phoenix fractal
├── newton.py            # Newton's method
├── cubic_julia.py       # Cubic Julia
├── feather.py           # Feather fractal
├── spider.py            # Spider fractal
├── orbit_trap.py        # Orbit trap variants
├── pickover_stalks.py   # Pickover stalks
├── interior_distance.py # Interior distance
├── exterior_distance.py # Exterior distance
└── deribail.py          # Derivative bailout

palettes/                # Color palette implementations
├── __init__.py          # Base classes and registry
└── standard.py          # Standard palettes

navigation/              # Navigation and zoom
└── __init__.py          # ZoomController class

rendering/               # Rendering engine
├── __init__.py          # RenderEngine class
└── parallel.py          # Parallel computation

ui/                      # User interface
└── __init__.py          # UIManager class
```

### Design Patterns

- **Registry Pattern** - Fractals and palettes register themselves automatically
- **Strategy Pattern** - Swappable fractal algorithms and color palettes
- **MVC Architecture** - Separation of UI, logic, and data
- **Parallel Processing** - Row-based parallel computation using multiprocessing

## Extending the Explorer

### Adding a New Fractal

Create a new file in `fractals/`:

```python
"""My custom fractal implementation."""

from . import FractalBase, register_fractal

@register_fractal("my_fractal")
class MyFractal(FractalBase):
    name = "My Fractal"
    description = "z = ..."
    parameters = {}  # Optional parameters
    
    def get_default_bounds(self):
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                return float(i)  # Or smooth value
            z = z * z + c  # Your iteration formula
        
        return float(max_iter)
```

Import it in `fractal_explorer.py`:

```python
from fractals.my_fractal import *
```

### Adding a New Color Palette

Create a new palette in `palettes/standard.py` or a new file:

```python
from . import PaletteBase, register_palette

@register_palette("my_palette")
class MyPalette(PaletteBase):
    name = "My Palette"
    description = "Custom color scheme"
    parameters = {}  # Optional parameters
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        # Your color logic here
        t = value / max_val
        r = int(255 * t)
        g = int(255 * (1 - t))
        b = 128
        
        return (r, g, b)
```

## Technical Details

### Smooth Coloring

The explorer uses smooth coloring algorithms for most fractals:
```
nu = log(log|z| / log(power)) / log(power)
value = i + 1 - nu
```

This provides continuous color gradients rather than discrete bands.

### Parallel Computation

Fractal rendering uses Python's `multiprocessing` module:
- Each worker process computes a subset of rows
- Uses `cpu_count - 1` workers (leaves one core for UI)
- Results combined into final image
- Progress updates every 10 rows

### Coordinate System

- Canvas coordinates: (0,0) at top-left
- Complex plane: Real axis horizontal, imaginary axis vertical
- Y-axis is flipped so positive imaginary is up

## Keyboard Shortcuts

- **Mouse Wheel** - Zoom in/out at cursor
- **Click** - Zoom in 2x at point
- **Click + Drag** - Select zoom rectangle
- **Reset View button** - Return to default view

## Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install numpy pillow`
- Check Tkinter is available: `python -c "import tkinter"`

### Slow rendering
- Reduce iteration count (slider)
- Check worker count in status bar
- Close other CPU-intensive applications

### Black/blank images
- Try different fractal types
- Check iteration count (minimum 50)
- Verify fractal implementation (some need specific bounds)

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Areas for improvement:
- Additional fractal types
- New color palettes
- Performance optimizations
- UI enhancements
- Documentation improvements

## Acknowledgments

- Mandelbrot set discovered by Benoit Mandelbrot
- Julia sets named after Gaston Julia
- Smooth coloring algorithm by Inigo Quilez
- Parallel processing inspired by fractal rendering community

---

**Enjoy exploring the infinite complexity of fractals!**
