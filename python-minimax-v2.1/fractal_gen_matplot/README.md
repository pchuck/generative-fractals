# Interactive Fractal Generator

A modular, interactive fractal explorer built with Python and matplotlib.

## Features

- **Interactive Zoom**: Click and drag to select any region to zoom in
- **Navigation**: Arrow keys for panning, +/- for zoom in/out
- **Multiple Color Maps**: 13 different color schemes included
- **Modular Design**: Easy to add new fractal sets and colormaps
- **History Navigation**: Track your exploration path

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python app.py --width 800 --height 600 --iterations 256
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| Click + Drag | Select region to zoom in |
| Arrow Keys (←↑→↓) | Pan around the image |
| +/- or Page Up/Down | Zoom in/out |
| Home | Reset to initial view |

### Mouse Controls

- **Left click + drag**: Draw a rectangle to zoom into that area
- **Mouse wheel** (when implemented): Scroll to zoom

## Architecture

```
fractal_gen/
├── app.py                 # Main application and UI
├── fractals/              # Fractal set implementations
│   ├── __init__.py
│   ├── base.py           # Abstract base class for all fractals
│   └── mandelbrot.py     # Mandelbrot set implementation
├── colormaps/             # Color mapping modules
│   ├── __init__.py
│   ├── base.py           # Base colormap interface
│   ├── fire.py           # Fire, Magma, Inferno palettes
│   ├── cool.py           # Cool blue/green palettes  
│   ├── rainbow.py        # Rainbow variations
│   ├── grayscale.py      # Grayscale options
│   └── classic.py        # Classic Mandelbrot styles
└── requirements.txt       # Dependencies
```

## Adding New Fractals

Create a new class inheriting from `FractalSet`:

```python
# fractals/new_fractal.py
from .base import FractalSet
import numpy as np

class NewFractal(FractalSet):
    @property
    def name(self) -> str:
        return "New Fractal"
    
    def compute_fractal(self, x_min, x_max, y_min, y_max, width, height):
        # Your implementation here
        return iteration_grid
    
    def get_default_bounds(self):
        return -2.0, 2.0, -1.5, 1.5
```

## Adding New Colormaps

Create a new colormap class:

```python
# colormaps/my_colormap.py
from .base import ContinuousColorMap

class MyColormap(ContinuousColorMap):
    def __init__(self, n_colors=256):
        super().__init__([
            (0.1, 0.05, 0.2),   # Color 1
            (0.9, 0.6, 0.3),    # Color 2
            (1.0, 0.95, 0.8),   # Color 3
        ], n_colors)
```

## Requirements

- Python 3.7+
- numpy
- matplotlib