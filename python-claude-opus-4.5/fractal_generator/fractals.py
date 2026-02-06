"""
Fractal type definitions and factory.

Each fractal implements a calculate method that determines
how many iterations before a point escapes to infinity.
"""

import math
from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, Tuple

import numpy as np


class FractalType(ABC):
    """Base class for all fractal types."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for the fractal."""
        pass
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        """Default view bounds (x_min, x_max, y_min, y_max)."""
        return (-2.5, 1.0, -1.5, 1.5)
    
    @property
    def parameters(self) -> Dict[str, any]:
        """Return configurable parameters for this fractal."""
        return {}
    
    def set_parameter(self, name: str, value: any) -> None:
        """Set a configurable parameter."""
        pass
    
    @abstractmethod
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        """
        Calculate the iteration count for a point.
        
        Args:
            x: Real component of the complex coordinate
            y: Imaginary component of the complex coordinate
            max_iter: Maximum iterations before considering point bounded
            
        Returns:
            Number of iterations before escape, or max_iter if bounded
        """
        pass
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """
        Calculate iteration counts for arrays of points (NumPy-accelerated).
        
        Args:
            x: 2D array of real components
            y: 2D array of imaginary components
            max_iter: Maximum iteration count
            
        Returns:
            2D array of iteration counts
        """
        # Default implementation falls back to per-pixel calculation
        # Subclasses should override for vectorized computation
        result = np.zeros(x.shape, dtype=np.int32)
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                result[i, j] = self.calculate(x[i, j], y[i, j], max_iter)
        return result


class MandelbrotFractal(FractalType):
    """The classic Mandelbrot set: z = z² + c where c is the pixel coordinate."""
    
    @property
    def name(self) -> str:
        return "Mandelbrot"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.5, 1.0, -1.5, 1.5)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                return i
            
            z_imag = 2.0 * z_real * z_imag + c_imag
            z_real = z_real_sq - z_imag_sq + c_real
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Mandelbrot calculation using NumPy."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            z[mask] = z[mask] * z[mask] + c[mask]
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class JuliaFractal(FractalType):
    """Julia set: z = z² + c where c is a constant parameter."""
    
    def __init__(self):
        self._c_real = -0.7
        self._c_imag = 0.27015
        self._z0_real = 0.0
        self._z0_imag = 0.0
    
    @property
    def name(self) -> str:
        return "Julia"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.0, 2.0, -1.5, 1.5)
    
    @property
    def parameters(self) -> Dict[str, any]:
        return {
            'c_real': self._c_real,
            'c_imag': self._c_imag,
            'z0_real': self._z0_real,
            'z0_imag': self._z0_imag,
        }
    
    def set_parameter(self, name: str, value: any) -> None:
        if name == 'c_real':
            self._c_real = float(value)
        elif name == 'c_imag':
            self._c_imag = float(value)
        elif name == 'z0_real':
            self._z0_real = float(value)
        elif name == 'z0_imag':
            self._z0_imag = float(value)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        z_real = x + self._z0_real
        z_imag = y + self._z0_imag
        c_real, c_imag = self._c_real, self._c_imag
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                return i
            
            z_imag = 2.0 * z_real * z_imag + c_imag
            z_real = z_real_sq - z_imag_sq + c_real
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Julia calculation using NumPy."""
        c = complex(self._c_real, self._c_imag)
        z = (x + self._z0_real) + 1j * (y + self._z0_imag)
        result = np.full(x.shape, max_iter, dtype=np.int32)
        mask = np.ones(x.shape, dtype=bool)
        
        for i in range(max_iter):
            z[mask] = z[mask] * z[mask] + c
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class MultibrotFractal(FractalType):
    """Multibrot set: z = z^n + c with configurable exponent n."""
    
    def __init__(self):
        self._exponent = 3
    
    @property
    def name(self) -> str:
        return "Multibrot"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.0, 2.0, -1.75, 1.75)
    
    @property
    def parameters(self) -> Dict[str, any]:
        return {'exponent': self._exponent}
    
    def set_parameter(self, name: str, value: any) -> None:
        if name == 'exponent':
            self._exponent = int(value)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        n = self._exponent
        
        for i in range(max_iter):
            # Convert to polar for exponentiation
            r_sq = z_real * z_real + z_imag * z_imag
            
            if r_sq > 4.0:
                return i
            
            if r_sq == 0:
                z_real, z_imag = c_real, c_imag
                continue
            
            # z^n using polar form
            r = math.sqrt(r_sq)
            theta = math.atan2(z_imag, z_real)
            
            r_n = r ** n
            theta_n = theta * n
            
            z_real = r_n * math.cos(theta_n) + c_real
            z_imag = r_n * math.sin(theta_n) + c_imag
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Multibrot calculation using NumPy."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        n = self._exponent
        
        for i in range(max_iter):
            z[mask] = z[mask] ** n + c[mask]
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class BurningShipFractal(FractalType):
    """
    Burning Ship fractal: z_{n+1} = (|Re(z_n)| + i|Im(z_n)|)² + c
    
    Standard formula: take absolute values of real and imaginary parts
    of z BEFORE squaring, then add c.
    """
    
    @property
    def name(self) -> str:
        return "Burning Ship"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.5, 1.5, -2.0, 1.0)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        
        for i in range(max_iter):
            if z_real * z_real + z_imag * z_imag > 4.0:
                return i
            
            # Take absolute values BEFORE squaring
            az_real = abs(z_real)
            az_imag = abs(z_imag)
            
            # Now square: (|zr| + i|zi|)^2 = |zr|^2 - |zi|^2 + 2i|zr||zi|
            new_real = az_real * az_real - az_imag * az_imag + c_real
            new_imag = 2.0 * az_real * az_imag + c_imag
            z_real = new_real
            z_imag = new_imag
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Burning Ship calculation using NumPy."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            # Take absolute values of real and imaginary parts BEFORE squaring
            z_abs = np.abs(z.real) + 1j * np.abs(z.imag)
            z[mask] = z_abs[mask] ** 2 + c[mask]
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class PhoenixFractal(FractalType):
    """Phoenix fractal: z_{n+1} = z_n² + c + p * z_{n-1}."""
    
    def __init__(self):
        self._c_real = 0.5667
        self._c_imag = 0.0
        self._p_real = -0.5
        self._p_imag = 0.0
    
    @property
    def name(self) -> str:
        return "Phoenix"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.0, 2.0, -1.5, 1.5)
    
    @property
    def parameters(self) -> Dict[str, any]:
        return {
            'c_real': self._c_real,
            'c_imag': self._c_imag,
            'p_real': self._p_real,
            'p_imag': self._p_imag,
        }
    
    def set_parameter(self, name: str, value: any) -> None:
        if name == 'c_real':
            self._c_real = float(value)
        elif name == 'c_imag':
            self._c_imag = float(value)
        elif name == 'p_real':
            self._p_real = float(value)
        elif name == 'p_imag':
            self._p_imag = float(value)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        # Initial z is the pixel coordinate (like Julia)
        z_real, z_imag = x, y
        z_prev_real, z_prev_imag = 0.0, 0.0
        
        c_real, c_imag = self._c_real, self._c_imag
        p_real, p_imag = self._p_real, self._p_imag
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                return i
            
            # p * z_prev (complex multiplication)
            pz_real = p_real * z_prev_real - p_imag * z_prev_imag
            pz_imag = p_real * z_prev_imag + p_imag * z_prev_real
            
            # Store current z as previous
            z_prev_real, z_prev_imag = z_real, z_imag
            
            # z = z² + c + p*z_prev
            new_real = z_real_sq - z_imag_sq + c_real + pz_real
            new_imag = 2.0 * z_real * z_imag + c_imag + pz_imag
            
            z_real, z_imag = new_real, new_imag
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Phoenix calculation using NumPy."""
        c = complex(self._c_real, self._c_imag)
        p = complex(self._p_real, self._p_imag)
        
        z = x + 1j * y
        z_prev = np.zeros_like(z, dtype=np.complex128)
        result = np.full(x.shape, max_iter, dtype=np.int32)
        mask = np.ones(x.shape, dtype=bool)
        
        for i in range(max_iter):
            z_new = z[mask] ** 2 + c + p * z_prev[mask]
            z_prev[mask] = z[mask]
            z[mask] = z_new
            
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class TricornFractal(FractalType):
    """Tricorn (Mandelbar) fractal: z = conj(z)² + c."""
    
    @property
    def name(self) -> str:
        return "Tricorn"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-3.0, 2.0, -2.5, 2.5)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                return i
            
            # Conjugate: flip sign of imaginary part before squaring
            z_imag = -2.0 * z_real * z_imag + c_imag
            z_real = z_real_sq - z_imag_sq + c_real
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Tricorn calculation using NumPy."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            # z = conj(z)^2 + c
            z[mask] = np.conj(z[mask]) ** 2 + c[mask]
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class CelticFractal(FractalType):
    """
    Celtic fractal: z_{n+1} = |Re(z_n²)| + i*Im(z_n²) + c
    
    Also known as "Generalized Celtic". Takes absolute value of the 
    real part AFTER squaring z.
    """
    
    @property
    def name(self) -> str:
        return "Celtic"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-3.0, 3.0, -2.0, 2.0)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                return i
            
            # Celtic: abs on the real part of z² (after squaring)
            new_real = abs(z_real_sq - z_imag_sq) + c_real
            new_imag = 2.0 * z_real * z_imag + c_imag
            z_real = new_real
            z_imag = new_imag
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Celtic calculation using NumPy."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            z_sq = z[mask] ** 2
            # Take abs of real part AFTER squaring
            z[mask] = np.abs(z_sq.real) + 1j * z_sq.imag + c[mask]
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class SineFractal(FractalType):
    """Sine fractal: z = c * sin(z), produces intricate patterns."""
    
    def __init__(self):
        self._c_real = 1.0
        self._c_imag = 0.3
    
    @property
    def name(self) -> str:
        return "Sine"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-6.0, 6.0, -5.0, 5.0)
    
    @property
    def parameters(self) -> Dict[str, any]:
        return {
            'c_real': self._c_real,
            'c_imag': self._c_imag,
        }
    
    def set_parameter(self, name: str, value: any) -> None:
        if name == 'c_real':
            self._c_real = float(value)
        elif name == 'c_imag':
            self._c_imag = float(value)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        z_real, z_imag = x, y
        c_real, c_imag = self._c_real, self._c_imag
        
        for i in range(max_iter):
            if z_real * z_real + z_imag * z_imag > 50.0:
                return i
            
            # sin(z) = sin(x)cosh(y) + i*cos(x)sinh(y)
            sin_real = math.sin(z_real) * math.cosh(z_imag)
            sin_imag = math.cos(z_real) * math.sinh(z_imag)
            
            # c * sin(z)
            z_real = c_real * sin_real - c_imag * sin_imag
            z_imag = c_real * sin_imag + c_imag * sin_real
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Sine calculation using NumPy."""
        c = complex(self._c_real, self._c_imag)
        z = x + 1j * y
        result = np.full(x.shape, max_iter, dtype=np.int32)
        mask = np.ones(x.shape, dtype=bool)
        
        for i in range(max_iter):
            z[mask] = c * np.sin(z[mask])
            escaped = mask & (np.abs(z) > 50.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class NewtonFractal(FractalType):
    """Newton fractal: Newton's method for z³ - 1 = 0. Colors by iteration count to converge."""
    
    def __init__(self):
        self._power = 3
        self._tolerance = 1e-4  # Larger tolerance for faster convergence
    
    @property
    def name(self) -> str:
        return "Newton z³-1"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.5, 2.5, -2.0, 2.0)
    
    @property
    def parameters(self) -> Dict[str, any]:
        return {'power': self._power}
    
    def set_parameter(self, name: str, value: any) -> None:
        if name == 'power':
            self._power = max(2, int(value))
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        z_real, z_imag = x, y
        n = self._power
        tol = self._tolerance
        
        # Limit iterations for Newton (converges fast or not at all)
        max_newton_iter = min(max_iter, 64)
        
        for i in range(max_newton_iter):
            r_sq = z_real * z_real + z_imag * z_imag
            
            # Escape check - point is diverging
            if r_sq > 1e10:
                return i
            
            if r_sq < 1e-12:
                return max_iter
            
            # Use complex arithmetic for simplicity
            z = complex(z_real, z_imag)
            zn = z ** n
            zn1 = z ** (n - 1)
            
            f = zn - 1.0
            fp = n * zn1
            
            if abs(fp) < 1e-12:
                return max_iter
            
            step = f / fp
            z = z - step
            z_real, z_imag = z.real, z.imag
            
            # Check convergence
            if abs(step) < tol:
                # Scale iteration to use more of the color palette
                return (i * max_iter) // max_newton_iter
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Newton calculation using NumPy."""
        z = x + 1j * y
        n = self._power
        result = np.full(x.shape, max_iter, dtype=np.int32)
        mask = np.ones(x.shape, dtype=bool)
        
        # Limit iterations for Newton
        max_newton_iter = min(max_iter, 64)
        
        for i in range(max_newton_iter):
            z_masked = z[mask]
            
            # Check for divergence
            diverged = mask & (np.abs(z) > 1e5)
            result[diverged] = (i * max_iter) // max_newton_iter
            mask[diverged] = False
            
            if not mask.any():
                break
            
            zn = z_masked ** n
            zn1 = z_masked ** (n - 1)
            
            f = zn - 1.0
            fp = n * zn1
            
            # Avoid division by zero
            fp_safe = np.where(np.abs(fp) < 1e-12, 1.0, fp)
            step = f / fp_safe
            z[mask] = z[mask] - step
            
            # Check convergence
            converged = mask & (np.abs(step) < self._tolerance)
            result[converged] = (i * max_iter) // max_newton_iter
            mask[converged] = False
            
            if not mask.any():
                break
        
        return result


class PerpendicularMandelbrotFractal(FractalType):
    """
    Perpendicular Mandelbrot: z_{n+1} = (Re(z_n) + i|Im(z_n)|)² + c
    
    Takes absolute value of imaginary part BEFORE squaring.
    Part of the "Burning Ship" family of abs-variations.
    """
    
    @property
    def name(self) -> str:
        return "Perpendicular"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-3.0, 2.0, -2.0, 2.0)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        
        for i in range(max_iter):
            if z_real * z_real + z_imag * z_imag > 4.0:
                return i
            
            # Perpendicular: abs on imaginary BEFORE squaring
            az_imag = abs(z_imag)
            
            # (zr + i|zi|)^2 = zr^2 - |zi|^2 + 2i*zr*|zi|
            new_real = z_real * z_real - az_imag * az_imag + c_real
            new_imag = 2.0 * z_real * az_imag + c_imag
            z_real = new_real
            z_imag = new_imag
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Perpendicular Mandelbrot calculation."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            # abs on imaginary BEFORE squaring
            z_mod = z[mask].real + 1j * np.abs(z[mask].imag)
            z[mask] = z_mod ** 2 + c[mask]
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class BuffaloFractal(FractalType):
    """
    Buffalo fractal: z_{n+1} = |z_n²| - |z_n|² + c  (simplified)
    
    More precisely: takes abs of both real and imaginary parts of z².
    Formula: |Re(z²)| - i|Im(z²)| + c (note the negative on imaginary)
    """
    
    @property
    def name(self) -> str:
        return "Buffalo"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.5, 1.5, -2.0, 2.0)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                return i
            
            # First compute z^2 normally
            sq_real = z_real_sq - z_imag_sq
            sq_imag = 2.0 * z_real * z_imag
            
            # Buffalo: |Re(z²)| - i*|Im(z²)| + c
            z_real = abs(sq_real) + c_real
            z_imag = -abs(sq_imag) + c_imag
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Buffalo calculation."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            z_sq = z[mask] ** 2
            # Buffalo: |Re(z²)| - i*|Im(z²)| + c
            z[mask] = np.abs(z_sq.real) - 1j * np.abs(z_sq.imag) + c[mask]
            
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class OrbitTrapFractal(FractalType):
    """
    Orbit Trap fractal: Colors based on how close the orbit comes to a geometric shape.
    
    Supports multiple trap types:
    - 'circle': Distance to a circle centered at origin
    - 'cross': Distance to cross axes
    - 'point': Distance to a specific point
    - 'square': Distance to a square boundary
    """
    
    TRAP_CIRCLE = 'circle'
    TRAP_CROSS = 'cross'
    TRAP_POINT = 'point'
    TRAP_SQUARE = 'square'
    
    def __init__(self):
        self._trap_type = self.TRAP_CIRCLE
        self._trap_radius = 0.5  # For circle trap
        self._trap_x = 0.0  # For point trap
        self._trap_y = 0.0  # For point trap
        self._trap_size = 1.0  # For square trap
    
    @property
    def name(self) -> str:
        return "Orbit Trap"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.5, 1.0, -1.5, 1.5)
    
    @property
    def parameters(self) -> Dict[str, any]:
        return {
            'trap_radius': self._trap_radius,
            'trap_x': self._trap_x,
            'trap_y': self._trap_y,
        }
    
    def set_parameter(self, name: str, value: any) -> None:
        if name == 'trap_radius':
            self._trap_radius = float(value)
        elif name == 'trap_x':
            self._trap_x = float(value)
        elif name == 'trap_y':
            self._trap_y = float(value)
        elif name == 'trap_size':
            self._trap_size = float(value)
        elif name == 'trap_type':
            self._trap_type = str(value)
    
    def _distance_to_trap(self, z_real: float, z_imag: float) -> float:
        """Calculate distance from point to the trap."""
        if self._trap_type == self.TRAP_CIRCLE:
            # Distance to circle of given radius
            dist_from_origin = math.sqrt(z_real * z_real + z_imag * z_imag)
            return abs(dist_from_origin - self._trap_radius)
        elif self._trap_type == self.TRAP_CROSS:
            # Distance to x or y axis (whichever is closer)
            return min(abs(z_real), abs(z_imag))
        elif self._trap_type == self.TRAP_POINT:
            # Distance to a specific point
            dx = z_real - self._trap_x
            dy = z_imag - self._trap_y
            return math.sqrt(dx * dx + dy * dy)
        elif self._trap_type == self.TRAP_SQUARE:
            # Distance to square boundary
            return min(
                abs(abs(z_real) - self._trap_size),
                abs(abs(z_imag) - self._trap_size)
            )
        else:
            # Default to circle
            dist_from_origin = math.sqrt(z_real * z_real + z_imag * z_imag)
            return abs(dist_from_origin - self._trap_radius)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        min_distance = float('inf')
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                # Convert min_distance to iteration count for coloring
                # Scale distance to use color palette effectively
                scaled = int(min_distance * max_iter * 2)
                return min(scaled, max_iter - 1)
            
            # Track minimum distance to trap
            dist = self._distance_to_trap(z_real, z_imag)
            min_distance = min(min_distance, dist)
            
            z_imag = 2.0 * z_real * z_imag + c_imag
            z_real = z_real_sq - z_imag_sq + c_real
        
        # Point didn't escape - return based on minimum distance
        scaled = int(min_distance * max_iter * 2)
        return min(scaled, max_iter)
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Orbit Trap calculation using NumPy."""
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        min_dist = np.full(c.shape, np.inf, dtype=np.float64)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            z[mask] = z[mask] * z[mask] + c[mask]
            
            # Calculate distance to trap
            if self._trap_type == self.TRAP_CIRCLE:
                dist = np.abs(np.abs(z) - self._trap_radius)
            elif self._trap_type == self.TRAP_CROSS:
                dist = np.minimum(np.abs(z.real), np.abs(z.imag))
            elif self._trap_type == self.TRAP_POINT:
                dist = np.abs(z - complex(self._trap_x, self._trap_y))
            elif self._trap_type == self.TRAP_SQUARE:
                dist = np.minimum(
                    np.abs(np.abs(z.real) - self._trap_size),
                    np.abs(np.abs(z.imag) - self._trap_size)
                )
            else:
                dist = np.abs(np.abs(z) - self._trap_radius)
            
            # Update minimum distance for active points
            min_dist = np.where(mask, np.minimum(min_dist, dist), min_dist)
            
            # Check for escape
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = np.minimum(
                (min_dist[escaped] * max_iter * 2).astype(np.int32),
                max_iter - 1
            )
            mask[escaped] = False
            
            if not mask.any():
                break
        
        # Handle points that didn't escape
        result[mask] = np.minimum(
            (min_dist[mask] * max_iter * 2).astype(np.int32),
            max_iter
        )
        
        return result


class BuddhabrotFractal(FractalType):
    """
    Buddhabrot fractal: Density plot of escape trajectories.
    
    Unlike traditional fractals, Buddhabrot tracks the paths of escaping points
    and creates a density map. Points that visit a pixel more often result in
    brighter colors.
    
    Note: True Buddhabrot requires accumulating many random samples. This
    implementation uses a simplified per-pixel approach that approximates
    the effect by counting orbit visits.
    """
    
    def __init__(self):
        self._min_iter = 20  # Minimum iterations for a path to count
        self._sample_density = 1  # Samples per pixel (higher = better quality, slower)
    
    @property
    def name(self) -> str:
        return "Buddhabrot"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.5, 1.0, -1.5, 1.5)
    
    @property
    def parameters(self) -> Dict[str, any]:
        return {
            'min_iter': self._min_iter,
        }
    
    def set_parameter(self, name: str, value: any) -> None:
        if name == 'min_iter':
            self._min_iter = max(1, int(value))
        elif name == 'sample_density':
            self._sample_density = max(1, int(value))
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        """
        For single-point calculation, we approximate by counting how many
        times the orbit of nearby points passes through this region.
        """
        c_real, c_imag = x, y
        z_real, z_imag = 0.0, 0.0
        
        # Store the orbit
        orbit = []
        
        for i in range(max_iter):
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            if z_real_sq + z_imag_sq > 4.0:
                # Point escapes - count orbit length for coloring
                if i > self._min_iter:
                    return i
                else:
                    return 0  # Too few iterations, don't color
            
            orbit.append((z_real, z_imag))
            z_imag = 2.0 * z_real * z_imag + c_imag
            z_real = z_real_sq - z_imag_sq + c_real
        
        # Point doesn't escape - in Buddhabrot, these are typically not counted
        return 0
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """
        Vectorized Buddhabrot approximation.
        
        This creates a simplified Buddhabrot by using escape iteration count
        for escaping points, which creates a similar visual effect.
        True Buddhabrot would require trajectory accumulation.
        """
        c = x + 1j * y
        z = np.zeros_like(c, dtype=np.complex128)
        result = np.zeros(c.shape, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            z[mask] = z[mask] * z[mask] + c[mask]
            escaped = mask & (np.abs(z) > 2.0)
            
            # Only color points that escaped after min_iter iterations
            valid_escape = escaped & (i > self._min_iter)
            result[valid_escape] = i
            
            mask[escaped] = False
            
            if not mask.any():
                break
        
        # Points that never escape get 0 (black in most palettes)
        return result


class LambdaFractal(FractalType):
    """Lambda fractal: z = c * z * (1 - z), related to logistic map."""
    
    @property
    def name(self) -> str:
        return "Lambda"
    
    @property
    def default_bounds(self) -> Tuple[float, float, float, float]:
        return (-2.0, 4.0, -2.0, 2.0)
    
    def calculate(self, x: float, y: float, max_iter: int) -> int:
        c_real, c_imag = x, y
        # Start at critical point z = 0.5
        z_real, z_imag = 0.5, 0.0
        
        for i in range(max_iter):
            if z_real * z_real + z_imag * z_imag > 4.0:
                return i
            
            # (1 - z)
            one_minus_z_real = 1.0 - z_real
            one_minus_z_imag = -z_imag
            
            # z * (1 - z)
            prod_real = z_real * one_minus_z_real - z_imag * one_minus_z_imag
            prod_imag = z_real * one_minus_z_imag + z_imag * one_minus_z_real
            
            # c * z * (1 - z)
            z_real = c_real * prod_real - c_imag * prod_imag
            z_imag = c_real * prod_imag + c_imag * prod_real
        
        return max_iter
    
    def calculate_array(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """Vectorized Lambda calculation."""
        c = x + 1j * y
        z = np.full_like(c, 0.5, dtype=np.complex128)
        result = np.full(c.shape, max_iter, dtype=np.int32)
        mask = np.ones(c.shape, dtype=bool)
        
        for i in range(max_iter):
            z[mask] = c[mask] * z[mask] * (1.0 - z[mask])
            escaped = mask & (np.abs(z) > 2.0)
            result[escaped] = i
            mask[escaped] = False
            
            if not mask.any():
                break
        
        return result


class FractalFactory:
    """Factory for creating and managing fractal types."""
    
    _registry: Dict[str, Type[FractalType]] = {}
    _instances: Dict[str, FractalType] = {}
    
    @classmethod
    def register(cls, name: str, fractal_class: Type[FractalType]) -> None:
        """Register a fractal type with the factory."""
        cls._registry[name] = fractal_class
    
    @classmethod
    def create(cls, name: str) -> Optional[FractalType]:
        """Create or retrieve a fractal instance by name."""
        if name not in cls._registry:
            # Try to find by display name
            for key, fractal_class in cls._registry.items():
                instance = fractal_class()
                if instance.name == name:
                    name = key
                    break
            else:
                return None
        
        # Return cached instance to preserve parameters
        if name not in cls._instances:
            cls._instances[name] = cls._registry[name]()
        
        return cls._instances[name]
    
    @classmethod
    def get_available(cls) -> Dict[str, str]:
        """Return dict of {internal_name: display_name} for all fractals."""
        result = {}
        for name, fractal_class in cls._registry.items():
            instance = fractal_class()
            result[name] = instance.name
        return result
    
    @classmethod
    def reset_instance(cls, name: str) -> None:
        """Reset a fractal instance to default state."""
        if name in cls._instances:
            del cls._instances[name]


# Register built-in fractal types
FractalFactory.register('mandelbrot', MandelbrotFractal)
FractalFactory.register('julia', JuliaFractal)
FractalFactory.register('burning_ship', BurningShipFractal)
FractalFactory.register('tricorn', TricornFractal)
FractalFactory.register('celtic', CelticFractal)
FractalFactory.register('buffalo', BuffaloFractal)
FractalFactory.register('perpendicular', PerpendicularMandelbrotFractal)
FractalFactory.register('lambda', LambdaFractal)
FractalFactory.register('multibrot', MultibrotFractal)
FractalFactory.register('phoenix', PhoenixFractal)
FractalFactory.register('newton', NewtonFractal)
FractalFactory.register('sine', SineFractal)
FractalFactory.register('orbit_trap', OrbitTrapFractal)
FractalFactory.register('buddhabrot', BuddhabrotFractal)
