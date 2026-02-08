"""
Color palette definitions for fractal rendering.

Palette Function Semantics:
All palette functions receive (iter_count, max_iter):
  - iter_count: iteration at which point escaped (1 to max_iter)
  - max_iter: if iter_count == max_iter, the point did NOT escape
  
Convention: Return black (0, 0, 0) for non-escaping points,
           except Retro which uses a dark brown tint.

PaletteFactory Registration/Lookup Rules:
-----------------------------------------
  - list_names(): Returns registered palette keys in original case
  - get(name): Case-insensitive lookup; invalid names return "Rainbow" fallback
  - register(name, func):
      * No underscores → preserve user capitalization ("CustomGray" → "CustomGray")
      * With underscores → Title-Case each segment ("my_test" → "My_Test")
      * Removes case-insensitive duplicates before inserting

Add new palettes via PaletteFactory.register() or direct PALETTES entries.
"""

from typing import Callable, Tuple
import colorsys


# Color palette function type: maps iteration count and max_iter to RGB tuple
PaletteFunc = Callable[[int, int], Tuple[int, int, int]]


def grayscale(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Simple grayscale gradient.
    
    Non-escaping points (iter_count == max_iter) render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    gray = int(255 * t)
    return (gray, gray, gray)


def plasma(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Plasma palette: deep purple to magenta to orange to yellow.
    
    Non-escaping points render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    # Nonlinear curve for richer colors
    hue = 0.7 - t * 0.65  # Purple (0.7) through pink/orange to yellow (0.05)
    sat = 0.9
    val = min(1.0, 0.5 + t * 0.5)  # Brighter at higher iterations
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return (int(r * 255), int(g * 255), int(b * 255))


def ocean(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Ocean palette: deep blue through cyan to white.
    
    Non-escaping points render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    # Deep navy to bright cyan/white
    r = min(255, int(30 * t ** 0.5))
    g = min(255, int(80 * t + 20 * (1 - t)))
    b = min(255, int(100 * t + 155 * t ** 3))
    return (r, g, b)


def rainbow(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Full rainbow color palette using HSV to RGB conversion.
    
    Non-escaping points render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    hue = t * 0.8  # Rotate through part of the color wheel
    r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
    return (int(r * 255), int(g * 255), int(b * 255))


def cool(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Cool blue/cyan/purple palette.
    
    Non-escaping points render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    r = 0
    g = min(255, int(255 * t))
    b = min(255, int(255 * (1 - 0.5 * t)))
    return (r, g, b)


def electric(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Electric blue/magenta palette.
    
    Non-escaping points render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    r = min(255, int(255 * t ** 0.5))
    g = min(255, int(255 * (t ** 2)))
    b = min(255, int(255 * ((1 - t) ** 0.3)))
    return (r, g, b)


def retro(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Retro sepia/vintage look.
    
    Non-escaping points render as dark brown (15, 10, 5).
    """
    if iter_count == max_iter:
        return (15, 10, 5)
    t = iter_count / max_iter
    r = min(255, int(200 * t + 50))
    g = min(255, int(180 * t + 30))
    b = min(255, int(130 * t + 20))
    return (r, g, b)


def sunset(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Sunset palette: purple to pink to orange to golden.
    
    Non-escaping points render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    # Smooth gradient from deep purple through magenta to sunset orange/gold
    r = min(255, int(80 + 175 * t))
    g = min(255, int(20 * t ** 2))
    b = max(0, int(150 - 100 * t))
    return (r, g, b)


def alien(iter_count: int, max_iter: int) -> Tuple[int, int, int]:
    """Alien greens with occasional purple accents.
    
    Non-escaping points render as black (0, 0, 0).
    """
    if iter_count == max_iter:
        return (0, 0, 0)
    t = iter_count / max_iter
    # Base green with color shift at high iterations
    r = min(255, int(20 * t + 80 * t ** 4))
    g = min(255, int(180 * t + 75 * (1 - t)))
    b = min(255, int(50 * t + 100 * t ** 3))
    return (r, g, b)


# Dictionary of available palettes - easy to extend
PALETTES: dict[str, PaletteFunc] = {
    "Grayscale": grayscale,
    "Plasma": plasma,
    "Rainbow": rainbow,
    "Cool": cool,
    "Electric": electric,
    "Retro": retro,
    "Sunset": sunset,
    "Ocean": ocean,
    "Alien": alien,
}


class PaletteFactory:
    """Factory for accessing and creating color palettes."""
    
    @classmethod
    def list_names(cls) -> list[str]:
        """Return list of available palette names (preserves original case)."""
        return list(PALETTES.keys())
    
    @classmethod
    def get(cls, name: str) -> PaletteFunc:
        """Get a palette function by name (case-insensitive)."""
        name_key = name.lower()
        for key in PALETTES:
            if key.lower() == name_key:
                return PALETTES[key]
        # Default fallback
        return PALETTES["Rainbow"]
    
    @classmethod
    def register(cls, name: str, palette_func: PaletteFunc):
        """Register a new color palette.
        
        Keys are normalized to avoid case-insensitive duplicates:
          - Without underscores: preserve user capitalization ("CustomGray" → "CustomGray")
          - With underscores: convert each segment to Title Case ("lowercase_test" → "Lowercase_Test")
          
        Example:
            register("MyPalette", func)  # stores as "MyPalette"
            register("my_palette", func)  # stores as "My_Palette"
        """
        if not name:
            PALETTES[name] = palette_func
            return
        
        # Check for case-insensitive duplicate before normalizing
        normalized_lower = name.lower()
        for existing_key in list(PALETTES.keys()):
            if existing_key.lower() == normalized_lower:
                # Remove the existing entry to prevent duplicates
                del PALETTES[existing_key]
                break
        
        # Normalize key based on underscore presence
        if "_" in name:
            # Convert each segment after underscore to title case
            segments = name.split("_")
            normalized = "_".join(seg.title() for seg in segments)
        else:
            # Preserve user capitalization when no underscores
            normalized = name
        
        PALETTES[normalized] = palette_func
