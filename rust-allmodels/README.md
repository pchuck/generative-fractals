# Fractal Explorer

Interactive fractal explorer built with Rust, eframe/egui, and Rayon for parallel CPU rendering.

![Fractal Explorer Screenshot](screenshot.png)

## Features

### Fractal Types (12)
- **Mandelbrot** - Classic Mandelbrot set with adjustable power
- **Julia** - Julia set with customizable c_real, c_imag parameters  
- **Burning Ship** - Iterated with absolute values
- **Tricorn** - Also known as Mandelbar (conjugated iteration)
- **Celtic** - Variant with absolute value on real component
- **Newton** - Newton's method visualization for z³ - 1 = 0
- **Biomorph** - Modified Newton with escape conditions (biological patterns)
- **Phoenix** - Julia variant with memory term creating flame-like patterns
- **Multibrot** - Mandelbrot with arbitrary power (3+ gives more lobes)
- **Spider** - Alternating Mandelbrot creating spiderweb patterns
- **Orbit Trap** - Mandelbrot variant tracking minimum distance to a trap point
- **Pickover Stalk** - Mandelbrot variant creating organic stalk patterns near axes

### Color Palettes (5)
- **Classic** - Rainbow gradient (black → blue → cyan → green → yellow → red → white)
- **Fire** - Heat map (black → red → orange → yellow → white)
- **Ice** - Cold tones (black → blue → cyan → white)
- **Grayscale** - Black to white gradient
- **Psychedelic** - HSV cycling with adjustable offset

### Interactive Controls
- **Click + Drag** - Select zoom region
- **Mouse Wheel** - Zoom in/out at cursor position
- **Arrow Keys** - Pan view with pixel reuse optimization (reuses ~87.5% of rendered pixels)
- **+ / -** - Zoom in/out by 1.5x
- **R** - Reset view to defaults
- **Shift+R** - Reset all settings (view, palette, parameters)
- **S** - Save image (1x resolution)
- **Ctrl+Z** - Undo last view change
- **Ctrl+Y** - Redo view change

### Display Features
- **Mouse Coordinates** - Shows fractal coordinates (real, imaginary) under cursor
- **Zoom Preview** - Blocky preview when zooming for instant feedback
- **Progress Bar** - Shows rendering progress for large images
- **Render Time** - Displays last render duration (e.g., "Last render: 450ms")
- **Supersampling** - 2x supersampling for smoother edges (toggle in UI)
- **Mini-map** - Small overview (150×150) showing full fractal with current view rectangle
- **Pan Optimization** - When panning with arrow keys, existing pixels are shifted and only new edge strips are recalculated (~87.5% performance improvement)

### State Management
- **Per-Fractal State** - Each fractal remembers its view position, zoom, iterations, palette, and parameters
- **Undo/Redo** - 50-step history of view changes
- **Bookmarks** - Save interesting locations with names, including position, zoom, iterations, and palette
- **Configuration File** - Saves window size, defaults, bookmarks, and settings to `~/.config/fractal-explorer/config.json`

### Smart Features
- **Adaptive Iterations** - Automatically increases max iterations as you zoom (prevents loss of detail at deep zoom levels)
- **Anti-Aliasing** - Supersampling option for smoother edges
- **Efficient Panning** - Arrow key panning reuses existing pixel data, only rendering new edge regions

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
| Arrow Keys | Pan view (optimized with pixel reuse) |
| R | Reset view |
| Shift+R | Reset all settings |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| S | Save image |

## Parameters

### Fractal-Specific
- **Power** (Mandelbrot, Burning Ship, Tricorn, Celtic, Multibrot, Spider) - Exponent value (1.0-10.0)
- **c_real / c_imag** (Julia, Phoenix) - Fractal constant (-2.0 to 2.0)
- **Memory** (Phoenix) - Memory parameter creating flame effects (-1.0 to 1.0)
- **Escape Radius** (Newton, Biomorph) - Convergence threshold (4.0-64.0)
- **Tolerance** (Newton, Biomorph) - Root detection sensitivity (0.0001-0.1)
- **trap_x / trap_y** (Orbit Trap) - Trap point coordinates (-2.0 to 2.0)
- **thickness / intensity** (Pickover Stalk) - Stalk thickness (0.01-1.0) and intensity (1.0-100.0)

### Global
- **Iterations** - Maximum iteration count (16-2000)
- **Color Offset** (Psychedelic palette) - Color rotation (0.0-1.0)
- **Supersampling** - Enable 2x supersampling for smoother edges
- **Adaptive Iterations** - Auto-adjust iterations based on zoom level

## Bookmarks

Save interesting locations for later:
- Click "Bookmark" button to save current view
- Each bookmark saves: name, fractal type, position, zoom, iterations, palette
- Click bookmark name to restore that view
- Bookmarks persist across sessions in config file

## Configuration

Settings are automatically saved to:
- **Linux**: `~/.config/fractal-explorer/config.json`
- **macOS**: `~/Library/Application Support/fractal-explorer/config.json`
- **Windows**: `%APPDATA%\fractal-explorer\config.json`

Saved settings include:
- Window size and position
- Default fractal type and palette
- Default iteration count
- Supersampling preference
- Adaptive iterations setting
- All bookmarks

## Architecture

```
src/
├── main.rs           # Application entry, event loop, state management
├── ui/mod.rs         # Control panel UI components
├── fractal/mod.rs    # Fractal trait & 12 implementations
├── palette/mod.rs    # Color palette system (5 palettes)
└── renderer/mod.rs   # Screen-to-fractal coordinate mapping
```

### Key Components

**FractalApp**: Main application state managing:
- View state per fractal type
- Undo/redo history
- Incremental rendering with timing
- Supersampling buffers
- Bookmarks
- Pan optimization with pixel reuse

**ViewHistory**: Manages undo/redo stack (50 entries max)

**Incremental Rendering**: Renders fractal in chunks for UI responsiveness with progress updates

**Pan Optimization**: When panning with arrow keys, shifts existing pixels and only renders new edge strips

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
- **Enable adaptive iterations** for automatic quality adjustment at different zoom levels
- **Use arrow keys** for panning - reuses ~87.5% of pixels via optimization
- Rendering is CPU-parallel using all available cores

## License

MIT License - See LICENSE file for details
