#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub enum FractalType {
    #[default]
    Mandelbrot,
    Julia,
    BurningShip,
}

#[derive(Debug, Clone)]
pub struct Parameter {
    pub name: String,
    pub value: f64,
    pub min: f64,
    pub max: f64,
}

pub trait Fractal: Send + Sync {
    #[allow(dead_code)]
    fn name(&self) -> &str;
    fn parameters(&self) -> Vec<Parameter>;
    fn set_parameter(&mut self, name: &str, value: f64);
    #[allow(dead_code)]
    fn get_parameter(&self, name: &str) -> Option<f64>;
    fn compute(&self, cx: f64, cy: f64, max_iter: u32) -> u32;
}

pub struct Mandelbrot {
    pub power: f64,
}

impl Default for Mandelbrot {
    fn default() -> Self {
        Mandelbrot { power: 2.0 }
    }
}

impl Fractal for Mandelbrot {
    fn name(&self) -> &str {
        "Mandelbrot"
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
        }

        max_iter
    }
}

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

pub struct BurningShip {
    pub power: f64,
}

impl Default for BurningShip {
    fn default() -> Self {
        BurningShip { power: 2.0 }
    }
}

impl Fractal for BurningShip {
    fn name(&self) -> &str {
        "Burning Ship"
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

pub fn create_fractal(fractal_type: FractalType) -> Box<dyn Fractal> {
    match fractal_type {
        FractalType::Mandelbrot => Box::new(Mandelbrot::default()),
        FractalType::Julia => Box::new(Julia::default()),
        FractalType::BurningShip => Box::new(BurningShip::default()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mandelbrot_center() {
        let m = Mandelbrot::default();
        let result = m.compute(-0.5, 0.0, 100);
        assert_eq!(result, 100, "Center of Mandelbrot should not escape");
    }

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
}
