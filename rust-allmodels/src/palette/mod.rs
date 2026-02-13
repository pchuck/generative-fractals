use eframe::egui::Color32;
use std::sync::OnceLock;

// Global singleton instances for each palette type
// Using OnceLock ensures thread-safe lazy initialization
static CLASSIC_PALETTE: OnceLock<ClassicPalette> = OnceLock::new();
static FIRE_PALETTE: OnceLock<FirePalette> = OnceLock::new();
static ICE_PALETTE: OnceLock<IcePalette> = OnceLock::new();
static GRAYSCALE_PALETTE: OnceLock<GrayscalePalette> = OnceLock::new();
static PSYCHEDELIC_PALETTE: OnceLock<PsychedelicPalette> = OnceLock::new();

/// Available color palette types for fractal rendering.
#[derive(Debug, Clone, Copy, PartialEq, Default)]
pub enum PaletteType {
    #[default]
    Classic,
    Fire,
    Ice,
    Grayscale,
    Psychedelic,
}

/// Trait for color palettes.
///
/// Palettes map a normalized value t (0.0 to 1.0) to a color.
/// For fractals, t typically represents the iteration count ratio.
pub trait Palette: Send + Sync {
    /// Returns the display name of this palette.
    #[allow(dead_code)]
    fn name(&self) -> &str;

    /// Returns the color for a given normalized value t (0.0 to 1.0).
    fn color(&self, t: f32) -> Color32;
}

/// Classic rainbow gradient palette.
///
/// Colors: black → dark blue → blue → cyan → green → yellow → red → white
/// Provides good contrast and visually pleasing results for most fractals.
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

        interpolate_colors(&colors, t)
    }
}

/// Fire-inspired palette.
///
/// Colors: black → dark red → red → orange → yellow → white
/// Creates a heat-map effect, good for highlighting iteration density.
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

        interpolate_colors(&colors, t)
    }
}

/// Ice/cold palette.
///
/// Colors: black → dark blue → blue → light blue → cyan → white
/// Creates a frozen/icy appearance.
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

        interpolate_colors(&colors, t)
    }
}

/// Simple grayscale palette.
///
/// Maps t directly to brightness from black to white.
/// Useful for analyzing fractal structure without color distraction.
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

/// Psychedelic cycling palette.
///
/// Uses HSV color space with full saturation and varying hue.
/// Supports hue rotation via offset parameter for animated effects.
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

/// Interpolates between a list of RGB colors.
///
/// t should be in range [0.0, 1.0]. Colors are evenly spaced across this range.
fn interpolate_colors(colors: &[(f32, f32, f32)], t: f32) -> Color32 {
    let n = (colors.len() - 1) as f32;
    let idx = (t * n).clamp(0.0, n);
    let i = idx.floor() as usize;
    let f = idx.fract();

    if i >= colors.len() - 1 {
        let last = colors[colors.len() - 1];
        return Color32::from_rgb(
            (last.0 * 255.0) as u8,
            (last.1 * 255.0) as u8,
            (last.2 * 255.0) as u8,
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

/// Converts HSV color to RGB.
///
/// h: hue in range [0.0, 1.0] (0=red, 1/3=green, 2/3=blue)
/// s: saturation in range [0.0, 1.0]
/// v: value/brightness in range [0.0, 1.0]
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

/// Gets a color from the specified palette.
///
/// For Psychedelic palette, offset is added to t for hue rotation.
pub fn get_color(palette_type: PaletteType, t: f32, offset: f32) -> Color32 {
    let adjusted_t = if matches!(palette_type, PaletteType::Psychedelic) {
        (t + offset) % 1.0
    } else {
        t
    };

    match palette_type {
        PaletteType::Classic => CLASSIC_PALETTE
            .get_or_init(|| ClassicPalette)
            .color(adjusted_t),
        PaletteType::Fire => FIRE_PALETTE.get_or_init(|| FirePalette).color(adjusted_t),
        PaletteType::Ice => ICE_PALETTE.get_or_init(|| IcePalette).color(adjusted_t),
        PaletteType::Grayscale => GRAYSCALE_PALETTE
            .get_or_init(|| GrayscalePalette)
            .color(adjusted_t),
        PaletteType::Psychedelic => PSYCHEDELIC_PALETTE
            .get_or_init(|| PsychedelicPalette)
            .color(adjusted_t),
    }
}
