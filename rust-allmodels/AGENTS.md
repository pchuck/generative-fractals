# Agent Guidelines - Rust Fractal Explorer

## Project Overview

Interactive fractal explorer built with Rust, eframe/egui, and Rayon for parallel CPU rendering. Supports 10 fractal types (Mandelbrot, Julia, Burning Ship, Tricorn, Celtic, Newton, Biomorph, Phoenix, Multibrot, Spider) with 5 color palettes, per-fractal state persistence, bookmarks, and undo/redo history.

## Build and Run Commands

```bash
# Build and run
make build && make run
cargo build --release && cargo run --release

# Debug mode with logging
RUST_LOG=debug cargo run

# Run tests
cargo test
make test

# Run single test
cargo test test_name -- --nocapture
cargo test fractal::tests::test_mandelbrot_center -- --nocapture

# Tests with output
cargo test -- --show-output

# Format and lint
cargo fmt
cargo clippy -- -D warnings

# Using Makefile
make fmt          # Format code
make lint         # Run clippy
make test-show    # Run tests with output
make clean        # Clean build artifacts
make deps         # Update dependencies
```

## Code Style

### Rust Conventions

1. **Imports**: Absolute paths for external crates (`use image::ImageBuffer`), relative for internal (`use crate::fractal::Fractal`)
2. **Formatting**: Follow rustfmt defaults (4 spaces, 100 char line length)
3. **Naming**: PascalCase types (`FractalRenderer`), snake_case functions (`compute_iteration`), UPPER_SNAKE constants
4. **Types**: Explicit in public APIs; use `i32`/`f32`/`f64`, `u32` for counts, `Vec<T>` for dynamic arrays, `HashMap` for parameters

### Error Handling

- Use `Result<T, E>` for fallible operations
- Prefer `anyhow` for app-level, `thiserror` for library errors
- Never panic in library code; return errors instead

```rust
pub fn save_config(&self) -> Result<(), String> {
    let path = Self::config_path().ok_or("Could not determine config directory")?;
    std::fs::write(&path, json).map_err(|e| format!("Failed to write: {}", e))?;
    Ok(())
}
```

### Documentation

- Document public APIs with doc comments (`///`)
- Include examples where helpful
- Document what `compute()` returns (0 to max_iter, where max_iter means inside set)

## Module Structure

```
src/
├── main.rs           # Entry point, event loop, FractalApp state
├── ui/mod.rs         # Control panel, fractal/palette dropdowns
├── fractal/mod.rs    # Fractal trait + 10 implementations
├── palette/mod.rs    # Color palette system (5 palettes)
└── renderer/mod.rs   # Screen-to-fractal coordinate mapping
```

## Core Data Structures

**FractalViewState:**
```rust
pub struct FractalViewState {
    pub center_x: f64,
    pub center_y: f64,
    pub zoom: f64,
    pub max_iterations: u32,
    pub fractal_params: HashMap<String, f64>,
    pub palette_type: PaletteType,
}
```

**Fractal Trait:**
```rust
pub trait Fractal: Send + Sync {
    fn name(&self) -> &str;
    fn parameters(&self) -> Vec<Parameter>;
    fn set_parameter(&mut self, name: &str, value: f64);
    fn get_parameter(&self, name: &str) -> Option<f64>;
    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32;
}
```

**Palette Trait:**
```rust
pub trait Palette: Send + Sync {
    fn name(&self) -> &str;
    fn color(&self, t: f32) -> Color32;
}
```

## Adding New Fractals

1. Add variant to `FractalType` enum in `src/fractal/mod.rs`
2. Implement the `Fractal` trait with `compute()` method in `src/fractal/mod.rs`
3. Add case in `create_fractal()` function
4. Add `default_center()` entry for the fractal type
5. Add default view entry in `FractalApp::default()`

## Per-Fractal State

Each fractal type maintains its own state in `views: HashMap<FractalType, FractalViewState>`:
- View position (center_x, center_y, zoom)
- Iteration count (max_iterations)
- Fractal-specific parameters (e.g., power, c_real, c_imag, memory)
- Selected palette

When switching fractals, the app automatically restores the previous state for that fractal type.

## Image Export

- Save button exports to `images/{fractal}_{palette}_{width}x{height}.png`
- Supports 1x, 2x, and 4x resolution exports
- Option for supersampling (2x internal render with box filter)

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_mandelbrot_center() {
        let m = Mandelbrot::default();
        let result = m.compute(-0.5, 0.0, 100);
        assert!(result >= 100, "Center should not escape");
    }
}
```

## Git Workflow

- Commit format: `type: description` (e.g., `feat: add Phoenix fractal`)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`
- Run `cargo fmt` and `cargo clippy` before committing

## Common Tasks

- **Add UI parameter**: Add to fractal's `parameters()` → saved in `FractalViewState.fractal_params` → restored on switch
- **Modify fractal computation**: Edit `compute()` method in fractal implementation
- **Performance**: Use Rayon parallel iterators (`par_iter()`), chunked rendering for progress updates
- **Bookmarks**: Saved in AppConfig and persist to `~/.config/fractal-explorer/config.json`

---

**Last updated**: 2026-02-13
