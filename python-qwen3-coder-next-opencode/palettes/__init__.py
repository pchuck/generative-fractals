"""Palette base classes and registry system."""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any


class PaletteBase(ABC):
    """Base class for all color palettes."""
    
    name: str = "Base Palette"
    description: str = "Base palette class"
    
    @abstractmethod
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        """Return RGB color for a given value."""
        pass


class PaletteRegistry:
    """Registry for palette classes."""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str):
        """Decorator to register a palette class."""
        def decorator(palette_class):
            cls._registry[name] = palette_class
            return palette_class
        return decorator
    
    @classmethod
    def get(cls, name: str) -> type:
        """Get a palette class by name."""
        return cls._registry[name]
    
    @classmethod
    def get_all(cls) -> Dict[str, type]:
        """Get all registered palettes."""
        return cls._registry.copy()


def register_palette(name: str):
    """Convenience function to register a palette."""
    return PaletteRegistry.register(name)


__all__ = ['PaletteBase', 'PaletteRegistry', 'register_palette']
