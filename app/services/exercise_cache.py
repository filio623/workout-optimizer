import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from app.models import ExerciseTemplate
from app.hevy.client import HevyClient

logger = logging.getLogger(__name__)

# Static file configuration
STATIC_EXERCISE_FILE = "app/data/exercise_templates.json"


class ExerciseCache:
    """Service for loading exercise templates from static file."""
    
    def __init__(self):
        # Look for the static file in the project root
        self.static_file = Path(STATIC_EXERCISE_FILE)
        self.hevy_client = HevyClient()  # Keep for potential future use
    
    def _load_from_static_file(self) -> List[ExerciseTemplate]:
        """Load exercise templates from static JSON file."""
        try:
            if not self.static_file.exists():
                logger.error(f"Static exercise file not found: {self.static_file}")
                return []
            
            with open(self.static_file, 'r') as f:
                exercises_data = json.load(f)
                
                # Convert to ExerciseTemplate objects
                exercises = [ExerciseTemplate(**exercise) for exercise in exercises_data]
                logger.info(f"Loaded {len(exercises)} exercises from static file")
                return exercises
                
        except Exception as e:
            logger.error(f"Error loading from static file: {e}")
            return []
    
    def get_exercise_templates(self, force_refresh: bool = False) -> List[ExerciseTemplate]:
        """
        Get exercise templates from static file.
        
        Args:
            force_refresh: Ignored for static file approach
            
        Returns:
            List of ExerciseTemplate objects
        """
        exercises = self._load_from_static_file()
        if not exercises:
            raise Exception(f"No exercises found in static file: {self.static_file}")
        return exercises
    
    def refresh_cache(self) -> List[ExerciseTemplate]:
        """For static file approach, this just reloads the file."""
        logger.info("Reloading exercise templates from static file...")
        return self.get_exercise_templates()
    
    def get_cache_info(self) -> dict:
        """Get information about the static exercise file."""
        if not self.static_file.exists():
            return {
                'exists': False,
                'file_path': str(self.static_file),
                'exercise_count': 0,
                'age': None
            }
        
        try:
            file_time = datetime.fromtimestamp(self.static_file.stat().st_mtime)
            age = datetime.now() - file_time
            
            # Count exercises in file
            with open(self.static_file, 'r') as f:
                exercises_data = json.load(f)
                exercise_count = len(exercises_data)
            
            return {
                'exists': True,
                'file_path': str(self.static_file),
                'exercise_count': exercise_count,
                'age': str(age),
                'last_modified': file_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {
                'exists': True,
                'file_path': str(self.static_file),
                'exercise_count': 0,
                'age': None,
                'error': str(e)
            }


# Global cache instance
exercise_cache = ExerciseCache() 