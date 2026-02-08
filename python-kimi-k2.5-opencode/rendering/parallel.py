"""Parallel computation utilities for fractal rendering."""

import numpy as np
import multiprocessing as mp
from typing import Callable, Optional


def compute_row_wrapper(args):
    """Wrapper for computing a single row - must be module-level for pickling."""
    row_idx, x_coords, y_coord, fractal_name, fractal_params, max_iter, palette_name, palette_params = args
    
    # Import here to avoid circular imports and ensure fresh imports in subprocess
    from fractals import FractalRegistry
    from palettes import PaletteRegistry
    
    # Create fractal and palette instances
    try:
        fractal = FractalRegistry.create(fractal_name, **fractal_params)
        palette = PaletteRegistry.create(palette_name, **palette_params)
    except Exception as e:
        # Return empty row on error
        width = len(x_coords)
        return (row_idx, np.zeros((width, 3), dtype=np.uint8))
    
    width = len(x_coords)
    row = np.zeros((width, 3), dtype=np.uint8)
    
    for j in range(width):
        x = x_coords[j]
        value = fractal.compute_pixel(x, y_coord, max_iter)
        row[j] = palette.get_color(value, max_iter)
    
    return (row_idx, row)


def compute_fractal_parallel(
    width: int,
    height: int,
    bounds: dict,
    fractal_name: str,
    fractal_params: dict,
    max_iter: int,
    palette_name: str,
    palette_params: dict,
    num_workers: Optional[int] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> Optional[np.ndarray]:
    """
    Compute fractal using parallel processing.
    
    Args:
        width, height: Image dimensions
        bounds: Viewport bounds dict with xmin, xmax, ymin, ymax
        fractal_name: Name of fractal to use
        fractal_params: Parameters for fractal
        max_iter: Maximum iterations
        palette_name: Name of palette to use
        palette_params: Parameters for palette
        num_workers: Number of worker processes (default: CPU count - 1)
        progress_callback: Called with progress percentage (0-100)
        cancel_check: Called periodically, return True to cancel
        
    Returns:
        Numpy array of shape (height, width, 3) or None if cancelled
    """
    if num_workers is None:
        num_workers = max(1, mp.cpu_count() - 1)
    
    # Generate coordinate arrays
    x = np.linspace(bounds["xmin"], bounds["xmax"], width)
    y = np.linspace(bounds["ymin"], bounds["ymax"], height)
    
    # Prepare arguments for each row
    rows_args = []
    for i in range(height):
        y_coord = y[height - 1 - i]  # Flip y for correct orientation
        rows_args.append((
            i, x, y_coord,
            fractal_name, fractal_params,
            max_iter,
            palette_name, palette_params
        ))
    
    # Create output array
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    try:
        with mp.Pool(processes=num_workers) as pool:
            results = pool.imap_unordered(compute_row_wrapper, rows_args)
            
            completed = 0
            for row_idx, row_data in results:
                if cancel_check and cancel_check():
                    pool.terminate()
                    return None
                
                img_array[row_idx] = row_data
                completed += 1
                
                if progress_callback and completed % 10 == 0:
                    progress = (completed / height) * 100
                    progress_callback(progress)
            
            if progress_callback:
                progress_callback(100.0)
                
    except Exception as e:
        print(f"Error in parallel computation: {e}")
        return None
    
    return img_array


def compute_fractal_sequential(
    width: int,
    height: int,
    bounds: dict,
    fractal_compute: Callable[[float, float, int], float],
    max_iter: int,
    palette_get_color: Callable[[float, float], tuple],
    progress_callback: Optional[Callable[[float], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> Optional[np.ndarray]:
    """
    Compute fractal sequentially (fallback method).
    
    Args:
        width, height: Image dimensions
        bounds: Viewport bounds
        fractal_compute: Function(x, y, max_iter) -> value
        max_iter: Maximum iterations
        palette_get_color: Function(value, max_iter) -> (r, g, b)
        progress_callback: Called with progress percentage
        cancel_check: Called periodically, return True to cancel
        
    Returns:
        Numpy array or None if cancelled
    """
    x = np.linspace(bounds["xmin"], bounds["xmax"], width)
    y = np.linspace(bounds["ymin"], bounds["ymax"], height)
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    for i in range(height):
        if cancel_check and cancel_check():
            return None
        
        y_coord = y[height - 1 - i]
        for j in range(width):
            value = fractal_compute(x[j], y_coord, max_iter)
            img_array[i, j] = palette_get_color(value, max_iter)
        
        if progress_callback and i % 10 == 0:
            progress = ((i + 1) / height) * 100
            progress_callback(progress)
    
    if progress_callback:
        progress_callback(100.0)
    
    return img_array
