"""
Session state management for fractal explorer.

Preserves view state and parameters when switching between fractal types.
Includes zoom history for undo/redo functionality.
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class ViewState:
    """Represents a single view state (for zoom history)."""
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    max_iter: int
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Return bounds as tuple."""
        return (self.x_min, self.x_max, self.y_min, self.y_max)


@dataclass
class FractalState:
    """State for a single fractal type with zoom history."""
    x_min: float = -2.5
    x_max: float = 1.0
    y_min: float = -1.5
    y_max: float = 1.5
    max_iter: int = 100
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Return bounds as tuple."""
        return (self.x_min, self.x_max, self.y_min, self.y_max)
    
    def set_bounds(self, x_min: float, x_max: float, y_min: float, y_max: float) -> None:
        """Set view bounds."""
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
    
    def to_view_state(self) -> ViewState:
        """Convert to a ViewState snapshot."""
        return ViewState(
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max,
            max_iter=self.max_iter,
            parameters=deepcopy(self.parameters)
        )
    
    def from_view_state(self, view: ViewState) -> None:
        """Restore state from a ViewState."""
        self.x_min = view.x_min
        self.x_max = view.x_max
        self.y_min = view.y_min
        self.y_max = view.y_max
        self.max_iter = view.max_iter
        self.parameters = deepcopy(view.parameters)


class ZoomHistory:
    """
    Manages zoom history for undo/redo functionality.
    
    Maintains a stack of previous views and a stack of "future" views
    for redo after undo operations.
    """
    
    MAX_HISTORY_SIZE = 50  # Maximum number of states to remember
    
    def __init__(self):
        self._history: List[ViewState] = []  # Past states (for undo)
        self._future: List[ViewState] = []   # Future states (for redo)
    
    def push(self, state: ViewState) -> None:
        """
        Push a new state onto the history.
        Clears the redo stack since we're branching from this point.
        """
        self._history.append(state)
        self._future.clear()
        
        # Limit history size
        if len(self._history) > self.MAX_HISTORY_SIZE:
            self._history.pop(0)
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._history) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._future) > 0
    
    def undo(self, current_state: ViewState) -> Optional[ViewState]:
        """
        Undo to the previous state.
        
        Args:
            current_state: The current view state (will be pushed to redo stack)
            
        Returns:
            The previous ViewState, or None if no history
        """
        if not self._history:
            return None
        
        # Push current state to future for potential redo
        self._future.append(current_state)
        
        # Pop and return the previous state
        return self._history.pop()
    
    def redo(self, current_state: ViewState) -> Optional[ViewState]:
        """
        Redo to the next state.
        
        Args:
            current_state: The current view state (will be pushed to history)
            
        Returns:
            The next ViewState, or None if no future states
        """
        if not self._future:
            return None
        
        # Push current state to history
        self._history.append(current_state)
        
        # Pop and return the future state
        return self._future.pop()
    
    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._future.clear()
    
    @property
    def history_count(self) -> int:
        """Number of states in undo history."""
        return len(self._history)
    
    @property
    def future_count(self) -> int:
        """Number of states in redo stack."""
        return len(self._future)


class SessionState:
    """
    Manages per-fractal session state with zoom history.
    
    Automatically saves and restores view coordinates and iteration limits
    when switching between fractal types. Maintains separate zoom history
    for each fractal type.
    """
    
    def __init__(self):
        self._states: Dict[str, FractalState] = {}
        self._histories: Dict[str, ZoomHistory] = {}
        self._current_fractal: Optional[str] = None
    
    def get_state(self, fractal_name: str) -> FractalState:
        """Get or create state for a fractal."""
        if fractal_name not in self._states:
            self._states[fractal_name] = FractalState()
        return self._states[fractal_name]
    
    def get_history(self, fractal_name: str) -> ZoomHistory:
        """Get or create zoom history for a fractal."""
        if fractal_name not in self._histories:
            self._histories[fractal_name] = ZoomHistory()
        return self._histories[fractal_name]
    
    def save_state(
        self,
        fractal_name: str,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        max_iter: int,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save state for a fractal type."""
        state = self.get_state(fractal_name)
        state.set_bounds(x_min, x_max, y_min, y_max)
        state.max_iter = max_iter
        if parameters:
            state.parameters = parameters.copy()
    
    def push_to_history(self, fractal_name: str, state: FractalState) -> None:
        """Push current state to zoom history before changing view."""
        history = self.get_history(fractal_name)
        history.push(state.to_view_state())
    
    def undo_zoom(self, fractal_name: str, current_view: ViewState) -> Optional[ViewState]:
        """
        Undo the last zoom operation.
        
        Args:
            fractal_name: Name of the current fractal
            current_view: The current view state from the app
        
        Returns:
            Previous ViewState if available, None otherwise
        """
        history = self.get_history(fractal_name)
        return history.undo(current_view)
    
    def redo_zoom(self, fractal_name: str, current_view: ViewState) -> Optional[ViewState]:
        """
        Redo the last undone zoom operation.
        
        Args:
            fractal_name: Name of the current fractal
            current_view: The current view state from the app
        
        Returns:
            Next ViewState if available, None otherwise
        """
        history = self.get_history(fractal_name)
        return history.redo(current_view)
    
    def can_undo(self, fractal_name: str) -> bool:
        """Check if undo is available for the given fractal."""
        return self.get_history(fractal_name).can_undo()
    
    def can_redo(self, fractal_name: str) -> bool:
        """Check if redo is available for the given fractal."""
        return self.get_history(fractal_name).can_redo()
    
    def restore_state(self, fractal_name: str) -> FractalState:
        """Restore state for a fractal type."""
        return self.get_state(fractal_name)
    
    def set_current_fractal(self, fractal_name: str) -> None:
        """Set the currently active fractal."""
        self._current_fractal = fractal_name
    
    @property
    def current_fractal(self) -> Optional[str]:
        """Get the currently active fractal name."""
        return self._current_fractal
    
    def reset_state(self, fractal_name: str) -> None:
        """Reset state for a fractal to defaults."""
        if fractal_name in self._states:
            del self._states[fractal_name]
        if fractal_name in self._histories:
            self._histories[fractal_name].clear()
    
    def clear_all(self) -> None:
        """Clear all saved states and histories."""
        self._states.clear()
        self._histories.clear()
        self._current_fractal = None
