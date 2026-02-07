"""Standard color palettes."""

import numpy as np
from math import sin, pi
from typing import Tuple, Dict, Any

from . import PaletteBase, register_palette


@register_palette("smooth")
class SmoothPalette(PaletteBase):
    """Smooth HSV color cycling."""
    
    name = "Smooth"
    description = "Smooth HSV color cycling"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        hue = t * 360
        
        return self._hsv_to_rgb(hue, 1.0, 1.0)
    
    @staticmethod
    def _hsv_to_rgb(hue: float, sat: float, val: float) -> Tuple[int, int, int]:
        h_i = int(hue / 60) % 6
        f = (hue / 60) - h_i
        p = val * (1 - sat)
        q = val * (1 - f * sat)
        t_val = val * (1 - (1 - f) * sat)
        
        if h_i == 0:
            r, g, b = val, t_val, p
        elif h_i == 1:
            r, g, b = q, val, p
        elif h_i == 2:
            r, g, b = p, val, t_val
        elif h_i == 3:
            r, g, b = p, q, val
        elif h_i == 4:
            r, g, b = t_val, p, val
        else:
            r, g, b = val, p, q
        
        return (int(r * 255), int(g * 255), int(b * 255))


@register_palette("banded")
class BandedPalette(PaletteBase):
    """Discrete color bands."""
    
    name = "Banded"
    description = "Discrete color bands"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        band = int(value / max_val * 10)
        t = (band + 0.5) / 10
        hue = t * 360
        
        return SmoothPalette._hsv_to_rgb(hue, 1.0, 1.0)


@register_palette("grayscale")
class GrayscalePalette(PaletteBase):
    """Black and white gradient."""
    
    name = "Grayscale"
    description = "Black and white gradient"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        gray = int((value / max_val) * 255)
        return (gray, gray, gray)


@register_palette("fire")
class FirePalette(PaletteBase):
    """Red, orange, yellow gradients."""
    
    name = "Fire"
    description = "Red, orange, yellow gradients"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        if t < 0.2:
            r = int(t * 5 * 255)
            g = 0
            b = 0
        elif t < 0.4:
            r = 255
            g = int((t - 0.2) * 5 * 255)
            b = 0
        elif t < 0.6:
            r = 255
            g = 255
            b = int((t - 0.4) * 5 * 128)
        elif t < 0.8:
            r = 255
            g = 255
            b = 128 + int((t - 0.6) * 5 * 127)
        else:
            r = 255
            g = 255
            b = 255
        
        return (r, g, b)


@register_palette("ocean")
class OceanPalette(PaletteBase):
    """Blues and greens."""
    
    name = "Ocean"
    description = "Blues and greens"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        if t < 0.3:
            r = int(t * 3 * 50)
            g = int(t * 3 * 100)
            b = int(t * 3 * 255)
        elif t < 0.6:
            r = int(150 + (t - 0.3) * 3 * 50)
            g = int(300 + (t - 0.3) * 3 * 50)
            b = 255
        else:
            r = min(300 + int((t - 0.6) * 2.5 * 55), 255)
            g = min(450 + int((t - 0.6) * 2.5 * 50), 255)
            b = 255
        
        return (r, g, b)


@register_palette("rainbow")
class RainbowPalette(PaletteBase):
    """Full spectrum."""
    
    name = "Rainbow"
    description = "Full spectrum"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        hue = int(t * 360)
        
        return SmoothPalette._hsv_to_rgb(hue, 1.0, 1.0)


@register_palette("electric")
class ElectricPalette(PaletteBase):
    """Electric blue and cyan."""
    
    name = "Electric"
    description = "Electric blue and cyan"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        r = int(128 * sin(t * pi) ** 2)
        g = int(255 * t)
        b = int(255 * (1 - t) + 128 * sin(t * pi))
        
        return (r, g, b)


@register_palette("neon")
class NeonPalette(PaletteBase):
    """Neon pink and green."""
    
    name = "Neon"
    description = "Neon pink and green"
    
    def get_color(self, value: float, max_val: float) -> Tuple[int, int, int]:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        r = int(255 * sin(t * pi))
        g = int(255 * sin((t + 0.5) * pi))
        b = int(255 * abs(sin(t * 2 * pi)))
        
        return (r, g, b)
