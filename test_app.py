#!/usr/bin/env python3
"""
Simple test script for the Workout Optimizer app.
Run with: python test_app.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.legacy.test_full_app import main

if __name__ == "__main__":
    main() 