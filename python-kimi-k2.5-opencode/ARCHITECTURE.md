# Architecture

This document describes the internal architecture of the Fractal Explorer application for developers.

## Modular Design

```
fractal_explorer.py      # Main orchestrator
fractals/                # Fractal implementations
  ├── __init__.py        # Base classes & registry
  ├── ifs_base.py        # IFS base class
  ├── mandelbrot.py      # Mandelbrot set
  ├── julia.py           # Julia sets
  └── ...                # Other fractals
palettes/                # Color palette implementations
  ├── __init__.py        # Base classes & registry
  └── standard.py        # 8 palette implementations
rendering/               # Rendering engine
  ├── __init__.py        # Render engine with threading
  └── parallel.py        # Multiprocessing utilities
navigation/              # Zoom controller
ui/                      # UI manager
```

## Key Classes

- **FractalBase** - Abstract base for all fractals
- **IFSFractalBase** - Base for point-based IFS fractals
- **PaletteBase** - Abstract base for color palettes
- **RenderEngine** - Handles async rendering with progress
- **ZoomController** - Mouse interaction handling
- **FractalRegistry** - Plugin system for fractals
- **PaletteRegistry** - Plugin system for palettes

## Rendering Pipeline

1. **Escape-time fractals** - Parallel row computation using multiprocessing
2. **IFS fractals** - Vectorized NumPy operations for point generation
3. **Color mapping** - Smooth HSV or discrete band coloring
4. **Image display** - PIL ImageTk for canvas rendering

## State Management

- Each fractal maintains independent bounds, iterations, palette
- History stack (50 entries max) per fractal
- Auto-save state on every view change

## Adding New Components

### New Fractal (Escape-Time)

```python
from . import FractalBase, register_fractal
import numpy as np

@register_fractal("my_fractal")
class MyFractal(FractalBase):
    name = "My Fractal"
    description = "Brief description"
    
    def get_default_bounds(self):
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        # Implementation here
        pass
```

Import in `fractal_explorer.py`: `from fractals.my_fractal import *`

### New Fractal (IFS)

```python
from .ifs_base import IFSFractalBase, register_fractal
import numpy as np

@register_fractal("my_ifs")
class MyIFS(IFSFractalBase):
    name = "My IFS"
    
    def get_transformations(self):
        return [
            (0.5, lambda x, y: (x/2, y/2)),
            (0.5, lambda x, y: (x/2 + 0.5, y/2)),
        ]
```

### New Palette

```python
from . import PaletteBase, register_palette
from typing import Tuple

@register_palette("my_palette")
class MyPalette(PaletteBase):
    name = "My Palette"
    description = "Custom color scheme"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        # Return RGB tuple (0-255)
        return (255, 128, 0)
```

## See Also

- [README.md](README.md) - User documentation
- [AGENTS.md](AGENTS.md) - Coding guidelines for AI agents
