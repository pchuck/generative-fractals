"""Fractal base classes and registry system."""

import cmath
from typing import Dict, Any, Optional


_fractal_registry: Dict[str, type] = {}


class FractalBase:
    """Base class for all fractal implementations."""
    
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}
    
    def __init__(self):
        self.params = self.parameters.copy()
    
    def get_default_bounds(self) -> Dict[str, float]:
        """Return default coordinate bounds for this fractal."""
        return {"xmin": -2.0, "xmax": 2.0, "ymin": -2.0, "ymax": 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute iteration count for a single pixel.
        
        Args:
            x: Real coordinate in complex plane
            y: Imaginary coordinate in complex plane
            max_iter: Maximum iterations to perform
            
        Returns:
            Iteration count (or smooth value if applicable)
        """
        return float(max_iter)
    
    def set_parameter(self, name: str, value: Any) -> None:
        """Set a parameter for this fractal."""
        if name in self.params:
            self.params[name] = value
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self.params.get(name, default)


def register_fractal(fractal_id: str):
    """Decorator to register a fractal class in the registry.
    
    Args:
        fractal_id: Unique identifier for this fractal type
        
    Returns:
        Decorator function
    """
    def decorator(cls):
        _fractal_registry[fractal_id] = cls
        return cls
    return decorator


def get_fractal(fractal_id: str) -> Optional[FractalBase]:
    """Get an instance of a registered fractal.
    
    Args:
        fractal_id: Identifier of the fractal to instantiate
        
    Returns:
        Fractal instance or None if not found
    """
    cls = _fractal_registry.get(fractal_id)
    if cls:
        return cls()
    return None


def list_fractals() -> Dict[str, str]:
    """Get a dictionary of all registered fractals.
    
    Returns:
        Dictionary mapping fractal IDs to their names
    """
    result = {}
    for fid, cls in _fractal_registry.items():
        instance = cls()
        result[fid] = instance.name
    return result


def smooth_coloring(z: complex, i: int, max_iter: int, power: float = 2.0) -> float:
    """Compute smooth coloring value.
    
    Args:
        z: Current complex value after iteration
        i: Iteration count at bailout
        max_iter: Maximum iterations
        power: Power used in iteration formula
        
    Returns:
        Smooth floating-point iteration count
    """
    if i >= max_iter:
        return float(max_iter)
    
    abs_z = abs(z)
    if abs_z < 1e-10:
        return float(i)
    
    nu = cmath.log(cmath.log(abs_z) / cmath.log(power)) / cmath.log(power)
    return i + 1 - nu.real