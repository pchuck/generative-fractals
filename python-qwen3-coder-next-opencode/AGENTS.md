# Agent Coding Guidelines - Fractal Explorer

## Project Overview

Interactive fractal visualization tool with support for Mandelbrot, Julia sets, Burning Ship, Tricorn, Multibrot, Phoenix, Newton's method, and more. Built with Python, Tkinter, NumPy, and Pillow.

## Directory Structure

```
python-qwen3-coder-next-opencode/
├── fractal_explorer.py          # Main application entry point
├── fractals/                    # Fractal implementations
│   ├── __init__.py             # Base classes & registry system
│   ├── mandelbrot.py           # Classic Mandelbrot set
│   ├── julia.py                # Julia sets with presets
│   ├── multibrot.py            # Generalized Mandelbrot (z^n + c)
│   ├── burning_ship.py         # Burning Ship fractal
│   ├── tricorn.py              # Tricorn/Mandelbar
│   ├── phoenix.py              # Phoenix fractal
│   ├── newton.py               # Newton's method visualization
│   ├── cubic_julia.py          # Cubic Julia sets
│   ├── feather.py              # Feather fractal pattern
│   ├── spider.py               # Spider fractal
│   └── orbit_trap.py           # Orbit trap variants
├── palettes/                    # Color palette implementations
│   ├── __init__.py             # Base classes & registry system
│   └── standard.py             # Standard palettes (smooth, banded, etc.)
├── navigation/                  # Zoom and pan controller
│   └── __init__.py             # ZoomController class
├── rendering/                   # Rendering engine
│   ├── __init__.py             # Base classes
│   └── parallel.py             # Parallel multiprocessing renderer
└── ui/                          # User interface components
    └── __init__.py             # UIManager class
```

## Build and Run Commands

### Running the Application

```bash
python fractal_explorer.py
```

### Requirements

- Python 3.8+
- NumPy (`pip install numpy`)
- Pillow (`pip install pillow`)

No build step required - pure Python application.

## Code Style Guidelines

### Python Conventions

1. **Imports**
   - Absolute imports preferred: `from fractals import FractalBase`
   - Group by: standard library, third-party, local modules
   - Use relative imports within packages: `from . import register_fractal`
   - Import in order: typing, numpy, PIL, local modules

2. **Type Hints**
   - Required for all function signatures
   - Use `Dict`, `List`, `Tuple` from `typing` module
   - Example: `def compute_pixel(self, x: float, y: float, max_iter: int) -> float`
   - Use `|` union syntax where appropriate: `ZoomController | None`

3. **Naming Conventions**
   - Classes: PascalCase (e.g., `FractalBase`, `ParallelRenderEngine`)
   - Functions/Methods: snake_case (e.g., `compute_pixel`, `get_default_bounds`)
   - Constants: UPPER_SNAKE_CASE (e.g., `JULIA_PRESETS`)
   - Variables: snake_case

4. **Docstrings**
   - Use Google-style docstrings
   - Include brief description, parameters, return values
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

5. **Error Handling**
   - Use try-except for recoverable errors (e.g., `ValueError`, `ZeroDivisionError`)
   - Log meaningful error messages
   - Example from Mandelbrot:
     ```python
     try:
         nu = np.log(np.log(abs(z)) / np.log(power)) / np.log(power)
     except (ValueError, ZeroDivisionError):
         nu = 0
     ```

6. **Formatting**
   - Maximum line length: 88 characters
   - Use 4 spaces for indentation
   - No trailing whitespace
   - Single blank line between top-level definitions

### Architecture Patterns

1. **Registry Pattern**
   - Fractals and palettes register automatically via decorators
   - Use `@register_fractal("name")` and `@register_palette("name")`
   - Access via `FractalRegistry.get(name)` or `PaletteRegistry.get(name)`

2. **Strategy Pattern**
   - Swappable fractal algorithms implement `FractalBase`
   - Swappable palettes implement `PaletteBase`

3. **MVC Architecture**
   - Model: Fractal classes, rendering engine
   - View: Tkinter UI components
   - Controller: Main application class

4. **Parallel Processing**
   - Row-based parallel computation using multiprocessing
   - Uses `cpu_count - 1` workers by default
   - Workers are processes (not threads) for true parallelism

### Adding New Fractals

1. Create file in `fractals/` directory
2. Import base classes: `from . import FractalBase, register_fractal`
3. Implement required methods:
   ```python
   @register_fractal("my_fractal")
   class MyFractal(FractalBase):
       name = "My Fractal"
       description = "Description of fractal"
       
       def get_default_bounds(self) -> Dict[str, float]:
           return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -2.0, 'ymax': 2.0}
       
       def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
           # Implementation here
   ```

4. Import in `fractal_explorer.py` if not auto-loaded

### Adding New Palettes

1. Add to `palettes/standard.py` or create new file in `palettes/`
2. Import base classes: `from . import PaletteBase, register_palette`
3. Implement required method:
   ```python
   @register_palette("my_palette")
   class MyPalette(PaletteBase):
       name = "My Palette"
       description = "Custom color scheme"
       
       def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
           # Return RGB tuple (0-255)
   ```

## Testing

**No tests currently exist.** When adding tests:

- Use pytest framework
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Test individual fractal implementations
- Test rendering with different palettes
- Test zoom/pan coordinate conversions

Example (to be implemented):
```bash
pytest tests/test_mandelbrot.py -v
pytest tests/ -k "julia or burning_ship" --tb=short
```

## Git Workflow

- Commit message format: `verb: brief description` (e.g., `add: new fractal type`)
- Use feature branches for new functionality
- Test changes before committing
- Update README.md when adding features

## Performance Considerations

1. **Rendering**
   - Uses parallel processing by default
   - Smooth coloring adds computational cost but improves visual quality
   - Lower iterations (50-200) for exploration, higher (500-2000) for final renders

2. **Memory**
   - Images rendered as NumPy arrays before converting to Pillow Image
   - Parallel workers share read-only data via multiprocessing

3. **Bounds**
   - Each fractal type has default bounds optimized for its appearance
   - ZoomController handles coordinate transformations

## Common Tasks

### Add a new parameter to existing fractal

1. Update `__init__` method with default value
2. Implement `get_parameters()` and `set_parameters()`
3. Update UI in `fractal_explorer.py` if needed

### Optimize rendering

1. Check row-based parallelization in `rendering/parallel.py`
2. Consider caching for repeated calculations
3. Use NumPy vectorization where possible

## Notes for AI Agents

- This is educational/open-source code - prioritize readability over micro-optimizations
- Follow existing patterns exactly when extending
- Test visual output manually when modifying rendering logic
- Keep type hints consistent across all files
- Document any breaking changes to the API

---

**Last updated**: 2026-02-07
