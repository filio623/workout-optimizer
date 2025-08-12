from pydantic import BaseModel, Field
from typing import List, Optional
from agents import function_tool
from app.hevy.client import HevyClient
from app.models import *

DEFAULT_REST_SECONDS = 90

# This is what Layer 1 (AI) will produce and pass to Layer 2
class WorkoutProgram(BaseModel):
    program_name: str
    program_notes: Optional[str] = None
    routines: List[RoutineCreate]  # Reuse existing RoutineCreate!

# Optional: If you want a simpler intermediate format
class ProgramRoutineTemplate(BaseModel):
    name: str
    notes: Optional[str] = None
    exercise_template_ids: List[str]
    # Layer 1 creates this, then we convert to RoutineCreate

class WorkoutProgramTemplate(BaseModel):
    program_name: str
    program_notes: Optional[str] = None
    routines: List[ProgramRoutineTemplate]

hevy_client = HevyClient()

@function_tool
def create_workout_program(program_data: str) -> str:
    """
    Create a workout program from AI-generated program structure.
    
    Args:
        program_data: JSON string containing program structure with:
            - program_name: Name of the program  
            - program_notes: Optional description
            - routines: List of routines, each with:
                - name: Routine name
                - notes: Optional routine notes
                - exercise_template_ids: List of exercise template IDs
    
    Example JSON structure:
    {
        "program_name": "PPL Hypertrophy",
        "program_notes": "Push/Pull/Legs split for muscle growth",
        "routines": [
            {
                "name": "Push Day",
                "notes": "Chest, shoulders, triceps",
                "exercise_template_ids": ["68CE0B9B", "99C1F2AD", "37FCC2BB"]
            }
        ]
    }
    """
    import json
    
    try:
        program_dict = json.loads(program_data)
        program_template = WorkoutProgramTemplate(**program_dict)  # Pydantic handles nested conversion
        result = _create_program_in_hevy(program_template)
        return f"Created '{program_template.program_name}' with {len(result['routines'])} routines!"
    
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format - {str(e)}"
    except Exception as e:
        return f"Error creating program: {str(e)}"



def _create_program_in_hevy(program: WorkoutProgramTemplate) -> dict:

    folder = hevy_client.create_routine_folder(program.program_name)

    folder_id = folder.id

    routines = []

    for routine_template in program.routines:
        exercises = []
        for exercise_id in routine_template.exercise_template_ids:
            exercise = ExerciseCreate(
                exercise_template_id=exercise_id,
                rest_seconds=DEFAULT_REST_SECONDS,
                notes ="",
                sets = [(SetCreate(
                    type="normal",
                    reps=10,
                    rep_range =  RepRange(
                        start=8,
                        end=12
                    ),
                    )) for _ in range(3)],
            )
            exercises.append(exercise)
        routine = RoutineCreate(
            title=routine_template.name,
            folder_id=folder_id,
            notes=routine_template.notes,
            exercises=exercises
        )
        routines.append(routine)

    for routine in routines:
        routine_payload = RoutineCreatePayload(routine=routine)
        hevy_client.create_routine(routine_payload)

    return {
        "folder": folder,
        "routines": routines,
        "success": True,
    }
    
if __name__ == "__main__":
    test_json = '''
    {
        "program_name": "Test Program",
        "program_notes": "Testing the function",
        "routines": [
            {
                "name": "Test Routine",
                "notes": "Just a test",
                "exercise_template_ids": ["68CE0B9B", "99C1F2AD"]
            }
        ]
    }
    '''
    
    result = create_workout_program(test_json)
    print(result)

