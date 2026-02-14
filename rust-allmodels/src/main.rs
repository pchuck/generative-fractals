use eframe::egui;
use image::{ImageBuffer, Rgb};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::Instant;

mod fractal;
mod palette;
mod renderer;
mod ui;

use fractal::{create_fractal, Fractal, FractalType};
use palette::PaletteType;
use renderer::{screen_to_fractal, RenderConfig, RenderEngine, RenderRegion};
use ui::FractalControls;

/// Application configuration for persistence
#[derive(Serialize, Deserialize, Clone)]
struct AppConfig {
    window_width: f32,
    window_height: f32,
    default_iterations: u32,
    default_fractal: FractalType,
    default_palette: PaletteType,
    supersampling_enabled: bool,
    adaptive_iterations: bool,
    bookmarks: Vec<Bookmark>,
}

impl Default for AppConfig {
    fn default() -> Self {
        AppConfig {
            window_width: 1200.0,
            window_height: 800.0,
            default_iterations: 200,
            default_fractal: FractalType::Mandelbrot,
            default_palette: PaletteType::Classic,
            supersampling_enabled: false,
            adaptive_iterations: false,
            bookmarks: Vec::new(),
        }
    }
}

impl AppConfig {
    fn config_path() -> Option<PathBuf> {
        dirs::config_dir().map(|dir| dir.join("fractal-explorer").join("config.json"))
    }

    fn load() -> Self {
        if let Some(path) = Self::config_path() {
            if let Ok(contents) = std::fs::read_to_string(&path) {
                if let Ok(config) = serde_json::from_str(&contents) {
                    return config;
                }
            }
        }
        Self::default()
    }

    fn save(&self) -> Result<(), String> {
        let path = Self::config_path().ok_or("Could not determine config directory")?;
        std::fs::create_dir_all(path.parent().unwrap())
            .map_err(|e| format!("Failed to create config directory: {}", e))?;
        let json = serde_json::to_string_pretty(self)
            .map_err(|e| format!("Failed to serialize config: {}", e))?;
        std::fs::write(&path, json).map_err(|e| format!("Failed to write config: {}", e))?;
        Ok(())
    }
}

/// Bookmark for saving interesting locations
#[derive(Serialize, Deserialize, Clone, Debug)]
struct Bookmark {
    name: String,
    fractal_type: FractalType,
    center_x: f64,
    center_y: f64,
    zoom: f64,
    max_iterations: u32,
    palette_type: PaletteType,
}

#[derive(Clone, Default)]
pub struct FractalViewState {
    pub center_x: f64,
    pub center_y: f64,
    pub zoom: f64,
    pub max_iterations: u32,
    pub fractal_params: HashMap<String, f64>,
    pub palette_type: PaletteType,
}

/// View history entry for undo/redo
#[derive(Clone)]
struct ViewHistoryEntry {
    fractal_type: FractalType,
    view: FractalViewState,
}

/// Manages undo/redo history
struct ViewHistory {
    entries: Vec<ViewHistoryEntry>,
    current_index: usize,
    max_size: usize,
}

impl ViewHistory {
    fn new(max_size: usize) -> Self {
        ViewHistory {
            entries: Vec::new(),
            current_index: 0,
            max_size,
        }
    }

    fn push(&mut self, fractal_type: FractalType, view: FractalViewState) {
        // Remove any entries after current index (redo history)
        if self.current_index < self.entries.len() {
            self.entries.truncate(self.current_index);
        }

        // Add new entry
        self.entries.push(ViewHistoryEntry { fractal_type, view });

        // Limit history size
        if self.entries.len() > self.max_size {
            self.entries.remove(0);
        } else {
            self.current_index += 1;
        }
    }

    fn can_undo(&self) -> bool {
        self.current_index > 1
    }

    fn can_redo(&self) -> bool {
        self.current_index < self.entries.len()
    }

    fn undo(&mut self) -> Option<(FractalType, FractalViewState)> {
        if self.can_undo() {
            self.current_index -= 1;
            let entry = &self.entries[self.current_index - 1];
            Some((entry.fractal_type, entry.view.clone()))
        } else {
            None
        }
    }

    fn redo(&mut self) -> Option<(FractalType, FractalViewState)> {
        if self.can_redo() {
            self.current_index += 1;
            let entry = &self.entries[self.current_index - 1];
            Some((entry.fractal_type, entry.view.clone()))
        } else {
            None
        }
    }

    #[allow(dead_code)]
    fn current(&self) -> Option<(FractalType, FractalViewState)> {
        if self.current_index > 0 && self.current_index <= self.entries.len() {
            let entry = &self.entries[self.current_index - 1];
            Some((entry.fractal_type, entry.view.clone()))
        } else {
            None
        }
    }
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
    render_start_time: Option<Instant>,
    last_render_time: Option<f64>, // in seconds
    status_message: Option<(String, Instant)>,
    mouse_fractal_pos: Option<(f64, f64)>,
    view_history: ViewHistory,
    last_saved_view: Option<(FractalType, FractalViewState)>,
    supersampling_enabled: bool,
    adaptive_iterations: bool,
    bookmarks: Vec<Bookmark>,
    show_bookmark_dialog: bool,
    bookmark_name_input: String,
    minimap_enabled: bool,
    // Rendering engine
    render_engine: RenderEngine,
    // Current render configuration
    render_config: Option<RenderConfig>,
    // Partial render regions for pan optimization
    partial_render_regions: Vec<RenderRegion>,
    current_region_index: usize,
    render_chunk_start: u32,
}

struct ZoomPreview {
    sel_min: egui::Pos2,
    sel_max: egui::Pos2,
}

impl FractalApp {
    fn new(config: &AppConfig) -> Self {
        let mut views = HashMap::new();
        for ft in [
            FractalType::Mandelbrot,
            FractalType::Julia,
            FractalType::BurningShip,
            FractalType::Tricorn,
            FractalType::Celtic,
            FractalType::Newton,
            FractalType::Biomorph,
            FractalType::Phoenix,
            FractalType::Multibrot,
            FractalType::Spider,
            FractalType::OrbitTrap,
            FractalType::PickoverStalk,
        ] {
            let (cx, cy) = ft.default_center();
            views.insert(
                ft,
                FractalViewState {
                    center_x: cx,
                    center_y: cy,
                    zoom: 1.0,
                    max_iterations: config.default_iterations,
                    fractal_params: HashMap::new(),
                    palette_type: config.default_palette,
                },
            );
        }

        let controls = FractalControls {
            fractal_type: config.default_fractal,
            max_iterations: config.default_iterations,
            pending_max_iterations: config.default_iterations,
            palette_type: config.default_palette,
            ..Default::default()
        };

        let mut app = FractalApp {
            fractal: create_fractal(config.default_fractal),
            controls,
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
            render_start_time: None,
            last_render_time: None,
            status_message: None,
            mouse_fractal_pos: None,
            view_history: ViewHistory::new(50),
            last_saved_view: None,
            supersampling_enabled: config.supersampling_enabled,
            adaptive_iterations: config.adaptive_iterations,
            bookmarks: config.bookmarks.clone(),
            show_bookmark_dialog: false,
            bookmark_name_input: String::new(),
            minimap_enabled: false,
            render_engine: RenderEngine::default(),
            render_config: None,
            partial_render_regions: Vec::new(),
            current_region_index: 0,
            render_chunk_start: 0,
        };

        // Push initial view to history
        let initial_view = app.get_view();
        app.view_history.push(config.default_fractal, initial_view);

        app
    }

    fn get_view(&self) -> FractalViewState {
        self.views
            .get(&self.controls.fractal_type)
            .cloned()
            .unwrap_or_default()
    }

    fn set_view(&mut self, view: FractalViewState) {
        self.views.insert(self.controls.fractal_type, view);
    }

    /// Invalidate the render cache and request a full re-render.
    /// Clears any partial render regions since we're doing a full render.
    fn invalidate_cache(&mut self) {
        self.needs_render = true;
        self.partial_render_regions.clear();
        self.current_region_index = 0;
    }

    fn calculate_adaptive_iterations(&self, zoom: f64) -> u32 {
        // Base iterations + additional iterations based on zoom level
        // Formula: base + 50 * log2(zoom)
        // At zoom 1: base iterations
        // At zoom 10: base + ~166 iterations
        // At zoom 100: base + ~332 iterations
        let base_iter = self.controls.max_iterations;
        let zoom_factor = if zoom > 1.0 { zoom.log2() } else { 0.0 };
        let additional = (50.0 * zoom_factor) as u32;
        (base_iter + additional).min(2000) // Cap at 2000
    }

    fn save_view_to_history(&mut self) {
        let current = self.get_view();
        let current_type = self.controls.fractal_type;

        // Only save if view actually changed
        if let Some((last_type, last_view)) = &self.last_saved_view {
            if *last_type == current_type
                && (last_view.center_x - current.center_x).abs() < 1e-10
                && (last_view.center_y - current.center_y).abs() < 1e-10
                && (last_view.zoom - current.zoom).abs() < 1e-10
            {
                return;
            }
        }

        self.view_history.push(current_type, current.clone());
        self.last_saved_view = Some((current_type, current));
    }

    fn save_image(&self, scale_factor: u32) -> Result<PathBuf, String> {
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
            FractalType::Phoenix => "phoenix",
            FractalType::Multibrot => "multibrot",
            FractalType::Spider => "spider",
            FractalType::OrbitTrap => "orbit_trap",
            FractalType::PickoverStalk => "pickover_stalk",
        };
        let palette_name = match self.controls.palette_type {
            PaletteType::Classic => "classic",
            PaletteType::Fire => "fire",
            PaletteType::Ice => "ice",
            PaletteType::Grayscale => "grayscale",
            PaletteType::Psychedelic => "psychedelic",
        };

        let base_width = image.width() as u32;
        let base_height = image.height() as u32;
        let width = base_width * scale_factor;
        let height = base_height * scale_factor;

        let mut img: ImageBuffer<Rgb<u8>, Vec<u8>> = ImageBuffer::new(width, height);

        // If scale_factor is 1, use cached image directly
        if scale_factor == 1 {
            for (i, color) in image.pixels.iter().enumerate() {
                let x = (i % base_width as usize) as u32;
                let y = (i / base_width as usize) as u32;
                img.put_pixel(x, y, Rgb([color.r(), color.g(), color.b()]));
            }
        } else {
            // Render at higher resolution
            self.render_high_res(&mut img, width, height)?;
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

    fn render_high_res(
        &self,
        buffer: &mut ImageBuffer<Rgb<u8>, Vec<u8>>,
        width: u32,
        height: u32,
    ) -> Result<(), String> {
        let view = self.get_view();
        let max_iter = if self.adaptive_iterations {
            self.calculate_adaptive_iterations(view.zoom)
        } else {
            self.controls.max_iterations
        };

        let pixels = self.render_engine.render_high_res(
            self.fractal.as_ref(),
            &view,
            width,
            height,
            max_iter,
            self.controls.palette_type,
            self.controls.palette_offset,
        );

        for (i, color) in pixels.iter().enumerate() {
            let x = (i % width as usize) as u32;
            let y = (i / width as usize) as u32;
            buffer.put_pixel(x, y, Rgb([color.r(), color.g(), color.b()]));
        }

        Ok(())
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

    fn reset_settings(&mut self) {
        // Reset everything for current fractal to factory defaults
        let (center_x, center_y) = self.controls.fractal_type.default_center();
        let default_view = FractalViewState {
            center_x,
            center_y,
            zoom: 1.0,
            max_iterations: 200,
            fractal_params: HashMap::new(),
            palette_type: PaletteType::Classic,
        };
        self.views.insert(self.controls.fractal_type, default_view);

        // Reset controls
        self.controls.max_iterations = 200;
        self.controls.pending_max_iterations = 200;
        self.controls.palette_type = PaletteType::Classic;
        self.controls.pending_palette_offset = 0.0;
        self.controls.palette_offset = 0.0;

        // Reset fractal parameters to defaults
        self.fractal = create_fractal(self.controls.fractal_type);
        self.controls.pending_fractal_params.clear();

        self.invalidate_cache();
        self.set_status("Settings reset".to_string());
    }

    fn zoom_view(&mut self, factor: f64) {
        self.save_view_to_history();
        let mut view = self.get_view();
        view.zoom *= factor;

        // If adaptive iterations is enabled, update max_iterations
        if self.adaptive_iterations {
            let new_iter = self.calculate_adaptive_iterations(view.zoom);
            view.max_iterations = new_iter;
            self.controls.max_iterations = new_iter;
            self.controls.pending_max_iterations = new_iter;
        }

        self.set_view(view);
        self.invalidate_cache();
    }

    fn pan_view(&mut self, dx: f64, dy: f64) {
        self.save_view_to_history();
        let mut view = self.get_view();
        let pan_amount = 0.5 / view.zoom;
        view.center_x += dx * pan_amount;
        view.center_y += dy * pan_amount;
        self.set_view(view.clone());

        // Try to optimize pan by shifting existing pixels
        if let Some(ref mut cached) = self.cached_fractal_image {
            let regions = self
                .render_engine
                .calculate_pan_regions(cached, dx, dy, view.zoom);

            if !regions.is_empty() {
                self.partial_render_regions = regions;
                self.current_region_index = 0;
                self.needs_render = true;
                return;
            }
        }

        self.needs_render = true;
    }

    fn undo(&mut self) {
        if let Some((fractal_type, view)) = self.view_history.undo() {
            self.controls.fractal_type = fractal_type;
            self.fractal = create_fractal(fractal_type);
            self.views.insert(fractal_type, view);
            self.invalidate_cache();
            self.set_status("Undo".to_string());
        }
    }

    fn redo(&mut self) {
        if let Some((fractal_type, view)) = self.view_history.redo() {
            self.controls.fractal_type = fractal_type;
            self.fractal = create_fractal(fractal_type);
            self.views.insert(fractal_type, view);
            self.invalidate_cache();
            self.set_status("Redo".to_string());
        }
    }

    fn add_bookmark(&mut self, name: String) {
        let view = self.get_view();
        let bookmark = Bookmark {
            name,
            fractal_type: self.controls.fractal_type,
            center_x: view.center_x,
            center_y: view.center_y,
            zoom: view.zoom,
            max_iterations: view.max_iterations,
            palette_type: view.palette_type,
        };
        self.bookmarks.push(bookmark);
        self.set_status("Bookmark saved".to_string());
    }

    fn delete_bookmark(&mut self, index: usize) {
        if index < self.bookmarks.len() {
            self.bookmarks.remove(index);
            self.set_status("Bookmark deleted".to_string());
        }
    }

    fn load_bookmark(&mut self, index: usize) {
        if let Some(bookmark) = self.bookmarks.get(index).cloned() {
            self.save_view_to_history();
            self.controls.fractal_type = bookmark.fractal_type;
            self.fractal = create_fractal(bookmark.fractal_type);

            let view = FractalViewState {
                center_x: bookmark.center_x,
                center_y: bookmark.center_y,
                zoom: bookmark.zoom,
                max_iterations: bookmark.max_iterations,
                fractal_params: HashMap::new(),
                palette_type: bookmark.palette_type,
            };
            self.views.insert(bookmark.fractal_type, view);

            self.controls.max_iterations = bookmark.max_iterations;
            self.controls.pending_max_iterations = bookmark.max_iterations;
            self.controls.palette_type = bookmark.palette_type;

            self.invalidate_cache();
            self.set_status(format!("Loaded: {}", bookmark.name));
        }
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

    fn update_mouse_position(&mut self, pos: egui::Pos2, rect: &egui::Rect) {
        let width = rect.width() as u32;
        let height = rect.height() as u32;
        let view = self.get_view();

        let x = (pos.x - rect.min.x) as u32;
        let y = (pos.y - rect.min.y) as u32;

        if x < width && y < height {
            let (fx, fy) = screen_to_fractal(x, y, width, height, &view);
            self.mouse_fractal_pos = Some((fx, fy));
        } else {
            self.mouse_fractal_pos = None;
        }
    }

    fn render_minimap(&self, ctx: &egui::Context) -> Option<egui::TextureHandle> {
        if !self.minimap_enabled {
            return None;
        }

        let minimap_size = 150;
        let mut pixels = vec![egui::Color32::BLACK; minimap_size * minimap_size];

        // Render a simplified version of the fractal
        let view = self.get_view();
        let max_iter = 50; // Low quality for speed

        // For the minimap, we show the full fractal at zoom level 1
        // with a rectangle showing current view
        let minimap_view = FractalViewState {
            center_x: self.controls.fractal_type.default_center().0,
            center_y: self.controls.fractal_type.default_center().1,
            zoom: 1.0,
            max_iterations: max_iter,
            fractal_params: view.fractal_params.clone(),
            palette_type: view.palette_type,
        };

        for y in 0..minimap_size {
            for x in 0..minimap_size {
                let (px, py) = screen_to_fractal(
                    x as u32,
                    y as u32,
                    minimap_size as u32,
                    minimap_size as u32,
                    &minimap_view,
                );
                let iterations = self.fractal.compute(px, py, max_iter);
                let color = if iterations >= max_iter {
                    egui::Color32::BLACK
                } else {
                    let t = iterations as f32 / max_iter as f32;
                    palette::get_color(view.palette_type, t, 0.0)
                };
                pixels[y * minimap_size + x] = color;
            }
        }

        // Draw view rectangle
        // Calculate where the current view would be on the minimap
        let default_center = self.controls.fractal_type.default_center();
        let view_width = 4.0 / view.zoom; // Width in fractal coordinates
        let view_height = view_width; // Square aspect

        // Map view center to minimap coordinates
        let map_range = 4.0; // Minimap shows -2 to 2 range
        let rel_x = (view.center_x - default_center.0 + map_range / 2.0) / map_range;
        let rel_y = (view.center_y - default_center.1 + map_range / 2.0) / map_range;

        let rect_x = (rel_x * minimap_size as f64) as i32;
        let rect_y = (rel_y * minimap_size as f64) as i32;
        let rect_w = ((view_width / map_range) * minimap_size as f64) as i32;
        let rect_h = ((view_height / map_range) * minimap_size as f64) as i32;

        // Draw rectangle outline
        for dy in -rect_h / 2..=rect_h / 2 {
            for dx in -rect_w / 2..=rect_w / 2 {
                if dx == -rect_w / 2 || dx == rect_w / 2 || dy == -rect_h / 2 || dy == rect_h / 2 {
                    let px = rect_x + dx;
                    let py = rect_y + dy;
                    if px >= 0 && px < minimap_size as i32 && py >= 0 && py < minimap_size as i32 {
                        pixels[py as usize * minimap_size + px as usize] = egui::Color32::YELLOW;
                    }
                }
            }
        }

        let image = egui::ColorImage {
            size: [minimap_size, minimap_size],
            pixels,
        };

        Some(ctx.load_texture("minimap", image, egui::TextureOptions::default()))
    }
}

impl eframe::App for FractalApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.check_status_timeout();

        // Handle keyboard input (disable when bookmark dialog is open)
        if !self.show_bookmark_dialog {
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
                if i.key_pressed(egui::Key::R) && !i.modifiers.shift {
                    self.save_view_to_history();
                    self.reset_view();
                    self.invalidate_cache();
                }

                // Undo/Redo
                if i.key_pressed(egui::Key::Z) && i.modifiers.ctrl {
                    self.undo();
                }
                if i.key_pressed(egui::Key::Y) && i.modifiers.ctrl {
                    self.redo();
                }

                // Save: S key
                if i.key_pressed(egui::Key::S) {
                    match self.save_image(1) {
                        Ok(path) => {
                            self.set_status(format!("Saved: {}", path.display()));
                        }
                        Err(e) => {
                            self.set_status(format!("Error: {}", e));
                        }
                    }
                }
            });
        }

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
                    self.invalidate_cache();
                }

                if changed {
                    if let Some(view) = self.views.get_mut(&self.controls.fractal_type) {
                        view.max_iterations = self.controls.max_iterations;
                        view.fractal_params = self.controls.pending_fractal_params.clone();
                        view.palette_type = self.controls.palette_type;
                    }
                    self.invalidate_cache();
                }

                ui.separator();

                // View controls
                ui.horizontal(|ui| {
                    if ui.button("Reset View (R)").clicked() {
                        self.save_view_to_history();
                        self.reset_view();
                        self.invalidate_cache();
                    }
                    if ui
                        .button("Reset All")
                        .on_hover_text("Reset view, palette, and parameters")
                        .clicked()
                    {
                        self.save_view_to_history();
                        self.reset_settings();
                    }
                });

                ui.horizontal(|ui| {
                    if ui.button("Save (S)").clicked() {
                        match self.save_image(1) {
                            Ok(path) => {
                                self.set_status(format!("Saved: {}", path.display()));
                            }
                            Err(e) => {
                                self.set_status(format!("Error: {}", e));
                            }
                        }
                    }
                    if ui.button("Bookmark").clicked() {
                        self.show_bookmark_dialog = true;
                        self.bookmark_name_input.clear();
                    }
                });

                ui.horizontal(|ui| {
                    if ui
                        .add_enabled(self.view_history.can_undo(), egui::Button::new("Undo"))
                        .clicked()
                    {
                        self.undo();
                    }
                    if ui
                        .add_enabled(self.view_history.can_redo(), egui::Button::new("Redo"))
                        .clicked()
                    {
                        self.redo();
                    }
                });

                ui.separator();
                ui.label("Export Resolution:");
                ui.horizontal(|ui| {
                    if ui.button("1x (Current)").clicked() {
                        match self.save_image(1) {
                            Ok(path) => self.set_status(format!("Saved: {}", path.display())),
                            Err(e) => self.set_status(format!("Error: {}", e)),
                        }
                    }
                    if ui.button("2x").clicked() {
                        match self.save_image(2) {
                            Ok(path) => self.set_status(format!("Saved 2x: {}", path.display())),
                            Err(e) => self.set_status(format!("Error: {}", e)),
                        }
                    }
                    if ui.button("4x").clicked() {
                        match self.save_image(4) {
                            Ok(path) => self.set_status(format!("Saved 4x: {}", path.display())),
                            Err(e) => self.set_status(format!("Error: {}", e)),
                        }
                    }
                });

                ui.separator();

                // Settings toggles
                let prev_supersampling = self.supersampling_enabled;
                ui.checkbox(&mut self.supersampling_enabled, "Supersampling (2x)");
                if self.supersampling_enabled != prev_supersampling {
                    self.invalidate_cache();
                }

                let prev_adaptive = self.adaptive_iterations;
                ui.checkbox(&mut self.adaptive_iterations, "Adaptive Iterations");
                if self.adaptive_iterations != prev_adaptive {
                    self.invalidate_cache();
                }
                if self.adaptive_iterations {
                    ui.label(format!(
                        "Current: {}",
                        self.calculate_adaptive_iterations(self.get_view().zoom)
                    ));
                }

                let prev_minimap = self.minimap_enabled;
                ui.checkbox(&mut self.minimap_enabled, "Show Minimap");
                if self.minimap_enabled != prev_minimap {
                    self.invalidate_cache();
                }

                // Bookmark dialog
                if self.show_bookmark_dialog {
                    ui.separator();
                    ui.label("Bookmark Name:");
                    ui.text_edit_singleline(&mut self.bookmark_name_input);
                    ui.horizontal(|ui| {
                        if ui.button("Save").clicked() && !self.bookmark_name_input.is_empty() {
                            self.add_bookmark(self.bookmark_name_input.clone());
                            self.show_bookmark_dialog = false;
                        }
                        if ui.button("Cancel").clicked() {
                            self.show_bookmark_dialog = false;
                        }
                    });
                }

                // Bookmarks list
                if !self.bookmarks.is_empty() {
                    ui.separator();
                    ui.label("Bookmarks:");
                    egui::ScrollArea::vertical()
                        .max_height(150.0)
                        .show(ui, |ui| {
                            for (i, bookmark) in self.bookmarks.clone().iter().enumerate() {
                                ui.horizontal(|ui| {
                                    if ui.button(&bookmark.name).clicked() {
                                        self.load_bookmark(i);
                                    }
                                    if ui.button("×").clicked() {
                                        self.delete_bookmark(i);
                                    }
                                });
                            }
                        });
                }

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
                ui.label(format!("Iter: {}", view.max_iterations));

                // Mouse coordinates display
                if let Some((fx, fy)) = self.mouse_fractal_pos {
                    ui.separator();
                    ui.label(format!("Cursor: ({:.6}, {:.6})", fx, fy));
                }

                if self.is_rendering || self.needs_render {
                    ui.separator();
                    ui.label("Rendering...");
                    ui.add(egui::ProgressBar::new(self.render_progress).desired_width(200.0));
                }

                // Show last render time
                if let Some(render_time) = self.last_render_time {
                    ui.separator();
                    if render_time < 1.0 {
                        ui.label(format!("Last render: {:.0}ms", render_time * 1000.0));
                    } else {
                        ui.label(format!("Last render: {:.2}s", render_time));
                    }
                }

                ui.separator();
                ui.label("Keyboard:");
                ui.label("+/- : Zoom in/out");
                ui.label("Arrows : Pan");
                ui.label("R : Reset view");
                ui.label("Shift+R : Reset all");
                ui.label("Ctrl+Z : Undo");
                ui.label("Ctrl+Y : Redo");
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

            // Update mouse position for coordinate display
            if let Some(pos) = pointer_pos {
                self.update_mouse_position(pos, &rect);
            } else {
                self.mouse_fractal_pos = None;
            }

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

                        let view = self.get_view();

                        let (fractal_min_x, fractal_max_y) =
                            screen_to_fractal(min_x as u32, max_y as u32, width, height, &view);
                        let (fractal_max_x, fractal_min_y) =
                            screen_to_fractal(max_x as u32, min_y as u32, width, height, &view);

                        let new_center_x = (fractal_min_x + fractal_max_x) / 2.0;
                        let new_center_y = (fractal_min_y + fractal_max_y) / 2.0;

                        let sel_height_px = max_y - min_y;
                        let new_zoom = view.zoom * (height as f64 / sel_height_px as f64);

                        self.save_view_to_history();

                        // Calculate adaptive iterations if enabled
                        let new_max_iter = if self.adaptive_iterations {
                            self.calculate_adaptive_iterations(new_zoom)
                        } else {
                            self.controls.max_iterations
                        };

                        self.set_view(FractalViewState {
                            center_x: new_center_x,
                            center_y: new_center_y,
                            zoom: new_zoom,
                            max_iterations: new_max_iter,
                            fractal_params: view.fractal_params.clone(),
                            palette_type: self.controls.palette_type,
                        });

                        // Update controls to reflect new iteration count
                        if self.adaptive_iterations {
                            self.controls.max_iterations = new_max_iter;
                            self.controls.pending_max_iterations = new_max_iter;
                        }

                        self.render_delay = 2;
                    }
                }

                self.drag_start = None;
                self.drag_current = None;
                ctx.request_repaint();
            }

            // Initial render check (pause when bookmark dialog is open)
            if !self.show_bookmark_dialog {
                if self.cached_width == 0 || self.cached_height == 0 {
                    self.invalidate_cache();
                } else if self.render_delay > 0 {
                    self.render_delay -= 1;
                    if self.render_delay == 0 {
                        self.invalidate_cache();
                    }
                }
            }

            // Main fractal display
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

            // Draw minimap if enabled (must be before getting painter)
            let minimap_rect = if self.minimap_enabled {
                if let Some(minimap_texture) = self.render_minimap(ctx) {
                    let minimap_size = 150.0;
                    let minimap_rect = egui::Rect::from_min_size(
                        egui::pos2(rect.max.x - minimap_size - 10.0, rect.min.y + 10.0),
                        egui::vec2(minimap_size, minimap_size),
                    );
                    ui.put(
                        minimap_rect,
                        egui::Image::new((minimap_texture.id(), minimap_rect.size())),
                    );
                    Some(minimap_rect)
                } else {
                    None
                }
            } else {
                None
            };

            let painter = ui.painter();

            // Draw zoom preview if available
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

            // Draw selection rectangle outline
            if self.zoom_preview.is_none() {
                if let (Some(start), Some(end)) = (self.drag_start, self.drag_current) {
                    let sel_rect = egui::Rect::from_two_pos(start, end);
                    painter.rect_stroke(sel_rect, 1.0, egui::Stroke::new(2.0, egui::Color32::BLUE));
                }
            }

            // Draw border around minimap
            if let Some(minimap_rect) = minimap_rect {
                painter.rect_stroke(
                    minimap_rect,
                    0.0,
                    egui::Stroke::new(2.0, egui::Color32::WHITE),
                );
            }

            // Rendering logic using the new RenderEngine
            if self.is_rendering {
                if let Some(ref config) = self.render_config.clone() {
                    if !self.partial_render_regions.is_empty() {
                        // Partial rendering for pan optimization
                        if self.current_region_index < self.partial_render_regions.len() {
                            let region = &self.partial_render_regions[self.current_region_index];
                            let chunk_size = ((region.height as f64 / 10.0).ceil() as u32).max(1);

                            if let Some(chunk_result) = self.render_engine.render_region(
                                region,
                                self.fractal.as_ref(),
                                &self.get_view(),
                                config,
                                self.render_chunk_start,
                                chunk_size,
                            ) {
                                // Update cached image with rendered pixels
                                if let Some(ref mut cached) = self.cached_fractal_image {
                                    for dy in 0..chunk_result.height {
                                        let y = chunk_result.y + dy;
                                        for dx in 0..chunk_result.width {
                                            let x = chunk_result.x + dx;
                                            let src_idx = (dy * chunk_result.width + dx) as usize;
                                            let dst_idx = (y * cached.width() as u32 + x) as usize;
                                            if dst_idx < cached.pixels.len() {
                                                cached.pixels[dst_idx] =
                                                    chunk_result.pixels[src_idx];
                                            }
                                        }
                                    }
                                }

                                self.render_chunk_start += chunk_result.height;
                                if self.render_chunk_start >= region.height {
                                    self.current_region_index += 1;
                                    self.render_chunk_start = 0;
                                }

                                self.render_progress = (self.current_region_index as f32
                                    + self.render_chunk_start as f32 / region.height as f32)
                                    / self.partial_render_regions.len() as f32;
                                ctx.request_repaint();
                            } else {
                                // Region complete
                                self.current_region_index += 1;
                                self.render_chunk_start = 0;
                                ctx.request_repaint();
                            }
                        } else {
                            // All regions complete
                            self.is_rendering = false;
                            self.render_progress = 0.0;
                            self.partial_render_regions.clear();
                            self.current_region_index = 0;
                            self.render_chunk_start = 0;
                            self.render_config = None;

                            if let Some(start_time) = self.render_start_time.take() {
                                self.last_render_time = Some(start_time.elapsed().as_secs_f64());
                            }
                            ctx.request_repaint();
                        }
                    } else {
                        // Full canvas rendering
                        let (_render_width, render_height) = config.render_dimensions();
                        let chunk_size = ((render_height as f64 / 60.0).ceil() as u32).max(1);

                        let has_more = self.render_engine.render_full_chunk(
                            self.fractal.as_ref(),
                            &self.get_view(),
                            config,
                            self.render_chunk_start,
                            chunk_size,
                        );

                        if has_more {
                            self.render_chunk_start +=
                                chunk_size.min(render_height - self.render_chunk_start);
                            self.render_progress =
                                self.render_chunk_start as f32 / render_height as f32;
                            ctx.request_repaint();
                        } else {
                            // Rendering complete
                            if let Some(pixels) = self.render_engine.finalize(config) {
                                self.cached_fractal_image = Some(egui::ColorImage {
                                    size: [config.width as _, config.height as _],
                                    pixels,
                                });
                            }

                            self.cached_width = config.width;
                            self.cached_height = config.height;
                            self.needs_render = false;
                            self.is_rendering = false;
                            self.render_progress = 0.0;
                            self.zoom_preview = None;
                            self.render_chunk_start = 0;
                            self.render_config = None;

                            if let Some(start_time) = self.render_start_time.take() {
                                self.last_render_time = Some(start_time.elapsed().as_secs_f64());
                            }
                            ctx.request_repaint();
                        }
                    }
                }
            }

            // Start new render if needed
            if self.needs_render && !self.is_rendering && !self.show_bookmark_dialog {
                let view = self.get_view();
                let max_iter = if self.adaptive_iterations {
                    self.calculate_adaptive_iterations(view.zoom)
                } else {
                    self.controls.max_iterations
                };

                let config = RenderConfig {
                    width,
                    height,
                    supersampling: self.supersampling_enabled,
                    max_iterations: max_iter,
                    palette_type: self.controls.palette_type,
                    palette_offset: self.controls.palette_offset,
                };

                self.render_engine.start_render(&config);
                self.render_config = Some(config);
                self.is_rendering = true;
                self.render_start_time = Some(Instant::now());
                self.render_progress = 0.0;
                self.render_chunk_start = 0;
                self.current_region_index = 0;
                self.needs_render = false;
                ctx.request_repaint();
            }
        });
    }

    fn on_exit(&mut self, _ctx: Option<&eframe::glow::Context>) {
        // Save window size on exit
        let config = AppConfig {
            window_width: 1200.0, // Could get actual size from ctx
            window_height: 800.0,
            default_iterations: self.controls.max_iterations,
            default_fractal: self.controls.fractal_type,
            default_palette: self.controls.palette_type,
            supersampling_enabled: self.supersampling_enabled,
            adaptive_iterations: self.adaptive_iterations,
            bookmarks: self.bookmarks.clone(),
        };
        if let Err(e) = config.save() {
            eprintln!("Failed to save config: {}", e);
        }
    }
}

fn main() -> eframe::Result {
    eprintln!("STARTING Fractal Explorer...");

    let config = AppConfig::load();

    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([config.window_width, config.window_height])
            .with_title("Fractal Explorer"),
        ..Default::default()
    };

    eframe::run_native(
        "Fractal Explorer",
        options,
        Box::new(|_cc| Ok(Box::new(FractalApp::new(&config)))),
    )
}
