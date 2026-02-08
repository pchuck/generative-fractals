"""UI Manager for fractal explorer."""

import tkinter as tk
from tkinter import ttk
from fractals import FractalRegistry
from palettes import PaletteRegistry


class UIManager:
    """Manages all UI creation and widget interactions."""
    
    def __init__(self, app):
        """
        Initialize UI manager.
        
        Args:
            app: The FractalExplorer instance
        """
        self.app = app
        self.widgets = {}
        
    def create_ui(self):
        """Create the complete user interface."""
        self._create_main_frame()
        self._create_controls()
        self._create_params_frame()
        self._create_canvas()
        self._create_info_bar()
        self._create_progress_bar()
        
    def _create_main_frame(self):
        """Create main application frame."""
        main_frame = ttk.Frame(self.app.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.app.root.columnconfigure(0, weight=1)
        self.app.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        self.widgets['main_frame'] = main_frame
        
    def _create_controls(self):
        """Create control panel with fractal selector, sliders, etc."""
        main_frame = self.widgets['main_frame']
        
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        row = 0
        
        # Fractal type
        ttk.Label(controls_frame, text="Fractal:").grid(row=row, column=0, padx=5, pady=2)
        self.app.fractal_var = tk.StringVar(value=self.app.fractal_name)
        fractal_combo = ttk.Combobox(controls_frame, textvariable=self.app.fractal_var,
                                     values=FractalRegistry.list_fractals(), 
                                     state="readonly", width=15, height=20)
        fractal_combo.grid(row=row, column=1, padx=5, pady=2)
        fractal_combo.bind("<<ComboboxSelected>>", self.app._on_fractal_change)
        
        # Max iterations (slider)
        ttk.Label(controls_frame, text="Iterations:").grid(row=row, column=2, padx=5, pady=2)
        self.app.iter_var = tk.IntVar(value=100)
        self.app.iter_slider = ttk.Scale(controls_frame, from_=50, to=2000, orient=tk.HORIZONTAL,
                                     variable=self.app.iter_var, length=120)
        self.app.iter_slider.grid(row=row, column=3, padx=5, pady=2)
        self.app.iter_label = ttk.Label(controls_frame, text="100", width=4)
        self.app.iter_label.grid(row=row, column=4, padx=(0, 5))
        self.app.iter_slider.bind("<Motion>", self.app._on_slider_motion)
        self.app.iter_slider.bind("<ButtonRelease-1>", self.app._on_slider_release)
        
        # Color palette
        ttk.Label(controls_frame, text="Palette:").grid(row=row, column=5, padx=5, pady=2)
        self.app.palette_var = tk.StringVar(value=self.app.palette_name)
        palette_combo = ttk.Combobox(controls_frame, textvariable=self.app.palette_var,
                                     values=PaletteRegistry.list_palettes(), 
                                     state="readonly", width=10)
        palette_combo.grid(row=row, column=6, padx=5, pady=2)
        palette_combo.bind("<<ComboboxSelected>>", self.app._on_palette_change)
        
        # Navigation buttons (Back/Forward arrows only)
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.grid(row=row, column=7, padx=5, pady=2)
        self.back_btn = ttk.Button(nav_frame, text="◀", command=self.app.go_back, width=3)
        self.back_btn.pack(side=tk.LEFT, padx=1)
        self.back_btn.config(state='disabled')
        self.forward_btn = ttk.Button(nav_frame, text="▶", command=self.app.go_forward, width=3)
        self.forward_btn.pack(side=tk.LEFT, padx=1)
        self.forward_btn.config(state='disabled')
        
        # Buttons (Reset/Save/Help)
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.grid(row=row, column=8, padx=10, pady=2)
        ttk.Button(btn_frame, text="Reset", command=self.app.reset_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save Image", command=self.app.save_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Help", command=self.app.show_about, width=6).pack(side=tk.LEFT, padx=2)
        
    def create_fractal_params_ui(self):
        """Create parameter controls for current fractal."""
        if 'params_frame' not in self.widgets:
            return
            
        params_frame = self.widgets['params_frame']
        
        # Clear existing widgets
        for widget in params_frame.winfo_children():
            widget.destroy()
        
        # Get fractal class info
        fractal_class = FractalRegistry.get(self.app.fractal_name)
        if not fractal_class:
            return
        
        # Create parameter inputs
        params = fractal_class.parameters
        if not params:
            ttk.Label(params_frame, text="No parameters for this fractal").pack(pady=5)
            return
        
        # Store parameter variables and slider value labels
        self.app.param_vars = {}
        self.app.param_slider_labels = {}
        
        for i, (param_name, param_def) in enumerate(params.items()):
            ttk.Label(params_frame, text=f"{param_name}:").grid(row=0, column=i*3, padx=5, pady=2)
            
            param_type = param_def.get("type", "string")
            param_min = param_def.get("min")
            param_max = param_def.get("max")
            
            if param_type == "int" and param_min is not None and param_max is not None:
                self._create_slider_input(params_frame, i, param_name, param_def, param_min, param_max)
            elif param_type == "choice":
                self._create_choice_input(params_frame, i, param_name, param_def)
            else:
                self._create_text_input(params_frame, i, param_name, param_def)
                
    def _create_slider_input(self, parent, index, param_name, param_def, param_min, param_max):
        """Create a slider input widget."""
        default_val = int(self.app.fractal_params.get(param_name, param_def.get("default", param_min)))
        var = tk.IntVar(value=default_val)
        self.app.param_vars[param_name] = var
        
        slider = ttk.Scale(
            parent,
            from_=param_min,
            to=param_max,
            orient=tk.HORIZONTAL,
            variable=var,
            length=100,
            command=lambda v, name=param_name: self._on_param_slider_motion(name, v)
        )
        slider.grid(row=0, column=index*3+1, padx=5, pady=2)
        
        label = ttk.Label(parent, text=str(default_val), width=3)
        label.grid(row=0, column=index*3+2, padx=(0, 5))
        self.app.param_slider_labels[param_name] = label
        
        slider.bind("<ButtonRelease-1>", lambda e, name=param_name: self._on_param_slider_release(name))
        
    def _create_choice_input(self, parent, index, param_name, param_def):
        """Create a dropdown choice input widget."""
        choices = param_def.get("choices", [])
        default_val = str(self.app.fractal_params.get(param_name, param_def.get("default", choices[0] if choices else "")))
        var = tk.StringVar(value=default_val)
        self.app.param_vars[param_name] = var
        
        combo = ttk.Combobox(
            parent,
            textvariable=var,
            values=choices,
            state="readonly",
            width=10
        )
        combo.grid(row=0, column=index*3+1, padx=5, pady=2)
        combo.bind("<<ComboboxSelected>>", self.app._on_param_change)
        
    def _create_text_input(self, parent, index, param_name, param_def):
        """Create a text entry input widget."""
        var = tk.StringVar(value=str(self.app.fractal_params.get(param_name, param_def.get("default", ""))))
        self.app.param_vars[param_name] = var
        
        entry = ttk.Entry(parent, textvariable=var, width=12)
        entry.grid(row=0, column=index*3+1, padx=5, pady=2)
        entry.bind("<Return>", self.app._on_param_change)
        
    def _on_param_slider_motion(self, param_name, value):
        """Update label while dragging slider."""
        label = self.app.param_slider_labels.get(param_name)
        if label:
            label.configure(text=f"{int(float(value))}")
    
    def _on_param_slider_release(self, param_name):
        """Render when slider is released."""
        var = self.app.param_vars.get(param_name)
        if var:
            self.app.fractal_params[param_name] = var.get()
            self.app.render()
        
    def _create_params_frame(self):
        """Create fractal parameters frame."""
        main_frame = self.widgets['main_frame']
        
        params_frame = ttk.LabelFrame(main_frame, text="Fractal Parameters", padding="5")
        params_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.widgets['params_frame'] = params_frame
        self.create_fractal_params_ui()
        
    def _create_canvas(self):
        """Create canvas for fractal display."""
        main_frame = self.widgets['main_frame']
        
        canvas_frame = ttk.Frame(main_frame, borderwidth=2, relief="sunken")
        canvas_frame.grid(row=2, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.app.canvas = tk.Canvas(canvas_frame, bg="black", highlightthickness=0)
        self.app.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Bind to canvas resize events
        self.app.canvas.bind("<Configure>", self.app._on_canvas_resize)
        
    def _create_info_bar(self):
        """Create info bar with status and workers label."""
        main_frame = self.widgets['main_frame']
        
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=0)
        
        # Status label (left, expands)
        self.app.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(info_frame, textvariable=self.app.status_var, 
                              relief="sunken", anchor="w")
        status_bar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Workers label (right, fixed width)
        self.app.workers_label = ttk.Label(info_frame, 
                                           text=f"Workers: {self.app.num_workers}",
                                           relief="sunken", anchor="center",
                                           width=12)
        self.app.workers_label.grid(row=0, column=1, sticky="e")
        
    def _create_progress_bar(self):
        """Create progress bar."""
        main_frame = self.widgets['main_frame']
        
        self.app.progress_var = tk.DoubleVar(value=0)
        self.app.progress = ttk.Progressbar(main_frame, variable=self.app.progress_var, maximum=100)
        self.app.progress.grid(row=4, column=0, sticky="ew", pady=(2, 0))
        
    def update_progress(self, progress):
        """Update progress bar value."""
        self.app.progress_var.set(progress)
        
    def update_status(self, message):
        """Update status bar message."""
        self.app.status_var.set(message)
