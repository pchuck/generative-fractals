use crate::FractalViewState;

pub fn screen_to_fractal(
    x: u32,
    y: u32,
    width: u32,
    height: u32,
    view: &FractalViewState,
) -> (f64, f64) {
    let aspect = width as f64 / height as f64;
    let uv_x = x as f64 / width as f64;
    let uv_y = y as f64 / height as f64;
    let px = view.center_x + (uv_x - 0.5) * 4.0 * aspect / view.zoom;
    let py = view.center_y - (uv_y - 0.5) * 4.0 / view.zoom;
    (px, py)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::palette::PaletteType;
    use std::collections::HashMap;

    fn approx_eq(a: f64, b: f64, epsilon: f64) -> bool {
        (a - b).abs() < epsilon
    }

    #[test]
    fn test_screen_to_fractal_center() {
        let view = FractalViewState {
            center_x: 0.0,
            center_y: 0.0,
            zoom: 1.0,
            max_iterations: 200,
            fractal_params: HashMap::new(),
            palette_type: PaletteType::Classic,
        };
        let (px, py) = screen_to_fractal(400, 300, 800, 600, &view);
        assert!(
            approx_eq(px, 0.0, 0.001),
            "Center x should be 0, got {}",
            px
        );
        assert!(
            approx_eq(py, 0.0, 0.001),
            "Center y should be 0, got {}",
            py
        );
    }

    #[test]
    fn test_screen_to_fractal_top_left() {
        let view = FractalViewState {
            center_x: 0.0,
            center_y: 0.0,
            zoom: 1.0,
            max_iterations: 200,
            fractal_params: HashMap::new(),
            palette_type: PaletteType::Classic,
        };
        let (px, py) = screen_to_fractal(0, 0, 800, 600, &view);
        let aspect = 800.0 / 600.0;
        assert!(
            approx_eq(px, -2.0 * aspect, 0.01),
            "Top-left x should be -2*aspect"
        );
        assert!(approx_eq(py, 2.0, 0.01), "Top-left y should be 2.0");
    }

    #[test]
    fn test_screen_to_fractal_bottom_right() {
        let view = FractalViewState {
            center_x: 0.0,
            center_y: 0.0,
            zoom: 1.0,
            max_iterations: 200,
            fractal_params: HashMap::new(),
            palette_type: PaletteType::Classic,
        };
        let (px, py) = screen_to_fractal(799, 599, 800, 600, &view);
        let aspect = 800.0 / 600.0;
        assert!(
            approx_eq(px, 2.0 * aspect, 0.01),
            "Bottom-right x should be 2*aspect"
        );
        assert!(approx_eq(py, -2.0, 0.01), "Bottom-right y should be -2.0");
    }

    #[test]
    fn test_screen_to_fractal_zoom_2() {
        let view = FractalViewState {
            center_x: 0.0,
            center_y: 0.0,
            zoom: 2.0,
            max_iterations: 200,
            fractal_params: HashMap::new(),
            palette_type: PaletteType::Classic,
        };
        let (px, py) = screen_to_fractal(400, 300, 800, 600, &view);
        assert!(
            approx_eq(px, 0.0, 0.001),
            "Center x should still be 0 at zoom 2"
        );
        assert!(
            approx_eq(py, 0.0, 0.001),
            "Center y should still be 0 at zoom 2"
        );
    }

    #[test]
    fn test_screen_to_fractal_offset_center() {
        let view = FractalViewState {
            center_x: 1.0,
            center_y: 1.0,
            zoom: 1.0,
            max_iterations: 200,
            fractal_params: HashMap::new(),
            palette_type: PaletteType::Classic,
        };
        let (px, py) = screen_to_fractal(400, 300, 800, 600, &view);
        assert!(approx_eq(px, 1.0, 0.001), "Offset center x should be 1.0");
        assert!(approx_eq(py, 1.0, 0.001), "Offset center y should be 1.0");
    }

    #[test]
    fn test_fractal_roundtrip() {
        let original = FractalViewState {
            center_x: -0.5,
            center_y: 0.0,
            zoom: 1.0,
            max_iterations: 200,
            fractal_params: HashMap::new(),
            palette_type: PaletteType::Classic,
        };
        let (px, py) = screen_to_fractal(200, 300, 800, 600, &original);
        assert!(approx_eq(px, -1.833, 0.01), "x at 200 should be -1.833");
        assert!(approx_eq(py, 0.0, 0.01), "y at center should be 0.0");
    }
}
