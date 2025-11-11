import logging
from typing import List, Dict, Any
from backend.services.exercise_cache import exercise_cache
from backend.models import ExerciseTemplate
from collections import defaultdict
from pprint import pprint
import json

logger = logging.getLogger(__name__)

class ExerciseAnalyzer:
    def __init__(self):
        self.exercises = []
        self.muscle_groups = defaultdict(list)
        self.equipment_types = defaultdict(list)
        self.exercise_types = defaultdict(list)
        self.compound_exercises = []

        self._load_and_categorize()


    def _load_and_categorize(self):
        """Load exercises from cache and categorize them."""
        logger.info("Loading and categorizing exercises...")
        self.exercises = exercise_cache.get_exercise_templates()
        for exercise in self.exercises:
            self.muscle_groups[exercise.primary_muscle_group].append(exercise)

            self.equipment_types[exercise.equipment].append(exercise)


    def get_exercises_by_muscle_group(self, muscle_group: str) -> List[ExerciseTemplate]:
        """Get exercises by muscle group."""
        return self.muscle_groups.get(muscle_group.lower())

    def get_exercises_by_equipment_type(self, equipment_type: str) -> List[ExerciseTemplate]:
        """Get exercises by equipment type."""
        return self.equipment_types.get(equipment_type.lower())

    def get_available_muscle_groups(self) -> List[str]:
        """Get all available muscle groups."""
        return list(self.muscle_groups.keys())

    def get_available_equipment_types(self) -> List[str]:
        """Get all available equipment types."""
        return list(self.equipment_types.keys())
        

exercise_analyzer = ExerciseAnalyzer()








