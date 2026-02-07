"""Rendering engine base classes."""

from abc import ABC, abstractmethod
from typing import Tuple, List, Optional


class RenderEngineBase(ABC):
    """Base class for rendering engines."""
    
    @abstractmethod
    def render(self, width: int, height: int, fractal, palette, max_iter: int) -> bytes:
        """Render a fractal to raw image data."""
        pass
    
    @abstractmethod
    def render_row(self, y: int, width: int, fractal, palette, max_iter: int) -> List[Tuple[int, int, int]]:
        """Render a single row."""
        pass


__all__ = ['RenderEngineBase']
