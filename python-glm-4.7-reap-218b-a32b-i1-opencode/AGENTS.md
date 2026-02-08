# Agent Guidelines for Fractal Explorer

This is a Python-based interactive fractal visualization application using Tkinter.

## Build/Run Commands

```bash
# Run the main application
python fractal_explorer.py

# Run quick test (opens GUI window)
python test_app.py

# Run a specific test file (if pytest available)
python -m pytest test_app.py -v

# Run a single test function
python -m pytest test_app.py::test_function_name -v
```

## Code Style Guidelines

### Python Style
- **Indentation**: 4 spaces (no tabs)
- **Line length**: ~100 characters max
- **Quotes**: Double quotes for docstrings, single quotes for strings
- **Type hints**: Use typing module (Dict, List, Optional, Callable, etc.)

### Naming Conventions
- **Classes**: PascalCase (e.g., `FractalBase`, `UIManager`)
- **Functions/variables**: snake_case (e.g., `compute_pixel`, `zoom_controller`)
- **Constants**: UPPER_CASE for module-level constants
- **Private**: Leading underscore for internal functions/vars (e.g., `_fractal_registry`)

### Imports Order
1. Standard library (os, sys, typing, etc.)
2. Third-party (numpy, PIL, etc.)
3. Local modules (use relative imports within packages)

```python
import cmath
from typing import Dict, Any, Optional

import numpy as np

from . import FractalBase, register_fractal
```

### Docstrings
Use Google-style docstrings with Args and Returns sections:

```python
def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
    """Compute iteration count for a single pixel.
    
    Args:
        x: Real coordinate in complex plane
        y: Imaginary coordinate in complex plane
        max_iter: Maximum iterations to perform
        
    Returns:
        Iteration count (or smooth value if applicable)
    """
```

### Error Handling
- Use try/except for optional dependencies (e.g., PIL)
- Return None for "not found" cases in registry lookups
- Graceful degradation for UI features

## Architecture

### Module Structure
- `fractals/` - Fractal implementations with registry pattern
- `palettes/` - Color palette implementations
- `navigation/` - Zoom and coordinate handling
- `rendering/` - Parallel computation engine
- `ui/` - Tkinter interface components

### Registry Pattern
Fractals and palettes use decorators for auto-registration:

```python
@register_fractal("my_fractal")
class MyFractal(FractalBase):
    name = "My Fractal"
    description = "z = ..."
    parameters = {"key": value}
```

## Adding New Features

### New Fractal
Create file in `fractals/`:

```python
"""Description."""

from . import FractalBase, register_fractal, smooth_coloring


@register_fractal("unique_id")
class MyFractal(FractalBase):
    """Description."""
    
    name = "Display Name"
    description = "Formula"
    parameters = {"c": -0.75 + 0.1j}
    
    def get_default_bounds(self) -> dict:
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        c = complex(x, y)
        z = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                return smooth_coloring(z, i, max_iter, 2.0)
            z = z * z + c
        
        return float(max_iter)
```

Then import in `fractal_explorer.py`:
```python
from fractals.my_fractal import *
```

### New Palette
Add to `palettes/standard.py`:

```python
@register_palette("my_palette")
class MyPalette(PaletteBase):
    """Description."""
    
    name = "My Palette"
    description = "..."
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        r = int(t * 255)
        g = int((1 - t) * 255)
        b = 128
        
        return (r, g, b)
```

## Dependencies

Core dependencies:
- Python 3.8+
- tkinter (usually bundled)
- numpy
- pillow (PIL) - optional, for saving images
- multiprocessing (stdlib)

## Testing Notes

- Tests open GUI windows and require user interaction to close
- Use `python test_app.py` for smoke testing
- No formal unit test suite currently configured
