# Agent Guidelines - Rust Fractal Explorer

## Project Overview

GPU-accelerated interactive fractal explorer built with Rust, WGPU, and Egui. Supports multiple fractal types (Mandelbrot, Julia) with extensible color palettes.

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

1. **Imports**: Absolute paths for external crates (`use wgpu::Device`), relative for internal (`use crate::fractal::Fractal`)
2. **Formatting**: Follow rustfmt defaults (4 spaces, 100 char line length)
3. **Naming**: PascalCase types (`FractalRenderer`), snake_case functions (`compute_iteration`), UPPER_SNAKE constants
4. **Types**: Explicit in public APIs; use `i32`/`f32`/`f64`, `u32` for counts, `Vec<T>` for dynamic arrays

### Error Handling

- Use `Result<T, E>` for fallible operations
- Prefer `anyhow` for app-level, `thiserror` for library errors
- Never panic in library code; return errors instead

```rust
pub fn create_renderer(device: &Device) -> Result<Renderer, RendererError> { ... }
```

### Documentation

- Document public APIs with doc comments (`///`)
- Include examples where helpful

### WGPU Patterns

- Store WGPU objects in application state
- Use `Arc<wgpu::Device>` for shared access
- Use compute shaders for fractal computation
- Pass uniforms via uniform buffers, update textures only when params change

## Module Structure

```
src/
├── main.rs           # Entry point, event loop
├── app.rs            # Application state
├── fractal/          # Fractal trait & implementations
│   ├── mod.rs        # Fractal trait
│   ├── mandelbrot.rs
│   ├── julia.rs
│   └── types.rs
├── palette/          # Color palette system
│   ├── mod.rs        # Palette trait
│   └── builtins.rs
├── renderer/         # WGPU rendering
│   ├── mod.rs
│   └── compute.rs
└── ui/              # Egui panels
    └── mod.rs
```

## Trait-Based Design

**Fractal Trait:**
```rust
pub trait Fractal: Send + Sync {
    fn name(&self) -> &str;
    fn parameters(&self) -> Vec<Parameter>;
    fn set_parameter(&mut self, name: &str, value: f64);
    fn wgsl_code(&self) -> &str;
}
```

**Palette Trait:**
```rust
pub trait Palette: Send + Sync {
    fn name(&self) -> &str;
    fn generate_wgsl(&self, num_colors: usize) -> String;
}
```

## Adding New Fractals

1. Create `src/fractal/new_fractal.rs`
2. Implement the `Fractal` trait
3. Add export to `src/fractal/mod.rs`
4. Register in application state

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_mandelbrot_center() {
        let result = compute_mandelbrot(Complex::new(-0.5, 0.0), 100);
        assert_eq!(result, 100);
    }
}
```

## Git Workflow

- Commit format: `type: description` (e.g., `feat: add Julia set`)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`
- Run `cargo fmt` and `cargo clippy` before committing

## Common Tasks

- **Add UI parameter**: Add field → implement getter/setter → add Egui slider → pass to shader
- **Modify shader**: Edit WGSL → rebuild → ensure uniform buffer matches
- **Performance**: Reduce iterations during exploration, use lower resolution during pan/zoom

---

**Last updated**: 2026-02-12
