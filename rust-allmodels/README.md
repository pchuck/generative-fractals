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

### Color Processors (5)
Color processors transform fractal iteration data into colors using different algorithms:
- **Standard Palette** - Direct palette mapping based on iteration count
- **Smooth Coloring** - Continuous coloring using logarithmic smoothing for gradient bands
- **Orbit Trap (Real Axis)** - Traps orbits near the real axis (y=0) for stalk-like patterns
- **Orbit Trap (Imaginary Axis)** - Traps orbits near the imaginary axis (x=0) for organic patterns
- **Orbit Trap (Origin)** - Traps orbits near the origin for center-focused patterns

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
- **Render Status** - Displays "Parallel: X threads" and "Last render: 450ms" next to Fractal Type
- **Supersampling** - 2x supersampling for smoother edges (toggle in UI)
- **Mini-map** - Small overview showing full fractal with current view rectangle
- **Pan Optimization** - When panning with arrow keys, existing pixels are shifted and only new edge strips are recalculated (~87.5% performance improvement)
- **About Dialog** - Shows App info with image and copyright

### State Management
- **Per-Fractal State** - Each fractal remembers its view position, zoom, iterations, palette, color processor, and parameters
- **Per-Fractal Undo/Redo** - Separate 50-step command history for each fractal type (view changes, parameters, palette, color processor, iterations are all tracked independently per fractal)
- **Bookmarks** - Save interesting locations with names, including position, zoom, iterations, palette, and color processor
- **Configuration File** - Saves window size, defaults, bookmarks, and settings to `~/.config/fractal-explorer/config.json`

### Smart Features
- **Adaptive Iterations** - Automatically increases max iterations as you zoom (prevents loss of detail at deep zoom levels)
- **Anti-Aliasing** - Supersampling option for smoother edges
- **Efficient Panning** - Arrow key panning reuses existing pixel data, only rendering new edge regions

### Export Options
- **Save (S) with Radio Buttons** - Select 1x, 2x, or 4x resolution, then click Save
- **High Resolution** - 2x and 4x renders at higher resolution for better quality
- **Supersampling** - 2x internal render with box filter downsampling
- All exports saved to `images/` directory with auto-generated filenames

## Building

```bash
# Build and run
make build && make run
# or
cargo build --release && cargo run --release

# Debug mode with logging
RUST_LOG=debug cargo run

# Run tests
cargo test
make test

# Format and lint
cargo fmt
cargo clippy -- -D warnings
make fmt
make lint
```

## Distribution

Create platform-specific installers:

```bash
# Create macOS .dmg package
make dist-mac

# Create Linux .deb package (for apt install)
make dist-linux

# Create Windows installer package
make dist-windows

# Create all distributions
make dist
```

**Distribution outputs:**
- macOS: `dist/FractalExplorer-0.1.0-macOS.dmg`
- Linux: `dist/fractal-explorer_0.1.0_amd64.deb`
- Windows: `dist/FractalExplorer-0.1.0-windows.zip`

### Installing on macOS
```bash
# Open the .dmg and drag to Applications
make dist-mac
open dist/FractalExplorer-0.1.0-macOS.dmg
```

### Installing on Linux (Debian/Ubuntu)
```bash
make dist-linux
sudo apt install ./dist/fractal-explorer_0.1.0_amd64.deb
# Run with: fractal-explorer
```

### Installing on Windows
```bash
make dist-windows
# Extract FractalExplorer-0.1.0-windows.zip
# Run install.bat as Administrator
# Or manually copy FractalExplorer.exe to your preferred location
```

## UI Layout

### Control Panel (Left Side)
- **Fractal Type** | **Render Status** - Side by side with vertical separator
  - Fractal dropdown on left
  - Thread count and render time on right
- **Color Palette** | **Color Processor** - Side by side with vertical separator
  - Palette dropdown on left
  - Color processor dropdown on right
- **Iterations** - Slider for max iterations
- **Fractal Parameters** - Dynamic controls based on fractal type
- **Save (S)** - Button with 1x/2x/4x radio buttons inline
- **Undo (^Z)** | **Redo (^Y)** - Side by side
- **Bookmarks** - List with Add button, status messages shown here
- **Settings** - Supersampling, Adaptive Iterations, Minimap toggles
- **Mouse** | **Keyboard** - Input reference
- **About** - Opens About dialog with image and copyright

### Display Panel (Center)
- Main fractal view
- Minimap overlay (top-right, when enabled)
- Selection rectangle (when dragging)

## Parameters

### Fractal-Specific
- **Power** (Mandelbrot, Burning Ship, Tricorn, Celtic, Multibrot, Spider) - Exponent value (1.0-10.0)
- **c_real / c_imag** (Julia, Phoenix) - Fractal constant (-2.0 to 2.0)
- **Memory** (Phoenix) - Memory parameter creating flame effects (-1.0 to 1.0), default 0.55
- **Default Phoenix**: c_real=0.0, c_imag=0.4, memory=0.55, iterations=100
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
├── main.rs              # Application entry, event loop, state management
├── ui/mod.rs            # Control panel UI components
├── fractal/mod.rs       # Fractal trait & 12 implementations
├── palette/mod.rs       # Color palette system (5 palettes)
├── color_pipeline.rs    # Color processor system (5 processors)
├── command.rs           # Command pattern for undo/redo
├── renderer/mod.rs      # Screen-to-fractal coordinate mapping
└── viewport.rs          # Viewport and coordinate transforms
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

## Recent Fixes

### Critical Bug Fixes (2026-02-13)
- **Fractal Computation** - Fixed hardcoded `2.0` multiplier to use actual `power` parameter in all power-based fractals
- **Burning Ship** - Moved `abs()` operations before power transformation for correct rendering
- **Smooth Coloring** - Fixed formula and optimized with `norm_sqr()` to avoid sqrt operations
- **Division by Zero Protection** - Added guards throughout viewport calculations
- **Phoenix Defaults** - Changed to c_real=0.0, c_imag=0.4, memory=0.55 with 100 iterations

## License

MIT License - See LICENSE file for details
