use crate::fractal::Fractal;
use crate::palette::Palette;
use crate::FractalViewState;
use eframe::egui::Color32;

#[allow(dead_code)]
pub trait Renderer: Send + Sync {
    fn name(&self) -> &str;
    #[allow(clippy::too_many_arguments)]
    fn render(
        &self,
        fractal: &dyn Fractal,
        palette: &dyn Palette,
        width: u32,
        height: u32,
        view: FractalViewState,
        max_iter: u32,
        palette_offset: f32,
    ) -> Vec<Color32>;
}

pub struct CpuRenderer;

impl CpuRenderer {
    pub fn new() -> Self {
        CpuRenderer
    }
}

impl Default for CpuRenderer {
    fn default() -> Self {
        CpuRenderer::new()
    }
}

impl Renderer for CpuRenderer {
    fn name(&self) -> &str {
        "CPU"
    }

    fn render(
        &self,
        fractal: &dyn Fractal,
        palette: &dyn Palette,
        width: u32,
        height: u32,
        view: FractalViewState,
        max_iter: u32,
        palette_offset: f32,
    ) -> Vec<Color32> {
        let mut pixels = vec![Color32::BLACK; (width * height) as usize];

        for y in 0..height {
            for x in 0..width {
                let uv_x = x as f64 / width as f64;
                let uv_y = y as f64 / height as f64;

                let px = view.center_x + (uv_x - 0.5) * 4.0 / view.zoom;
                let py = view.center_y - (uv_y - 0.5) * 4.0 / view.zoom;

                let iterations = fractal.compute(px, py, max_iter);

                let color = if iterations >= max_iter {
                    Color32::BLACK
                } else {
                    let t = iterations as f32 / max_iter as f32;
                    let adjusted_t = (t + palette_offset) % 1.0;
                    palette.color(adjusted_t)
                };

                pixels[(y * width + x) as usize] = color;
            }
        }

        pixels
    }
}
