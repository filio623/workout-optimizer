import logging
import pandas as pd
from typing import List, Dict, Any
from app.hevy.client import HevyClient


logger = logging.getLogger(__name__)

class WorkoutAnalyzer:

    def __init__(self):
        self.hevy_client = HevyClient()
        self.workouts = []
        self.workouts_df = None
        self.exercises_df = None
        self.sets_df = None

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
        """Create all dataframes."""
        self.workouts_df = pd.DataFrame(self.workouts)



if __name__ == "__main__":
    #testing area
    workout_analyzer = WorkoutAnalyzer()
    print(workout_analyzer.workouts_df.head())