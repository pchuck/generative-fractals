use eframe::egui::Color32;

#[derive(Debug, Clone, Copy, PartialEq, Default)]
pub enum PaletteType {
    #[default]
    Classic,
    Fire,
    Ice,
    Grayscale,
    Psychedelic,
}

#[allow(dead_code)]
pub trait Palette: Send + Sync {
    fn name(&self) -> &str;
    fn color(&self, t: f32) -> Color32;
}

pub struct ClassicPalette;
impl Palette for ClassicPalette {
    fn name(&self) -> &str {
        "Classic"
    }

    fn color(&self, t: f32) -> Color32 {
        let colors: [(f32, f32, f32); 8] = [
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.5),
            (0.0, 0.0, 1.0),
            (0.0, 1.0, 1.0),
            (0.0, 1.0, 0.0),
            (1.0, 1.0, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
        ];

        let idx = (t * 7.0).clamp(0.0, 7.0);
        let i = idx.floor() as usize;
        let f = idx.fract();

        if i >= 7 {
            return Color32::from_rgb(
                (colors[7].0 * 255.0) as u8,
                (colors[7].1 * 255.0) as u8,
                (colors[7].2 * 255.0) as u8,
            );
        }

        let (r1, g1, b1) = colors[i];
        let (r2, g2, b2) = colors[i + 1];

        Color32::from_rgb(
            ((r1 + (r2 - r1) * f) * 255.0) as u8,
            ((g1 + (g2 - g1) * f) * 255.0) as u8,
            ((b1 + (b2 - b1) * f) * 255.0) as u8,
        )
    }
}

pub struct FirePalette;
impl Palette for FirePalette {
    fn name(&self) -> &str {
        "Fire"
    }

    fn color(&self, t: f32) -> Color32 {
        let colors: [(f32, f32, f32); 6] = [
            (0.0, 0.0, 0.0),
            (0.5, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 0.5, 0.0),
            (1.0, 1.0, 0.0),
            (1.0, 1.0, 1.0),
        ];

        let idx = (t * 5.0).clamp(0.0, 5.0);
        let i = idx.floor() as usize;
        let f = idx.fract();

        if i >= 5 {
            return Color32::from_rgb(
                (colors[5].0 * 255.0) as u8,
                (colors[5].1 * 255.0) as u8,
                (colors[5].2 * 255.0) as u8,
            );
        }

        let (r1, g1, b1) = colors[i];
        let (r2, g2, b2) = colors[i + 1];

        Color32::from_rgb(
            ((r1 + (r2 - r1) * f) * 255.0) as u8,
            ((g1 + (g2 - g1) * f) * 255.0) as u8,
            ((b1 + (b2 - b1) * f) * 255.0) as u8,
        )
    }
}

pub struct IcePalette;
impl Palette for IcePalette {
    fn name(&self) -> &str {
        "Ice"
    }

    fn color(&self, t: f32) -> Color32 {
        let colors: [(f32, f32, f32); 6] = [
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.5),
            (0.0, 0.0, 1.0),
            (0.0, 0.5, 1.0),
            (0.5, 1.0, 1.0),
            (1.0, 1.0, 1.0),
        ];

        let idx = (t * 5.0).clamp(0.0, 5.0);
        let i = idx.floor() as usize;
        let f = idx.fract();

        if i >= 5 {
            return Color32::from_rgb(
                (colors[5].0 * 255.0) as u8,
                (colors[5].1 * 255.0) as u8,
                (colors[5].2 * 255.0) as u8,
            );
        }

        let (r1, g1, b1) = colors[i];
        let (r2, g2, b2) = colors[i + 1];

        Color32::from_rgb(
            ((r1 + (r2 - r1) * f) * 255.0) as u8,
            ((g1 + (g2 - g1) * f) * 255.0) as u8,
            ((b1 + (b2 - b1) * f) * 255.0) as u8,
        )
    }
}

pub struct GrayscalePalette;
impl Palette for GrayscalePalette {
    fn name(&self) -> &str {
        "Grayscale"
    }

    fn color(&self, t: f32) -> Color32 {
        let v = (t * 255.0) as u8;
        Color32::from_rgb(v, v, v)
    }
}

pub struct PsychedelicPalette;
impl Palette for PsychedelicPalette {
    fn name(&self) -> &str {
        "Psychedelic"
    }

    fn color(&self, t: f32) -> Color32 {
        let (r, g, b) = hsv_to_rgb(t, 1.0, 0.5);
        Color32::from_rgb((r * 255.0) as u8, (g * 255.0) as u8, (b * 255.0) as u8)
    }
}

fn hsv_to_rgb(h: f32, s: f32, v: f32) -> (f32, f32, f32) {
    let i = (h * 6.0).floor() as i32;
    let f = h * 6.0 - i as f32;
    let p = v * (1.0 - s);
    let q = v * (1.0 - f * s);
    let t = v * (1.0 - (1.0 - f) * s);

    match i % 6 {
        0 => (v, t, p),
        1 => (q, v, p),
        2 => (p, v, t),
        3 => (p, q, v),
        4 => (t, p, v),
        _ => (v, p, q),
    }
}

#[allow(dead_code)]
pub fn create_palette(palette_type: PaletteType) -> Box<dyn Palette> {
    match palette_type {
        PaletteType::Classic => Box::new(ClassicPalette),
        PaletteType::Fire => Box::new(FirePalette),
        PaletteType::Ice => Box::new(IcePalette),
        PaletteType::Grayscale => Box::new(GrayscalePalette),
        PaletteType::Psychedelic => Box::new(PsychedelicPalette),
    }
}

pub fn get_color(palette_type: PaletteType, t: f32, offset: f32) -> Color32 {
    let adjusted_t = if matches!(palette_type, PaletteType::Psychedelic) {
        (t + offset) % 1.0
    } else {
        t
    };

    match palette_type {
        PaletteType::Classic => ClassicPalette {}.color(adjusted_t),
        PaletteType::Fire => FirePalette {}.color(adjusted_t),
        PaletteType::Ice => IcePalette {}.color(adjusted_t),
        PaletteType::Grayscale => GrayscalePalette {}.color(adjusted_t),
        PaletteType::Psychedelic => PsychedelicPalette {}.color(adjusted_t),
    }
}
