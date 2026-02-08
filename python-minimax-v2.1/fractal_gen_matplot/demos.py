"""
Quick demo scripts for common fractal explorations.

Run with: python demos.py --fractal mandelbrot|julia|burning_ship
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import FractalExplorer
from fractals.mandelbrot import MandelbrotSet
from fractals.julia import JuliaSet


def demo_mandelbrot():
    """Explore the classic Mandelbrot set."""
    print("Starting Mandelbrot Explorer...")
    explorer = FractalExplorer(
        fractal_set=MandelbrotSet(max_iterations=500),
        width=900,
        height=700
    )
    explorer.show()


def demo_julia_douady_rabbit():
    """Explore Douady's rabbit Julia set."""
    print("Starting Douady's Rabbit Explorer...")
    # c = -0.7 + 0.27015j produces the famous "rabbit" shape
    explorer = FractalExplorer(
        fractal_set=JuliaSet(c=-0.7 + 0.27015j, max_iterations=500),
        width=900,
        height=700
    )
    explorer.show()


def demo_julia_dendrite():
    """Explore the dendrite Julia set."""
    print("Starting Dendrite Explorer...")
    # c = -0.7269 + 0.1889j produces dendritic patterns
    explorer = FractalExplorer(
        fractal_set=JuliaSet(c=-0.7269 + 0.1889j, max_iterations=500),
        width=900,
        height=700
    )
    explorer.show()


def demo_julia_custom():
    """Explore with custom c value."""
    import cmath
    
    # Let user specify c or use default interesting value
    print("Starting Custom Julia Set Explorer...")
    # This produces a connected " Siegel disk" type structure
    explorer = FractalExplorer(
        fractal_set=JuliaSet(c=-0.4 + 0.6j, max_iterations=500),
        width=900,
        height=700
    )
    explorer.show()


def list_demos():
    print("Available demos:")
    print("  mandelbrot     - Classic Mandelbrot set")
    print("  julia-rabbit   - Douady's rabbit Julia set")
    print("  julia-dendrite - Dendrite Julia set")
    print("  julia-custom   - Custom c value (-0.4 + 0.6j)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_demos()
        sys.exit(1)

    demo_name = sys.argv[1].lower()

    demos = {
        'mandelbrot': demo_mandelbrot,
        'julia-rabbit': lambda: demo_julia_douady_rabbit(),
        'julia-dendrite': lambda: demo_julia_dendrite(),
        'julia-custom': lambda: demo_julia_custom(),
    }

    if demo_name in demos:
        try:
            demos[demo_name]()
        except KeyboardInterrupt:
            print("\nGoodbye!")
    else:
        print(f"Unknown demo: {demo_name}")
        list_demos()