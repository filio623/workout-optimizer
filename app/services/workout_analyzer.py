import logging
import pandas as pd
from typing import List, Dict, Any
from app.hevy.client import HevyClient
from app.models import *
from app.services.exercise_cache import exercise_cache


logger = logging.getLogger(__name__)

class WorkoutAnalyzer:

    def __init__(self):
        self.hevy_client = HevyClient()
        self.workouts = []
        
        # Initialize DataFrames as None
        self.workouts_df = None
        self.exercises_df = None
        self.sets_df = None
        self.exercise_templates = exercise_cache.get_exercise_templates()
        self.exercise_template_map = {
            template.id: template for template in self.exercise_templates
        }
        
        # Load workouts and create DataFrames
        self._load_workouts()
        self.create_all_dataframes()

    def _load_workouts(self):
        """Load all workouts from the Hevy API."""
        logger.info("Loading workouts...")
        current_page = 1
        max_pages = 200

        while current_page < max_pages:
            workouts_response = self.hevy_client.get_workouts(page=current_page)
            if current_page >= workouts_response.page_count:
                break
            self.workouts.extend(workouts_response.workouts)
            current_page += 1


    def create_all_dataframes(self):
        """Create all DataFrames at once using Pydantic model_dump()."""
        
        # Workouts DataFrame
        self.workouts_df = pd.DataFrame([w.model_dump() for w in self.workouts])
        
        # Exercises DataFrame
        exercise_data = [
            {**exercise.model_dump(), 
            'workout_id': workout.id,
            'workout_title': workout.title,
            'workout_date': workout.start_time.date(),
            'primary_muscle_group': (
                template.primary_muscle_group if (
                    template := self.exercise_template_map.get(exercise.exercise_template_id)
                    ) else None
                )
            }
            for workout in self.workouts
            for exercise in workout.exercises
        ]
        self.exercises_df = pd.DataFrame(exercise_data)
        
        # Sets DataFrame
        set_data = [
            {**set_item.model_dump(),
            'workout_id': workout.id,
            'workout_date': workout.start_time.date(),
            'exercise_title': exercise.title,
            'exercise_template_id': exercise.exercise_template_id}
            for workout in self.workouts
            for exercise in workout.exercises
            for set_item in exercise.sets
        ]
        self.sets_df = pd.DataFrame(set_data)
        
        logger.info("All DataFrames created successfully")



if __name__ == "__main__":
    # Create analyzer (DataFrames created automatically)
    workout_analyzer = WorkoutAnalyzer()
    
    # Check that DataFrames were created
    print(f"Workouts DataFrame shape: {workout_analyzer.workouts_df.shape}")
    print(f"Exercises DataFrame shape: {workout_analyzer.exercises_df.shape}")
    print(f"Sets DataFrame shape: {workout_analyzer.sets_df.shape}")
    
    # Show a sample of each DataFrame
    print("\nWorkouts DataFrame sample:")
    print(workout_analyzer.workouts_df.head())
    
    print("\nExercises DataFrame sample:")
    print(workout_analyzer.exercises_df.head())
    
    print("\nSets DataFrame sample:")
    print(workout_analyzer.sets_df.head())
    
    # Test some basic analysis
    print("\n" + "="*50)
    print("BASIC ANALYSIS TESTS")
    print("="*50)
    
    # Test 1: Most used exercises
    print("\n🏋️ Most Used Exercises:")
    if not workout_analyzer.exercises_df.empty:
        top_exercises = workout_analyzer.exercises_df['title'].value_counts().head(5)
        for exercise, count in top_exercises.items():
            print(f"   {exercise}: {count} times")
    
    # Test 2: Workout duration stats
    print("\n⏱️ Workout Duration Stats:")
    if not workout_analyzer.workouts_df.empty:
        duration_col = 'duration_minutes' if 'duration_minutes' in workout_analyzer.workouts_df.columns else 'end_time'
        if duration_col == 'duration_minutes':
            avg_duration = workout_analyzer.workouts_df[duration_col].mean()
            print(f"   Average duration: {avg_duration:.1f} minutes")
        else:
            print("   Duration data not available in expected format")
    
    # Test 3: Exercise with most sets
    print("\n�� Exercise with Most Sets:")
    if not workout_analyzer.sets_df.empty:
        exercise_set_counts = workout_analyzer.sets_df['exercise_title'].value_counts().head(3)
        for exercise, count in exercise_set_counts.items():
            print(f"   {exercise}: {count} sets")
    
    # Test 4: Weighted exercises
    print("\n🏋️ Weighted Exercises Sample:")
    if not workout_analyzer.sets_df.empty and 'weight_kg' in workout_analyzer.sets_df.columns:
        weighted_sets = workout_analyzer.sets_df[workout_analyzer.sets_df['weight_kg'].notna()]
        if not weighted_sets.empty:
            print(weighted_sets[['exercise_title', 'weight_kg', 'reps']].head())
        else:
            print("   No weighted exercises found")
    
    print("\n✅ Analysis testing completed!")

    print("H" * 50)
    print("H" * 50)
    print(workout_analyzer.exercises_df.primary_muscle_group.head())
