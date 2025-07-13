import requests
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

URL = "https://api.hevyapp.com"

class HevyClient:
    def __init__(self) -> None:
        self.base_url = URL
        self.api_key = os.getenv("HEVY_API_KEY")
        if not self.api_key:
            raise ValueError("HEVY_API_KEY environment variable not set")
        self.headers = {
            "accept": "application/json",
            "api-key": self.api_key,
        }

    def get_(self, endpoint: str, params: dict = None) -> dict:
        """Generic GET request method."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_workouts(self, page: int = 1, page_size: int = 5) -> dict:
        """Fetch all workouts from Hevy."""
        endpoint = "v1/workouts"
        params = {
            "page": page,
            "pageSize": page_size,
        }
        return self.get_(endpoint, params)
    
    def get_workout_count(self) -> int:
        """Fetch the total number of workouts."""
        endpoint = "v1/workouts/count"
        data = self.get_(endpoint)
        return int(data['workout_count'])

    def get_workout_event(self, date: str = "1970-01-01T00:00:00Z") -> dict:
        """Fetch workout events from a specific date."""
        endpoint = "v1/workouts/events"
        params = {
            "page": 1,
            "pageSize": 5,
            "since": date,
        }
        return self.get_(endpoint, params)

    def get_workout_by_id(self, workout_id: str) -> dict:
        """Fetch a specific workout by ID."""
        endpoint = f"v1/workouts/{workout_id}"
        return self.get_(endpoint)
    
    def get_routines(self, page: int = 1, page_size: int = 5) -> dict:
        """Fetch all routines from Hevy."""
        endpoint = "v1/routines"
        params = {
            "page": page,
            "pageSize": page_size,
        }
        return self.get_(endpoint, params)
    
    def get_routine_by_id(self, routine_id: str) -> dict:
        """Fetch a specific routine by ID."""
        endpoint = f"v1/routines/{routine_id}"
        return self.get_(endpoint)
    
    def get_exercise_templates(self, page: int = 1, page_size: int = 5) -> dict:
        """Fetch all exercise templates from Hevy."""
        endpoint = "v1/exercise_templates"
        params = {
            "page": page,
            "pageSize": page_size,
        }
        return self.get_(endpoint, params)

    def get_exercise_template_by_id(self, template_id: str) -> dict:
        """Fetch a specific exercise template by ID."""
        endpoint = f"v1/exercise_templates/{template_id}"
        return self.get_(endpoint)
    
    def get_routine_folders(self, page: int = 1, page_size: int = 5) -> dict:
        """Fetch all routine folders from Hevy."""
        endpoint = "v1/routine_folders"
        params = {
            "page": page,
            "pageSize": page_size,
        }
        return self.get_(endpoint, params)

    def get_routine_folder_by_id(self, folder_id: str) -> dict:
        """Fetch a specific routine folder by ID."""
        endpoint = f"v1/routine_folders/{folder_id}"
        return self.get_(endpoint)
    
    def post_(self, endpoint: str, data: dict) -> dict:
        """Generic POST request method."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=data,
            timeout=10    
        )
        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def put_(self, endpoint: str, data: dict) -> dict:
        """Generic PUT request method."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=data,
            timeout=10    
        )
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
if __name__ == "__main__":
    #testing area
    hevy_client = HevyClient()

    data = hevy_client.get_workout_count()
    print(data)