import requests
import logging
from agents import Agent, Runner, function_tool
from app.config import config
from typing import Optional, Dict, Any
from app.models import Workout, Routine, ExerciseTemplate, Program, WorkoutResponse, RoutineResponse, ExerciseTemplateResponse, ProgramResponse


logger = logging.getLogger(__name__)

class HevyClientError(Exception):
    """Custom exception for Hevy API errors."""
    
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(f"Hevy Error: {message} (Status: {status_code})" if status_code else f"Hevy Error: {message}")


class HevyClient:
    """Client for interacting with the Hevy API.
    
    Provides methods to fetch workouts, routines, exercise templates, and programs
    from the Hevy fitness app API.
    """
    def __init__(self) -> None:
        self.base_url = config.HEVY_BASE_URL
        self.api_key = config.HEVY_API_KEY
        if not self.api_key:
            raise HevyClientError("HEVY_API_KEY is required but not provided")
        self.headers = {
            "accept": "application/json",
            "api-key": self.api_key,
        }
        logger.info("HevyClient initialized successfully")

    def _get_headers(self, method: str, has_data: bool = False) -> Dict[str, str]:
        """Get appropriate headers for the request type."""
        headers = self.headers.copy()
        
        if method in ["POST", "PUT"] and has_data:
            headers["Content-Type"] = "application/json"
        
        return headers

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                     data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: 
        """
        Generic request method with proper error handling.
        """
        url = f"{self.base_url}/{endpoint}"
        
        # Get dynamic headers based on request type
        headers = self._get_headers(method, has_data=data is not None)
        
        try:
            logger.debug(f"Making {method} request to {url}")
            response = requests.request(
                method=method,
                url=url,
                headers=headers,  # Use dynamic headers
                params=params,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise HevyClientError(f"Request failed: {e}")

    def get_workouts(self, page: int = 1, page_size: int = 5) -> WorkoutResponse:
        """Fetch all workouts from Hevy."""
        try:
            endpoint = "v1/workouts"
            params = {
                "page": page,
                "pageSize": page_size,
            }
            data = self._make_request("GET", endpoint, params=params)
            return WorkoutResponse(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch workouts: {e}")
            raise HevyClientError(f"Failed to fetch workouts: {e}")

    def get_workout_count(self) -> int:
        """Fetch the total number of workouts."""
        try:
            endpoint = "v1/workouts/count"
            data = self._make_request("GET", endpoint)
            return int(data['workout_count'])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch workout count: {e}")
            raise HevyClientError(f"Failed to fetch workout count: {e}")

    def get_workout_event(self, date: str = "1970-01-01T00:00:00Z") -> WorkoutResponse:
        """Fetch workout events from a specific date.
        
        Args:
            date: ISO format date string (default: "1970-01-01T00:00:00Z")
        """
        try:
            endpoint = "v1/workouts/events"
            params = {
                "page": 1,
                "pageSize": 5,
                "since": date,
            }
            data = self._make_request("GET", endpoint, params=params)
            return WorkoutResponse(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch workout events: {e}")
            raise HevyClientError(f"Failed to fetch workout events: {e}")

    def get_workout_by_id(self, workout_id: str) -> Workout:
        """Fetch a specific workout by ID."""
        try:
            endpoint = f"v1/workouts/{workout_id}"
            data = self._make_request("GET", endpoint)
            return Workout(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch workout by ID: {e}")
            raise HevyClientError(f"Failed to fetch workout by ID: {e}")
    
    def get_routines(self, page: int = 1, page_size: int = 5) -> RoutineResponse:
        """Fetch all routines from Hevy."""
        try:
            endpoint = "v1/routines"
            params = {
                "page": page,
                "pageSize": page_size,
            }
            data = self._make_request("GET", endpoint, params=params)
            return RoutineResponse(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch routines: {e}")
            raise HevyClientError(f"Failed to fetch routines: {e}")
    
    def get_routine_by_id(self, routine_id: str) -> Routine:
        """Fetch a specific routine by ID."""
        try:
            endpoint = f"v1/routines/{routine_id}"
            data = self._make_request("GET", endpoint)
            return Routine(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch routine by ID: {e}")
            raise HevyClientError(f"Failed to fetch routine by ID: {e}")
    
    def get_exercise_templates(self, page: int = 1, page_size: int = 5) -> ExerciseTemplateResponse:
        """Fetch all exercise templates from Hevy."""

        current_page = page
        page_size = page_size
        try:
            all_exercise_templates = []
            endpoint = "v1/exercise_templates"
            while True:
                params = {
                    "page": current_page,
                    "pageSize": page_size,
                }

                data = self._make_request("GET", endpoint, params=params)

                if current_page >= data.page_count:
                    break

                all_exercise_templates.extend(data.exercise_templates)
                current_page += 1
            return ExerciseTemplateResponse(exercise_templates=all_exercise_templates)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch exercise templates: {e}")
            raise HevyClientError(f"Failed to fetch exercise templates: {e}")

    def get_exercise_template_by_id(self, template_id: str) -> ExerciseTemplate:
        """Fetch a specific exercise template by ID."""
        try:
            endpoint = f"v1/exercise_templates/{template_id}"
            data = self._make_request("GET", endpoint)
            return ExerciseTemplate(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch exercise template by ID: {e}")
            raise HevyClientError(f"Failed to fetch exercise template by ID: {e}")
    
    def get_routine_folders(self, page: int = 1, page_size: int = 5) -> ProgramResponse:
        """Fetch all routine folders from Hevy."""
        try:
            endpoint = "v1/routine_folders"
            params = {
                "page": page,
                "pageSize": page_size,
            }
            data = self._make_request("GET", endpoint, params=params)
            return ProgramResponse(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch routine folders: {e}")
            raise HevyClientError(f"Failed to fetch routine folders: {e}")

    def get_routine_folder_by_id(self, folder_id: str) -> Program:
        """Fetch a specific routine folder by ID."""
        try: 
            endpoint = f"v1/routine_folders/{folder_id}"
            data = self._make_request("GET", endpoint)
            return Program(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch routine folder by ID: {e}")
            raise HevyClientError(f"Failed to fetch routine folder by ID: {e}")
    
    def create_workout(self, workout_data: Dict[str, Any]) -> Workout:
        """Create a new workout."""
        try:
            endpoint = "v1/workouts"
            data = self._make_request("POST", endpoint, data=workout_data)
            return Workout(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create workout: {e}")
            raise HevyClientError(f"Failed to create workout: {e}")

    def update_workout(self, workout_id: str, workout_data: Dict[str, Any]) -> Workout:
        """Update an existing workout."""
        try:
            endpoint = f"v1/workouts/{workout_id}"
            data = self._make_request("PUT", endpoint, data=workout_data)
            return Workout(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update workout: {e}")
            raise HevyClientError(f"Failed to update workout: {e}")

    def create_routine(self, routine_data: Dict[str, Any]) -> Routine:
        """Create a new routine."""
        try:
            endpoint = "v1/routines"
            data = self._make_request("POST", endpoint, data=routine_data)
            return Routine(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create routine: {e}")
            raise HevyClientError(f"Failed to create routine: {e}")

    def update_routine(self, routine_id: str, routine_data: Dict[str, Any]) -> Routine:
        """Update an existing routine."""
        try:
            endpoint = f"v1/routines/{routine_id}"
            data = self._make_request("PUT", endpoint, data=routine_data)
            return Routine(**data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update routine: {e}")
            raise HevyClientError(f"Failed to update routine: {e}")

    
if __name__ == "__main__":
    #testing area
    hevy_client = HevyClient()

    data = hevy_client.get_workout_by_id("4cf5694a-0685-4239-829a-969e659a")
    print(data)