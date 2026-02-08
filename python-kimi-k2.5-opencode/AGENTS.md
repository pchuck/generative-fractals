# Agent Coding Guidelines - Fractal Explorer

## Project Overview

Interactive fractal visualization application with 27 fractal types and 8 color palettes. Built with Python, Tkinter, NumPy, and Pillow. Uses parallel processing for escape-time fractals and vectorized NumPy for IFS fractals.

## Build, Test, and Run Commands

### Run Application
```bash
python3 fractal_explorer.py
```

### Run Tests
```bash
# Run all tests
python3 tests/run_tests.py

# Run specific test file
python3 tests/test_fractals.py
python3 tests/test_integration.py

# Run single test class
python3 -m unittest tests.test_fractals.TestFractalRegistry -v

# Run single test method
python3 -m unittest tests.test_fractals.TestMandelbrot.test_origin_in_set -v
```

### Dependencies
```bash
pip install numpy pillow
```

No build step required - pure Python application.

## Code Style Guidelines

### Imports
- Group by: standard library, third-party, local modules
- Use absolute imports: `from fractals import FractalBase`
- Within packages, use relative imports: `from . import register_fractal`
- Import order: `typing`, `numpy`, `PIL`, local modules
- Add module docstring after imports

### Type Hints
- Required for all function signatures
- Use `typing` imports: `Dict`, `List`, `Tuple`, `Any`, `Optional`
- Example: `def compute_pixel(self, x: float, y: float, max_iter: int) -> float`
- Use union syntax where supported: `image: Image | None`

### Naming Conventions
- **Classes**: PascalCase (e.g., `MandelbrotFractal`, `ParallelRenderEngine`)
- **Functions/Methods**: snake_case (e.g., `compute_pixel`, `get_default_bounds`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_ITERATIONS`, `MAX_HISTORY_SIZE`)
- **Variables**: snake_case
- **Private methods**: prefix with underscore (e.g., `_render_thread`)

### Docstrings
- Use triple-double quotes: `"""Docstring here"""`
- Include brief description and Args/Returns sections
- Example:
  ```python
  def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
      """Compute a single pixel value.
      
      Args:
          x: Real component of complex coordinate
          y: Imaginary component of complex coordinate
          max_iter: Maximum iteration count
          
      Returns:
          Float value representing iteration count with smooth coloring
      """
  ```

### Formatting
- Maximum line length: 100 characters
- Use 4 spaces for indentation
- No trailing whitespace
- Single blank line between top-level definitions
- Two blank lines between classes

### Error Handling
- Use specific exceptions (e.g., `ValueError`, `TypeError`)
- Handle NumPy warnings with try-except when appropriate
- Log meaningful error messages where applicable

## Architecture Patterns

### Registry Pattern
- Fractals and palettes auto-register via decorators
- Use `@register_fractal("name")` and `@register_palette("name")`
- Access via `FractalRegistry.create(name)` or `PaletteRegistry.create(name)`

### Base Classes
- **FractalBase**: Abstract base for escape-time fractals
  - Implement `compute_pixel(x, y, max_iter) -> float`
  - Override `get_default_bounds()` for viewport
- **IFSFractalBase**: Base for iterated function system fractals
  - Implement transformations as list of (probability, func)
  - Use vectorized NumPy operations for performance
- **PaletteBase**: Abstract base for color palettes
  - Implement `get_color(value, max_val) -> Tuple[int, int, int]`

### MVC Architecture
- **Model**: Fractal classes, Palette classes, RenderEngine
- **View**: Tkinter UI components (UIManager creates widgets)
- **Controller**: FractalExplorer main class, ZoomController

### Key Directories
```
fractal_explorer.py      # Main application orchestrator
fractals/                # Fractal implementations
palettes/                # Color palette implementations
rendering/               # Parallel rendering engine
navigation/              # Zoom/pan controller
ui/                      # UI manager and components
tests/                   # Unit and integration tests
```

## Adding New Components

### New Fractal (Escape-Time)
```python
# fractals/my_fractal.py
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
# palettes/standard.py
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

## Testing Guidelines

- Use Python's built-in `unittest` framework
- Test file naming: `test_*.py`
- Test class naming: `Test*` (e.g., `TestMandelbrot`)
- Test method naming: `test_*` (e.g., `test_origin_in_set`)
- Import modules to trigger registration before testing
- Place tests in `tests/` directory

## Performance Considerations

- Use NumPy for vectorized operations (IFS fractals)
- Parallel row-based computation for escape-time fractals
- Debounced window resize (200ms)
- Lower iterations (50-200) for exploration, higher (500-2000) for final renders

## Git Workflow

- Commit format: `verb: brief description` (e.g., `add: new phoenix fractal variant`)
- Test changes before committing
- Update README.md for new features

## Notes for AI Agents

- Prioritize readability over micro-optimizations
- Follow existing patterns exactly when extending
- Test visual output manually when modifying rendering
- Keep type hints consistent across all files
- Document any breaking API changes
- Educational/open-source code - maintain clarity

---

**Last updated**: 2026-02-07
