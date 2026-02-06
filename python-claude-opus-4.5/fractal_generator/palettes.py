"""
Color palette definitions and factory.

Each palette is a function that maps (iteration_count, max_iter) to an RGB tuple.
Points that don't escape (iter_count == max_iter) should return black.
"""

import math
from typing import Dict, Callable, Tuple

# Type alias for palette functions
PaletteFunc = Callable[[int, int], Tuple[int, int, int]]


def palette_classic(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Classic blue-to-white gradient palette."""
    if iter_count == max_iter:
        return (0, 0, 0)  # Black for bounded points
    
    t = iter_count / max_iter
    r = int(9 * (1 - t) * t * t * t * 255)
    g = int(15 * (1 - t) * (1 - t) * t * t * 255)
    b = int(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255)
    
    return (min(255, r), min(255, g), min(255, b))


def palette_fire(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Fire-like palette with reds, oranges, and yellows."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    t = iter_count / max_iter
    r = int(min(255, 255 * min(1, t * 3)))
    g = int(min(255, 255 * max(0, min(1, (t - 0.33) * 3))))
    b = int(min(255, 255 * max(0, min(1, (t - 0.67) * 3))))
    
    return (r, g, b)


def palette_ocean(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Ocean-themed blue and teal palette."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    t = iter_count / max_iter
    r = int(30 + 50 * t)
    g = int(80 + 175 * t)
    b = int(120 + 135 * (1 - t * 0.5))
    
    return (min(255, r), min(255, g), min(255, b))


def palette_rainbow(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Smooth rainbow palette using HSV-like conversion."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    # Map iteration to hue (0-360)
    hue = (iter_count * 360 / max_iter) % 360
    
    # HSV to RGB with S=1, V=1
    c = 1.0
    x = 1 - abs((hue / 60) % 2 - 1)
    
    if hue < 60:
        r, g, b = c, x, 0
    elif hue < 120:
        r, g, b = x, c, 0
    elif hue < 180:
        r, g, b = 0, c, x
    elif hue < 240:
        r, g, b = 0, x, c
    elif hue < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int(r * 255), int(g * 255), int(b * 255))


def palette_grayscale(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Simple grayscale palette."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    gray = int(255 * iter_count / max_iter)
    return (gray, gray, gray)


def palette_electric(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Electric blue and purple palette."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    t = iter_count / max_iter
    r = int(128 + 127 * math.sin(t * math.pi * 2))
    g = int(50 + 50 * math.sin(t * math.pi * 3 + 2))
    b = int(200 + 55 * math.sin(t * math.pi * 1.5))
    
    return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))


def palette_forest(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Forest green and brown palette."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    t = iter_count / max_iter
    r = int(50 + 100 * t * t)
    g = int(80 + 150 * math.sqrt(t))
    b = int(30 + 50 * t)
    
    return (min(255, r), min(255, g), min(255, b))


def palette_pastel(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Soft pastel colors."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    t = iter_count / max_iter
    r = int(180 + 75 * math.sin(t * math.pi * 2))
    g = int(180 + 75 * math.sin(t * math.pi * 2 + 2.094))
    b = int(180 + 75 * math.sin(t * math.pi * 2 + 4.188))
    
    return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))


def palette_neon(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Bright neon colors."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    t = iter_count / max_iter
    phase = t * 6
    
    if phase < 1:
        r, g, b = 255, int(255 * phase), 0
    elif phase < 2:
        r, g, b = int(255 * (2 - phase)), 255, 0
    elif phase < 3:
        r, g, b = 0, 255, int(255 * (phase - 2))
    elif phase < 4:
        r, g, b = 0, int(255 * (4 - phase)), 255
    elif phase < 5:
        r, g, b = int(255 * (phase - 4)), 0, 255
    else:
        r, g, b = 255, 0, int(255 * (6 - phase))
    
    return (r, g, b)


def palette_sunset(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Warm sunset colors."""
    if iter_count == max_iter:
        return (0, 0, 0)
    
    t = iter_count / max_iter
    r = int(255 * min(1, 0.5 + t))
    g = int(255 * max(0, min(1, 1.5 * t - 0.25)))
    b = int(255 * max(0, min(1, 2 * t - 1)))
    
    return (min(255, r), min(255, g), min(255, b))


class PaletteFactory:
    """Factory for managing color palettes."""
    
    _registry: Dict[str, PaletteFunc] = {}
    
    @classmethod
    def register(cls, name: str, palette_func: PaletteFunc) -> None:
        """Register a palette function with the factory."""
        cls._registry[name] = palette_func
    
    @classmethod
    def get(cls, name: str) -> PaletteFunc:
        """Get a palette function by name."""
        return cls._registry.get(name, palette_classic)
    
    @classmethod
    def get_available(cls) -> list:
        """Return list of available palette names."""
        return list(cls._registry.keys())


# Register built-in palettes
PaletteFactory.register('Classic', palette_classic)
PaletteFactory.register('Fire', palette_fire)
PaletteFactory.register('Ocean', palette_ocean)
PaletteFactory.register('Rainbow', palette_rainbow)
PaletteFactory.register('Grayscale', palette_grayscale)
PaletteFactory.register('Electric', palette_electric)
PaletteFactory.register('Forest', palette_forest)
PaletteFactory.register('Pastel', palette_pastel)
PaletteFactory.register('Neon', palette_neon)
PaletteFactory.register('Sunset', palette_sunset)
