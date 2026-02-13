use eframe::egui;
use image::{ImageBuffer, Rgb};
use rayon::prelude::*;
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::Instant;

mod fractal;
mod palette;
mod renderer;
mod ui;

use fractal::{create_fractal, Fractal, FractalType};
use palette::PaletteType;
use renderer::screen_to_fractal;
use ui::FractalControls;

#[derive(Clone, Default)]
pub struct FractalViewState {
    pub center_x: f64,
    pub center_y: f64,
    pub zoom: f64,
    pub max_iterations: u32,
    pub fractal_params: HashMap<String, f64>,
    pub palette_type: PaletteType,
}

struct FractalApp {
    fractal: Box<dyn Fractal>,
    controls: FractalControls,
    views: HashMap<FractalType, FractalViewState>,
    drag_start: Option<egui::Pos2>,
    drag_current: Option<egui::Pos2>,
    needs_render: bool,
    cached_fractal_image: Option<egui::ColorImage>,
    cached_width: u32,
    cached_height: u32,
    prev_fractal_image: Option<egui::ColorImage>,
    render_delay: u32,
    zoom_preview: Option<ZoomPreview>,
    render_progress: f32,
    is_rendering: bool,
    status_message: Option<(String, Instant)>, // (message, timestamp)
    // Incremental rendering state
    render_target_width: u32,
    render_target_height: u32,
    render_target_view: FractalViewState,
    render_target_max_iter: u32,
    render_target_palette_offset: f32,
    render_target_palette_type: PaletteType,
    render_chunk_start: u32,
    render_pixels: Option<Vec<egui::Color32>>,
}

struct ZoomPreview {
    sel_min: egui::Pos2,
    sel_max: egui::Pos2,
}

impl Default for FractalApp {
    fn default() -> Self {
        let mut views = HashMap::new();
        for ft in [
            FractalType::Mandelbrot,
            FractalType::Julia,
            FractalType::BurningShip,
            FractalType::Tricorn,
            FractalType::Celtic,
            FractalType::Newton,
            FractalType::Biomorph,
        ] {
            let (cx, cy) = ft.default_center();
            views.insert(
                ft,
                FractalViewState {
                    center_x: cx,
                    center_y: cy,
                    zoom: 1.0,
                    max_iterations: 200,
                    fractal_params: HashMap::new(),
                    palette_type: PaletteType::Classic,
                },
            );
        }

        FractalApp {
            fractal: create_fractal(FractalType::Mandelbrot),
            controls: FractalControls::default(),
            views,
            drag_start: None,
            drag_current: None,
            needs_render: true,
            cached_fractal_image: None,
            cached_width: 0,
            cached_height: 0,
            prev_fractal_image: None,
            render_delay: 0,
            zoom_preview: None,
            render_progress: 0.0,
            is_rendering: false,
            status_message: None,
            render_target_width: 0,
            render_target_height: 0,
            render_target_view: FractalViewState {
                center_x: 0.0,
                center_y: 0.0,
                zoom: 1.0,
                max_iterations: 200,
                fractal_params: HashMap::new(),
                palette_type: PaletteType::Classic,
            },
            render_target_max_iter: 200,
            render_target_palette_offset: 0.0,
            render_target_palette_type: PaletteType::Classic,
            render_chunk_start: 0,
            render_pixels: None,
        }
    }
}

impl FractalApp {
    fn get_view(&self) -> FractalViewState {
        self.views
            .get(&self.controls.fractal_type)
            .cloned()
            .unwrap_or_default()
    }

    fn set_view(&mut self, view: FractalViewState) {
        self.views.insert(self.controls.fractal_type, view);
    }

    fn save_image(&self) -> Result<PathBuf, String> {
        let image = self
            .cached_fractal_image
            .as_ref()
            .ok_or("No image to save - wait for render to complete")?;

        let fractal_name = match self.controls.fractal_type {
            FractalType::Mandelbrot => "mandelbrot",
            FractalType::Julia => "julia",
            FractalType::BurningShip => "burning_ship",
            FractalType::Tricorn => "tricorn",
            FractalType::Celtic => "celtic",
            FractalType::Newton => "newton",
            FractalType::Biomorph => "biomorph",
        };
        let palette_name = match self.controls.palette_type {
            PaletteType::Classic => "classic",
            PaletteType::Fire => "fire",
            PaletteType::Ice => "ice",
            PaletteType::Grayscale => "grayscale",
            PaletteType::Psychedelic => "psychedelic",
        };
        let width = image.width() as u32;
        let height = image.height() as u32;
        let mut img: ImageBuffer<Rgb<u8>, Vec<u8>> = ImageBuffer::new(width, height);
        for (i, color) in image.pixels.iter().enumerate() {
            let x = (i % width as usize) as u32;
            let y = (i / width as usize) as u32;
            img.put_pixel(x, y, Rgb([color.r(), color.g(), color.b()]));
        }
        let filename = format!(
            "images/{}_{}_{}x{}.png",
            fractal_name, palette_name, width, height
        );
        std::fs::create_dir_all("images")
            .map_err(|e| format!("Failed to create images directory: {}", e))?;
        let path = PathBuf::from(&filename);
        img.save(&path)
            .map_err(|e| format!("Failed to save image: {}", e))?;
        Ok(path)
    }

    fn reset_view(&mut self) {
        let (center_x, center_y) = self.controls.fractal_type.default_center();
        let current_max_iter = self.controls.max_iterations;
        let current_palette = self.controls.palette_type;
        let current_params = self
            .views
            .get(&self.controls.fractal_type)
            .map(|v| v.fractal_params.clone())
            .unwrap_or_default();
        let default_view = FractalViewState {
            center_x,
            center_y,
            zoom: 1.0,
            max_iterations: current_max_iter,
            fractal_params: current_params,
            palette_type: current_palette,
        };
        self.views.insert(self.controls.fractal_type, default_view);
    }

    fn zoom_view(&mut self, factor: f64) {
        let mut view = self.get_view();
        view.zoom *= factor;
        self.set_view(view);
        self.needs_render = true;
    }

    fn pan_view(&mut self, dx: f64, dy: f64) {
        let mut view = self.get_view();
        // Pan amount depends on current zoom level
        let pan_amount = 0.5 / view.zoom;
        view.center_x += dx * pan_amount;
        view.center_y += dy * pan_amount;
        self.set_view(view);
        self.needs_render = true;
    }

    fn set_status(&mut self, message: String) {
        self.status_message = Some((message, Instant::now()));
    }

    fn check_status_timeout(&mut self) {
        if let Some((_, timestamp)) = self.status_message {
            if timestamp.elapsed().as_secs_f64() > 3.0 {
                self.status_message = None;
            }
        }
    }
}

impl eframe::App for FractalApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.check_status_timeout();

        // Handle keyboard input
        ctx.input(|i| {
            // Zoom controls: +/- keys
            if i.key_pressed(egui::Key::Plus) || i.key_pressed(egui::Key::Equals) {
                self.zoom_view(1.5);
            }
            if i.key_pressed(egui::Key::Minus) {
                self.zoom_view(1.0 / 1.5);
            }

            // Pan controls: arrow keys
            if i.key_pressed(egui::Key::ArrowLeft) {
                self.pan_view(-1.0, 0.0);
            }
            if i.key_pressed(egui::Key::ArrowRight) {
                self.pan_view(1.0, 0.0);
            }
            if i.key_pressed(egui::Key::ArrowUp) {
                self.pan_view(0.0, 1.0);
            }
            if i.key_pressed(egui::Key::ArrowDown) {
                self.pan_view(0.0, -1.0);
            }

            // Reset view: R key
            if i.key_pressed(egui::Key::R) {
                self.reset_view();
                self.needs_render = true;
            }

            // Save: S key
            if i.key_pressed(egui::Key::S) {
                match self.save_image() {
                    Ok(path) => {
                        self.set_status(format!("Saved: {}", path.display()));
                    }
                    Err(e) => {
                        self.set_status(format!("Error: {}", e));
                    }
                }
            }
        });

        egui::SidePanel::left("controls")
            .default_width(280.0)
            .show(ctx, |ui| {
                let prev_fractal = self.controls.fractal_type;
                let mut changed = false;
                self.controls.ui(ui, &mut self.fractal, &mut changed);

                if prev_fractal != self.controls.fractal_type {
                    self.fractal = create_fractal(self.controls.fractal_type);
                    if let Some(view) = self.views.get(&self.controls.fractal_type) {
                        self.controls.max_iterations = view.max_iterations;
                        self.controls.pending_max_iterations = view.max_iterations;
                        self.controls.pending_fractal_params = view.fractal_params.clone();
                        self.controls.palette_type = view.palette_type;
                        self.controls.pending_palette_offset = self.controls.palette_offset;
                        for (name, value) in &view.fractal_params {
                            self.fractal.set_parameter(name, *value);
                        }
                    }
                    self.needs_render = true;
                }

                if changed {
                    if let Some(view) = self.views.get_mut(&self.controls.fractal_type) {
                        view.max_iterations = self.controls.max_iterations;
                        view.fractal_params = self.controls.pending_fractal_params.clone();
                        view.palette_type = self.controls.palette_type;
                    }
                    self.needs_render = true;
                }

                ui.separator();
                ui.horizontal(|ui| {
                    if ui.button("Reset View (R)").clicked() {
                        self.reset_view();
                        self.needs_render = true;
                    }
                    if ui.button("Save (S)").clicked() {
                        match self.save_image() {
                            Ok(path) => {
                                self.set_status(format!("Saved: {}", path.display()));
                            }
                            Err(e) => {
                                self.set_status(format!("Error: {}", e));
                            }
                        }
                    }
                });

                if self.drag_start.is_some() {
                    ui.separator();
                    ui.label("Release to apply zoom");
                }

                // Show status message if present
                if let Some((msg, _)) = &self.status_message {
                    ui.separator();
                    ui.label(egui::RichText::new(msg).color(egui::Color32::YELLOW));
                }

                ui.separator();
                let view = self.get_view();
                ui.label(format!(
                    "Center: ({:.6}, {:.6})",
                    view.center_x, view.center_y
                ));
                ui.label(format!("Zoom: {:.2e}", view.zoom));
                ui.label(format!("Iter: {}", self.controls.max_iterations));

                if self.is_rendering || self.needs_render {
                    ui.separator();
                    ui.label("Rendering...");
                    ui.add(egui::ProgressBar::new(self.render_progress).desired_width(200.0));
                }

                ui.separator();
                ui.label("Keyboard:");
                ui.label("+/- : Zoom in/out");
                ui.label("Arrows : Pan");
                ui.label("R : Reset view");
                ui.label("S : Save image");
            });

        egui::CentralPanel::default().show(ctx, |ui| {
            let rect = ui.max_rect();
            let width = rect.width() as u32;
            let height = rect.height() as u32;

            if width == 0 || height == 0 {
                return;
            }

            let response =
                ui.interact(rect, egui::Id::new("canvas"), egui::Sense::click_and_drag());

            let mut pointer_pos = None;
            ctx.input(|i| {
                pointer_pos = i.pointer.interact_pos();
            });

            if response.drag_started() {
                self.drag_start = pointer_pos;
                self.drag_current = pointer_pos;
                self.zoom_preview = None;
            }

            if response.dragged() {
                if let Some(pos) = pointer_pos {
                    self.drag_current = Some(pos);
                }
                ctx.request_repaint();
            }

            if response.drag_stopped() {
                if let (Some(start), Some(end)) = (self.drag_start, self.drag_current) {
                    let dx = (end.x - start.x).abs();
                    let dy = (end.y - start.y).abs();

                    if dx > 10.0 || dy > 10.0 {
                        let min_x = start.x.min(end.x) - rect.min.x;
                        let max_x = start.x.max(end.x) - rect.min.x;
                        let min_y = start.y.min(end.y) - rect.min.y;
                        let max_y = start.y.max(end.y) - rect.min.y;

                        self.prev_fractal_image = self.cached_fractal_image.clone();

                        self.zoom_preview = Some(ZoomPreview {
                            sel_min: egui::pos2(min_x, min_y),
                            sel_max: egui::pos2(max_x, max_y),
                        });

                        // Use the mapping functions for zoom calculation
                        let view = self.get_view();

                        // Get fractal coordinates of selection corners
                        let (fractal_min_x, fractal_max_y) =
                            screen_to_fractal(min_x as u32, max_y as u32, width, height, &view);
                        let (fractal_max_x, fractal_min_y) =
                            screen_to_fractal(max_x as u32, min_y as u32, width, height, &view);

                        // Center of selection in fractal coordinates
                        let new_center_x = (fractal_min_x + fractal_max_x) / 2.0;
                        let new_center_y = (fractal_min_y + fractal_max_y) / 2.0;

                        // Zoom = old_zoom * (old_height / new_height)
                        let sel_height_px = max_y - min_y;
                        let new_zoom = view.zoom * (height as f64 / sel_height_px as f64);

                        self.set_view(FractalViewState {
                            center_x: new_center_x,
                            center_y: new_center_y,
                            zoom: new_zoom,
                            max_iterations: self.controls.max_iterations,
                            fractal_params: view.fractal_params.clone(),
                            palette_type: self.controls.palette_type,
                        });
                        self.render_delay = 2;
                    }
                }

                self.drag_start = None;
                self.drag_current = None;
                ctx.request_repaint();
            }

            // Initial render check
            if self.cached_width == 0 || self.cached_height == 0 {
                self.needs_render = true;
            } else if self.render_delay > 0 {
                self.render_delay -= 1;
                if self.render_delay == 0 {
                    self.needs_render = true;
                }
            }

            if let Some(ref image) = self.cached_fractal_image {
                let texture =
                    ctx.load_texture("fractal", image.clone(), egui::TextureOptions::default());
                ui.put(
                    egui::Rect::from_min_size(rect.min, rect.size()),
                    egui::Image::new((texture.id(), rect.size())).uv(egui::Rect::from_min_max(
                        egui::pos2(0.0, 0.0),
                        egui::pos2(1.0, 1.0),
                    )),
                );
            }

            let painter = ui.painter();

            // Draw zoom preview if available (blocky preview - stretch selected region to fill canvas)
            if let Some(ref preview) = self.zoom_preview {
                if let Some(ref image) = self.prev_fractal_image {
                    let texture = ctx.load_texture(
                        "fractal_preview",
                        image.clone(),
                        egui::TextureOptions::default(),
                    );
                    let uv_min = egui::pos2(
                        (preview.sel_min.x / rect.width()).clamp(0.0, 1.0),
                        (preview.sel_min.y / rect.height()).clamp(0.0, 1.0),
                    );
                    let uv_max = egui::pos2(
                        (preview.sel_max.x / rect.width()).clamp(0.0, 1.0),
                        (preview.sel_max.y / rect.height()).clamp(0.0, 1.0),
                    );
                    painter.image(
                        texture.id(),
                        rect,
                        egui::Rect::from_min_max(uv_min, uv_max),
                        egui::Color32::WHITE,
                    );
                }
            }

            // Draw selection rectangle outline (when no preview)
            if self.zoom_preview.is_none() {
                if let (Some(start), Some(end)) = (self.drag_start, self.drag_current) {
                    let sel_rect = egui::Rect::from_two_pos(start, end);
                    painter.rect_stroke(sel_rect, 1.0, egui::Stroke::new(2.0, egui::Color32::BLUE));
                }
            }

            // Incremental rendering - one chunk per frame
            if self.is_rendering {
                let width = self.render_target_width;
                let height = self.render_target_height;

                // Process one chunk
                let chunk_size = ((height as f64 / 60.0).ceil() as u32).max(1);
                let y_start = self.render_chunk_start;
                let y_end = (y_start + chunk_size).min(height);

                if y_start < height {
                    // Render this chunk
                    let chunk_pixels: Vec<egui::Color32> = (y_start..y_end)
                        .into_par_iter()
                        .flat_map(|y| {
                            (0..width)
                                .map(|x| {
                                    let (px, py) = screen_to_fractal(
                                        x,
                                        y,
                                        width,
                                        height,
                                        &self.render_target_view,
                                    );
                                    let iterations =
                                        self.fractal.compute(px, py, self.render_target_max_iter);
                                    if iterations >= self.render_target_max_iter {
                                        egui::Color32::BLACK
                                    } else {
                                        let t =
                                            iterations as f32 / self.render_target_max_iter as f32;
                                        palette::get_color(
                                            self.render_target_palette_type,
                                            t,
                                            self.render_target_palette_offset,
                                        )
                                    }
                                })
                                .collect::<Vec<_>>()
                        })
                        .collect();

                    // Copy to pixel buffer
                    if let Some(ref mut pixels) = self.render_pixels {
                        let start_idx = y_start as usize * width as usize;
                        let chunk_len = (y_end - y_start) as usize * width as usize;
                        pixels[start_idx..start_idx + chunk_len].copy_from_slice(&chunk_pixels);
                    }

                    self.render_chunk_start = y_end;
                    self.render_progress = self.render_chunk_start as f32 / height as f32;
                    ctx.request_repaint();
                } else {
                    // Render complete
                    if let Some(pixels) = self.render_pixels.take() {
                        self.cached_fractal_image = Some(egui::ColorImage {
                            size: [width as _, height as _],
                            pixels,
                        });
                    }
                    self.cached_width = width;
                    self.cached_height = height;
                    self.needs_render = false;
                    self.is_rendering = false;
                    self.render_progress = 0.0;
                    self.zoom_preview = None;
                    self.render_chunk_start = 0;
                    ctx.request_repaint();
                }
            }

            // Start new render if needed
            if self.needs_render && !self.is_rendering {
                // Initialize incremental render state
                self.render_target_width = width;
                self.render_target_height = height;
                self.render_target_view = self.get_view();
                self.render_target_max_iter = self.controls.max_iterations;
                self.render_target_palette_offset = self.controls.palette_offset;
                self.render_target_palette_type = self.controls.palette_type;
                self.render_chunk_start = 0;
                self.render_pixels = Some(vec![egui::Color32::BLACK; (width * height) as usize]);
                self.is_rendering = true;
                self.render_progress = 0.0;
                ctx.request_repaint();
            }
        });
    }
}

fn main() -> eframe::Result {
    eprintln!("STARTING Fractal Explorer...");

    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1200.0, 800.0])
            .with_title("Fractal Explorer"),
        ..Default::default()
    };

    eframe::run_native(
        "Fractal Explorer",
        options,
        Box::new(|_cc| Ok(Box::new(FractalApp::default()))),
    )
}
