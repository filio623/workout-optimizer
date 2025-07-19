#!/usr/bin/env python3
"""
Test script for the exercise static file functionality.
"""

import logging
import time
from app.services.exercise_cache import exercise_cache

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_static_file_functionality():
    """Test the exercise static file functionality."""
    
    print("🧪 Testing Exercise Static File Functionality")
    print("=" * 55)
    
    # Test 1: Get file info (should show static file info)
    print("\n1. Checking static file status...")
    cache_info = exercise_cache.get_cache_info()
    print(f"   File exists: {cache_info['exists']}")
    print(f"   File path: {cache_info['file_path']}")
    print(f"   Exercise count: {cache_info['exercise_count']}")
    
    # Test 2: First fetch (should load from static file)
    print("\n2. First fetch (should load from static file)...")
    start_time = time.time()
    exercises = exercise_cache.get_exercise_templates()
    fetch_time = time.time() - start_time
    print(f"   Fetched {len(exercises)} exercises in {fetch_time:.2f} seconds")
    
    # Test 3: Second fetch (should load from static file again)
    print("\n3. Second fetch (should load from static file again)...")
    start_time = time.time()
    exercises_cached = exercise_cache.get_exercise_templates()
    fetch_time = time.time() - start_time
    print(f"   Fetched {len(exercises_cached)} exercises in {fetch_time:.2f} seconds")
    
    # Test 4: Verify file info
    print("\n4. Checking file status after fetch...")
    cache_info = exercise_cache.get_cache_info()
    print(f"   File exists: {cache_info['exists']}")
    print(f"   Exercise count: {cache_info['exercise_count']}")
    print(f"   File age: {cache_info['age']}")
    print(f"   Last modified: {cache_info.get('last_modified', 'N/A')}")
    
    # Test 5: Force reload
    print("\n5. Force reloading from static file...")
    start_time = time.time()
    exercises_refreshed = exercise_cache.refresh_cache()
    fetch_time = time.time() - start_time
    print(f"   Reloaded {len(exercises_refreshed)} exercises in {fetch_time:.2f} seconds")
    
    # Test 6: Sample exercise data
    print("\n6. Sample exercise data:")
    if exercises:
        sample_exercise = exercises[0]
        print(f"   First exercise: {sample_exercise.title}")
        print(f"   Type: {sample_exercise.exercise_type}")
        print(f"   Primary muscle: {sample_exercise.primary_muscle_group}")
        print(f"   Equipment: {sample_exercise.equipment}")
    
    print("\n✅ Static file testing completed!")


if __name__ == "__main__":
    test_static_file_functionality() 