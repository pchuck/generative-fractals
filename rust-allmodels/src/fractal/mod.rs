#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub enum FractalType {
    #[default]
    Mandelbrot,
    Julia,
}

#[derive(Debug, Clone)]
pub struct Parameter {
    pub name: String,
    pub value: f64,
    pub min: f64,
    pub max: f64,
}

#[allow(dead_code)]
pub trait Fractal: Send + Sync {
    fn name(&self) -> &str;
    fn parameters(&self) -> Vec<Parameter>;
    fn set_parameter(&mut self, name: &str, value: f64);
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

pub fn create_fractal(fractal_type: FractalType) -> Box<dyn Fractal> {
    match fractal_type {
        FractalType::Mandelbrot => Box::new(Mandelbrot::default()),
        FractalType::Julia => Box::new(Julia::default()),
    }
}
