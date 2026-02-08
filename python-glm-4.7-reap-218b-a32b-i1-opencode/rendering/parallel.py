"""Parallel computation for fractal rendering."""

import multiprocessing
from typing import Callable, Optional
import numpy as np


def _render_worker(args):
    """Worker function for parallel rendering.
    
    Args:
        args: Tuple of (fractal_class_id, palette_class_id, row_indices,
                       bounds, width, height, max_iter)
                       
    Returns:
        List of (row_index, RGB_values) tuples
    """
    from fractals import get_fractal
    from palettes import get_palette
    
    (fractal_instance, palette_instance, row_indices,
     bounds, width, height, max_iter) = args
    
    dx = (bounds["xmax"] - bounds["xmin"]) / width
    dy = (bounds["ymax"] - bounds["ymin"]) / height
    
    results = []
    
    for py in row_indices:
        y = bounds["ymax"] - (py + 0.5) * dy
        
        rgb_row = np.zeros((width, 3), dtype=np.uint8)
        
        for px in range(width):
            x = bounds["xmin"] + (px + 0.5) * dx
            
            value = fractal_instance.compute_pixel(x, y, max_iter)
            color = palette_instance.get_color(value, max_iter)
            
            rgb_row[px] = color
        
        results.append((py, rgb_row))
    
    return results


class ParallelRenderer:
    """Parallel renderer using multiprocessing."""
    
    def __init__(self, workers: int = None):
        """Initialize the parallel renderer.
        
        Args:
            workers: Number of worker processes (None to auto-detect)
        """
        if workers is None:
            self.workers = max(1, multiprocessing.cpu_count() - 1)
        else:
            self.workers = max(1, workers)
    
    def render(self, fractal, palette, bounds: dict, width: int, height: int,
               max_iter: int, progress_callback: Optional[Callable[[int, int], None]] = None):
        """Render a fractal image in parallel.
        
        Args:
            fractal: Fractal instance to render
            palette: Palette instance for coloring
            bounds: Coordinate bounds dictionary
            width: Image width in pixels
            height: Image height in pixels
            max_iter: Maximum iterations per pixel
            progress_callback: Optional callback function (completed_rows, total_rows)
            
        Returns:
            2D numpy array of RGB values shape (height, width, 3)
        """
        result = np.zeros((height, width, 3), dtype=np.uint8)
        
        rows_per_worker = height // self.workers
        worker_args = []
        
        for i in range(self.workers):
            start_row = i * rows_per_worker
            if i == self.workers - 1:
                end_row = height
            else:
                end_row = start_row + rows_per_worker
            
            row_indices = list(range(start_row, end_row))
            
            worker_args.append((
                fractal,
                palette,
                row_indices,
                bounds,
                width,
                height,
                max_iter
            ))
        
        completed_rows = 0
        
        with multiprocessing.Pool(processes=self.workers) as pool:
            for worker_results in pool.imap(_render_worker, worker_args):
                for py, rgb_row in worker_results:
                    result[py] = rgb_row
                    completed_rows += 1
                    
                    if progress_callback and completed_rows % 10 == 0:
                        progress_callback(completed_rows, height)
        
        if progress_callback:
            progress_callback(height, height)
        
        return result