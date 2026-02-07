"""Parallel rendering engine using multiprocessing."""

import numpy as np
from typing import List, Tuple
from PIL import Image


class FractalRenderer:
    """Thread-safe fractal renderer that works with multiprocessing."""
    
    def __init__(self, fractal, palette, max_iter, bounds):
        self.fractal = fractal
        self.palette = palette
        self.max_iter = max_iter
        if isinstance(bounds, dict):
            self.bounds = (bounds['xmin'], bounds['xmax'], bounds['ymin'], bounds['ymax'])
        else:
            self.bounds = bounds
    
    def render_row(self, y, width, height):
        """Render a single row."""
        row_colors = []
        
        for px in range(width):
            x = self.bounds[0] + (px / width) * (self.bounds[1] - self.bounds[0])
            y_val = self.bounds[2] + ((height - y) / height) * (self.bounds[3] - self.bounds[2])
            
            z = complex(x, y_val)
            value = self.fractal.compute_pixel(z.real, z.imag, self.max_iter)
            color = self.palette.get_color(value, float(self.max_iter))
            row_colors.append(color)
        
        return (y, row_colors)


def render_row_worker(args):
    """Worker function to render a single row."""
    renderer, y, width, height = args
    return renderer.render_row(y, width, height)


class ParallelRenderEngine:
    """Parallel rendering engine."""
    
    def __init__(self, num_workers=None):
        import multiprocessing
        self.num_workers = num_workers or max(1, multiprocessing.cpu_count() - 1)
    
    def render(self, width, height, fractal, palette, max_iter, progress_callback=None):
        """Render a fractal using parallel processing."""
        bounds = fractal.get_default_bounds()
        
        renderer = FractalRenderer(fractal, palette, max_iter, bounds)
        
        row_args = [(renderer, y, width, height) for y in range(height)]
        
        import multiprocessing
        with multiprocessing.Pool(processes=self.num_workers) as pool:
            results = []
            for y, row_colors in pool.imap_unordered(render_row_worker, row_args):
                results.append((y, row_colors))
                if progress_callback:
                    progress_callback(y + 1, height)
        
        results.sort(key=lambda x: x[0])
        
        img = Image.new('RGB', (width, height))
        for y, row_colors in results:
            for x, color in enumerate(row_colors):
                img.putpixel((x, y), color)
        
        return img
    
    def render_with_bounds(self, width, height, fractal, palette,
                          max_iter, bounds, progress_callback=None):
        """Render with custom bounds."""
        renderer = FractalRenderer(fractal, palette, max_iter, bounds)
        
        row_args = [(renderer, y, width, height) for y in range(height)]
        
        import multiprocessing
        with multiprocessing.Pool(processes=self.num_workers) as pool:
            results = []
            for y, row_colors in pool.imap_unordered(render_row_worker, row_args):
                results.append((y, row_colors))
                if progress_callback:
                    progress_callback(y + 1, height)
        
        results.sort(key=lambda x: x[0])
        
        img = Image.new('RGB', (width, height))
        for y, row_colors in results:
            for x, color in enumerate(row_colors):
                img.putpixel((x, y), color)
        
        return img
    
    def render_progressive(self, width, height, fractal, palette,
                          max_iter, progress_callback=None):
        """Render with progressive refinement."""
        preview_width = width // 4
        preview_height = height // 4
        
        bounds = fractal.get_default_bounds()
        
        total_rows = (preview_height + height)
        rows_completed = [0]
        
        def progress_wrapper(current, total):
            rows_completed[0] += current
            if progress_callback:
                progress_callback(rows_completed[0], total_rows)
        
        self.render_with_bounds(preview_width, preview_height, fractal, palette,
                               max_iter // 4, bounds, progress_wrapper)
        self.render_with_bounds(width, height, fractal, palette,
                                max_iter, bounds, progress_wrapper)
        
        return None


class ProgressiveRenderEngine(ParallelRenderEngine):
    """Progressive renderer that renders lower resolution first."""
    
    def render_progressive(self, width, height, fractal, palette,
                          max_iter):
        """Render both preview and detailed versions."""
        preview_width = width // 4
        preview_height = height // 4
        
        bounds = fractal.get_default_bounds()
        
        preview_img = self.render_with_bounds(
            preview_width, preview_height, fractal, palette,
            max_iter // 4, bounds
        )
        
        detailed_img = self.render_with_bounds(
            width, height, fractal, palette, max_iter, bounds
        )
        
        return preview_img, detailed_img


__all__ = ['ParallelRenderEngine', 'ProgressiveRenderEngine']
