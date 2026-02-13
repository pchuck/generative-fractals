# Agent Guidelines - Rust Fractal Explorer

## Project Overview

Interactive fractal explorer built with Rust, eframe/egui, and Rayon for parallel CPU rendering. Supports multiple fractal types (Mandelbrot, Julia, Burning Ship) with extensible color palettes and per-fractal state persistence.

## Build and Run Commands

```bash
# Build and run
cargo build --release && cargo run --release

# Debug mode with logging
RUST_LOG=debug cargo run

# Run single test
cargo test test_name -- --nocapture

# Tests with output
cargo test -- --show-output

# Format and lint
cargo fmt
cargo clippy -- -D warnings
```

## Code Style

### Rust Conventions

1. **Imports**: Absolute paths for external crates (`use image::ImageBuffer`), relative for internal (`use crate::fractal::Fractal`)
2. **Formatting**: Follow rustfmt defaults (4 spaces, 100 char line length)
3. **Naming**: PascalCase types (`FractalRenderer`), snake_case functions (`compute_iteration`), UPPER_SNAKE constants
4. **Types**: Explicit in public APIs; use `i32`/`f32`/`f64`, `u32` for counts, `Vec<T>` for dynamic arrays

### Error Handling

- Use `Result<T, E>` for fallible operations
- Prefer `anyhow` for app-level, `thiserror` for library errors
- Never panic in library code; return errors instead

```rust
pub fn create_renderer() -> Result<Renderer, RendererError> { ... }
```

### Documentation

- Document public APIs with doc comments (`///`)
- Include examples where helpful

## Module Structure

```
src/
├── main.rs           # Entry point, event loop, application state
├── fractal/          # Fractal trait & implementations
│   ├── mod.rs        # Fractal trait, Mandelbrot, Julia, BurningShip
├── palette/          # Color palette system
│   ├── mod.rs        # Palette trait and implementations
└── renderer/         # CPU rendering with Rayon
    └── mod.rs        # Parallel rendering, coordinate mapping
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

1. Create `src/fractal/new_fractal.rs`
2. Implement the `Fractal` trait with `compute()` method
3. Add variant to `FractalType` enum in `src/fractal/mod.rs`
4. Add case in `create_fractal()` function
5. Add default view entry in `FractalApp::default()`

## Per-Fractal State

Each fractal type maintains its own state in `views: HashMap<FractalType, FractalViewState>`:
- View position (center_x, center_y, zoom)
- Iteration count (max_iterations)
- Fractal-specific parameters (e.g., power, c_real, c_imag)

When switching fractals, the app automatically restores the previous state for that fractal type.

## Image Export

The Save button exports the current fractal to `images/{fractal}_{palette}_{width}x{height}.png`.

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

- Commit format: `type: description` (e.g., `feat: add Julia set`)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`
- Run `cargo fmt` and `cargo clippy` before committing

## Common Tasks

- **Add UI parameter**: Add to fractal's `parameters()` → saved in `FractalViewState.fractal_params` → restored on switch
- **Modify fractal computation**: Edit `compute()` method in fractal implementation
- **Performance**: Use Rayon parallel iterators, chunked rendering for progress updates

---

**Last updated**: 2026-02-13
