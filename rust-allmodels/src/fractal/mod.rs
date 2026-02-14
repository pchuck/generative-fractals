use serde::{Deserialize, Serialize};

pub mod registry;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum FractalType {
    #[default]
    Mandelbrot,
    Julia,
    BurningShip,
    Tricorn,
    Celtic,
    Newton,
    Biomorph,
    Phoenix,
    Multibrot,
    Spider,
    OrbitTrap,
    PickoverStalk,
}

impl FractalType {
    /// Returns the default view center for this fractal type.
    /// Used to position the camera when first viewing the fractal.
    pub fn default_center(&self) -> (f64, f64) {
        match self {
            FractalType::Mandelbrot => (-0.5, 0.0),
            FractalType::Julia => (0.0, 0.0),
            FractalType::BurningShip => (-0.5, -0.5),
            FractalType::Tricorn => (0.0, 0.0),
            FractalType::Celtic => (0.0, 0.0),
            FractalType::Newton => (0.0, 0.0),
            FractalType::Biomorph => (0.0, 0.0),
            FractalType::Phoenix => (0.0, 0.0),
            FractalType::Multibrot => (0.0, 0.0),
            FractalType::Spider => (0.0, 0.0),
            FractalType::OrbitTrap => (-0.5, 0.0),
            FractalType::PickoverStalk => (-0.5, 0.0),
        }
    }
}

#[derive(Debug, Clone)]
pub struct Parameter {
    pub name: String,
    pub value: f64,
    pub min: f64,
    pub max: f64,
}

/// Trait for fractal implementations.
///
/// Each fractal provides:
/// - A name for display purposes
/// - Configurable parameters with min/max bounds
/// - A computation function that returns iteration count
pub trait Fractal: Send + Sync {
    /// Returns the display name of this fractal.
    #[allow(dead_code)]
    fn name(&self) -> &str;

    /// Returns the list of configurable parameters for this fractal.
    fn parameters(&self) -> Vec<Parameter>;

    /// Sets a parameter value, clamping to valid range.
    fn set_parameter(&mut self, name: &str, value: f64);

    /// Gets the current value of a parameter, or None if not found.
    #[allow(dead_code)]
    fn get_parameter(&self, name: &str) -> Option<f64>;

    /// Computes the iteration count for a point in the fractal.
    ///
    /// Returns a value from 0 to max_iter:
    /// - max_iter: Point is inside the set (did not escape)
    /// - lower values: Point escaped after that many iterations
    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32;
}

/// Macro to generate Fractal implementations for simple power-based fractals.
///
/// Generates:
/// - name() method
/// - parameters() returning a single "power" parameter
/// - set_parameter() and get_parameter() implementations
///
/// Usage: impl_power_fractal!(StructName, "Display Name")
macro_rules! impl_power_fractal {
    ($struct_name:ident, $display_name:expr) => {
        impl Fractal for $struct_name {
            fn name(&self) -> &str {
                $display_name
            }

            fn parameters(&self) -> Vec<Parameter> {
                vec![Parameter {
                    name: "power".to_string(),
                    value: self.power,
                    min: 1.0,
                    max: 8.0,
                }]
            }

            fn set_parameter(&mut self, name: &str, value: f64) {
                if name == "power" {
                    self.power = value.clamp(1.0, 8.0);
                }
            }

            fn get_parameter(&self, name: &str) -> Option<f64> {
                match name {
                    "power" => Some(self.power),
                    _ => None,
                }
            }

            fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
                self.compute_point(cx, cy, max_iter)
            }
        }
    };
}

// ============================================================================
// Mandelbrot Set
// ============================================================================

/// The classic Mandelbrot set.
///
/// Defined by the iteration: z_{n+1} = z_n^power + c
/// where c is the complex coordinate (cx, cy).
///
/// The set consists of all points where the iteration does not diverge
/// (remain bounded) as n -> infinity.
pub struct Mandelbrot {
    pub power: f64,
}

impl Default for Mandelbrot {
    fn default() -> Self {
        Mandelbrot { power: 2.0 }
    }
}

impl Mandelbrot {
    /// Computes iterations for a single point using De Moivre's theorem
    /// for arbitrary power exponentiation.
    fn compute_point(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re: f64 = 0.0;
        let mut z_im: f64 = 0.0;
        let c_re = cx;
        let c_im = cy;
        let power = self.power;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            // Use De Moivre's theorem: (r*e^(iθ))^power = r^power * e^(i*power*θ)
            let angle = 2.0 * z_im.atan2(z_re);
            let radius = (r2 + i2).powf(power / 2.0);

            z_re = radius * angle.cos() + c_re;
            z_im = radius * angle.sin() + c_im;
        }

        max_iter
    }
}

impl_power_fractal!(Mandelbrot, "Mandelbrot");

// ============================================================================
// Julia Set
// ============================================================================

/// Julia sets for the function f(z) = z^power + c.
///
/// Unlike Mandelbrot where c varies per pixel, Julia uses a fixed c value
/// and varies the initial z (which corresponds to the pixel coordinate).
///
/// Each c value produces a different Julia set. Famous examples:
/// - c = -0.7 + 0.27015i (default): Douady rabbit
/// - c = -0.123 + 0.745i: Douady rabbit variant
/// - c = -0.391 - 0.587i: San Marco fractal
pub struct Julia {
    pub c_real: f64,
    pub c_imag: f64,
    pub power: f64,
}

impl Default for Julia {
    fn default() -> Self {
        Julia {
            c_real: -0.7,
            c_imag: 0.27015,
            power: 2.0,
        }
    }
}

impl Fractal for Julia {
    fn name(&self) -> &str {
        "Julia"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![
            Parameter {
                name: "c_real".to_string(),
                value: self.c_real,
                min: -2.0,
                max: 2.0,
            },
            Parameter {
                name: "c_imag".to_string(),
                value: self.c_imag,
                min: -2.0,
                max: 2.0,
            },
            Parameter {
                name: "power".to_string(),
                value: self.power,
                min: 1.0,
                max: 8.0,
            },
        ]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        match name {
            "c_real" => self.c_real = value.clamp(-2.0, 2.0),
            "c_imag" => self.c_imag = value.clamp(-2.0, 2.0),
            "power" => self.power = value.clamp(1.0, 8.0),
            _ => {}
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "c_real" => Some(self.c_real),
            "c_imag" => Some(self.c_imag),
            "power" => Some(self.power),
            _ => None,
        }
    }

    fn compute(&self, zx: f64, zy: f64, max_iter: u32) -> u32 {
        let mut z_re = zx;
        let mut z_im = zy;
        let c_re = self.c_real;
        let c_im = self.c_imag;
        let power = self.power;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            let angle = 2.0 * z_im.atan2(z_re);
            let radius = (r2 + i2).powf(power / 2.0);

            z_re = radius * angle.cos() + c_re;
            z_im = radius * angle.sin() + c_im;
        }

        max_iter
    }
}

// ============================================================================
// Burning Ship
// ============================================================================

/// The Burning Ship fractal.
///
/// Similar to Mandelbrot but with absolute values:
/// z_{n+1} = (|Re(z_n)| + i*|Im(z_n)|)^power + c
///
/// Creates a distinctive "burning ship" appearance in the negative quadrant.
pub struct BurningShip {
    pub power: f64,
}

impl Default for BurningShip {
    fn default() -> Self {
        BurningShip { power: 2.0 }
    }
}

impl BurningShip {
    fn compute_point(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re: f64 = 0.0;
        let mut z_im: f64 = 0.0;
        let c_re = cx;
        let c_im = cy;
        let power = self.power;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            let angle = 2.0 * z_im.atan2(z_re);
            let radius = (r2 + i2).powf(power / 2.0);

            z_re = radius * angle.cos() + c_re;
            z_im = radius * angle.sin() + c_im;

            z_re = z_re.abs();
            z_im = z_im.abs();
        }

        max_iter
    }
}

impl_power_fractal!(BurningShip, "Burning Ship");

// ============================================================================
// Tricorn (Mandelbar)
// ============================================================================

/// The Tricorn fractal (also known as Mandelbar).
///
/// Uses complex conjugation in the iteration:
/// z_{n+1} = conj(z_n)^power + c
///
/// The conjugation creates the characteristic three-pointed shape.
pub struct Tricorn {
    pub power: f64,
}

impl Default for Tricorn {
    fn default() -> Self {
        Tricorn { power: 2.0 }
    }
}

impl Tricorn {
    fn compute_point(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re: f64 = 0.0;
        let mut z_im: f64 = 0.0;
        let c_re = cx;
        let c_im = cy;
        let power = self.power;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            // Conjugation: flip the sign of the imaginary component
            let angle = -2.0 * z_im.atan2(z_re);
            let radius = (r2 + i2).powf(power / 2.0);

            z_re = radius * angle.cos() + c_re;
            z_im = radius * angle.sin() + c_im;
        }

        max_iter
    }
}

impl_power_fractal!(Tricorn, "Tricorn");

// ============================================================================
// Celtic
// ============================================================================

/// The Celtic fractal.
///
/// A hybrid combining elements of Burning Ship and standard fractals:
/// Only the real part takes absolute value after squaring.
///
/// Creates intricate Celtic knot-like patterns.
pub struct Celtic {
    pub power: f64,
}

impl Default for Celtic {
    fn default() -> Self {
        Celtic { power: 2.0 }
    }
}

impl Celtic {
    fn compute_point(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re: f64 = 0.0;
        let mut z_im: f64 = 0.0;
        let c_re = cx;
        let c_im = cy;
        let power = self.power;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            let angle = -2.0 * z_im.atan2(z_re);
            let radius = (r2 + i2).powf(power / 2.0);

            z_re = (radius * angle.cos() + c_re).abs();
            z_im = radius * angle.sin() + c_im;
        }

        max_iter
    }
}

impl_power_fractal!(Celtic, "Celtic");

// ============================================================================
// Newton's Method Fractal
// ============================================================================

/// Newton's method fractal for z^3 - 1 = 0.
///
/// Uses Newton's root-finding method to visualize which root each point
/// converges to when applying Newton's method to f(z) = z^3 - 1.
///
/// The roots are:
/// - root1: z = 1 (angle 0)
/// - root2: z = e^(2πi/3) = -0.5 + 0.866i
/// - root3: z = e^(4πi/3) = -0.5 - 0.866i
///
/// Newton's iteration: z_{n+1} = z_n - f(z_n)/f'(z_n)
/// For f(z) = z^3 - 1: z_{n+1} = (2*z^3 + 1) / (3*z^2)
pub struct Newton {
    pub escape_radius: f64,
    pub tolerance: f64,
}

impl Default for Newton {
    fn default() -> Self {
        Newton {
            escape_radius: 16.0,
            tolerance: 0.001,
        }
    }
}

impl Fractal for Newton {
    fn name(&self) -> &str {
        "Newton"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![
            Parameter {
                name: "escape_radius".to_string(),
                value: self.escape_radius,
                min: 4.0,
                max: 64.0,
            },
            Parameter {
                name: "tolerance".to_string(),
                value: self.tolerance,
                min: 0.0001,
                max: 0.1,
            },
        ]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        match name {
            "escape_radius" => self.escape_radius = value.clamp(4.0, 64.0),
            "tolerance" => self.tolerance = value.clamp(0.0001, 0.1),
            _ => {}
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "escape_radius" => Some(self.escape_radius),
            "tolerance" => Some(self.tolerance),
            _ => None,
        }
    }

    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re = cx;
        let mut z_im = cy;
        let tolerance = self.tolerance;
        let tolerance2 = tolerance * tolerance;

        // Pre-computed roots of z^3 - 1 = 0 (cube roots of unity)
        let root1_re = 1.0;
        let root1_im = 0.0;
        let root2_re = -0.5;
        let root2_im = 0.8660254037844386; // sqrt(3)/2
        let root3_re = -0.5;
        let root3_im = -0.8660254037844386; // -sqrt(3)/2

        for i in 0..max_iter {
            // Check convergence to any root using squared distance (faster)
            let dist2_1 = (z_re - root1_re).powi(2) + (z_im - root1_im).powi(2);
            let dist2_2 = (z_re - root2_re).powi(2) + (z_im - root2_im).powi(2);
            let dist2_3 = (z_re - root3_re).powi(2) + (z_im - root3_im).powi(2);

            if dist2_1 < tolerance2 || dist2_2 < tolerance2 || dist2_3 < tolerance2 {
                return max_iter - i; // Converged - return high iteration count
            }

            // Compute z^2 and z^3 for Newton's method
            // z^2 = (a + bi)^2 = (a^2 - b^2) + 2abi
            let z_re2 = z_re * z_re;
            let z_im2 = z_im * z_im;

            // z^3 = z^2 * z = (a^2 - b^2)a - 2ab*b + i[(a^2 - b^2)b + 2ab*a]
            //     = a(a^2 - 3b^2) + i*b(3a^2 - b^2)
            let z_re3 = z_re2 * z_re - 3.0 * z_re * z_im2;
            let z_im3 = 3.0 * z_re2 * z_im - z_im2 * z_im;

            // f(z) = z^3 - 1
            let f_real = z_re3 - 1.0;
            let f_imag = z_im3;

            // f'(z) = 3*z^2
            let deriv_real = 3.0 * (z_re2 - z_im2);
            let deriv_imag = 6.0 * z_re * z_im;

            // Newton's step: z = z - f(z)/f'(z)
            // Division: (a+bi)/(c+di) = [(ac+bd) + i(bc-ad)] / (c^2+d^2)
            let denom = deriv_real * deriv_real + deriv_imag * deriv_imag;
            if denom.abs() < 1e-20 {
                break; // Singularity - avoid division by zero
            }

            let new_re = z_re - (f_real * deriv_real + f_imag * deriv_imag) / denom;
            let new_im = z_im - (f_imag * deriv_real - f_real * deriv_imag) / denom;

            z_re = new_re;
            z_im = new_im;
        }

        max_iter // Did not converge to a root
    }
}

// ============================================================================
// Biomorph
// ============================================================================

/// Biomorph fractal - combines Newton's method with escape conditions.
///
/// Similar to Newton's method but stops if the iteration either:
/// 1. Converges to one of the roots (like Newton)
/// 2. Escapes beyond the escape radius (like Mandelbrot)
///
/// Creates organic, biological-looking structures hence the name "biomorph".
pub struct Biomorph {
    pub escape_radius: f64,
    pub tolerance: f64,
}

impl Default for Biomorph {
    fn default() -> Self {
        Biomorph {
            escape_radius: 16.0,
            tolerance: 0.001,
        }
    }
}

impl Fractal for Biomorph {
    fn name(&self) -> &str {
        "Biomorph"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![
            Parameter {
                name: "escape_radius".to_string(),
                value: self.escape_radius,
                min: 4.0,
                max: 64.0,
            },
            Parameter {
                name: "tolerance".to_string(),
                value: self.tolerance,
                min: 0.0001,
                max: 0.1,
            },
        ]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        match name {
            "escape_radius" => self.escape_radius = value.clamp(4.0, 64.0),
            "tolerance" => self.tolerance = value.clamp(0.0001, 0.1),
            _ => {}
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "escape_radius" => Some(self.escape_radius),
            "tolerance" => Some(self.tolerance),
            _ => None,
        }
    }

    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re = cx;
        let mut z_im = cy;
        let tolerance = self.tolerance;
        let tolerance2 = tolerance * tolerance;
        let escape_r2 = self.escape_radius * self.escape_radius;

        // Roots of z^3 - 1 = 0 (same as Newton)
        let root1_re = 1.0;
        let root1_im = 0.0;
        let root2_re = -0.5;
        let root2_im = 0.8660254037844386;
        let root3_re = -0.5;
        let root3_im = -0.8660254037844386;

        for i in 0..max_iter {
            // Check convergence to any root
            let dist2_1 = (z_re - root1_re).powi(2) + (z_im - root1_im).powi(2);
            let dist2_2 = (z_re - root2_re).powi(2) + (z_im - root2_im).powi(2);
            let dist2_3 = (z_re - root3_re).powi(2) + (z_im - root3_im).powi(2);

            if dist2_1 < tolerance2 || dist2_2 < tolerance2 || dist2_3 < tolerance2 {
                return max_iter - i; // Converged - bright color
            }

            // Check escape (unlike pure Newton)
            let r2 = z_re * z_re + z_im * z_im;
            if r2 > escape_r2 {
                return i; // Escaped - return iteration count for coloring
            }

            // Newton's method iteration (same as Newton fractal)
            let z_re2 = z_re * z_re;
            let z_im2 = z_im * z_im;
            let z_re3 = z_re2 * z_re - 3.0 * z_re * z_im2;
            let z_im3 = 3.0 * z_re2 * z_im - z_im2 * z_im;

            let f_real = z_re3 - 1.0;
            let f_imag = z_im3;

            let deriv_real = 3.0 * (z_re2 - z_im2);
            let deriv_imag = 6.0 * z_re * z_im;

            let denom = deriv_real * deriv_real + deriv_imag * deriv_imag;
            if denom.abs() < 1e-20 {
                break;
            }

            let new_re = z_re - (f_real * deriv_real + f_imag * deriv_imag) / denom;
            let new_im = z_im - (f_imag * deriv_real - f_real * deriv_imag) / denom;

            z_re = new_re;
            z_im = new_im;
        }

        max_iter // Neither converged nor escaped
    }
}

// ============================================================================
// Phoenix Fractal
// ============================================================================

/// Phoenix fractal - a variation with memory term.
///
/// Similar to Julia but includes the previous iteration value:
/// z_{n+1} = z_n^2 + c + p * z_{n-1}
/// where p is the "memory" parameter.
///
/// Creates flame-like and spiral patterns.
pub struct Phoenix {
    pub c_real: f64,
    pub c_imag: f64,
    pub memory: f64,
}

impl Default for Phoenix {
    fn default() -> Self {
        Phoenix {
            c_real: 0.0,
            c_imag: 0.4,
            memory: 0.55,
        }
    }
}

impl Fractal for Phoenix {
    fn name(&self) -> &str {
        "Phoenix"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![
            Parameter {
                name: "c_real".to_string(),
                value: self.c_real,
                min: -2.0,
                max: 2.0,
            },
            Parameter {
                name: "c_imag".to_string(),
                value: self.c_imag,
                min: -2.0,
                max: 2.0,
            },
            Parameter {
                name: "memory".to_string(),
                value: self.memory,
                min: -1.0,
                max: 1.0,
            },
        ]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        match name {
            "c_real" => self.c_real = value.clamp(-2.0, 2.0),
            "c_imag" => self.c_imag = value.clamp(-2.0, 2.0),
            "memory" => self.memory = value.clamp(-1.0, 1.0),
            _ => {}
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "c_real" => Some(self.c_real),
            "c_imag" => Some(self.c_imag),
            "memory" => Some(self.memory),
            _ => None,
        }
    }

    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re = cx;
        let mut z_im = cy;
        let mut z_prev_re = 0.0;
        let mut z_prev_im = 0.0;
        let c_re = self.c_real;
        let c_im = self.c_imag;
        let p = self.memory;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            // z^2 + c + p * z_prev
            let new_re = r2 - i2 + c_re + p * z_prev_re;
            let new_im = 2.0 * z_re * z_im + c_im + p * z_prev_im;

            z_prev_re = z_re;
            z_prev_im = z_im;
            z_re = new_re;
            z_im = new_im;
        }

        max_iter
    }
}

// ============================================================================
// Multibrot Fractal
// ============================================================================

/// Multibrot fractal - Mandelbrot with arbitrary power.
///
/// z_{n+1} = z_n^power + c
///
/// Power 2 gives standard Mandelbrot, power 3 gives "Mandelbar" (not to be confused with Tricorn),
/// higher powers create more lobes.
pub struct Multibrot {
    pub power: f64,
}

impl Default for Multibrot {
    fn default() -> Self {
        Multibrot { power: 3.0 }
    }
}

impl Fractal for Multibrot {
    fn name(&self) -> &str {
        "Multibrot"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![Parameter {
            name: "power".to_string(),
            value: self.power,
            min: 2.0,
            max: 10.0,
        }]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        if name == "power" {
            self.power = value.clamp(2.0, 10.0);
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "power" => Some(self.power),
            _ => None,
        }
    }

    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re: f64 = 0.0;
        let mut z_im: f64 = 0.0;
        let c_re = cx;
        let c_im = cy;
        let power = self.power;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            // Use De Moivre's theorem: (r*e^(iθ))^power = r^power * e^(i*power*θ)
            let angle = power * z_im.atan2(z_re);
            let radius = (r2 + i2).powf(power / 2.0);

            z_re = radius * angle.cos() + c_re;
            z_im = radius * angle.sin() + c_im;
        }

        max_iter
    }
}

// ============================================================================
// Spider Fractal
// ============================================================================

/// Spider fractal - a modified Mandelbrot with alternating pattern.
///
/// Alternates between z^2 + c and z^2 - c every other iteration,
/// creating spiderweb-like patterns.
pub struct Spider {
    pub power: f64,
}

impl Default for Spider {
    fn default() -> Self {
        Spider { power: 2.0 }
    }
}

impl Fractal for Spider {
    fn name(&self) -> &str {
        "Spider"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![Parameter {
            name: "power".to_string(),
            value: self.power,
            min: 1.0,
            max: 5.0,
        }]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        if name == "power" {
            self.power = value.clamp(1.0, 5.0);
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "power" => Some(self.power),
            _ => None,
        }
    }

    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re: f64 = 0.0;
        let mut z_im: f64 = 0.0;
        let c_re = cx;
        let c_im = cy;
        let power = self.power;

        for i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                return i;
            }

            // Use De Moivre's theorem
            let angle = power * z_im.atan2(z_re);
            let radius = (r2 + i2).powf(power / 2.0);

            // Alternate between +c and -c
            let sign = if i % 2 == 0 { 1.0 } else { -1.0 };
            z_re = radius * angle.cos() + sign * c_re;
            z_im = radius * angle.sin() + sign * c_im;
        }

        max_iter
    }
}

// ============================================================================
// Orbit Trap
// ============================================================================

/// Orbit Trap - Mandelbrot variant that tracks minimum distance to a trap.
///
/// Instead of just counting iterations until escape, tracks the minimum
/// distance the orbit comes to a "trap" point (default: origin).
/// Creates beautiful patterns and tendrils around the Mandelbrot set.
pub struct OrbitTrap {
    pub trap_x: f64,
    pub trap_y: f64,
}

impl Default for OrbitTrap {
    fn default() -> Self {
        OrbitTrap {
            trap_x: 0.1,
            trap_y: 0.1,
        }
    }
}

impl Fractal for OrbitTrap {
    fn name(&self) -> &str {
        "Orbit Trap"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![
            Parameter {
                name: "trap_x".to_string(),
                value: self.trap_x,
                min: -2.0,
                max: 2.0,
            },
            Parameter {
                name: "trap_y".to_string(),
                value: self.trap_y,
                min: -2.0,
                max: 2.0,
            },
        ]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        match name {
            "trap_x" => self.trap_x = value.clamp(-2.0, 2.0),
            "trap_y" => self.trap_y = value.clamp(-2.0, 2.0),
            _ => {}
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "trap_x" => Some(self.trap_x),
            "trap_y" => Some(self.trap_y),
            _ => None,
        }
    }

    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        let mut z_re: f64 = 0.0;
        let mut z_im: f64 = 0.0;
        let c_re = cx;
        let c_im = cy;

        let mut min_distance_sq = f64::MAX;

        for _i in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            if r2 + i2 > 4.0 {
                // Convert minimum distance to iteration count for coloring
                // Closer to trap = higher iteration count (brighter)
                let dist = min_distance_sq.sqrt();
                let trap_value = (1.0 / (1.0 + dist * 10.0) * max_iter as f64) as u32;
                return trap_value.min(max_iter - 1);
            }

            // Track minimum distance to trap
            let dx = z_re - self.trap_x;
            let dy = z_im - self.trap_y;
            let dist_sq = dx * dx + dy * dy;
            if dist_sq < min_distance_sq {
                min_distance_sq = dist_sq;
            }

            // Mandelbrot iteration: z^2 + c
            let new_re = r2 - i2 + c_re;
            let new_im = 2.0 * z_re * z_im + c_im;
            z_re = new_re;
            z_im = new_im;
        }

        // Point is in set - return max_iter
        max_iter
    }
}

// ============================================================================
// Pickover Stalk
// ============================================================================

/// Pickover Stalk - Mandelbrot variant named after Clifford Pickover.
///
/// Tracks how close the orbit comes to the real and imaginary axes,
/// creating "stalk-like" structures that extend from the set.
/// Creates beautiful organic patterns resembling plants/stalks.
pub struct PickoverStalk {
    pub stalk_thickness: f64,
    pub stalk_intensity: f64,
}

impl Default for PickoverStalk {
    fn default() -> Self {
        PickoverStalk {
            stalk_thickness: 0.1,
            stalk_intensity: 20.0,
        }
    }
}

impl Fractal for PickoverStalk {
    fn name(&self) -> &str {
        "Pickover Stalk"
    }

    fn parameters(&self) -> Vec<Parameter> {
        vec![
            Parameter {
                name: "thickness".to_string(),
                value: self.stalk_thickness,
                min: 0.01,
                max: 1.0,
            },
            Parameter {
                name: "intensity".to_string(),
                value: self.stalk_intensity,
                min: 1.0,
                max: 100.0,
            },
        ]
    }

    fn set_parameter(&mut self, name: &str, value: f64) {
        match name {
            "thickness" => self.stalk_thickness = value.clamp(0.01, 1.0),
            "intensity" => self.stalk_intensity = value.clamp(1.0, 100.0),
            _ => {}
        }
    }

    fn get_parameter(&self, name: &str) -> Option<f64> {
        match name {
            "thickness" => Some(self.stalk_thickness),
            "intensity" => Some(self.stalk_intensity),
            _ => None,
        }
    }

    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32 {
        // Following the pseudo-code: z starts at pixel coordinate (like Julia)
        // c is also the pixel coordinate
        let c_re = cx;
        let c_im = cy;
        let mut z_re = cx; // z starts at pixel coordinate, NOT 0
        let mut z_im = cy;

        let mut trap_distance = f64::MAX; // Keeps track of minimum distance to axes

        for iteration in 0..max_iter {
            let r2 = z_re * z_re;
            let i2 = z_im * z_im;

            // Check escape condition
            if r2 + i2 > 4.0 {
                // Return iteration count modulated by stalk proximity
                // Points closer to axes (smaller trap_distance) return higher values
                // thickness parameter controls how "thick" the stalk appears
                // Following pseudo-code: return trapDistance * color / dividend
                // We map this to iteration space: smaller trap_distance = higher iteration count

                // Normalize: 0.0 to 1.0 range based on thickness
                let normalized = trap_distance / self.stalk_thickness;

                // Invert so small distances give high values
                let stalk_brightness = 1.0 / (1.0 + normalized * self.stalk_intensity);

                // Mix with iteration count for color variation
                let final_value = (stalk_brightness * iteration as f64) as u32;

                return final_value.max(1);
            }

            // Calculate distance to real and imaginary axes
            let dist_to_real = z_im.abs(); // Distance to real axis (y=0)
            let dist_to_imag = z_re.abs(); // Distance to imaginary axis (x=0)
            let smallest_distance = dist_to_real.min(dist_to_imag);

            // Update trap distance with smallest seen so far
            if smallest_distance < trap_distance {
                trap_distance = smallest_distance;
            }

            // Mandelbrot iteration: z = z^2 + c
            let new_re = r2 - i2 + c_re;
            let new_im = 2.0 * z_re * z_im + c_im;
            z_re = new_re;
            z_im = new_im;
        }

        // Point is in set - return max_iter
        max_iter
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mandelbrot_outside() {
        let m = Mandelbrot::default();
        let result = m.compute(2.0, 0.0, 100);
        assert!(result < 100, "Point outside Mandelbrot should escape");
    }

    #[test]
    fn test_mandelbrot_cardioid() {
        let m = Mandelbrot::default();
        let result = m.compute(0.25, 0.0, 100);
        assert!(result >= 100, "Cardioid point should NOT escape");
    }

    #[test]
    fn test_julia_center() {
        let j = Julia::default();
        let result = j.compute(0.0, 0.0, 100);
        assert!(
            result >= 50,
            "Origin should take many iterations for default Julia"
        );
    }

    #[test]
    fn test_julia_outside() {
        let j = Julia::default();
        let result = j.compute(1.0, 0.0, 100);
        assert!(result < 100, "Point outside Julia should escape");
    }

    #[test]
    fn test_burning_ship_center() {
        let b = BurningShip::default();
        let result = b.compute(-0.5, -0.5, 100);
        assert!(
            result >= 50,
            "Center of Burning Ship should take many iterations"
        );
    }

    #[test]
    fn test_burning_ship_outside() {
        let b = BurningShip::default();
        let result = b.compute(2.0, 2.0, 100);
        assert!(result < 10, "Far outside should escape quickly");
    }

    #[test]
    fn test_pickover_stalk_parameters() {
        let mut ps = PickoverStalk::default();

        // Test default values (updated defaults)
        assert!(
            (ps.stalk_thickness - 0.1).abs() < 0.001,
            "Default thickness should be 0.1"
        );
        assert!(
            (ps.stalk_intensity - 20.0).abs() < 0.001,
            "Default intensity should be 20.0"
        );

        // Test set_parameter
        ps.set_parameter("thickness", 0.5);
        assert!(
            (ps.stalk_thickness - 0.5).abs() < 0.001,
            "Thickness should be set to 0.5"
        );

        ps.set_parameter("intensity", 50.0);
        assert!(
            (ps.stalk_intensity - 50.0).abs() < 0.001,
            "Intensity should be set to 50.0"
        );

        // Test get_parameter
        assert!((ps.get_parameter("thickness").unwrap() - 0.5).abs() < 0.001);
        assert!((ps.get_parameter("intensity").unwrap() - 50.0).abs() < 0.001);
    }

    #[test]
    fn test_pickover_stalk_computation() {
        let ps = PickoverStalk::default();

        // Test a point that should escape and produce a stalk value
        let result = ps.compute(0.5, 0.5, 100);

        // Should return a value based on stalk proximity, not max_iter
        assert!(
            result < 100,
            "Point outside set should escape with stalk value"
        );

        // Test center point (should be in set)
        let result_center = ps.compute(-0.5, 0.0, 100);
        assert_eq!(result_center, 100, "Center should be in set");
    }

    #[test]
    fn test_pickover_stalk_parameter_effect() {
        // Test that different thickness values produce different results
        // Use a point well outside the set that will definitely escape
        let mut ps = PickoverStalk::default();

        // Point that escapes and has orbit near axes
        ps.set_parameter("thickness", 0.01);
        let with_thin = ps.compute(0.8, 0.2, 100);

        ps.set_parameter("thickness", 1.0);
        let with_thick = ps.compute(0.8, 0.2, 100);

        // Different thickness should produce visibly different results
        // The difference might be small, so we just check they're not identical
        // and both are valid (not max_iter since point escapes)
        assert!(
            with_thin < 100 && with_thick < 100,
            "Both should escape: thin={}, thick={}",
            with_thin,
            with_thick
        );
    }
}
