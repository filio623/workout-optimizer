import pprint
from app.hevy.client import HevyClient
from app.services.workout_analyzer import get_all_program_routines, get_current_program

program_id = get_current_program()
if not program_id:
    print("No current program found.")
    exit()  

def aggregate_program_exercises(program_id) -> list:
    """Aggregate exercises from all routines in a program."""
    routines = get_all_program_routines(program_id)
    exercises = []
    for routine in routines:
        exercises.extend(routine.get("exercises", []))
    return exercises

if __name__ == "__main__":
    exercises = aggregate_program_exercises(program_id)
    print(f"Total exercises in program {program_id}: {len(exercises)}")
    print("Exercises:")
    pprint.pprint(exercises)    