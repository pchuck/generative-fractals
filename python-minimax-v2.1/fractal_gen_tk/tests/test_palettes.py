"""Unit tests for color palettes.

Run with: python -m pytest tests/ -v
"""

import pytest
from palettes import (
    grayscale, plasma, rainbow, cool, electric, retro, sunset, ocean, alien,
    PaletteFactory, PALETTES
)


class TestPaletteFunctions:
    """Test individual palette functions."""
    
    def test_grayscale_output(self):
        """Grayscale should return tuple of three values."""
        result = grayscale(50, 100)
        assert isinstance(result, tuple)
        assert len(result) == 3
        r, g, b = result
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255
    
    def test_grayscale_gradient(self):
        """Grayscale should increase with iteration count."""
        low = grayscale(10, 100)
        high = grayscale(90, 100)
        # Higher iterations should be brighter (higher values)
        assert sum(high) > sum(low)
    
    def test_plasma_output(self):
        """Plasma should return valid RGB tuple."""
        result = plasma(50, 100)
        r, g, b = result
        assert all(0 <= v <= 255 for v in (r, g, b))
    
    def test_rainbow_output(self):
        """Rainbow should return valid RGB tuple."""
        result = rainbow(25, 100)
        r, g, b = result
        assert all(0 <= v <= 255 for v in (r, g, b))
    
    def test_cool_output(self):
        """Cool palette should be blue-dominant."""
        result = cool(50, 100)
        r, g, b = result
        # Blue component should be significant
        assert b > r
    
    def test_electric_output(self):
        """Electric should return valid RGB tuple."""
        result = electric(75, 100)
        r, g, b = result
        assert all(0 <= v <= 255 for v in (r, g, b))
    
    def test_retro_output(self):
        """Retro palette should have warm tones."""
        result = retro(50, 100)
        # Retro tends toward warmer colors
        r, g, b = result
        assert r >= g and r >= b
    
    def test_sunset_output(self):
        """Sunset should return valid RGB tuple."""
        result = sunset(60, 100)
        r, g, b = result
        assert all(0 <= v <= 255 for v in (r, g, b))
    
    def test_ocean_output(self):
        """Ocean palette should be blue-dominant."""
        result = ocean(50, 100)
        r, g, b = result
        # Ocean is blue-heavy
        assert b > r
    
    def test_alien_output(self):
        """Alien palette should return valid RGB tuple."""
        result = alien(60, 100)
        r, g, b = result
        assert all(0 <= v <= 255 for v in (r, g, b))
    
    def test_max_iter_black(self):
        """max_iter count should return black (0,0,0) except retro."""
        # Most palettes use black for points that don't escape
        for name, func in PALETTES.items():
            if name != "Retro":  # Retro uses a different color for max iter
                result = func(100, 100)
                assert result == (0, 0, 0), f"{name} should return black at max_iter"
    
    def test_zero_iteration(self):
        """Iteration count of 0 should not crash."""
        # Should handle edge case gracefully
        for func in PALETTES.values():
            result = func(0, 100)
            assert isinstance(result, tuple)
            assert len(result) == 3


class TestPaletteFactory:
    """Test PaletteFactory class methods."""
    
    def test_list_names(self):
        """list_names should return list of palette names."""
        names = PaletteFactory.list_names()
        assert isinstance(names, list)
        assert "Rainbow" in names
        assert len(names) > 5
    
    def test_get_valid_palette(self):
        """get should return a function for valid name."""
        func = PaletteFactory.get("Plasma")
        assert callable(func)
    
    def test_get_case_insensitive(self):
        """get should be case-insensitive."""
        func1 = PaletteFactory.get("rainbow")
        func2 = PaletteFactory.get("Rainbow")
        # Should return the same function
        result1 = func1(50, 100)
        result2 = func2(50, 100)
        assert result1 == result2
    
    def test_get_invalid_returns_rainbow(self):
        """Invalid name should return Rainbow as fallback."""
        func = PaletteFactory.get("nonexistent")
        # Should not raise, should return a valid function
        assert callable(func)


class TestPaletteRegistry:
    """Test palette registration functionality."""
    
    def test_register_new_palette(self):
        """Should be able to register a new palette."""
        def custom_palette(iter_count, max_iter):
            return (128, 128, 128)
        
        PaletteFactory.register("CustomGray", custom_palette)
        
        # Key is stored as-is for names without underscores
        assert "CustomGray" in PaletteFactory.list_names()
        func = PaletteFactory.get("customgray")
        assert func(50, 100) == (128, 128, 128)
    
    def test_register_with_underscores(self):
        """Names with underscores should be Title-Case per segment."""
        # Register a name with underscores - each segment becomes title-cased
        PaletteFactory.register("my_test_palette", lambda i, m: (0, 0, 0))
        
        # Should become "My_Test_Palette" after normalization
        assert "My_Test_Palette" in PALETTES
        
        # And should be retrievable case-insensitively
        func = PaletteFactory.get("MY_TEST_PALETTE")
        assert callable(func)
    
    def test_register_removes_case_duplicate(self):
        """Registering same name with different case should replace existing."""
        from palettes import PALETTES
        
        initial_count = len(PALETTES)
        
        # Register a new palette
        PaletteFactory.register("CaseTest", lambda i, m: (1, 1, 1))
        after_first = len(PALETTES)
        assert after_first == initial_count + 1
        
        # Re-register with different case - should replace, not duplicate
        PaletteFactory.register("casetest", lambda i, m: (2, 2, 2))
        after_second = len(PALETTES)
        
        # Should still be the same count (replaced instead of added)
        assert after_first == after_second
        
        # The palette should have been updated
        func = PaletteFactory.get("CASETEST")
        result = func(50, 100)
        assert result == (2, 2, 2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])