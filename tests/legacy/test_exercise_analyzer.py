#!/usr/bin/env python3
"""
Test script for the exercise analyzer functionality.
"""

import logging
from backend.services.exercise_analyzer import exercise_analyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_exercise_analyzer():
    """Test the exercise analyzer functionality."""
    
    print("🧪 Testing Exercise Analyzer Functionality")
    print("=" * 50)
    
    # Test 1: Check categorization
    print("\n1. Exercise Categorization:")
    print(f"   Total exercises: {len(exercise_analyzer.exercises)}")
    print(f"   Available muscle groups: {len(exercise_analyzer.get_available_muscle_groups())}")
    print(f"   Available equipment: {len(exercise_analyzer.get_available_equipment_types())}")
    
    # Test 2: Muscle group analysis
    print("\n2. Muscle Group Analysis:")
    muscle_groups = exercise_analyzer.get_available_muscle_groups()
    print(f"   Available muscle groups: {sorted(muscle_groups)}")
    
    # Show some examples
    for muscle in ["chest", "back", "quadriceps", "biceps"]:
        exercises = exercise_analyzer.get_exercises_by_muscle_group(muscle)
        if exercises:
            print(f"   {muscle.capitalize()}: {len(exercises)} exercises")
            print(f"     Example: {exercises[0].title}")
        else:
            print(f"   {muscle.capitalize()}: 0 exercises")
    
    # Test 3: Equipment analysis
    print("\n3. Equipment Analysis:")
    equipment = exercise_analyzer.get_available_equipment_types()
    print(f"   Available equipment: {sorted(equipment)}")
    
    # Show some examples
    for equip in ["dumbbell", "barbell", "machine", "none"]:
        exercises = exercise_analyzer.get_exercises_by_equipment_type(equip)
        if exercises:
            print(f"   {equip.capitalize()}: {len(exercises)} exercises")
            print(f"     Example: {exercises[0].title}")
        else:
            print(f"   {equip.capitalize()}: 0 exercises")
    
    print("\n✅ Exercise analyzer testing completed!")


if __name__ == "__main__":
    test_exercise_analyzer()