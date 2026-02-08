"""Base panel class for fractal parameter UI.

Panels use Tkinter variable traces (trace_add('write', ...)) for reliable value change
detection across all platforms. This is preferred over binding <<Increment>>/<<Decrement>>
events which may not fire consistently on all systems.
"""

import tkinter as tk
from tkinter import ttk


class BasePanel(ttk.Frame):
    """Base class for parameter panels.
    
    Subclasses should override create_widgets() to define their widgets and bind
    variable traces (see JuliaPanel, MultibrotPanel for examples).
    """
    
    def __init__(self, parent, fractal, on_change_callback=None):
        super().__init__(parent)
        self.fractal = fractal
        self.on_change = on_change_callback
        self.widgets = {}
        self.create_widgets()
    
    def create_widgets(self):
        """Subclasses should override to create their widgets."""
        raise NotImplementedError
    
    @property
    def root(self):
        """Get the root window for scheduling after() callbacks."""
        return self.master.winfo_toplevel()