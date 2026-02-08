# Unit Tests for Fractal Explorer

## Running Tests

### Run all tests:
```bash
python3 tests/run_tests.py
```

### Run specific test file:
```bash
python3 tests/test_fractals.py
python3 tests/test_integration.py
```

## Test Coverage

### test_fractals.py (19 tests)
- **FractalRegistry**: Registration, creation, default bounds validation
- **Mandelbrot**: Origin in set, points outside set, negative coordinates
- **Julia**: Creation with parameters
- **IFSFractals**: Point generation, image rendering for Sierpinski and Barnsley fern
- **PaletteRegistry**: Registration, color generation, max iter handling
- **BoundsCalculations**: Mandelbrot default bounds
- **ParameterHandling**: Julia and Multibrot parameters
- **Performance**: IFS rendering speed (< 1s for 10k points)

### test_integration.py (10 tests)
- **FractalComputationCorrectness**: Known points in/out of Mandelbrot set
- **PaletteConsistency**: Smooth palette variation, banded palette discrete bands
- **IFSGeometry**: Sierpinski area coverage, dragon curve bounds
- **Registry**: Singleton behavior, unknown fractal/palette handling

## Test Results

All 29 tests pass successfully:
- Registry functionality
- Fractal computation correctness
- Palette color generation
- IFS point generation and rendering
- Parameter handling
- Error handling
- Performance requirements

## Adding New Tests

To add tests for a new fractal:

1. Import the fractal module in `test_fractals.py`
2. Add tests to appropriate test class or create new class
3. Run `python3 tests/run_tests.py` to verify

Example:
```python
def test_new_fractal(self):
    fractal = FractalRegistry.create('new_fractal')
    self.assertIsNotNone(fractal)
    result = fractal.compute_pixel(0.0, 0.0, 100)
    self.assertIsInstance(result, (int, float))
```
