from datetime import datetime, timedelta
import pprint
from app.hevy.client import HevyClient


MUSCLE_GROUP_KEYWORDS = {
    "chest": ["chest", "pectorals", "pecs"],
    "back": ["back", "lats", "latissimus dorsi"],
    "legs": ["legs", "quadriceps", "hamstrings", "calves"],
    "shoulders": ["shoulders", "deltoids", "delts"],
    "arms": ["arms", "biceps", "triceps", "forearms"],
    "core": ["core", "abdominals", "abs", "obliques"],
    "glutes": ["glutes", "gluteus maximus", "buttocks"],
    "upper body": ["upper body", "upper", "chest", "back", "shoulders", "arms"],
    "lower body": ["lower body", "lower", "legs", "glutes", "calves", "quadriceps", "hamstrings"],
}

heavy_client = HevyClient()

now = datetime.now()
yesterday = now - timedelta(days=2)

def get_yesterdays_workout() -> dict:
    date_str = yesterday.strftime("%Y-%m-%d")
    data = heavy_client.get_workouts()
    for workout in data['workouts']:
        try:
            if workout['start_time'].split('T')[0] == date_str:
                return workout
        except Exception as e:
            print(f"Error fetching yesterday's workout: {e}")
            return None
     
def get_workout_duration(workout) -> timedelta:
    start_time = datetime.fromisoformat(workout['start_time'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(workout['end_time'].replace('Z', '+00:00'))
    duration = end_time - start_time
    return duration

def get_current_program() -> str:
    last_workout = heavy_client.get_workouts(page=1, page_size=2)['workouts'][1]
    last_workout_title = last_workout['title']
    for routine in heavy_client.get_routines()['routines']:
        if routine['title'] == last_workout_title:
            return routine['folder_id']

def get_all_program_routines(program_id) -> list:
    routines = heavy_client.get_routines()
    return [routine for routine in routines['routines'] if routine['folder_id'] == program_id]
    
if __name__ == "__main__":
    #testing area
    duration = get_workout_duration(get_yesterdays_workout())
    print(f"Yesterday's workout duration: {duration}")
    print(type(duration))