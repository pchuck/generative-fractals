#!/usr/bin/env python3
"""
Color palette module.
Each palette should inherit from PaletteBase and implement get_color().
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, Tuple


class PaletteBase(ABC):
    """Base class for all color palette implementations."""
    
    # Class attributes - override in subclasses
    name: str = "Base Palette"
    description: str = "Base palette class"
    parameters: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, **params):
        """Initialize with parameters."""
        self.params = params
    
    @abstractmethod
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        """
        Get RGB color for a given iteration value.
        
        Args:
            value: Iteration count (can be float for smooth coloring)
            max_val: Maximum iteration count
            
        Returns:
            RGB tuple (r, g, b) with values 0-255
        """
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.params
    
    def set_params(self, **params):
        """Update parameters."""
        self.params.update(params)


class PaletteRegistry:
    """Registry for palette implementations."""
    
    _palettes: Dict[str, Type[PaletteBase]] = {}
    
    @classmethod
    def register(cls, name: str, palette_class: Type[PaletteBase]):
        """Register a palette implementation."""
        if not issubclass(palette_class, PaletteBase):
            raise ValueError(f"Palette must inherit from PaletteBase: {palette_class}")
        cls._palettes[name] = palette_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[PaletteBase]]:
        """Get a palette class by name."""
        return cls._palettes.get(name)
    
    @classmethod
    def list_palettes(cls) -> list:
        """List all registered palette names."""
        return sorted(cls._palettes.keys())
    
    @classmethod
    def create(cls, name: str, **params) -> PaletteBase:
        """Create a palette instance."""
        palette_class = cls.get(name)
        if palette_class is None:
            raise ValueError(f"Unknown palette: {name}")
        return palette_class(**params)


# Decorator for easy registration
def register_palette(name: str):
    """Decorator to register a palette implementation."""
    def decorator(cls):
        PaletteRegistry.register(name, cls)
        cls.name = name
        return cls
    return decorator
