"""Julia parameter panel for c and initial z₀ values."""

import tkinter as tk
from tkinter import ttk
from .base import BasePanel


class JuliaPanel(BasePanel):
    """Panel for Julia and Julia³ fractal parameters (c and z₀)."""
    
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
        
        # z₀ label
        ttk.Label(self, text="z₀:").pack(side=tk.LEFT)
        
        # z₀ real part spinner
        self.z0_real_var = tk.DoubleVar(value=getattr(self.fractal, 'z0', complex(0, 0)).real)
        self.widgets['z0_real'] = self.z0_real_var
        z0_real_spin = ttk.Spinbox(self, from_=-3.0, to=3.0, increment=0.05,
                                    textvariable=self.z0_real_var, width=6)
        z0_real_spin.pack(side=tk.LEFT, padx=(2, 2))
        
        # z₀ imaginary part spinner
        self.z0_imag_var = tk.DoubleVar(value=getattr(self.fractal, 'z0', complex(0, 0)).imag)
        self.widgets['z0_imag'] = self.z0_imag_var
        z0_imag_spin = ttk.Spinbox(self, from_=-3.0, to=3.0, increment=0.05,
                                    textvariable=self.z0_imag_var, width=6)
        z0_imag_spin.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add variable traces so any change triggers on_change
        self._trace_ids = []
        self._trace_ids.append(self.c_real_var.trace_add('write', lambda *args: self._on_value_changed()))
        self._trace_ids.append(self.c_imag_var.trace_add('write', lambda *args: self._on_value_changed()))
        self._trace_ids.append(self.z0_real_var.trace_add('write', lambda *args: self._on_value_changed()))
        self._trace_ids.append(self.z0_imag_var.trace_add('write', lambda *args: self._on_value_changed()))
    
    def _on_value_changed(self):
        """Called when any spinner value changes."""
        if hasattr(self.fractal, 'set_c'):
            c_real = float(self.c_real_var.get())
            c_imag = float(self.c_imag_var.get())
            
            self.fractal.set_c(c_real, c_imag)
            if hasattr(self.fractal, 'set_z0'):
                z0_real = float(self.z0_real_var.get())
                z0_imag = float(self.z0_imag_var.get())
                self.fractal.set_z0(z0_real, z0_imag)
            
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
            self.z0_real_var.trace_remove('write', self._trace_ids[2])
        if len(self._trace_ids) >= 4:
            self.z0_imag_var.trace_remove('write', self._trace_ids[3])
        
        try:
            self.c_real_var.set(self.fractal.c.real)
            self.c_imag_var.set(self.fractal.c.imag)
            if hasattr(self.fractal, 'z0'):
                self.z0_real_var.set(self.fractal.z0.real)
                self.z0_imag_var.set(self.fractal.z0.imag)
        finally:
            # Restore traces
            self._trace_ids = []
            self._trace_ids.append(self.c_real_var.trace_add('write', lambda *args: self._on_value_changed()))
            self._trace_ids.append(self.c_imag_var.trace_add('write', lambda *args: self._on_value_changed()))
            self._trace_ids.append(self.z0_real_var.trace_add('write', lambda *args: self._on_value_changed()))
            self._trace_ids.append(self.z0_imag_var.trace_add('write', lambda *args: self._on_value_changed()))