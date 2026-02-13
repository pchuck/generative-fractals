use eframe::egui;
use std::collections::HashMap;

mod fractal;
mod palette;
mod renderer;

use fractal::{create_fractal, Fractal, FractalType};
use palette::{get_color, PaletteType};
use renderer::{screen_to_fractal, CpuRenderer, Renderer};

#[derive(Clone, Copy, Default)]
pub struct FractalViewState {
    pub center_x: f64,
    pub center_y: f64,
    pub zoom: f64,
}

struct FractalApp {
    fractal: Box<dyn Fractal>,
    controls: FractalControls,
    views: HashMap<FractalType, FractalViewState>,
    renderer: CpuRenderer,
    drag_start: Option<egui::Pos2>,
    drag_current: Option<egui::Pos2>,
    needs_render: bool,
    cached_fractal_image: Option<egui::ColorImage>,
    cached_width: u32,
    cached_height: u32,
    prev_fractal_image: Option<egui::ColorImage>,
    render_delay: u32,
    zoom_preview: Option<ZoomPreview>,
}

struct ZoomPreview {
    sel_min: egui::Pos2,
    sel_max: egui::Pos2,
}

struct FractalControls {
    fractal_type: FractalType,
    palette_type: PaletteType,
    max_iterations: u32,
    palette_offset: f32,
    pending_max_iterations: u32,
    pending_palette_offset: f32,
    pending_fractal_params: std::collections::HashMap<String, f64>,
}

impl Default for FractalControls {
    fn default() -> Self {
        FractalControls {
            fractal_type: FractalType::Mandelbrot,
            palette_type: PaletteType::Classic,
            max_iterations: 200,
            palette_offset: 0.0,
            pending_max_iterations: 200,
            pending_palette_offset: 0.0,
            pending_fractal_params: std::collections::HashMap::new(),
        }
    }
}

impl Default for FractalApp {
    fn default() -> Self {
        let mut views = HashMap::new();
        views.insert(
            FractalType::Mandelbrot,
            FractalViewState {
                center_x: -0.5,
                center_y: 0.0,
                zoom: 1.0,
            },
        );
        views.insert(
            FractalType::Julia,
            FractalViewState {
                center_x: 0.0,
                center_y: 0.0,
                zoom: 1.0,
            },
        );

        FractalApp {
            fractal: create_fractal(FractalType::Mandelbrot),
            controls: FractalControls::default(),
            views,
            renderer: CpuRenderer::new(),
            drag_start: None,
            drag_current: None,
            needs_render: true,
            cached_fractal_image: None,
            cached_width: 0,
            cached_height: 0,
            prev_fractal_image: None,
            render_delay: 0,
            zoom_preview: None,
        }
    }
}

impl FractalApp {
    fn get_view(&self) -> FractalViewState {
        self.views
            .get(&self.controls.fractal_type)
            .copied()
            .unwrap_or_default()
    }

    fn set_view(&mut self, view: FractalViewState) {
        self.views.insert(self.controls.fractal_type, view);
    }

    fn reset_view(&mut self) {
        let default_view = match self.controls.fractal_type {
            FractalType::Mandelbrot => FractalViewState {
                center_x: -0.5,
                center_y: 0.0,
                zoom: 1.0,
            },
            FractalType::Julia => FractalViewState {
                center_x: 0.0,
                center_y: 0.0,
                zoom: 1.0,
            },
        };
        self.views.insert(self.controls.fractal_type, default_view);
    }
}

impl eframe::App for FractalApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::SidePanel::left("controls")
            .default_width(280.0)
            .show(ctx, |ui| {
                let prev_fractal = self.controls.fractal_type;
                let mut changed = false;
                self.controls.ui(ui, &mut self.fractal, &mut changed);

                if prev_fractal != self.controls.fractal_type {
                    self.fractal = create_fractal(self.controls.fractal_type);
                    self.needs_render = true;
                }

                if changed {
                    self.needs_render = true;
                }

                ui.separator();
                if ui.button("Reset View").clicked() {
                    self.reset_view();
                    self.needs_render = true;
                }

                if self.drag_start.is_some() {
                    ui.separator();
                    ui.label("Release to apply zoom");
                }

                ui.separator();
                let view = self.get_view();
                ui.label(format!(
                    "Center: ({:.6}, {:.6})",
                    view.center_x, view.center_y
                ));
                ui.label(format!("Zoom: {:.2e}", view.zoom));
                ui.label(format!("Iter: {}", self.controls.max_iterations));
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
                            screen_to_fractal(min_x as u32, max_y as u32, width, height, view);
                        let (fractal_max_x, fractal_min_y) =
                            screen_to_fractal(max_x as u32, min_y as u32, width, height, view);

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

            // Render after drawing (so preview shows first)
            if self.needs_render {
                let start_time = std::time::Instant::now();

                let view = self.get_view();
                let max_iter = self.controls.max_iterations;
                let palette_offset = self.controls.palette_offset;

                let pixels = self.renderer.render(
                    self.fractal.as_ref(),
                    &DummyPalette {
                        palette_type: self.controls.palette_type,
                    },
                    width,
                    height,
                    view,
                    max_iter,
                    palette_offset,
                );

                let render_time = start_time.elapsed();
                let pixels_total = width * height * max_iter;

                println!(
                    "RENDER: {:?} | {:?} | {}x{}x{}={} | center=({:.6},{:.6}) zoom={:.2e} | {:?}",
                    self.controls.fractal_type,
                    self.controls.palette_type,
                    width,
                    height,
                    max_iter,
                    pixels_total,
                    view.center_x,
                    view.center_y,
                    view.zoom,
                    render_time
                );

                self.cached_fractal_image = Some(egui::ColorImage {
                    size: [width as _, height as _],
                    pixels,
                });
                self.cached_width = width;
                self.cached_height = height;
                self.needs_render = false;
                self.zoom_preview = None;
                self.prev_fractal_image = None;
                ctx.request_repaint();
            }
        });
    }
}

struct DummyPalette {
    palette_type: PaletteType,
}

impl palette::Palette for DummyPalette {
    fn name(&self) -> &str {
        ""
    }

    fn color(&self, t: f32) -> egui::Color32 {
        get_color(self.palette_type, t, 0.0)
    }
}

impl FractalControls {
    fn ui(&mut self, ui: &mut egui::Ui, fractal: &mut Box<dyn Fractal>, changed: &mut bool) {
        ui.heading("Fractal Explorer");
        ui.separator();

        ui.label("Fractal Type:");
        egui::ComboBox::from_id_salt("fractal_type")
            .selected_text(match self.fractal_type {
                FractalType::Mandelbrot => "Mandelbrot",
                FractalType::Julia => "Julia",
            })
            .show_ui(ui, |ui| {
                ui.selectable_value(
                    &mut self.fractal_type,
                    FractalType::Mandelbrot,
                    "Mandelbrot",
                );
                ui.selectable_value(&mut self.fractal_type, FractalType::Julia, "Julia");
            });

        ui.separator();
        ui.label("Color Palette:");
        let prev_palette = self.palette_type;
        egui::ComboBox::from_id_salt("palette_type")
            .selected_text(match self.palette_type {
                PaletteType::Classic => "Classic",
                PaletteType::Fire => "Fire",
                PaletteType::Ice => "Ice",
                PaletteType::Grayscale => "Grayscale",
                PaletteType::Psychedelic => "Psychedelic",
            })
            .show_ui(ui, |ui| {
                ui.selectable_value(&mut self.palette_type, PaletteType::Classic, "Classic");
                ui.selectable_value(&mut self.palette_type, PaletteType::Fire, "Fire");
                ui.selectable_value(&mut self.palette_type, PaletteType::Ice, "Ice");
                ui.selectable_value(&mut self.palette_type, PaletteType::Grayscale, "Grayscale");
                ui.selectable_value(
                    &mut self.palette_type,
                    PaletteType::Psychedelic,
                    "Psychedelic",
                );
            });

        let mut palette_changed = prev_palette != self.palette_type;
        if palette_changed {
            self.pending_palette_offset = self.palette_offset;
        }
        if self.palette_type == PaletteType::Psychedelic {
            ui.label("Color Offset:");
            let response = ui
                .add(egui::Slider::new(&mut self.pending_palette_offset, 0.0..=1.0).text("offset"));
            if response.drag_stopped() {
                self.palette_offset = self.pending_palette_offset;
                palette_changed = true;
            }
        } else {
            self.pending_palette_offset = self.palette_offset;
        }

        ui.separator();
        ui.label("Iterations:");
        let response =
            ui.add(egui::Slider::new(&mut self.pending_max_iterations, 16..=2000).text("max_iter"));
        if response.drag_stopped() {
            self.max_iterations = self.pending_max_iterations;
            *changed = true;
        }

        ui.separator();
        ui.label("Fractal Parameters:");

        for param in fractal.parameters() {
            let mut value = self
                .pending_fractal_params
                .get(&param.name)
                .copied()
                .unwrap_or(param.value);
            let response =
                ui.add(egui::Slider::new(&mut value, param.min..=param.max).text(&param.name));
            self.pending_fractal_params
                .insert(param.name.clone(), value);
            if response.drag_stopped() {
                fractal.set_parameter(&param.name, value);
                *changed = true;
            }
        }

        if palette_changed {
            *changed = true;
        }

        ui.separator();
        ui.label("Controls:");
        ui.label("- Click + Drag: Select zoom region");
        ui.label("- Click: Drag to pan view");
    }
}

fn main() {
    eprintln!("STARTING Fractal Explorer...");

    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1200.0, 800.0])
            .with_title("Fractal Explorer"),
        ..Default::default()
    };

    let _ = eframe::run_native(
        "Fractal Explorer",
        options,
        Box::new(|_cc| Ok(Box::new(FractalApp::default()))),
    );
}
