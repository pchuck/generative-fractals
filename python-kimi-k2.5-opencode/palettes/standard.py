"""Standard color palette implementations."""

import colorsys
from . import PaletteBase, register_palette


@register_palette("smooth")
class SmoothPalette(PaletteBase):
    """Smooth HSV color cycling."""
    
    name = "Smooth"
    description = "Smooth HSV color cycling"
    parameters = {
        "hue": {"type": "float", "default": 0.0, "min": 0.0, "max": 1.0, "description": "Base hue"},
        "saturation": {"type": "float", "default": 0.8, "min": 0.0, "max": 1.0, "description": "Saturation"},
        "value": {"type": "float", "default": 0.9, "min": 0.0, "max": 1.0, "description": "Brightness"}
    }
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        hue = (self.params.get("hue", 0.0) + value / max_val) % 1.0
        sat = self.params.get("saturation", 0.8)
        val = self.params.get("value", 0.9)
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return (int(r * 255), int(g * 255), int(b * 255))


@register_palette("banded")
class BandedPalette(PaletteBase):
    """Banded color palette."""
    
    name = "Banded"
    description = "Discrete color bands"
    parameters = {
        "bands": {"type": "int", "default": 16, "min": 2, "max": 64, "description": "Number of bands"},
        "saturation": {"type": "float", "default": 0.8, "min": 0.0, "max": 1.0, "description": "Saturation"},
        "value": {"type": "float", "default": 0.9, "min": 0.0, "max": 1.0, "description": "Brightness"}
    }
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        bands = self.params.get("bands", 16)
        band = int(value / max_val * bands) % bands
        hue = band / bands
        sat = self.params.get("saturation", 0.8)
        val = self.params.get("value", 0.9)
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return (int(r * 255), int(g * 255), int(b * 255))


@register_palette("grayscale")
class GrayscalePalette(PaletteBase):
    """Grayscale palette."""
    
    name = "Grayscale"
    description = "Black and white gradient"
    parameters = {
        "invert": {"type": "bool", "default": False, "description": "Invert colors"}
    }
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        v = int(255 * value / max_val)
        if self.params.get("invert", False):
            v = 255 - v
        return (v, v, v)


@register_palette("fire")
class FirePalette(PaletteBase):
    """Fire palette (red, orange, yellow)."""
    
    name = "Fire"
    description = "Fire colors: red, orange, yellow"
    parameters = {}
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        r = int(255 * min(1, t * 2))
        g = int(255 * max(0, min(1, (t - 0.5) * 2)))
        b = int(255 * max(0, t - 0.75) * 4)
        return (r, g, b)


@register_palette("ocean")
class OceanPalette(PaletteBase):
    """Ocean palette (blues and greens)."""
    
    name = "Ocean"
    description = "Ocean colors: blues and greens"
    parameters = {}
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        r = int(255 * max(0, t - 0.5) * 2)
        g = int(255 * min(1, t * 1.5))
        b = int(255 * (0.3 + 0.7 * t))
        return (r, g, b)


@register_palette("rainbow")
class RainbowPalette(PaletteBase):
    """Full rainbow spectrum."""
    
    name = "Rainbow"
    description = "Full rainbow spectrum"
    parameters = {
        "saturation": {"type": "float", "default": 1.0, "min": 0.0, "max": 1.0, "description": "Saturation"},
        "value": {"type": "float", "default": 1.0, "min": 0.0, "max": 1.0, "description": "Brightness"}
    }
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        hue = (value / max_val) % 1.0
        sat = self.params.get("saturation", 1.0)
        val = self.params.get("value", 1.0)
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return (int(r * 255), int(g * 255), int(b * 255))


@register_palette("electric")
class ElectricPalette(PaletteBase):
    """Electric blue palette."""
    
    name = "Electric"
    description = "Electric blue and cyan"
    parameters = {}
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        r = int(255 * t * 0.2)
        g = int(255 * (0.5 + t * 0.5))
        b = int(255 * (0.8 + t * 0.2))
        return (min(255, r), min(255, g), min(255, b))


@register_palette("neon")
class NeonPalette(PaletteBase):
    """Neon pink and green palette."""
    
    name = "Neon"
    description = "Neon pink and green"
    parameters = {}
    
    def get_color(self, value: float, max_val: float):
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        # Alternate between pink and green
        if int(t * 8) % 2 == 0:
            return (int(255 * (0.5 + 0.5 * t)), int(255 * 0.2), int(255 * (0.8 + 0.2 * t)))
        else:
            return (int(255 * 0.2), int(255 * (0.8 + 0.2 * t)), int(255 * 0.3))
