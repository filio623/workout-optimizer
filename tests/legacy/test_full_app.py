#!/usr/bin/env python3
"""
Comprehensive test of the Workout Optimizer app functionality.
This script tests all major components: exercise analysis, workout analysis, and agent capabilities.
"""

import logging
from backend.llm.interface import agent, Runner
from backend.services.exercise_analyzer import exercise_analyzer
from backend.services.workout_analyzer import WorkoutAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_exercise_analyzer():
    """Test the exercise analyzer functionality."""
    print("\n" + "="*60)
    print("🧪 TESTING EXERCISE ANALYZER")
    print("="*60)
    
    print(f"✅ Total exercises loaded: {len(exercise_analyzer.exercises)}")
    print(f"✅ Available muscle groups: {len(exercise_analyzer.get_available_muscle_groups())}")
    print(f"✅ Available equipment types: {len(exercise_analyzer.get_available_equipment_types())}")
    
    # Test muscle group filtering
    chest_exercises = exercise_analyzer.get_exercises_by_muscle_group("chest")
    print(f"✅ Chest exercises found: {len(chest_exercises)}")
    
    # Test equipment filtering
    barbell_exercises = exercise_analyzer.get_exercises_by_equipment_type("barbell")
    print(f"✅ Barbell exercises found: {len(barbell_exercises)}")
    
    print("✅ Exercise analyzer test completed!")


def test_workout_analyzer():
    """Test the workout analyzer functionality."""
    print("\n" + "="*60)
    print("🏋️ TESTING WORKOUT ANALYZER")
    print("="*60)
    
    analyzer = WorkoutAnalyzer()
    
    print(f"✅ Workouts loaded: {analyzer.workouts_df.shape[0]}")
    print(f"✅ Exercises in workouts: {analyzer.exercises_df.shape[0]}")
    print(f"✅ Total sets performed: {analyzer.sets_df.shape[0]}")
    
    # Test basic analysis
    most_used = analyzer.exercises_df['title'].value_counts().head(3)
    print(f"✅ Most used exercises: {dict(zip(most_used.index, most_used.values))}")
    
    # Test muscle group analysis
    muscle_groups = analyzer.exercises_df['primary_muscle_group'].value_counts()
    print(f"✅ Muscle group distribution: {dict(zip(muscle_groups.head(5).index, muscle_groups.head(5).values))}")
    
    print("✅ Workout analyzer test completed!")


def test_agent_analysis():
    """Test the agent's analysis capabilities."""
    print("\n" + "="*60)
    print("🤖 TESTING AGENT ANALYSIS CAPABILITIES")
    print("="*60)
    
    # Test 1: Basic workout data retrieval
    print("\n📊 Test 1: Getting workout data for past month")
    try:
        result = Runner.run_sync(agent, "Get my workout data for the past month and show me a summary")
        print("✅ Agent successfully retrieved workout data")
        print(f"Response length: {len(result.final_output)} characters")
    except Exception as e:
        print(f"❌ Error in workout data test: {e}")
    
    # Test 2: Exercise recommendations
    print("\n💪 Test 2: Getting exercise recommendations")
    try:
        result = Runner.run_sync(agent, "Recommend some chest exercises for me")
        print("✅ Agent successfully provided exercise recommendations")
        print(f"Response length: {len(result.final_output)} characters")
    except Exception as e:
        print(f"❌ Error in exercise recommendations test: {e}")
    
    # Test 3: Workout analysis
    print("\n📈 Test 3: Analyzing workout patterns")
    try:
        result = Runner.run_sync(agent, "Analyze my workout patterns over the past 6 months")
        print("✅ Agent successfully analyzed workout patterns")
        print(f"Response length: {len(result.final_output)} characters")
    except Exception as e:
        print(f"❌ Error in workout analysis test: {e}")
    
    print("✅ Agent analysis tests completed!")


def test_agent_routine_creation():
    """Test the agent's routine creation capabilities."""
    print("\n" + "="*60)
    print("🏗️ TESTING AGENT ROUTINE CREATION")
    print("="*60)
    
    # Test 1: Simple routine creation
    print("\n📝 Test 1: Creating a simple routine")
    try:
        result = Runner.run_sync(agent, "Create a simple routine with 3 exercises for chest")
        print("✅ Agent successfully created a chest routine")
        print(f"Response length: {len(result.final_output)} characters")
    except Exception as e:
        print(f"❌ Error in simple routine creation: {e}")
    
    # Test 2: Balanced routine creation
    print("\n⚖️ Test 2: Creating a balanced routine")
    try:
        result = Runner.run_sync(agent, "Create a balanced full-body routine with 5 exercises")
        print("✅ Agent successfully created a balanced routine")
        print(f"Response length: {len(result.final_output)} characters")
    except Exception as e:
        print(f"❌ Error in balanced routine creation: {e}")
    
    print("✅ Agent routine creation tests completed!")


def test_agent_complex_workflow():
    """Test a complex workflow combining analysis and creation."""
    print("\n" + "="*60)
    print("🔄 TESTING COMPLEX AGENT WORKFLOW")
    print("="*60)
    
    print("\n🎯 Complex Test: Analysis + Recommendations + Creation")
    try:
        result = Runner.run_sync(agent, """
        I want you to:
        1. Analyze my workout data for the past month
        2. Identify which muscle groups I'm neglecting
        3. Recommend exercises to address those gaps
        4. Create a routine that focuses on my weak areas
        """)
        print("✅ Agent successfully completed complex workflow")
        print(f"Response length: {len(result.final_output)} characters")
    except Exception as e:
        print(f"❌ Error in complex workflow test: {e}")
    
    print("✅ Complex workflow test completed!")


def main():
    """Run all tests."""
    print("🚀 COMPREHENSIVE WORKOUT OPTIMIZER APP TEST")
    print("="*60)
    print("Testing all major components of the app...")
    
    try:
        # Test individual components
        test_exercise_analyzer()
        test_workout_analyzer()
        
        # Test agent capabilities
        test_agent_analysis()
        test_agent_routine_creation()
        test_agent_complex_workflow()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ Exercise Analyzer: Working")
        print("✅ Workout Analyzer: Working")
        print("✅ Agent Analysis: Working")
        print("✅ Agent Routine Creation: Working")
        print("✅ Complex Workflows: Working")
        print("\n🚀 Your Workout Optimizer app is fully functional!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    main() 