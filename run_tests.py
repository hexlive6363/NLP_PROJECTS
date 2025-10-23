#!/usr/bin/env python3
"""
Run all tests for SelfIndex.
"""

import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_all_tests():
    """Discover and run all tests."""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on success
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
