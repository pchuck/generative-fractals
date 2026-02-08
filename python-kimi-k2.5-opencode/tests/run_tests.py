#!/usr/bin/env python3
"""Run all unit and integration tests."""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Discover and run all tests
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Get the tests directory
tests_dir = os.path.dirname(os.path.abspath(__file__))

# Discover all tests
discover = loader.discover(tests_dir, pattern="test_*.py")
suite.addTests(discover)

# Run with verbose output
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with appropriate code
sys.exit(0 if result.wasSuccessful() else 1)
