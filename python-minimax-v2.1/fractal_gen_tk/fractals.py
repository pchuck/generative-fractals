"""
Modular fractal types for the fractal generator.
Add new fractal types by creating classes that inherit from FractalType.

FractalFactory Registration/Lookup Rules:
-----------------------------------------
  - list_types(): Returns display names (e.g., "Julia³")
  - create(name): Accepts display name or internal key, case-insensitive
    Examples: "Mandelbrot", "julia", "burning_ship" all work
    Invalid names fall back to Mandelbrot for robustness
  - register(name, class): Registers with normalized internal key (lowercase,
    ³→3, spaces→underscores). Display name is derived from class.name property

Duck-typing Interface Summary:
------------------------------
When switching between fractals, certain attributes are checked:

  - hasattr(fractal, 'set_c'): Julia, Julia³, Phoenix have configurable c parameter
  - hasattr(fractal, 'z0'):     Julia and Julia³ support z0 starting coordinate offset
  - hasattr(fractal, 'power'):  Multibrot uses variable exponent (Phoenix also has .p)
  - isinstance(fractal, Phoenix): Special handling for Phoenix's p parameter

When adding new fractals:
  - Implement the calculate() method returning iteration counts (max_iter = bounded)
  - Use FractalFactory.register('internal_key', MyFractalClass) to add
"""

from abc import ABC, abstractmethod
import numpy as np


class FractalType(ABC):
    """Abstract base class for fractal types.
    
    All fractals must implement:
      - name: display name property
      - calculate(): returns iteration count array (max_iter = bounded)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of this fractal type."""
        pass
    
    @abstractmethod
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        """
        Calculate the iteration counts for each point.
        
        Args:
            x, y: 2D coordinate arrays from meshgrid
            max_iter: maximum number of iterations
            
        Returns:
            Array of iteration counts (shape matches input).
            Values range from 1 to max_iter; max_iter indicates "did not escape".
        """
        pass


class Mandelbrot(FractalType):
    """Mandelbrot set fractal."""
    
    ESCAPE_RADIUS = 2.0
    
    @property
    def name(self) -> str:
        return "Mandelbrot"
    
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        c = x + 1j * y
        z = np.zeros_like(c)
        # Initialize with max_iter (bounded points), will be overwritten for escaped ones
        div_time = np.full(z.shape, max_iter, dtype=np.int32)
        
        for i in range(max_iter):
            mask = np.abs(z) <= self.ESCAPE_RADIUS
            if not np.any(mask):
                break
            
            z[mask] = z[mask] ** 2 + c[mask]
            
            escaped_mask = mask & (np.abs(z) > self.ESCAPE_RADIUS)
            div_time[escaped_mask] = i
        
        return div_time


class Julia(FractalType):
    """Julia set fractal with configurable parameter and starting coordinates."""
    
    ESCAPE_RADIUS = 2.0
    
    def __init__(self, c_real: float = -0.7, c_imag: float = 0.27015,
                 z0_real: float = 0.0, z0_imag: float = 0.0):
        self.c = complex(c_real, c_imag)
        self.z0 = complex(z0_real, z0_imag)
    
    @property
    def name(self) -> str:
        return f"Julia (c={self.c.real:.2f}+{self.c.imag:.2f}i)"
    
    def set_c(self, real: float, imag: float):
        """Set the Julia set constant c."""
        self.c = complex(real, imag)
    
    def set_z0(self, real: float, imag: float):
        """Set the starting coordinate z0."""
        self.z0 = complex(real, imag)
    
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        # Start from z0 instead of origin
        z = (x + 1j * y) + self.z0
        div_time = np.full(z.shape, max_iter, dtype=np.int32)
        
        for i in range(max_iter):
            mask = np.abs(z) <= self.ESCAPE_RADIUS
            if not np.any(mask):
                break
            
            z[mask] = z[mask] ** 2 + self.c
            
            escaped_mask = mask & (np.abs(z) > self.ESCAPE_RADIUS)
            div_time[escaped_mask] = i
        
        return div_time


class Julia3(FractalType):
    """Julia set with c^3 iteration (cubic), configurable parameter and starting coordinates."""
    
    ESCAPE_RADIUS = 2.0
    
    def __init__(self, real: float = -0.65, imag: float = 0.5,
                 z0_real: float = 0.5, z0_imag: float = 0.0):
        self.c = complex(real, imag)
        self.z0 = complex(z0_real, z0_imag)
    
    @property
    def name(self) -> str:
        return f"Julia³ (c={self.c.real:.2f}+{self.c.imag:.2f}i)"
    
    def set_c(self, real: float, imag: float):
        """Set the Julia set constant c."""
        self.c = complex(real, imag)
    
    def set_z0(self, real: float, imag: float):
        """Set the starting coordinate z0."""
        self.z0 = complex(real, imag)
    
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        # Start from z0 instead of origin
        z = (x + 1j * y) + self.z0
        div_time = np.full(z.shape, max_iter, dtype=np.int32)
        
        for i in range(max_iter):
            mask = np.abs(z) <= self.ESCAPE_RADIUS
            if not np.any(mask):
                break
            
            # Cubic iteration: z³ + c
            z[mask] = (z[mask] ** 3) + self.c
            
            escaped_mask = mask & (np.abs(z) > self.ESCAPE_RADIUS)
            div_time[escaped_mask] = i
        
        return div_time


class BurningShip(FractalType):
    """Burning Ship fractal."""
    
    ESCAPE_RADIUS = 2.0
    
    @property
    def name(self) -> str:
        return "Burning Ship"
    
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        # Burning Ship: z starts at 0, c is the coordinate
        c = x + 1j * y
        z = np.zeros_like(c)
        div_time = np.full(z.shape, max_iter, dtype=np.int32)
        
        for i in range(max_iter):
            mask = np.abs(z) <= self.ESCAPE_RADIUS
            if not np.any(mask):
                break
            
            # Apply absolute value to both real and imaginary parts of z before squaring
            z[mask] = (np.abs(np.real(z[mask])) + 1j * np.abs(np.imag(z[mask]))) ** 2 + c[mask]
            
            escaped_mask = mask & (np.abs(z) > self.ESCAPE_RADIUS)
            div_time[escaped_mask] = i
        
        return div_time


class Collatz(FractalType):
    """Collatz (Hailstone) fractal based on the 3n+1 conjecture."""
    
    ESCAPE_RADIUS = 1000
    
    @property
    def name(self) -> str:
        return "Collatz"
    
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        # Collatz iteration for complex z (uses same pattern as other fractals)
        # Uses continuous generalization: f(z) = (1 + 4*z - (1 - 2*z)*cos(pi*z)) / 3
        z = x + 1j * y  # Note: use 'z' like other fractals, not 'c'
        div_time = np.full(z.shape, max_iter, dtype=np.int32)
        
        for i in range(max_iter):
            mask = np.abs(z) <= self.ESCAPE_RADIUS
            if not np.any(mask):
                break
            
            # Collatz function: f(z) = (1 + 4*z - (1 - 2*z)*cos(pi*z)) / 3
            with np.errstate(invalid='ignore', over='ignore'):
                z[mask] = (1 + 4 * z[mask] - (1 - 2 * z[mask]) * np.cos(np.pi * z[mask])) / 3
            
            # Mark points that escaped this iteration
            escaped_mask = mask & (np.abs(z) > self.ESCAPE_RADIUS)
            div_time[escaped_mask] = i
        
        return div_time


class Multibrot(FractalType):
    """Multibrot set: z^n + c for arbitrary real exponent n."""
    
    ESCAPE_RADIUS = 2.0
    
    def __init__(self, power: float = 4.0):
        self.power = power
    
    @property
    def name(self) -> str:
        return f"Multibrot (z^{self.power})"
    
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        c = x + 1j * y
        z = np.zeros_like(c)
        div_time = np.full(z.shape, max_iter, dtype=np.int32)
        
        for i in range(max_iter):
            mask = np.abs(z) <= self.ESCAPE_RADIUS
            if not np.any(mask):
                break
            
            # z^n using complex exponentiation: z^power = exp(power * log(z))
            with np.errstate(divide='ignore', invalid='ignore'):
                z[mask] = np.power(z[mask], self.power)
            
            z[mask] += c[mask]
            
            escaped_mask = mask & (np.abs(z) > self.ESCAPE_RADIUS)
            div_time[escaped_mask] = i
        
        return div_time


class Phoenix(FractalType):
    """Phoenix fractal: z_{n+1} = z_n^2 + c + p * z_{n-1}."""
    
    ESCAPE_RADIUS = 2.0
    
    def __init__(self, real: float = -1.0, imag: float = 0.2, p: float = 1.0):
        self.c = complex(real, imag)
        self.p = p
    
    @property
    def name(self) -> str:
        return f"Phoenix (c={self.c.real:.2f}{self.c.imag:+.2f}i)"
    
    def set_c(self, real: float, imag: float):
        """Set the c parameter."""
        self.c = complex(real, imag)
    
    def calculate(self, x: np.ndarray, y: np.ndarray, max_iter: int) -> np.ndarray:
        # z_n is the pixel coordinate as initial value
        z_prev = np.zeros_like(x + 1j * y)  # z_{n-1} starts at 0
        z = x + 1j * y  # z_0 is the pixel coordinate
        div_time = np.full(z.shape, max_iter, dtype=np.int32)
        
        for i in range(max_iter):
            mask = np.abs(z) <= self.ESCAPE_RADIUS
            if not np.any(mask):
                break
            
            # Phoenix iteration: z_{n+1} = z_n^2 + c + p * z_{n-1}
            z_prev[mask] = z[mask]
            z[mask] = z[mask] ** 2 + self.c + self.p * z_prev[mask]
            
            escaped_mask = mask & (np.abs(z) > self.ESCAPE_RADIUS)
            div_time[escaped_mask] = i
        
        return div_time


class FractalFactory:
    """Factory for creating fractal type instances."""
    
    _fractals: dict[str, type[FractalType]] = {
        "mandelbrot": Mandelbrot,
        "julia": Julia,
        "julia3": Julia3,
        "burning_ship": BurningShip,
        "collatz": Collatz,
        "multibrot": Multibrot,
        "phoenix": Phoenix,
    }
    
    # Maps display names from list_types() to internal keys
    _display_to_key: dict[str, str] = {
        "Mandelbrot": "mandelbrot",
        "Julia": "julia",
        "Julia³": "julia3",
        "Burning Ship": "burning_ship",
        "Collatz": "collatz",
        "Multibrot": "multibrot",
        "Phoenix": "phoenix",
    }
    
    @classmethod
    def list_types(cls) -> list[str]:
        """Return list of available fractal type names."""
        return list(cls._display_to_key.keys())
    
    @classmethod
    def create(cls, name: str | None = None) -> FractalType:
        """Create a fractal instance by name (case-insensitive).
        
        Args:
            name: Fractal display name or internal key.
                  Examples: "Mandelbrot", "Julia³", "julia", "burning_ship"
                  If None, returns Mandelbrot.
            
        Returns:
            New fractal instance of the specified type
        """
        if name is None:
            return cls._fractals["mandelbrot"]()
        
        # Try display name mapping first, then normalized key lookup
        key = cls._display_to_key.get(name) or cls._normalize_name(name)
        
        fractal_class = cls._fractals.get(key)
        if fractal_class is None:
            # Fall back to Mandelbrot for robustness (e.g., invalid keys from UI)
            return cls._fractals["mandelbrot"]()
        
        return fractal_class()
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize name for internal key lookup.
        
        Converts display names to lowercase, replaces special chars with underscores.
        Examples: "Julia³" → "julia3", "Burning Ship" → "burning_ship"
        """
        return name.lower().replace("³", "3").replace(" ", "_")
    
    @classmethod
    def register(cls, name: str, fractal_class: type[FractalType]):
        """Register a new fractal type.
        
        Args:
            name: Internal key for the fractal (will be normalized).
                  Example: "my_fractal" or "My Fractal"
            fractal_class: Class inheriting from FractalType
        
        The key is normalized via _normalize_name() before storage.
        Display names are derived from fractal_class.name property.
        """
        normalized = cls._normalize_name(name)
        cls._fractals[normalized] = fractal_class
        # Also add to display mapping if not already present
        display_name = getattr(fractal_class, 'name', str(fractal_class.__name__))
        if display_name not in cls._display_to_key:
            cls._display_to_key[display_name] = normalized