"""
Fractal rendering engine with support for sequential, parallel, and NumPy-accelerated computation.
"""

import multiprocessing
from typing import Tuple, List, Optional, Callable
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .fractals import FractalType, FractalFactory
from .palettes import PaletteFunc, PaletteFactory


def _calculate_chunk_numpy(args: Tuple) -> Tuple[int, int, np.ndarray]:
    """
    Calculate a chunk of rows using NumPy vectorization.
    Used as a worker function for parallel+numpy processing.
    
    Args:
        args: Tuple of (start_row, end_row, width, x_min, x_max, y_min, y_max,
              max_iter, fractal_name, fractal_params)
    
    Returns:
        Tuple of (start_row, end_row, iterations_array)
    """
    (start_row, end_row, width, height, x_min, x_max, y_min, y_max,
     max_iter, fractal_name, fractal_params) = args
    
    # Create fresh fractal instance in this process
    fractal = FractalFactory.create(fractal_name)
    if fractal is None:
        return (start_row, end_row, np.zeros((end_row - start_row, width), dtype=np.int32))
    
    # Apply parameters
    for param_name, param_value in fractal_params.items():
        fractal.set_parameter(param_name, param_value)
    
    # Calculate y bounds for this chunk
    y_step = (y_max - y_min) / height
    chunk_y_min = y_min + start_row * y_step
    chunk_y_max = y_min + end_row * y_step
    
    # Create coordinate arrays for this chunk
    x_coords = np.linspace(x_min, x_max, width)
    y_coords = np.linspace(chunk_y_min, chunk_y_max, end_row - start_row, endpoint=False)
    x_grid, y_grid = np.meshgrid(x_coords, y_coords)
    
    # Calculate iterations using vectorized method
    iterations = fractal.calculate_array(x_grid, y_grid, max_iter)
    
    return (start_row, end_row, iterations)


class FractalRenderer:
    """
    Renders fractals to pixel data with support for
    sequential, parallel, and NumPy-accelerated computation.
    """
    
    def __init__(self):
        self._use_parallel = True  # Parallel enabled by default
        self._use_numpy = True     # NumPy acceleration enabled by default
        self._worker_count = max(1, multiprocessing.cpu_count())
        self._min_rows_per_worker = 50  # Minimum rows per chunk to amortize overhead
    
    @property
    def use_parallel(self) -> bool:
        return self._use_parallel
    
    @use_parallel.setter
    def use_parallel(self, value: bool) -> None:
        self._use_parallel = value
    
    @property
    def use_numpy(self) -> bool:
        return self._use_numpy
    
    @use_numpy.setter
    def use_numpy(self, value: bool) -> None:
        self._use_numpy = value
    
    def render(
        self,
        fractal: FractalType,
        palette_name: str,
        width: int,
        height: int,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        max_iter: int,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[List[Tuple[int, int, int]]]:
        """
        Render a fractal to a 2D array of RGB tuples.
        
        Args:
            fractal: The fractal type to render
            palette_name: Name of the color palette to use
            width: Width in pixels
            height: Height in pixels
            x_min, x_max: Real axis bounds
            y_min, y_max: Imaginary axis bounds
            max_iter: Maximum iteration count
            progress_callback: Optional callback for progress updates (0.0-1.0)
            
        Returns:
            2D list of RGB tuples [row][column]
        """
        if self._use_numpy and self._use_parallel:
            return self._render_numpy_parallel(
                fractal, palette_name, width, height,
                x_min, x_max, y_min, y_max, max_iter, progress_callback
            )
        elif self._use_numpy:
            return self._render_numpy(
                fractal, palette_name, width, height,
                x_min, x_max, y_min, y_max, max_iter, progress_callback
            )
        elif self._use_parallel:
            return self._render_parallel(
                fractal, palette_name, width, height,
                x_min, x_max, y_min, y_max, max_iter, progress_callback
            )
        else:
            return self._render_sequential(
                fractal, palette_name, width, height,
                x_min, x_max, y_min, y_max, max_iter, progress_callback
            )
    
    def _render_sequential(
        self,
        fractal: FractalType,
        palette_name: str,
        width: int,
        height: int,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        max_iter: int,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[List[Tuple[int, int, int]]]:
        """Render using sequential processing."""
        palette = PaletteFactory.get(palette_name)
        pixels = []
        
        x_step = (x_max - x_min) / width
        y_step = (y_max - y_min) / height
        
        for py in range(height):
            y = y_min + py * y_step
            row = []
            
            for px in range(width):
                x = x_min + px * x_step
                iter_count = fractal.calculate(x, y, max_iter)
                color = palette(iter_count, max_iter)
                row.append(color)
            
            pixels.append(row)
            
            if progress_callback and py % 10 == 0:
                progress_callback(py / height)
        
        if progress_callback:
            progress_callback(1.0)
        
        return pixels
    
    def _render_parallel(
        self,
        fractal: FractalType,
        palette_name: str,
        width: int,
        height: int,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        max_iter: int,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[List[Tuple[int, int, int]]]:
        """Render using parallel processing."""
        # Determine optimal worker count
        num_workers = min(
            self._worker_count,
            max(1, height // self._min_rows_per_worker)
        )
        # Always have at least one worker
        num_workers = max(1, num_workers)
        
        y_step = (y_max - y_min) / height
        
        # Get fractal name and parameters for serialization
        fractal_name = None
        for name, display_name in FractalFactory.get_available().items():
            if display_name == fractal.name:
                fractal_name = name
                break
        
        if fractal_name is None:
            # Fallback to sequential if we can't identify the fractal
            return self._render_sequential(
                fractal, palette_name, width, height,
                x_min, x_max, y_min, y_max, max_iter, progress_callback
            )
        
        fractal_params = fractal.parameters
        
        # Prepare row arguments
        row_args = []
        for py in range(height):
            y_coord = y_min + py * y_step
            row_args.append((
                py, width, x_min, x_max, y_coord,
                max_iter, fractal_name, fractal_params, palette_name
            ))
        
        # Initialize result array
        pixels = [None] * height
        completed = 0
        
        # Process rows in parallel
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            for row_idx, row_colors in executor.map(_calculate_row, row_args):
                pixels[row_idx] = row_colors
                completed += 1
                
                if progress_callback and completed % 10 == 0:
                    progress_callback(completed / height)
        
        if progress_callback:
            progress_callback(1.0)
        
        return pixels
    
    def _render_numpy(
        self,
        fractal: FractalType,
        palette_name: str,
        width: int,
        height: int,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        max_iter: int,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[List[Tuple[int, int, int]]]:
        """Render using NumPy-accelerated computation (single-threaded)."""
        palette = PaletteFactory.get(palette_name)
        
        if progress_callback:
            progress_callback(0.1)
        
        # Create coordinate arrays
        x_coords = np.linspace(x_min, x_max, width)
        y_coords = np.linspace(y_min, y_max, height)
        x_grid, y_grid = np.meshgrid(x_coords, y_coords)
        
        if progress_callback:
            progress_callback(0.2)
        
        # Calculate iterations using vectorized method
        iterations = fractal.calculate_array(x_grid, y_grid, max_iter)
        
        if progress_callback:
            progress_callback(0.8)
        
        # Apply color palette using vectorized approach
        pixels = self._apply_palette_vectorized(iterations, palette, max_iter, height, width)
        
        if progress_callback:
            progress_callback(1.0)
        
        return pixels
    
    def _render_numpy_parallel(
        self,
        fractal: FractalType,
        palette_name: str,
        width: int,
        height: int,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        max_iter: int,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[List[Tuple[int, int, int]]]:
        """Render using NumPy + multiprocessing for maximum performance."""
        palette = PaletteFactory.get(palette_name)
        
        # Get fractal name and parameters for serialization
        fractal_name = None
        for name, display_name in FractalFactory.get_available().items():
            if display_name == fractal.name:
                fractal_name = name
                break
        
        if fractal_name is None:
            # Fallback to single-threaded numpy
            return self._render_numpy(
                fractal, palette_name, width, height,
                x_min, x_max, y_min, y_max, max_iter, progress_callback
            )
        
        fractal_params = fractal.parameters
        
        # Determine chunk distribution
        num_workers = min(self._worker_count, max(1, height // self._min_rows_per_worker))
        rows_per_chunk = height // num_workers
        
        # Prepare chunk arguments
        chunk_args = []
        for i in range(num_workers):
            start_row = i * rows_per_chunk
            end_row = height if i == num_workers - 1 else (i + 1) * rows_per_chunk
            chunk_args.append((
                start_row, end_row, width, height,
                x_min, x_max, y_min, y_max,
                max_iter, fractal_name, fractal_params
            ))
        
        if progress_callback:
            progress_callback(0.1)
        
        # Process chunks in parallel
        iterations = np.zeros((height, width), dtype=np.int32)
        completed_chunks = 0
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            for start_row, end_row, chunk_iterations in executor.map(_calculate_chunk_numpy, chunk_args):
                iterations[start_row:end_row, :] = chunk_iterations
                completed_chunks += 1
                if progress_callback:
                    progress_callback(0.1 + 0.7 * (completed_chunks / num_workers))
        
        if progress_callback:
            progress_callback(0.8)
        
        # Apply color palette
        pixels = self._apply_palette_vectorized(iterations, palette, max_iter, height, width)
        
        if progress_callback:
            progress_callback(1.0)
        
        return pixels
    
    def _apply_palette_vectorized(
        self,
        iterations: np.ndarray,
        palette: PaletteFunc,
        max_iter: int,
        height: int,
        width: int
    ) -> List[List[Tuple[int, int, int]]]:
        """Apply color palette to iteration counts."""
        # Build a lookup table for the palette (more efficient than per-pixel calls)
        palette_lut = [palette(i, max_iter) for i in range(max_iter + 1)]
        
        # Apply palette using lookup table
        pixels = []
        for py in range(height):
            row = [palette_lut[iterations[py, px]] for px in range(width)]
            pixels.append(row)
        
        return pixels
