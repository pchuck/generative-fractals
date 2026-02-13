# Fractal Explorer

Interactive fractal explorer built with Rust, eframe/egui, and Rayon for parallel CPU rendering.

## Features

- **Multiple fractal types**: Mandelbrot, Julia, Burning Ship, Tricorn, Celtic, Newton, Biomorph
- **Color palettes**: Classic, Fire, Ice, Grayscale, Psychedelic
- **Interactive controls**: Click and drag to zoom, adjustable iterations, fractal parameters
- **Per-fractal state**: Each fractal remembers its view position, zoom, iterations, and palette
- **Image export**: Save fractals as PNG files
- **Incremental rendering**: Progress updates during rendering

## Building

```bash
# Build and run
cargo build --release && cargo run --release

# Debug mode with logging
RUST_LOG=debug cargo run

# Run tests
cargo test
```

## Controls

- **Click + Drag**: Select zoom region
- **Reset View**: Return to default view for current fractal
- **Save**: Export current view as PNG to `images/` directory

### Parameters

- **Iterations**: Control detail level (16-2000)
- **Power** (Mandelbrot, Julia, Burning Ship, Tricorn, Celtic): Fractal exponent (1.0-8.0)
- **Escape Radius** (Newton, Biomorph): Convergence threshold (4.0-64.0)
- **Tolerance** (Newton, Biomorph): Root detection sensitivity (0.0001-0.1)
- **Color Offset** (Psychedelic palette): Color rotation (0.0-1.0)

## Fractal Types

| Fractal | Description |
|---------|-------------|
| **Mandelbrot** | Classic Mandelbrot set |
| **Julia** | Julia set with adjustable c_real, c_imag |
| **Burning Ship** | Iterated with absolute values |
| **Tricorn** | Mandelbar/tri-corn fractal |
| **Celtic** | Variant with abs() on real component |
| **Newton** | Newton's method for z³ - 1 = 0 |
| **Biomorph** | Modified Newton with biological patterns |

## Architecture

```
src/
├── main.rs           # Application entry, event loop, state
├── ui/mod.rs         # Control panel UI
├── fractal/          # Fractal trait & implementations
├── palette/          # Color palette system
└── renderer/         # Coordinate mapping
```

## Dependencies

- `eframe` / `egui` - GUI framework
- `rayon` - Parallel processing
- `image` - PNG export
- `anyhow` - Error handling
