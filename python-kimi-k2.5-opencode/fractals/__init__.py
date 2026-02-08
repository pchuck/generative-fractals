#!/usr/bin/env python3
"""
Fractal algorithms base module.
Each fractal should inherit from FractalBase and implement compute_pixel().
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional, Type


class FractalBase(ABC):
    """Base class for all fractal implementations."""
    
    # Class attributes - override in subclasses
    name: str = "Base Fractal"
    description: str = "Base fractal class"
    parameters: Dict[str, Dict[str, Any]] = {}  # Parameter definitions
    
    def __init__(self, **params):
        """Initialize with parameters."""
        self.params = params
    
    @abstractmethod
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """
        Compute a single pixel value.
        
        Args:
            x, y: Coordinates in the complex plane
            max_iter: Maximum iterations
            
        Returns:
            Iteration count (float for smooth coloring)
        """
        pass
    
    def get_default_bounds(self) -> Dict[str, float]:
        """Return default viewport bounds."""
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def get_params(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.params
    
    def set_params(self, **params):
        """Update parameters."""
        self.params.update(params)


class FractalRegistry:
    """Registry for fractal implementations."""
    
    _fractals: Dict[str, Type[FractalBase]] = {}
    
    @classmethod
    def register(cls, name: str, fractal_class: Type[FractalBase]):
        """Register a fractal implementation."""
        if not issubclass(fractal_class, FractalBase):
            raise ValueError(f"Fractal must inherit from FractalBase: {fractal_class}")
        cls._fractals[name] = fractal_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[FractalBase]]:
        """Get a fractal class by name."""
        return cls._fractals.get(name)
    
    @classmethod
    def list_fractals(cls) -> list:
        """List all registered fractal names."""
        return sorted(cls._fractals.keys())
    
    @classmethod
    def create(cls, name: str, **params) -> FractalBase:
        """Create a fractal instance."""
        fractal_class = cls.get(name)
        if fractal_class is None:
            raise ValueError(f"Unknown fractal: {name}")
        return fractal_class(**params)


# Decorator for easy registration
def register_fractal(name: str):
    """Decorator to register a fractal implementation."""
    def decorator(cls):
        FractalRegistry.register(name, cls)
        cls.name = name
        return cls
    return decorator


# Utility function for parsing complex numbers
def parse_complex_string(s: str) -> complex:
    """Parse a complex number from string.
    
    Args:
        s: String representation of complex number (e.g., "-0.7+0.27j", "0.5", "1+2i")
        
    Returns:
        complex: Parsed complex number
    """
    s = s.replace(" ", "").replace("i", "j").lower()
    if s.endswith("j") and not any(c in s for c in "+-"):
        s = s[:-1]
    return complex(s)
