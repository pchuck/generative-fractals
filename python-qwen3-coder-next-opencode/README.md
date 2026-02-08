# Interactive Fractal Explorer

An interactive visualization tool for exploring fractals like Mandelbrot, Julia sets, Burning Ship, and more.

## Features

- **10+ Fractal Types**: Mandelbrot, Julia, Burning Ship, Tricorn, Multibrot, Phoenix, Newton, Cubic Julia, Feather, Spider
- **8 Color Palettes**: Smooth, Banded, Grayscale, Fire, Ocean, Rainbow, Electric, Neon
- **Interactive Zoom**: Drag to select area, scroll to zoom, back/forward navigation
- **Adjustable Detail**: 50-2000 iterations for performance vs quality
- **Parallel Rendering**: Uses multiple CPU cores for fast rendering

## Requirements

- Python 3.8+
- NumPy
- Pillow

```bash
pip install numpy pillow
```

## Running

```bash
python fractal_explorer.py
```

For developers and implementation details, see [AGENTS.md](AGENTS.md).
