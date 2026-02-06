# Fractal Generator

An interactive fractal explorer application built with Python and Tkinter.

## Features

- **Multiple Fractal Types**: Mandelbrot, Julia, Multibrot, Burning Ship, Phoenix
- **Color Palettes**: 10 built-in palettes (Classic, Fire, Ocean, Rainbow, etc.)
- **Interactive Zoom**: Click and drag to select zoom region
- **Zoom Preview**: Shows expanded preview before calculating new pixels
- **Zoom History**: Undo/Redo zoom operations with full history
- **Coordinate Display**: Real-time display of complex coordinates under cursor
- **Parameter Controls**: Adjust fractal-specific parameters (c values, exponents)
- **Session State**: Remembers view and parameters when switching fractals
- **NumPy Acceleration**: Fast vectorized computation (enabled by default)
- **Parallel Rendering**: Optional multi-process computation
- **Image Export**: Save renders as JPEG files
- **Keyboard Shortcuts**: Quick access to common operations

## Installation

1. Ensure you have Python 3.7+ installed

2. Install Tkinter (if not already available):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # macOS (usually pre-installed)
   # Windows (usually pre-installed with Python)
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python run.py
# or
python -m fractal_generator
```

### Controls

- **Fractal Dropdown**: Select fractal type
- **Palette Dropdown**: Select color palette
- **Iterations Slider**: Adjust iteration limit (affects detail and computation time)
- **Parallel Checkbox**: Enable multi-process rendering
- **Reset View**: Return to default view for current fractal
- **Save Image**: Export current render as JPEG

### Navigation

- **Zoom In**: Click and drag to select a rectangular region
- **Undo Zoom**: Click "← Undo" button or press `Ctrl+Z`
- **Redo Zoom**: Click "Redo →" button or press `Ctrl+Y` or `Ctrl+Shift+Z`
- **Coordinate Display**: Move mouse over canvas to see complex coordinates

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Z` | Undo zoom |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo zoom |
| `R` | Reset view |
| `Ctrl+S` | Save image |

### Fractal Parameters

Some fractals have configurable parameters that appear when selected:

- **Julia**: c (real/imag), z₀ offset (real/imag)
- **Multibrot**: Exponent power
- **Phoenix**: c (real/imag), p coefficient (real/imag)

## Architecture

The application follows a modular design for easy extensibility:

```
fractal_generator/
├── __init__.py      # Package exports
├── __main__.py      # Module entry point
├── app.py           # Main Tkinter application
├── fractals.py      # Fractal types and factory
├── palettes.py      # Color palettes and factory
├── renderer.py      # Rendering engine (sequential/parallel)
└── state.py         # Session state management
```

## Extending

### Adding a New Fractal

```python
from fractal_generator import FractalType, FractalFactory

class MyFractal(FractalType):
    @property
    def name(self) -> str:
        return "My Fractal"
    
    @property
    def default_bounds(self):
        return (-2.0, 2.0, -1.5, 1.5)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        # Your iteration logic here
        z_real, z_imag = 0, 0
        for i in range(max_iter):
            # ... calculation ...
            if escaped:
                return i
        return max_iter

# Register the fractal
FractalFactory.register('my_fractal', MyFractal)
```

### Adding a New Palette

```python
from fractal_generator import PaletteFactory

def my_palette(iter_count: int, max_iter: int) -> tuple:
    if iter_count == max_iter:
        return (0, 0, 0)  # Black for bounded points
    
    # Map iteration to color
    t = iter_count / max_iter
    r = int(255 * t)
    g = int(128 * (1 - t))
    b = int(255 * (1 - t))
    
    return (r, g, b)

# Register the palette
PaletteFactory.register('My Palette', my_palette)
```

## License

MIT License
