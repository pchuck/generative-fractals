"""Standard color palette implementations."""

from . import PaletteBase, register_palette, hsv_to_rgb


@register_palette("smooth")
class SmoothPalette(PaletteBase):
    """Smooth HSV color cycling."""
    
    name = "Smooth"
    description = "Smooth HSV color cycling"
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        hue = (t * 4.0) % 1.0
        
        return hsv_to_rgb(hue, 1.0, 1.0)


@register_palette("banded")
class BandedPalette(PaletteBase):
    """Discrete color bands."""
    
    name = "Banded"
    description = "Discrete color bands"
    parameters = {"bands": 16}
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        bands = self.get_parameter("bands", 16)
        band_idx = int(value / max_val * bands) % bands
        hue = band_idx / bands
        
        return hsv_to_rgb(hue, 1.0, 1.0)


@register_palette("grayscale")
class GrayscalePalette(PaletteBase):
    """Black and white gradient."""
    
    name = "Grayscale"
    description = "Black and white gradient"
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        gray = int(t * 255)
        
        return (gray, gray, gray)


@register_palette("fire")
class FirePalette(PaletteBase):
    """Red, orange, yellow gradients."""
    
    name = "Fire"
    description = "Red, orange, yellow gradients"
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        if t < 0.33:
            r = int(t * 3 * 255)
            g = 0
            b = 0
        elif t < 0.66:
            r = 255
            g = int((t - 0.33) * 3 * 128)
            b = 0
        else:
            r = 255
            g = 128 + int((t - 0.66) * 3 * 127)
            b = 0
        
        return (r, g, b)


@register_palette("ocean")
class OceanPalette(PaletteBase):
    """Blues and greens."""
    
    name = "Ocean"
    description = "Blues and greens"
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        if t < 0.5:
            r = 0
            g = int(t * 2 * 255)
            b = 255
        else:
            r = 0
            g = 255
            b = int((1 - (t - 0.5) * 2) * 255)
        
        return (r, g, b)


@register_palette("rainbow")
class RainbowPalette(PaletteBase):
    """Full spectrum rainbow."""
    
    name = "Rainbow"
    description = "Full spectrum rainbow"
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        hue = t % 1.0
        
        return hsv_to_rgb(hue, 1.0, 1.0)


@register_palette("electric")
class ElectricPalette(PaletteBase):
    """Electric blue and cyan."""
    
    name = "Electric"
    description = "Electric blue and cyan"
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        r = int((1 - t) * 100)
        g = int(t * 255)
        b = 255
        
        return (r, g, b)


@register_palette("neon")
class NeonPalette(PaletteBase):
    """Neon pink and green."""
    
    name = "Neon"
    description = "Neon pink and green"
    
    def get_color(self, value: float, max_val: float) -> tuple:
        if value >= max_val:
            return (0, 0, 0)
        
        t = value / max_val
        
        if t < 0.5:
            r = 255
            g = int(t * 2 * 100)
            b = 200
        else:
            r = int((1 - (t - 0.5) * 2) * 150)
            g = 255
            b = 50
        
        return (r, g, b)