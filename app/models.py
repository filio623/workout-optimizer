from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# -----------------------------
# Common Building Blocks
# -----------------------------

class RepRange(BaseModel):
    start: int
    end: int

class SetBase(BaseModel):
    type: str
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    distance_meters: Optional[float] = None
    duration_seconds: Optional[int] = None
    custom_metric: Optional[float] = None
    rep_range: Optional[RepRange] = None


# -----------------------------
# Request Models
# -----------------------------

class SetCreate(SetBase):
    pass

class ExerciseCreate(BaseModel):
    exercise_template_id: str
    superset_id: Optional[int] = None
    rest_seconds: Optional[int] = 0
    notes: Optional[str] = None
    sets: List[SetCreate]

class RoutineCreate(BaseModel):
    title: str
    folder_id: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[ExerciseCreate]

class RoutineCreatePayload(BaseModel):
    routine: RoutineCreate

class WorkoutCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_private: bool = False
    exercises: List[ExerciseCreate]

class WorkoutCreatePayload(BaseModel):
    workout: WorkoutCreate

class RoutineFolderCreatePayload(BaseModel):
    routine_folder: dict[str, str]  # {'title': 'Push Pull 🏋️‍♂️'}


# -----------------------------
# Response Models
# -----------------------------

class SetResponse(SetBase):
    index: int
    rpe: Optional[float] = None

class ExerciseResponse(BaseModel):
    index: int
    title: str
    notes: Optional[str] = None
    exercise_template_id: str
    supersets_id: Optional[int] = None
    rest_seconds: Optional[int] = 0
    sets: List[SetResponse]

class RoutineResponseItem(BaseModel):
    id: str
    title: str
    folder_id: Optional[int]
    updated_at: datetime
    created_at: datetime
    exercises: List[ExerciseResponse]

class WorkoutResponseItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    updated_at: datetime
    created_at: datetime
    exercises: List[ExerciseResponse]

class ExerciseTemplate(BaseModel):
    id: str
    title: str
    exercise_type: str = Field(alias="type")
    primary_muscle_group: str
    secondary_muscle_groups: List[str]
    equipment: str
    is_custom: bool

class RoutineFolder(BaseModel):
    id: int
    index: int
    title: str
    updated_at: datetime
    created_at: datetime

# -----------------------------
# Response Wrappers (Pagination)
# -----------------------------

class BaseResponse(BaseModel):
    page: int
    page_count: int

class WorkoutResponse(BaseResponse):
    workouts: List[WorkoutResponseItem]

class RoutineResponse(BaseResponse):
    routines: List[RoutineResponseItem]

class ExerciseTemplateResponse(BaseResponse):
    exercise_templates: List[ExerciseTemplate]

class RoutineFolderResponse(BaseResponse):
    routine_folders: List[RoutineFolder]