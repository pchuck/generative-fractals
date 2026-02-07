"""Orbit trap fractal variants."""

import numpy as np
from . import FractalBase, register_fractal


@register_fractal("orbit_trap")
class OrbitTrap(FractalBase):
    """Orbit trap fractal - tracks distance to geometric shapes."""
    
    name = "Orbit Trap"
    description = "Tracks distance to geometric shapes"
    parameters: Dict[str, Any] = {
        'trap_type': {'type': 'str', 'options': ['point', 'cross', 'circle', 'rectangle'], 'default': 'point'},
        'trap_point': {'type': 'complex', 'default': (0, 0)}
    }
    
    def __init__(self):
        self.trap_type = 'point'
        self.trap_point = complex(0, 0)
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -2.0, 'ymax': 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Orbit Trap for a point."""
        c = complex(x, y)
        z = 0j
        trap_point = self.trap_point
        trap_type = self.trap_type
        
        min_dist = float('inf')
        
        for i in range(max_iter):
            if abs(z) > 2:
                break
            
            if trap_type == 'point':
                dist = abs(z - trap_point)
            elif trap_type == 'cross':
                dist = min(abs(z.real - trap_point.real), abs(z.imag - trap_point.imag))
            elif trap_type == 'circle':
                dist = abs(abs(z) - abs(trap_point))
            elif trap_type == 'rectangle':
                dx = max(abs(z.real) - abs(trap_point.real), 0)
                dy = max(abs(z.imag) - abs(trap_point.imag), 0)
                dist = np.sqrt(dx**2 + dy**2)
            else:
                dist = abs(z - trap_point)
            
            min_dist = min(min_dist, dist)
            z = z ** 2 + c
        
        if min_dist == float('inf'):
            return float(max_iter)
        
        return np.log(1 / min_dist) if min_dist > 0 else float(max_iter)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set parameters."""
        if 'trap_type' in params:
            self.trap_type = params['trap_type']
        if 'trap_point' in params:
            tp = params['trap_point']
            self.trap_point = complex(tp[0], tp[1]) if isinstance(tp, (list, tuple)) else complex(tp)
        super().set_parameters(params)


@register_fractal("pickover_stalks")
class PickoverStalks(FractalBase):
    """Pickover stalks - colors based on closest approach to axes."""
    
    name = "Pickover Stalks"
    description = "Colors based on closest approach to axes"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 2.0, 'ymin': -2.0, 'ymax': 2.0}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute Pickover Stalks for a point."""
        c = complex(x, y)
        z = 0j
        closest_to_axes = float('inf')
        
        for i in range(max_iter):
            if abs(z) > 2:
                break
            
            dist_to_real = abs(z.imag)
            dist_to_imag = abs(z.real)
            closest = min(dist_to_real, dist_to_imag)
            closest_to_axes = min(closest_to_axes, closest)
            
            z = z ** 2 + c
        
        if closest_to_axes == float('inf'):
            return float(max_iter)
        
        return np.log(1 / closest_to_axes) if closest_to_axes > 0 else float(max_iter)


@register_fractal("interior_distance")
class InteriorDistance(FractalBase):
    """Interior distance estimation."""
    
    name = "Interior Distance"
    description = "Estimates distance from interior to boundary"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 1.5, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute interior distance estimation."""
        c = complex(x, y)
        z = 0j
        dz = 0j
        
        for i in range(max_iter):
            if abs(z) > 2:
                break
            
            dz = 2 * z * dz + 1
            z = z ** 2 + c
        
        if abs(z) > 2:
            return float(max_iter)
        
        distance = 0.5 * abs(z) * np.log(abs(z)) / abs(dz) if abs(dz) > 1e-10 else 0
        return distance


@register_fractal("exterior_distance")
class ExteriorDistance(FractalBase):
    """Exterior distance estimation using analytic method."""
    
    name = "Exterior Distance"
    description = "Analytic distance estimation"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 1.5, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute exterior distance estimation."""
        c = complex(x, y)
        z = 0j
        dz = 1j
        
        for i in range(max_iter):
            if abs(z) > 2:
                break
            
            dz = 2 * z * dz + 1
            z = z ** 2 + c
        
        if abs(z) <= 2:
            return float(max_iter)
        
        distance = 2 * np.log(abs(z)) / abs(dz)
        return distance


@register_fractal("derivative_bailout")
class DerivativeBailout(FractalBase):
    """Uses |dz/dc| for bailout condition."""
    
    name = "Derivative Bailout"
    description = "Uses |dz/dc| for bailout condition"
    parameters: Dict[str, Any] = {}
    
    def get_default_bounds(self) -> Dict[str, float]:
        return {'xmin': -2.0, 'xmax': 1.5, 'ymin': -1.5, 'ymax': 1.5}
    
    def compute_pixel(self, x: float, y: float, max_iter: int) -> float:
        """Compute derivative bailout fractal."""
        c = complex(x, y)
        z = 0j
        dz = 0j
        
        for i in range(max_iter):
            dz = 2 * z * dz + 1
            z = z ** 2 + c
            
            if abs(dz) > 1e6:
                return i
        
        return float(max_iter)
