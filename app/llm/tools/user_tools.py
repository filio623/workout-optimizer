"""
User profile and goals management tools for personalized workout coaching.
Handles user context, fitness goals, preferences, and progress tracking.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from agents import function_tool
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

# User profile data models
class UserProfile(BaseModel):
    age: int
    weight_lbs: float
    height_inches: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    experience_level: str = "intermediate"  # beginner, intermediate, advanced
    available_days_per_week: int = 4
    session_duration_minutes: int = 60
    equipment_access: List[str] = ["gym"]  # gym, home, minimal
    injury_history: Optional[List[str]] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class FitnessGoals(BaseModel):
    primary_goal: str = "hypertrophy"  # strength, hypertrophy, endurance, aesthetic, weight_loss
    body_type_target: Optional[str] = None  # surfer, powerlifter, runner, model, etc.
    specific_focuses: List[str] = []  # upper_body, legs, core, arms, back, etc.
    timeline: Optional[str] = None  # 3_months, 6_months, 1_year
    target_weight_lbs: Optional[float] = None
    target_body_fat: Optional[float] = None
    priority_areas: List[str] = []  # aesthetic_focus areas
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UserPreferences(BaseModel):
    preferred_rep_ranges: Dict[str, List[int]] = {
        "strength": [3, 5],
        "hypertrophy": [8, 12],
        "endurance": [15, 20]
    }
    exercise_preferences: List[str] = []
    exercise_dislikes: List[str] = []
    training_style: str = "balanced"  # high_volume, strength_focused, time_efficient, balanced
    rest_preferences: Dict[str, int] = {
        "compound": 120,  # seconds
        "isolation": 90
    }
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# File paths for user data storage
USER_DATA_DIR = "user_data"
PROFILE_FILE = os.path.join(USER_DATA_DIR, "profile.json")
GOALS_FILE = os.path.join(USER_DATA_DIR, "goals.json")
PREFERENCES_FILE = os.path.join(USER_DATA_DIR, "preferences.json")

def _ensure_user_data_dir():
    """Ensure user data directory exists."""
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

def _load_json_file(file_path: str, default_data: dict = None) -> dict:
    """Load JSON file with error handling."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
    return default_data or {}

def _save_json_file(file_path: str, data: dict):
    """Save data to JSON file with error handling."""
    _ensure_user_data_dir()
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved data to {file_path}")
    except Exception as e:
        logger.error(f"Error saving {file_path}: {e}")
        raise

@function_tool
def get_user_profile() -> Dict[str, Any]:
    """Retrieve the current user profile with fitness background and constraints.
    
    Returns comprehensive user information including physical stats, experience level,
    available training time, equipment access, and any injury considerations.
    
    Returns:
        dict: Complete user profile including age, weight, experience, schedule, equipment
    
    Example:
        >>> get_user_profile()
    """
    logger.info("🔧 Tool called: get_user_profile")
    
    profile_data = _load_json_file(PROFILE_FILE)
    
    if not profile_data:
        return {
            "profile_exists": False,
            "message": "No user profile found. Use update_user_profile to create one.",
            "default_profile": {
                "age": None,
                "weight_lbs": None,
                "experience_level": "intermediate",
                "available_days_per_week": 4,
                "session_duration_minutes": 60,
                "equipment_access": ["gym"]
            }
        }
    
    profile = UserProfile(**profile_data)
    return {
        "profile_exists": True,
        "profile": profile.model_dump(),
        "summary": f"{profile.age}-year-old, {profile.weight_lbs}lbs, {profile.experience_level} level, {profile.available_days_per_week}x/week training"
    }

@function_tool
def update_user_profile(
    age: int,
    weight_lbs: float,
    experience_level: str = "intermediate",
    available_days_per_week: int = 4,
    session_duration_minutes: int = 60,
    equipment_access: str = "gym",
    height_inches: float = None,
    body_fat_percentage: float = None,
    injury_history: str = ""
) -> Dict[str, Any]:
    """Update or create user profile with fitness background and training constraints.
    
    Creates or updates the user's physical and training profile information.
    This data is used for all personalized recommendations and program design.
    
    Args:
        age: User's age in years
        weight_lbs: Current weight in pounds
        experience_level: Training experience ("beginner", "intermediate", "advanced")
        available_days_per_week: Number of days available for training per week
        session_duration_minutes: Available time per workout session in minutes
        equipment_access: Available equipment ("gym", "home", "minimal") - comma-separated if multiple
        height_inches: Height in inches (optional)
        body_fat_percentage: Current body fat percentage (optional)
        injury_history: Past injuries to consider (comma-separated, optional)
    
    Returns:
        dict: Confirmation of profile update with summary
    
    Example:
        >>> update_user_profile(41, 175, "intermediate", 4, 60, "gym", body_fat_percentage=20)
    """
    logger.info(f"🔧 Tool called: update_user_profile for {age}-year-old, {weight_lbs}lbs user")
    
    # Load existing profile or create new
    existing_data = _load_json_file(PROFILE_FILE, {})
    
    # Parse equipment access
    equipment_list = [eq.strip() for eq in equipment_access.split(",") if eq.strip()] if equipment_access else ["gym"]
    
    # Parse injury history
    injury_list = [inj.strip() for inj in injury_history.split(",") if inj.strip()] if injury_history else []
    
    # Update profile data
    profile_data = {
        **existing_data,
        "age": age,
        "weight_lbs": weight_lbs,
        "experience_level": experience_level,
        "available_days_per_week": available_days_per_week,
        "session_duration_minutes": session_duration_minutes,
        "equipment_access": equipment_list,
        "updated_at": datetime.now().isoformat()
    }
    
    # Add optional fields if provided
    if height_inches:
        profile_data["height_inches"] = height_inches
    if body_fat_percentage:
        profile_data["body_fat_percentage"] = body_fat_percentage
    if injury_list:
        profile_data["injury_history"] = injury_list
    
    # If this is a new profile, set created_at
    if "created_at" not in existing_data:
        profile_data["created_at"] = datetime.now().isoformat()
    
    # Validate and save
    try:
        profile = UserProfile(**profile_data)
        _save_json_file(PROFILE_FILE, profile.model_dump(mode="json"))
        
        return {
            "success": True,
            "action": "updated" if existing_data else "created",
            "profile_summary": f"{age}-year-old, {weight_lbs}lbs, {experience_level} level, {available_days_per_week}x/week training",
            "message": "Profile updated successfully. Ready for personalized recommendations."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update profile: {str(e)}"
        }

@function_tool
def get_fitness_goals() -> Dict[str, Any]:
    """Retrieve the user's current fitness goals and targets.
    
    Returns the user's stated fitness objectives, target physique, timeline,
    and specific focus areas for personalized program design.
    
    Returns:
        dict: Complete fitness goals including primary goal, target physique, focuses, timeline
    
    Example:
        >>> get_fitness_goals()
    """
    logger.info("🔧 Tool called: get_fitness_goals")
    
    goals_data = _load_json_file(GOALS_FILE)
    
    if not goals_data:
        return {
            "goals_exist": False,
            "message": "No fitness goals found. Use set_fitness_goals to define your objectives.",
            "default_goals": {
                "primary_goal": "hypertrophy",
                "body_type_target": None,
                "specific_focuses": [],
                "timeline": None
            }
        }
    
    goals = FitnessGoals(**goals_data)
    return {
        "goals_exist": True,
        "goals": goals.model_dump(),
        "summary": f"Primary goal: {goals.primary_goal}, Target: {goals.body_type_target or 'Not specified'}, Focus: {', '.join(goals.specific_focuses) or 'General'}"
    }

@function_tool
def set_fitness_goals(
    primary_goal: str,
    body_type_target: str = None,
    specific_focuses: str = "",
    timeline: str = None,
    target_weight_lbs: float = None,
    target_body_fat: float = None
) -> Dict[str, Any]:
    """Set or update fitness goals for personalized program design.
    
    Defines the user's fitness objectives which drive all program recommendations
    and coaching advice. Goals should be specific and measurable when possible.
    
    Args:
        primary_goal: Main fitness objective ("strength", "hypertrophy", "endurance", "aesthetic", "weight_loss")
        body_type_target: Desired physique type ("surfer", "model", "powerlifter", "runner", etc.)
        specific_focuses: Areas of emphasis (comma-separated: "upper_body,chest,arms")
        timeline: Target timeframe ("3_months", "6_months", "1_year")
        target_weight_lbs: Goal weight in pounds (optional)
        target_body_fat: Goal body fat percentage (optional)
    
    Returns:
        dict: Confirmation of goals update with summary
    
    Example:
        >>> set_fitness_goals("aesthetic", "surfer", "upper_body,core", "6_months")
    """
    logger.info(f"🔧 Tool called: set_fitness_goals with primary_goal={primary_goal}")
    
    # Load existing goals or create new
    existing_data = _load_json_file(GOALS_FILE, {})
    
    # Parse specific focuses
    focuses_list = [focus.strip() for focus in specific_focuses.split(",") if focus.strip()] if specific_focuses else []
    
    # Update goals data
    goals_data = {
        **existing_data,
        "primary_goal": primary_goal,
        "body_type_target": body_type_target,
        "specific_focuses": focuses_list,
        "timeline": timeline,
        "updated_at": datetime.now().isoformat()
    }
    
    # Add optional targets if provided
    if target_weight_lbs:
        goals_data["target_weight_lbs"] = target_weight_lbs
    if target_body_fat:
        goals_data["target_body_fat"] = target_body_fat
    
    # If this is new goals, set created_at
    if "created_at" not in existing_data:
        goals_data["created_at"] = datetime.now().isoformat()
    
    # Validate and save
    try:
        goals = FitnessGoals(**goals_data)
        _save_json_file(GOALS_FILE, goals.model_dump(mode="json"))
        
        focus_summary = f", focusing on {', '.join(focuses_list)}" if focuses_list else ""
        timeline_summary = f" within {timeline}" if timeline else ""
        
        return {
            "success": True,
            "action": "updated" if existing_data else "created",
            "goals_summary": f"{primary_goal.title()} goal targeting {body_type_target or 'general fitness'}{focus_summary}{timeline_summary}",
            "message": "Fitness goals updated successfully. Ready for goal-oriented programming."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update goals: {str(e)}"
        }

@function_tool
def get_user_preferences() -> Dict[str, Any]:
    """Retrieve user training preferences and exercise likes/dislikes.
    
    Returns preferences for rep ranges, training style, exercise selection,
    and other factors that influence program design.
    
    Returns:
        dict: Training preferences including rep ranges, exercise preferences, training style
    
    Example:
        >>> get_user_preferences()
    """
    logger.info("🔧 Tool called: get_user_preferences")
    
    prefs_data = _load_json_file(PREFERENCES_FILE)
    
    if not prefs_data:
        # Return default preferences
        default_prefs = UserPreferences()
        return {
            "preferences_exist": False,
            "message": "Using default preferences. Use update_user_preferences to customize.",
            "preferences": default_prefs.model_dump()
        }
    
    preferences = UserPreferences(**prefs_data)
    return {
        "preferences_exist": True,
        "preferences": preferences.model_dump(),
        "summary": f"Training style: {preferences.training_style}, Preferred exercises: {len(preferences.exercise_preferences)}, Dislikes: {len(preferences.exercise_dislikes)}"
    }

@function_tool
def update_user_preferences(
    training_style: str = "balanced",
    exercise_preferences: str = "",
    exercise_dislikes: str = "",
    rep_range_strength: str = "3-5",
    rep_range_hypertrophy: str = "8-12",
    rep_range_endurance: str = "15-20"
) -> Dict[str, Any]:
    """Update user training preferences for personalized program design.
    
    Sets preferences that influence exercise selection, rep ranges, and training
    approach to create programs aligned with user preferences.
    
    Args:
        training_style: Preferred training approach ("high_volume", "strength_focused", "time_efficient", "balanced")
        exercise_preferences: Comma-separated list of preferred exercises
        exercise_dislikes: Comma-separated list of exercises to avoid
        rep_range_strength: Rep range for strength training (e.g., "3-5")
        rep_range_hypertrophy: Rep range for hypertrophy training (e.g., "8-12")
        rep_range_endurance: Rep range for endurance training (e.g., "15-20")
    
    Returns:
        dict: Confirmation of preferences update
    
    Example:
        >>> update_user_preferences("time_efficient", "deadlift,pull-ups", "leg press", "5-6", "8-12", "15-20")
    """
    logger.info(f"🔧 Tool called: update_user_preferences with training_style={training_style}")
    
    # Load existing preferences or use defaults
    existing_data = _load_json_file(PREFERENCES_FILE, {})
    
    # Parse string inputs to lists
    exercise_prefs_list = [ex.strip() for ex in exercise_preferences.split(",") if ex.strip()] if exercise_preferences else []
    exercise_dislikes_list = [ex.strip() for ex in exercise_dislikes.split(",") if ex.strip()] if exercise_dislikes else []
    
    # Parse rep ranges
    def parse_rep_range(range_str: str) -> List[int]:
        if "-" in range_str:
            start, end = range_str.split("-")
            return [int(start.strip()), int(end.strip())]
        return [8, 12]  # Default
    
    preferred_rep_ranges = {
        "strength": parse_rep_range(rep_range_strength),
        "hypertrophy": parse_rep_range(rep_range_hypertrophy),
        "endurance": parse_rep_range(rep_range_endurance)
    }
    
    # Update preferences data
    prefs_data = {
        **existing_data,
        "training_style": training_style,
        "exercise_preferences": exercise_prefs_list,
        "exercise_dislikes": exercise_dislikes_list,
        "preferred_rep_ranges": preferred_rep_ranges,
        "updated_at": datetime.now().isoformat()
    }
    
    # If this is new preferences, set created_at
    if "created_at" not in existing_data:
        prefs_data["created_at"] = datetime.now().isoformat()
    
    # Validate and save
    try:
        preferences = UserPreferences(**prefs_data)
        _save_json_file(PREFERENCES_FILE, preferences.model_dump(mode="json"))
        
        return {
            "success": True,
            "action": "updated" if existing_data else "created",
            "preferences_summary": f"Training style: {training_style}, {len(exercise_prefs_list)} preferred exercises, {len(exercise_dislikes_list)} dislikes",
            "message": "Training preferences updated successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update preferences: {str(e)}"
        }

# Export all tools for easy importing
__all__ = [
    'get_user_profile',
    'update_user_profile',
    'get_fitness_goals',
    'set_fitness_goals',
    'get_user_preferences',
    'update_user_preferences'
]