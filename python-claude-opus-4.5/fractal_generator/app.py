"""
Main application - Tkinter-based fractal explorer GUI.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
from typing import Optional, Tuple, List

from .fractals import FractalFactory, FractalType
from .palettes import PaletteFactory
from .renderer import FractalRenderer
from .state import SessionState, FractalState, ViewState


class FractalApp:
    """Main fractal explorer application."""
    
    # Canvas dimensions
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    
    # Iteration limits
    MIN_ITERATIONS = 10
    MAX_ITERATIONS = 1000
    DEFAULT_ITERATIONS = 100
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Fractal Explorer")
        self.root.resizable(True, True)
        
        # Core components
        self.renderer = FractalRenderer()
        self.session = SessionState()
        
        # Current state
        self._current_fractal: Optional[FractalType] = None
        self._current_palette: str = "Classic"
        self._max_iter: int = self.DEFAULT_ITERATIONS
        
        # View bounds
        self._x_min = -2.5
        self._x_max = 1.0
        self._y_min = -1.5
        self._y_max = 1.5
        
        # Selection rectangle for zooming
        self._selection_start: Optional[Tuple[int, int]] = None
        self._selection_rect: Optional[int] = None
        
        # Image data
        self._photo_image: Optional[ImageTk.PhotoImage] = None
        self._pixel_data: Optional[List[List[Tuple[int, int, int]]]] = None
        
        # Rendering state
        self._is_rendering = False
        
        # Track canvas size to detect real resizes vs layout jitter
        self._last_render_size: Optional[Tuple[int, int]] = None
        
        # Build UI
        self._create_ui()
        
        # Bind keyboard shortcuts
        self._bind_keyboard_shortcuts()
        
        # Schedule initial fractal load after window is fully laid out
        self.root.after(50, self._initialize_fractal)
    
    def _create_ui(self):
        """Create the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Controls frame (top)
        self._create_controls(main_frame)
        
        # Canvas frame (center)
        self._create_canvas(main_frame)
        
        # Status bar (bottom)
        self._create_status_bar(main_frame)
    
    def _create_controls(self, parent):
        """Create the control panel."""
        controls_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Row 1: Fractal and palette selection
        row1 = ttk.Frame(controls_frame)
        row1.pack(fill="x", pady=2)
        
        # Fractal selector
        ttk.Label(row1, text="Fractal:").pack(side="left", padx=(0, 5))
        self._fractal_var = tk.StringVar()
        self._fractal_combo = ttk.Combobox(
            row1, 
            textvariable=self._fractal_var,
            state="readonly",
            width=15
        )
        fractals = FractalFactory.get_available()
        self._fractal_combo['values'] = list(fractals.values())
        self._fractal_combo.pack(side="left", padx=(0, 15))
        self._fractal_combo.bind('<<ComboboxSelected>>', self._on_fractal_changed)
        
        # Palette selector
        ttk.Label(row1, text="Palette:").pack(side="left", padx=(0, 5))
        self._palette_var = tk.StringVar(value="Classic")
        self._palette_combo = ttk.Combobox(
            row1,
            textvariable=self._palette_var,
            state="readonly",
            width=12
        )
        self._palette_combo['values'] = PaletteFactory.get_available()
        self._palette_combo.pack(side="left", padx=(0, 15))
        self._palette_combo.bind('<<ComboboxSelected>>', self._on_palette_changed)
        
        # Parallel toggle (on by default)
        self._parallel_var = tk.BooleanVar(value=True)
        self._parallel_check = ttk.Checkbutton(
            row1,
            text="Parallel",
            variable=self._parallel_var,
            command=self._on_parallel_toggled
        )
        self._parallel_check.pack(side="left", padx=(0, 15))
        
        # Undo button
        self._undo_btn = ttk.Button(
            row1,
            text="← Undo",
            command=self._on_undo_zoom,
            width=7
        )
        self._undo_btn.pack(side="left", padx=(0, 2))
        
        # Redo button
        self._redo_btn = ttk.Button(
            row1,
            text="Redo →",
            command=self._on_redo_zoom,
            width=7
        )
        self._redo_btn.pack(side="left", padx=(0, 10))
        
        # Reset button
        self._reset_btn = ttk.Button(
            row1,
            text="Reset View",
            command=self._on_reset_view
        )
        self._reset_btn.pack(side="left", padx=(0, 5))
        
        # Save button
        self._save_btn = ttk.Button(
            row1,
            text="Save Image",
            command=self._on_save_image
        )
        self._save_btn.pack(side="left")
        
        # Row 2: Iteration slider
        row2 = ttk.Frame(controls_frame)
        row2.pack(fill="x", pady=2)
        
        ttk.Label(row2, text="Iterations:").pack(side="left", padx=(0, 5))
        self._iter_var = tk.IntVar(value=self.DEFAULT_ITERATIONS)
        self._iter_slider = ttk.Scale(
            row2,
            from_=self.MIN_ITERATIONS,
            to=self.MAX_ITERATIONS,
            orient="horizontal",
            variable=self._iter_var,
            command=self._on_iteration_changed
        )
        self._iter_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self._iter_label = ttk.Label(row2, text=str(self.DEFAULT_ITERATIONS), width=5)
        self._iter_label.pack(side="left")
        
        # Row 3: Parameter panel (dynamic)
        self._params_frame = ttk.Frame(controls_frame)
        self._params_frame.pack(fill="x", pady=2)
        self._param_widgets = {}
    
    def _create_canvas(self, parent):
        """Create the fractal canvas."""
        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self._canvas = tk.Canvas(
            canvas_frame,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg="black",
            cursor="crosshair"
        )
        self._canvas.grid(row=0, column=0, sticky="nsew")
        
        # Bind mouse events for zoom selection
        self._canvas.bind("<Button-1>", self._on_mouse_down)
        self._canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        
        # Bind mouse motion for coordinate display
        self._canvas.bind("<Motion>", self._on_mouse_move)
        self._canvas.bind("<Leave>", self._on_mouse_leave)
        
        # Handle resize
        self._canvas.bind("<Configure>", self._on_canvas_resize)
    
    def _create_status_bar(self, parent):
        """Create the status bar."""
        # Use a fixed height frame to prevent layout shifts
        status_frame = ttk.Frame(parent, height=30)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        status_frame.grid_propagate(False)  # Prevent frame from resizing to fit contents
        status_frame.columnconfigure(0, weight=0)  # Status label
        status_frame.columnconfigure(1, weight=1)  # Coordinate label (expandable)
        status_frame.columnconfigure(2, weight=0)  # Progress bar
        
        self._status_var = tk.StringVar(value="Ready")
        self._status_label = ttk.Label(
            status_frame,
            textvariable=self._status_var,
            width=50,
            anchor="w"
        )
        self._status_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Coordinate display (shows position under cursor)
        self._coord_var = tk.StringVar(value="")
        self._coord_label = ttk.Label(
            status_frame,
            textvariable=self._coord_var,
            width=45,
            anchor="w"
        )
        self._coord_label.grid(row=0, column=1, sticky="w")
        
        # Progress bar
        self._progress_var = tk.DoubleVar(value=0)
        self._progress_bar = ttk.Progressbar(
            status_frame,
            variable=self._progress_var,
            maximum=100,
            length=200
        )
        self._progress_bar.grid(row=0, column=2, sticky="e", padx=(10, 0))
    
    def _initialize_fractal(self):
        """Initialize with the first available fractal."""
        fractals = FractalFactory.get_available()
        if fractals:
            first_name = list(fractals.keys())[0]
            first_display = fractals[first_name]
            self._fractal_var.set(first_display)
            self._select_fractal(first_name)
    
    def _select_fractal(self, fractal_name: str):
        """Select and set up a fractal type."""
        # Save current state if we have a fractal
        if self._current_fractal:
            self._save_current_state()
        
        # Get or create the fractal
        self._current_fractal = FractalFactory.create(fractal_name)
        if not self._current_fractal:
            return
        
        self.session.set_current_fractal(fractal_name)
        
        # Restore or initialize state
        state = self.session.restore_state(fractal_name)
        
        # Check if this is a new fractal (use defaults)
        if state.x_min == -2.5 and state.x_max == 1.0:
            # Use fractal's default bounds
            bounds = self._current_fractal.default_bounds
            self._x_min, self._x_max, self._y_min, self._y_max = bounds
        else:
            self._x_min = state.x_min
            self._x_max = state.x_max
            self._y_min = state.y_min
            self._y_max = state.y_max
        
        self._max_iter = state.max_iter if state.max_iter != 100 else self.DEFAULT_ITERATIONS
        self._iter_var.set(self._max_iter)
        self._iter_label.config(text=str(self._max_iter))
        
        # Restore parameters
        for param_name, param_value in state.parameters.items():
            self._current_fractal.set_parameter(param_name, param_value)
        
        # Update parameter UI
        self._update_parameter_panel()
        
        # Render
        self._render()
    
    def _save_current_state(self):
        """Save current view state."""
        if self._current_fractal:
            fractal_name = self.session.current_fractal
            if fractal_name:
                self.session.save_state(
                    fractal_name,
                    self._x_min, self._x_max,
                    self._y_min, self._y_max,
                    self._max_iter,
                    self._current_fractal.parameters
                )
    
    def _update_parameter_panel(self):
        """Update the dynamic parameter panel for the current fractal."""
        # Clear existing widgets
        for widget in self._params_frame.winfo_children():
            widget.destroy()
        self._param_widgets.clear()
        
        if not self._current_fractal:
            return
        
        params = self._current_fractal.parameters
        if not params:
            return
        
        # Create widgets for each parameter
        col = 0
        for param_name, param_value in params.items():
            # Label
            label_text = param_name.replace('_', ' ').title()
            ttk.Label(self._params_frame, text=f"{label_text}:").grid(
                row=0, column=col, padx=(0, 2), sticky="e"
            )
            col += 1
            
            # Entry
            var = tk.StringVar(value=str(param_value))
            entry = ttk.Entry(self._params_frame, textvariable=var, width=10)
            entry.grid(row=0, column=col, padx=(0, 10), sticky="w")
            entry.bind('<Return>', lambda e, n=param_name: self._on_param_changed(n))
            entry.bind('<FocusOut>', lambda e, n=param_name: self._on_param_changed(n))
            
            self._param_widgets[param_name] = var
            col += 1
    
    def _on_param_changed(self, param_name: str):
        """Handle parameter value change."""
        if param_name not in self._param_widgets:
            return
        
        try:
            value = float(self._param_widgets[param_name].get())
            if param_name == 'exponent':
                value = int(value)
            self._current_fractal.set_parameter(param_name, value)
            self._render()
        except ValueError:
            pass  # Ignore invalid input
    
    def _on_fractal_changed(self, event):
        """Handle fractal selection change."""
        display_name = self._fractal_var.get()
        
        # Find internal name
        for name, disp in FractalFactory.get_available().items():
            if disp == display_name:
                self._select_fractal(name)
                break
    
    def _on_palette_changed(self, event):
        """Handle palette selection change."""
        self._current_palette = self._palette_var.get()
        self._render()
    
    def _on_iteration_changed(self, value):
        """Handle iteration slider change."""
        self._max_iter = int(float(value))
        self._iter_label.config(text=str(self._max_iter))
        # Don't render on every slider move - render on release
        self._iter_slider.bind('<ButtonRelease-1>', self._on_iteration_released)
    
    def _on_iteration_released(self, event):
        """Handle iteration slider release."""
        self._render()
    
    def _on_parallel_toggled(self):
        """Handle parallel toggle."""
        self.renderer.use_parallel = self._parallel_var.get()
        self._render()
    
    def _on_reset_view(self):
        """Reset to default view for current fractal."""
        if self._current_fractal:
            # Save current state to history before reset
            self._push_current_to_history()
            
            bounds = self._current_fractal.default_bounds
            self._x_min, self._x_max, self._y_min, self._y_max = bounds
            self._render()
            self._update_undo_redo_buttons()
    
    def _on_undo_zoom(self):
        """Undo the last zoom operation."""
        fractal_name = self.session.current_fractal
        if not fractal_name or not self._current_fractal:
            return
        
        # Get current view state to pass to undo
        current_view = self._get_current_view_state()
        view_state = self.session.undo_zoom(fractal_name, current_view)
        if view_state:
            self._apply_view_state(view_state)
            self._render()
            self._update_undo_redo_buttons()
    
    def _on_redo_zoom(self):
        """Redo the last undone zoom operation."""
        fractal_name = self.session.current_fractal
        if not fractal_name or not self._current_fractal:
            return
        
        # Get current view state to pass to redo
        current_view = self._get_current_view_state()
        view_state = self.session.redo_zoom(fractal_name, current_view)
        if view_state:
            self._apply_view_state(view_state)
            self._render()
            self._update_undo_redo_buttons()
    
    def _get_current_view_state(self) -> ViewState:
        """Get the current view as a ViewState object."""
        return ViewState(
            x_min=self._x_min,
            x_max=self._x_max,
            y_min=self._y_min,
            y_max=self._y_max,
            max_iter=self._max_iter,
            parameters=self._current_fractal.parameters.copy() if self._current_fractal else {}
        )
    
    def _apply_view_state(self, view_state: ViewState):
        """Apply a ViewState to the current view."""
        self._x_min = view_state.x_min
        self._x_max = view_state.x_max
        self._y_min = view_state.y_min
        self._y_max = view_state.y_max
        self._max_iter = view_state.max_iter
        self._iter_var.set(self._max_iter)
        self._iter_label.config(text=str(self._max_iter))
        
        # Apply parameters if available
        if view_state.parameters and self._current_fractal:
            for param_name, param_value in view_state.parameters.items():
                self._current_fractal.set_parameter(param_name, param_value)
            self._update_parameter_panel()
    
    def _push_current_to_history(self):
        """Push current view state to zoom history."""
        fractal_name = self.session.current_fractal
        if fractal_name and self._current_fractal:
            state = FractalState(
                x_min=self._x_min,
                x_max=self._x_max,
                y_min=self._y_min,
                y_max=self._y_max,
                max_iter=self._max_iter,
                parameters=self._current_fractal.parameters.copy()
            )
            self.session.push_to_history(fractal_name, state)
    
    def _update_undo_redo_buttons(self):
        """Update the enabled state of undo/redo buttons."""
        fractal_name = self.session.current_fractal
        if fractal_name:
            can_undo = self.session.can_undo(fractal_name)
            can_redo = self.session.can_redo(fractal_name)
            self._undo_btn.config(state="normal" if can_undo else "disabled")
            self._redo_btn.config(state="normal" if can_redo else "disabled")
        else:
            self._undo_btn.config(state="disabled")
            self._redo_btn.config(state="disabled")
    
    def _bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for common actions."""
        self.root.bind("<Control-z>", lambda e: self._on_undo_zoom())
        self.root.bind("<Control-y>", lambda e: self._on_redo_zoom())
        self.root.bind("<Control-Shift-Z>", lambda e: self._on_redo_zoom())
        self.root.bind("<r>", lambda e: self._on_reset_view())
        self.root.bind("<R>", lambda e: self._on_reset_view())
        self.root.bind("<Control-s>", lambda e: self._on_save_image())
    
    def _on_save_image(self):
        """Save current image to file."""
        if not self._pixel_data:
            messagebox.showwarning("No Image", "No image to save.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if filepath:
            self._save_image_to_file(filepath)
    
    def _save_image_to_file(self, filepath: str):
        """Save pixel data to image file."""
        height = len(self._pixel_data)
        width = len(self._pixel_data[0]) if height > 0 else 0
        
        image = Image.new('RGB', (width, height))
        
        for y, row in enumerate(self._pixel_data):
            for x, color in enumerate(row):
                image.putpixel((x, y), color)
        
        image.save(filepath, 'JPEG', quality=95)
        self._status_var.set(f"Saved to {filepath}")
    
    def _on_mouse_down(self, event):
        """Handle mouse button press for zoom selection."""
        if self._is_rendering:
            return
        
        self._selection_start = (event.x, event.y)
        
        # Create selection rectangle
        if self._selection_rect:
            self._canvas.delete(self._selection_rect)
        
        self._selection_rect = self._canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="white", width=2, dash=(4, 4)
        )
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag for zoom selection."""
        if not self._selection_start or not self._selection_rect:
            return
        
        # Update selection rectangle
        x0, y0 = self._selection_start
        self._canvas.coords(self._selection_rect, x0, y0, event.x, event.y)
    
    def _on_mouse_up(self, event):
        """Handle mouse button release - initiate zoom."""
        if not self._selection_start:
            return
        
        x0, y0 = self._selection_start
        x1, y1 = event.x, event.y
        
        # Clear selection
        if self._selection_rect:
            self._canvas.delete(self._selection_rect)
            self._selection_rect = None
        self._selection_start = None
        
        # Ensure valid selection (minimum size)
        if abs(x1 - x0) < 10 or abs(y1 - y0) < 10:
            return
        
        # Normalize coordinates
        px_min, px_max = min(x0, x1), max(x0, x1)
        py_min, py_max = min(y0, y1), max(y0, y1)
        
        # Get canvas dimensions
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        # Convert pixel coords to fractal coords
        x_range = self._x_max - self._x_min
        y_range = self._y_max - self._y_min
        
        new_x_min = self._x_min + (px_min / canvas_width) * x_range
        new_x_max = self._x_min + (px_max / canvas_width) * x_range
        new_y_min = self._y_min + (py_min / canvas_height) * y_range
        new_y_max = self._y_min + (py_max / canvas_height) * y_range
        
        # Save current state to history before zooming
        self._push_current_to_history()
        
        # First, show zoomed preview of existing pixels
        self._show_zoom_preview(px_min, py_min, px_max, py_max)
        
        # Update bounds
        self._x_min, self._x_max = new_x_min, new_x_max
        self._y_min, self._y_max = new_y_min, new_y_max
        
        # Render new view
        self._render()
        self._update_undo_redo_buttons()
    
    def _show_zoom_preview(self, px_min: int, py_min: int, px_max: int, py_max: int):
        """Show a preview by expanding the selected region."""
        if not self._pixel_data:
            return
        
        # Get selection dimensions
        sel_width = px_max - px_min
        sel_height = py_max - py_min
        
        # Get canvas dimensions
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        # Create zoomed preview image
        preview_image = Image.new('RGB', (canvas_width, canvas_height))
        
        for cy in range(canvas_height):
            # Map canvas y to selection y
            src_y = int(py_min + (cy / canvas_height) * sel_height)
            src_y = max(0, min(src_y, len(self._pixel_data) - 1))
            
            for cx in range(canvas_width):
                # Map canvas x to selection x
                src_x = int(px_min + (cx / canvas_width) * sel_width)
                src_x = max(0, min(src_x, len(self._pixel_data[0]) - 1))
                
                color = self._pixel_data[src_y][src_x]
                preview_image.putpixel((cx, cy), color)
        
        # Display preview
        self._photo_image = ImageTk.PhotoImage(preview_image)
        self._canvas.create_image(0, 0, anchor="nw", image=self._photo_image)
        self._canvas.update()
    
    def _on_mouse_move(self, event):
        """Handle mouse movement for coordinate display."""
        if self._is_rendering:
            return
        
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        if canvas_width <= 0 or canvas_height <= 0:
            return
        
        # Convert pixel coordinates to fractal coordinates
        x_range = self._x_max - self._x_min
        y_range = self._y_max - self._y_min
        
        real = self._x_min + (event.x / canvas_width) * x_range
        imag = self._y_min + (event.y / canvas_height) * y_range
        
        # Display coordinates
        self._coord_var.set(f"c = {real:.10f} + {imag:.10f}i")
    
    def _on_mouse_leave(self, event):
        """Handle mouse leaving canvas."""
        self._coord_var.set("")
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize."""
        new_size = (event.width, event.height)
        
        # Skip if we haven't rendered yet (will be handled by _initialize_fractal)
        if self._last_render_size is None:
            return
        
        # Only re-render if size actually changed significantly from last render
        if abs(new_size[0] - self._last_render_size[0]) < 10 and \
           abs(new_size[1] - self._last_render_size[1]) < 10:
            return
        
        # Debounce resize events
        if hasattr(self, '_resize_after_id'):
            self.root.after_cancel(self._resize_after_id)
        
        self._resize_after_id = self.root.after(200, self._render)
    
    def _render(self):
        """Render the current fractal."""
        if not self._current_fractal or self._is_rendering:
            return
        
        # Get current canvas size
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        
        # If canvas isn't ready yet (too small), schedule a retry
        if canvas_width < 50 or canvas_height < 50:
            self.root.after(100, self._render)
            return
        
        self._is_rendering = True
        self._set_controls_state("disabled")
        self._status_var.set("Rendering...")
        self._progress_var.set(0)
        
        # Capture render parameters for diagnostics
        fractal_name = self._current_fractal.name
        palette_name = self._current_palette
        max_iter = self._max_iter
        use_numpy = self.renderer.use_numpy
        use_parallel = self.renderer.use_parallel
        
        # Render in background thread
        def render_task():
            try:
                start_time = time.perf_counter()
                
                pixels = self.renderer.render(
                    self._current_fractal,
                    self._current_palette,
                    canvas_width,
                    canvas_height,
                    self._x_min, self._x_max,
                    self._y_min, self._y_max,
                    self._max_iter,
                    progress_callback=self._update_progress
                )
                
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                
                # Diagnostic output
                if use_numpy and use_parallel:
                    mode = "numpy+parallel"
                elif use_numpy:
                    mode = "numpy"
                elif use_parallel:
                    mode = "parallel"
                else:
                    mode = "sequential"
                print(f"[Render] {fractal_name} | {palette_name} | {canvas_width}x{canvas_height} | iter={max_iter} | {mode} | {elapsed_ms:.1f}ms")
                
                # Update UI in main thread
                self.root.after(0, lambda: self._display_pixels(pixels))
                
            except Exception as e:
                self.root.after(0, lambda: self._on_render_error(str(e)))
        
        thread = threading.Thread(target=render_task, daemon=True)
        thread.start()
    
    def _update_progress(self, progress: float):
        """Update progress bar (called from render thread)."""
        self.root.after(0, lambda: self._progress_var.set(progress * 100))
    
    def _display_pixels(self, pixels: List[List[Tuple[int, int, int]]]):
        """Display rendered pixels on canvas."""
        self._pixel_data = pixels
        
        height = len(pixels)
        width = len(pixels[0]) if height > 0 else 0
        
        # Create image from pixels
        image = Image.new('RGB', (width, height))
        
        for y, row in enumerate(pixels):
            for x, color in enumerate(row):
                image.putpixel((x, y), color)
        
        # Display on canvas
        self._photo_image = ImageTk.PhotoImage(image)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, anchor="nw", image=self._photo_image)
        
        self._is_rendering = False
        self._set_controls_state("normal")
        self._status_var.set(
            f"View: [{self._x_min:.6f}, {self._x_max:.6f}] x "
            f"[{self._y_min:.6f}, {self._y_max:.6f}]"
        )
        self._progress_var.set(100)
        self._update_undo_redo_buttons()
        
        # Store the size we rendered at to detect actual resizes
        self._last_render_size = (width, height)
    
    def _on_render_error(self, error: str):
        """Handle rendering error."""
        self._is_rendering = False
        self._set_controls_state("normal")
        self._status_var.set(f"Error: {error}")
        messagebox.showerror("Render Error", error)
    
    def _set_controls_state(self, state: str):
        """Enable or disable controls."""
        self._fractal_combo.config(state=state if state == "normal" else "disabled")
        self._palette_combo.config(state=state if state == "normal" else "disabled")
        self._reset_btn.config(state=state)
        self._save_btn.config(state=state)
        
        # Update undo/redo based on history availability
        if state == "normal":
            self._update_undo_redo_buttons()
        else:
            self._undo_btn.config(state="disabled")
            self._redo_btn.config(state="disabled")


def main():
    """Application entry point."""
    root = tk.Tk()
    app = FractalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
