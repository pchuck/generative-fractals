use crate::fractal::Fractal;
use crate::palette::Palette;
use crate::FractalViewState;
use eframe::egui::Color32;
use rayon::prelude::*;

pub fn screen_to_fractal(
    x: u32,
    y: u32,
    width: u32,
    height: u32,
    view: FractalViewState,
) -> (f64, f64) {
    let aspect = width as f64 / height as f64;
    let uv_x = x as f64 / width as f64;
    let uv_y = y as f64 / height as f64;
    let px = view.center_x + (uv_x - 0.5) * 4.0 * aspect / view.zoom;
    let py = view.center_y - (uv_y - 0.5) * 4.0 / view.zoom;
    (px, py)
}

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
        progress_callback: Option<&dyn Fn(f32)>,
    ) -> Vec<Color32>;
}

#[allow(dead_code)]
pub struct CpuRenderer;

impl CpuRenderer {
    #[allow(dead_code)]
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
        progress_callback: Option<&dyn Fn(f32)>,
    ) -> Vec<Color32> {
        let mut pixels = vec![Color32::BLACK; (width * height) as usize];

        // Process in chunks for progress reporting - more chunks = smoother progress bar
        let chunk_size = ((height as f64 / 60.0).ceil() as u32).max(1);
        let total_chunks = ((height as f64 / chunk_size as f64).ceil() as u32).max(1);

        for chunk_idx in 0..total_chunks {
            let y_start = (chunk_idx * chunk_size) as usize;
            let y_end = (y_start + chunk_size as usize).min(height as usize);

            let chunk_pixels: Vec<Color32> = (y_start as u32..y_end as u32)
                .into_par_iter()
                .flat_map(|y| {
                    (0..width)
                        .map(|x| {
                            let (px, py) = screen_to_fractal(x, y, width, height, view);
                            let iterations = fractal.compute(px, py, max_iter);
                            if iterations >= max_iter {
                                Color32::BLACK
                            } else {
                                let t = iterations as f32 / max_iter as f32;
                                let adjusted_t = (t + palette_offset) % 1.0;
                                palette.color(adjusted_t)
                            }
                        })
                        .collect::<Vec<_>>()
                })
                .collect();

            // Copy chunk to main buffer
            for (i, color) in chunk_pixels.iter().enumerate() {
                let y = y_start + i / width as usize;
                let x = i % width as usize;
                pixels[y * width as usize + x] = *color;
            }

            if let Some(callback) = progress_callback {
                callback((chunk_idx + 1) as f32 / total_chunks as f32);
            }
        }

        pixels
    }
}
