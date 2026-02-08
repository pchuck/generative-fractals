"""Phoenix parameter panel for c and p values."""

import tkinter as tk
from tkinter import ttk
from .base import BasePanel


class PhoenixPanel(BasePanel):
    """Panel for Phoenix fractal parameters (c and p)."""
    
    def create_widgets(self):
        # Label
        ttk.Label(self, text="c:").pack(side=tk.LEFT, padx=(5, 2))
        
        # c real part spinner
        self.c_real_var = tk.DoubleVar(value=self.fractal.c.real)
        self.widgets['c_real'] = self.c_real_var
        c_real_spin = ttk.Spinbox(self, from_=-3.0, to=3.0, increment=0.05,
                                   textvariable=self.c_real_var, width=6)
        c_real_spin.pack(side=tk.LEFT, padx=(0, 2))
        
        # c imaginary part spinner
        self.c_imag_var = tk.DoubleVar(value=self.fractal.c.imag)
        self.widgets['c_imag'] = self.c_imag_var
        c_imag_spin = ttk.Spinbox(self, from_=-3.0, to=3.0, increment=0.05,
                                   textvariable=self.c_imag_var, width=6)
        c_imag_spin.pack(side=tk.LEFT, padx=(0, 10))
        
        # p label
        ttk.Label(self, text="p:").pack(side=tk.LEFT)
        
        # p spinner
        self.p_var = tk.DoubleVar(value=self.fractal.p)
        self.widgets['p'] = self.p_var
        p_spin = ttk.Spinbox(self, from_=-2.0, to=2.0, increment=0.05,
                              textvariable=self.p_var, width=6)
        p_spin.pack(side=tk.LEFT, padx=(2, 5))
        
        # Add variable traces so any change triggers on_change
        self._trace_ids = []
        self._trace_ids.append(self.c_real_var.trace_add('write', lambda *args: self._on_value_changed()))
        self._trace_ids.append(self.c_imag_var.trace_add('write', lambda *args: self._on_value_changed()))
        self._trace_ids.append(self.p_var.trace_add('write', lambda *args: self._on_value_changed()))
    
    def _on_value_changed(self):
        """Called when any spinner value changes."""
        if hasattr(self.fractal, 'set_c'):
            c_real = float(self.c_real_var.get())
            c_imag = float(self.c_imag_var.get())
            
            self.fractal.set_c(c_real, c_imag)
            self.fractal.p = float(self.p_var.get())
            
            if self.on_change:
                self.on_change()
    
    def on_change(self):
        """For backward compatibility - trigger render callback."""
        # This is now handled by _on_value_changed
        pass
    
    def update_from_fractal(self):
        """Sync UI values with current fractal state."""
        # Remove all traces temporarily to prevent them from firing during sync
        if len(self._trace_ids) >= 1:
            self.c_real_var.trace_remove('write', self._trace_ids[0])
        if len(self._trace_ids) >= 2:
            self.c_imag_var.trace_remove('write', self._trace_ids[1])
        if len(self._trace_ids) >= 3:
            self.p_var.trace_remove('write', self._trace_ids[2])
        
        try:
            self.c_real_var.set(self.fractal.c.real)
            self.c_imag_var.set(self.fractal.c.imag)
            self.p_var.set(self.fractal.p)
        finally:
            # Restore traces
            self._trace_ids = []
            self._trace_ids.append(self.c_real_var.trace_add('write', lambda *args: self._on_value_changed()))
            self._trace_ids.append(self.c_imag_var.trace_add('write', lambda *args: self._on_value_changed()))
            self._trace_ids.append(self.p_var.trace_add('write', lambda *args: self._on_value_changed()))