import requests
import logging
from typing import Optional, Dict, Any, List

from app.config import config
from app.models import *
import pprint

logger = logging.getLogger(__name__)


class HevyClientError(Exception):
    """Custom exception for Hevy API errors."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(
            f"Hevy Error: {message} (Status: {status_code})"
            if status_code else f"Hevy Error: {message}"
        )


class HevyClient:
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
        headers = self.headers.copy()
        if method in ["POST", "PUT"] and has_data:
            headers["Content-Type"] = "application/json"
        return headers

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                      json_data: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(method, has_data=json_data is not None)

        try:
            logger.debug(f"Making {method} request to {url}")
            logger.debug(f"Request headers: {headers}")
            logger.debug(f"Request body (json_data): {json_data}")
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=json_data,
                timeout=10
            )
            logger.debug(f"Response: {response.status_code} {response.text}")
            logger.debug(f"Response content: {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise HevyClientError(f"Request failed: {e}")

    def get_workouts(self, page: int = 1, page_size: int = 5) -> WorkoutResponse:
        endpoint = "v1/workouts"
        params = {"page": page, "pageSize": page_size}
        data = self._make_request("GET", endpoint, params=params)
        return WorkoutResponse(**data)

    def get_workout_count(self) -> int:
        endpoint = "v1/workouts/count"
        data = self._make_request("GET", endpoint)
        return int(data['workout_count'])

    def get_workout_event(self, date: str = "1970-01-01T00:00:00Z") -> WorkoutResponse:
        endpoint = "v1/workouts/events"
        params = {"page": 1, "pageSize": 5, "since": date}
        data = self._make_request("GET", endpoint, params=params)
        return WorkoutResponse(**data)

    def get_workout_by_id(self, workout_id: str) -> WorkoutResponseItem:
        endpoint = f"v1/workouts/{workout_id}"
        data = self._make_request("GET", endpoint)
        return WorkoutResponseItem(**data)

    def get_routines(self, page: int = 1, page_size: int = 5) -> RoutineResponse:
        endpoint = "v1/routines"
        params = {"page": page, "pageSize": page_size}
        data = self._make_request("GET", endpoint, params=params)
        return RoutineResponse(**data)

    def get_routine_by_id(self, routine_id: str) -> RoutineResponseItem:
        endpoint = f"v1/routines/{routine_id}"
        data = self._make_request("GET", endpoint)
        return RoutineResponseItem(**data)

    def get_exercise_templates(self, page: int = 1, page_size: int = 5) -> List[ExerciseTemplate]:
        all_exercise_templates = []
        current_page = page
        while True:
            params = {"page": current_page, "pageSize": page_size}
            raw_data = self._make_request("GET", "v1/exercise_templates", params=params)
            response = ExerciseTemplateResponse(**raw_data)
            all_exercise_templates.extend(response.exercise_templates)
            if current_page >= response.page_count:
                break
            current_page += 1
        return all_exercise_templates

    def get_exercise_template_by_id(self, template_id: str) -> ExerciseTemplate:
        endpoint = f"v1/exercise_templates/{template_id}"
        data = self._make_request("GET", endpoint)
        return ExerciseTemplate(**data)

    def get_routine_folders(self, page: int = 1, page_size: int = 5) -> RoutineFolderResponse:
        endpoint = "v1/routine_folders"
        params = {"page": page, "pageSize": page_size}
        data = self._make_request("GET", endpoint, params=params)
        return RoutineFolderResponse(**data)

    def get_routine_folder_by_id(self, folder_id: str) -> RoutineFolder:
        endpoint = f"v1/routine_folders/{folder_id}"
        data = self._make_request("GET", endpoint)
        return RoutineFolder(**data)

    def create_routine_folder(self, title: str) -> RoutineFolder:
        """Create a new Routine Folder with a title"""
        endpoint = "/v1/routine_folders"

        folder_create = RoutineFolderCreate(title=title)
        payload = RoutineFolderCreatePayload(routine_folder=folder_create).model_dump_json(by_alias=True, exclude_none=False)

        data = self._make_request("POST", endpoint, json_data=payload)
        return RoutineFolder(**data['routine_folder'])


    def create_workout(self, workout_data: WorkoutCreatePayload) -> WorkoutResponseItem:
        endpoint = "v1/workouts"
        payload = workout_data.model_dump_json(by_alias=True, exclude_none=False)
        data = self._make_request("POST", endpoint, json_data=payload)
        return WorkoutResponseItem(**data)

    def update_workout(self, workout_id: str, workout_data: WorkoutCreatePayload) -> WorkoutResponseItem:
        endpoint = f"v1/workouts/{workout_id}"
        payload = workout_data.model_dump_json(by_alias=True, exclude_none=False)
        data = self._make_request("PUT", endpoint, json_data=payload)
        return WorkoutResponseItem(**data)

    def create_routine(self, routine_data: RoutineCreatePayload) -> RoutineResponseItem:
        """Create a new routine via the Hevy API."""
        endpoint = "v1/routines"
        payload = routine_data.model_dump_json(by_alias=True, exclude_none=False)
        data = self._make_request("POST", endpoint, json_data=payload)
        
        # More robust response handling
        if 'routine' not in data or not data['routine']:
            raise HevyClientError("Invalid response format: missing routine data")
        
        routine_data = data['routine'][0]
        return RoutineResponseItem(**routine_data)

    def update_routine(self, routine_id: str, routine_data: RoutineCreatePayload) -> RoutineResponseItem:
        endpoint = f"v1/routines/{routine_id}"
        payload = routine_data.model_dump_json(by_alias=True, exclude_none=False)
        data = self._make_request("PUT", endpoint, json_data=payload)
        return RoutineResponseItem(**data)


if __name__ == "__main__":
    # Testing area
    hevy_client = HevyClient()

    def folder_test():
        folder = hevy_client.create_routine_folder("Test Folder")
        print(folder)
        pprint.pprint(folder.model_dump(by_alias=True, exclude_none=False), indent=2)

    
    folder_test()