"""Fractal base classes and registry system."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class FractalBase(ABC):
    """Base class for all fractal implementations."""
    
    name: str = "Base Fractal"
    description: str = "Base fractal class"
    parameters: Dict[str, Any] = {}
    
    @abstractmethod
    def get_default_bounds(self) -> Dict[str, float]:
        """Return default bounds for the fractal."""
        pass
    
    @abstractmethod
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute a single pixel value."""
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.parameters.copy()
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set parameters."""
        pass


class FractalRegistry:
    """Registry for fractal classes."""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str):
        """Decorator to register a fractal class."""
        def decorator(fractal_class):
            cls._registry[name] = fractal_class
            return fractal_class
        return decorator
    
    @classmethod
    def get(cls, name: str) -> type:
        """Get a fractal class by name."""
        return cls._registry[name]
    
    @classmethod
    def get_all(cls) -> Dict[str, type]:
        """Get all registered fractals."""
        return cls._registry.copy()


def register_fractal(name: str):
    """Convenience function to register a fractal."""
    def decorator(fractal_class):
        FractalRegistry._registry[name] = fractal_class
        return fractal_class
    return decorator


__all__ = ['FractalBase', 'FractalRegistry', 'register_fractal']
