# Fractal Explorer

Interactive fractal explorer built with Rust, eframe/egui, and Rayon for parallel CPU rendering.

![Fractal Explorer Screenshot](screenshot.png)

## Features

### Fractal Types (7)
- **Mandelbrot** - Classic Mandelbrot set with adjustable power
- **Julia** - Julia set with customizable c_real, c_imag parameters
- **Burning Ship** - Iterated with absolute values
- **Tricorn** - Also known as Mandelbar (conjugated iteration)
- **Celtic** - Variant with absolute value on real component
- **Newton** - Newton's method visualization for z³ - 1 = 0
- **Biomorph** - Modified Newton with escape conditions (biological patterns)

### Color Palettes (5)
- **Classic** - Rainbow gradient (black → blue → cyan → green → yellow → red → white)
- **Fire** - Heat map (black → red → orange → yellow → white)
- **Ice** - Cold tones (black → blue → cyan → white)
- **Grayscale** - Black to white gradient
- **Psychedelic** - HSV cycling with adjustable offset

### Interactive Controls
- **Click + Drag** - Select zoom region
- **Mouse Wheel** - Zoom in/out at cursor position
- **Arrow Keys** - Pan view
- **+ / -** - Zoom in/out by 1.5x
- **R** - Reset view to defaults
- **S** - Save image (1x resolution)
- **Ctrl+Z** - Undo last view change
- **Ctrl+Y** - Redo view change

### Display Features
- **Mouse Coordinates** - Shows fractal coordinates (real, imaginary) under cursor
- **Zoom Preview** - Blocky preview when zooming for instant feedback
- **Progress Bar** - Shows rendering progress for large images
- **Supersampling** - 2x supersampling for smoother edges (toggle in UI)

### State Management
- **Per-Fractal State** - Each fractal remembers its view position, zoom, iterations, and palette
- **Undo/Redo** - 50-step history of view changes
- **Configuration File** - Saves window size, defaults, and settings to `~/.config/fractal-explorer/config.json`

### Export Options
- **1x (Current)** - Fast save of cached image
- **2x / 4x** - High-resolution export (renders at higher resolution)
- **Supersampling** - 2x internal render with box filter downsampling
- All exports saved to `images/` directory with auto-generated filenames

## Building

```bash
# Build and run
cargo build --release && cargo run --release

# Debug mode with logging
RUST_LOG=debug cargo run

# Run tests
cargo test

# Format and lint
cargo fmt
cargo clippy -- -D warnings
```

## Controls Reference

| Key | Action |
|-----|--------|
| Click + Drag | Select zoom region |
| +/- | Zoom in/out |
| Arrow Keys | Pan view |
| R | Reset view |
| S | Save image |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |

## Parameters

### Fractal-Specific
- **Power** (Mandelbrot, Julia, Burning Ship, Tricorn, Celtic) - Exponent value (1.0-8.0)
- **c_real / c_imag** (Julia) - Julia set constant (-2.0 to 2.0)
- **Escape Radius** (Newton, Biomorph) - Convergence threshold (4.0-64.0)
- **Tolerance** (Newton, Biomorph) - Root detection sensitivity (0.0001-0.1)

### Global
- **Iterations** - Maximum iteration count (16-2000)
- **Color Offset** (Psychedelic palette) - Color rotation (0.0-1.0)
- **Supersampling** - Enable 2x supersampling for smoother edges

## Configuration

Settings are automatically saved to:
- **Linux**: `~/.config/fractal-explorer/config.json`
- **macOS**: `~/Library/Application Support/fractal-explorer/config.json`
- **Windows**: `%APPDATA%\fractal-explorer\config.json`

Saved settings include:
- Window size
- Default fractal type
- Default palette
- Default iteration count
- Supersampling preference

## Architecture

```
src/
├── main.rs           # Application entry, event loop, state management
├── ui/mod.rs         # Control panel UI components
├── fractal/mod.rs    # Fractal trait & 7 implementations
├── palette/mod.rs    # Color palette system (5 palettes)
└── renderer/mod.rs   # Screen-to-fractal coordinate mapping
```

### Key Components

**FractalApp**: Main application state managing:
- View state per fractal type
- Undo/redo history
- Incremental rendering
- Supersampling buffers

**ViewHistory**: Manages undo/redo stack (50 entries max)

**Incremental Rendering**: Renders fractal in chunks for UI responsiveness

## Dependencies

- `eframe` / `egui` - GUI framework
- `rayon` - Data-parallel processing for rendering
- `image` - PNG export functionality
- `serde` / `serde_json` - Configuration serialization
- `dirs` - Cross-platform config directory detection

## Performance Tips

- **Disable supersampling** for faster navigation
- **Lower iterations** when exploring (increase for final renders)
- **Use 1x export** for quick saves, 2x/4x for high quality
- Rendering is CPU-parallel using all available cores

## License

MIT License - See LICENSE file for details
