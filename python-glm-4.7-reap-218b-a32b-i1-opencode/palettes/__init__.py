"""Palette base classes and registry system."""

from typing import Dict, Any, Optional


_palette_registry: Dict[str, type] = {}


class PaletteBase:
    """Base class for all color palettes."""
    
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}
    
    def __init__(self):
        self.params = self.parameters.copy()
    
    def get_color(self, value: float, max_val: float) -> tuple:
        """Get RGB color for a given iteration value.
        
        Args:
            value: Iteration count or smooth coloring value
            max_val: Maximum iteration count
            
        Returns:
            Tuple of (r, g, b) values in range 0-255
        """
        return (0, 0, 0)
    
    def set_parameter(self, name: str, value: Any) -> None:
        """Set a parameter for this palette."""
        if name in self.params:
            self.params[name] = value
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self.params.get(name, default)


def register_palette(palette_id: str):
    """Decorator to register a palette class in the registry.
    
    Args:
        palette_id: Unique identifier for this palette
        
    Returns:
        Decorator function
    """
    def decorator(cls):
        _palette_registry[palette_id] = cls
        return cls
    return decorator


def get_palette(palette_id: str) -> Optional[PaletteBase]:
    """Get an instance of a registered palette.
    
    Args:
        palette_id: Identifier of the palette to instantiate
        
    Returns:
        Palette instance or None if not found
    """
    cls = _palette_registry.get(palette_id)
    if cls:
        return cls()
    return None


def list_palettes() -> Dict[str, str]:
    """Get a dictionary of all registered palettes.
    
    Returns:
        Dictionary mapping palette IDs to their names
    """
    result = {}
    for pid, cls in _palette_registry.items():
        instance = cls()
        result[pid] = instance.name
    return result


def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
    """Convert HSV color values to RGB.
    
    Args:
        h: Hue (0-1)
        s: Saturation (0-1)
        v: Value/brightness (0-1)
        
    Returns:
        Tuple of (r, g, b) in range 0-255
    """
    import math
    
    if s == 0:
        return (int(v * 255), int(v * 255), int(v * 255))
    
    i = int(h * 6)
    f = h * 6 - i
    
    p = v * (1 - s)
    q = v * (1 - s * f)
    r_ = v * (1 - s * (1 - f))
    
    if i == 0:
        rgb = (v, r_, p)
    elif i == 1:
        rgb = (q, v, p)
    elif i == 2:
        rgb = (p, v, r_)
    elif i == 3:
        rgb = (p, q, v)
    elif i == 4:
        rgb = (r_, p, v)
    else:
        rgb = (v, p, q)
    
    return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))