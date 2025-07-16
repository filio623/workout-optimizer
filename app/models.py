# Pydantic data models for the Workout Optimizer app 
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Set(BaseModel):
    index: int
    type: str
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    distance_meters: Optional[float] = None
    duration_seconds: Optional[int] = None
    rpe: Optional[float] = None
    custom_metric: Optional[str] = None

class Exercise(BaseModel):
    index: int
    title: str
    notes: Optional[str] = None
    exercise_template_id: str
    superset_id: Optional[str] = None
    sets: List[Set]
    #rest_seconds: Optional[int] = 0

class Routine(BaseModel):
    id: str
    title: str
    folder_id: int
    updated_at: datetime
    created_at: datetime
    exercises: List[Exercise]

class Workout(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    updated_at: datetime
    created_at: datetime
    exercises: List[Exercise]

class ExerciseTemplate(BaseModel):
    id: str
    title: str
    exercise_type: str
    primary_muscle_group: str
    secondary_muscle_groups: List[str]
    equipment: str
    is_custom: bool

class Program(BaseModel):
    id: int
    index: int
    title: str
    updated_at: datetime
    created_at: datetime

class BaseResponse(BaseModel):
    page: int
    page_count: int

class WorkoutResponse(BaseResponse):
    workouts: List[Workout]

class RoutineResponse(BaseResponse):
    routines: List[Routine]

class ExerciseTemplateResponse(BaseResponse):
    exercise_templates: List[ExerciseTemplate]

class ProgramResponse(BaseResponse):
    routine_folders: List[Program]
