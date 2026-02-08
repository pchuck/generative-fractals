"""Multibrot parameter panel for power value."""

import tkinter as tk
from tkinter import ttk
from .base import BasePanel


class MultibrotPanel(BasePanel):
    """Panel for Multibrot fractal power parameter."""
    
    def create_widgets(self):
        # Label
        ttk.Label(self, text="Power:").pack(side=tk.LEFT, padx=(5, 2))
        
        # Power spinner
        self.power_var = tk.DoubleVar(value=self.fractal.power)
        self.widgets['power'] = self.power_var
        power_spin = ttk.Spinbox(self, from_=-3.0, to=10.0, increment=0.1,
                                  textvariable=self.power_var, width=6)
        power_spin.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add variable trace so any change triggers on_change
        self._trace_id = self.power_var.trace_add('write', lambda *args: self._on_value_changed())
    
    def _on_value_changed(self):
        """Called when the spinner value changes."""
        if hasattr(self.fractal, 'power'):
            self.fractal.power = float(self.power_var.get())
            if self.on_change:
                self.on_change()
    
    def on_change(self):
        """For backward compatibility - trigger render callback."""
        # This is now handled by _on_value_changed
        pass
    
    def update_from_fractal(self):
        """Sync UI values with current fractal state."""
        # Remove trace temporarily to prevent it from firing during sync
        if self._trace_id:
            self.power_var.trace_remove('write', self._trace_id)
        
        try:
            self.power_var.set(self.fractal.power)
        finally:
            # Restore trace
            self._trace_id = self.power_var.trace_add('write', lambda *args: self._on_value_changed())