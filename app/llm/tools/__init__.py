"""
Consolidated LLM Tools package for the AI-agentic workout optimizer.
Provides intelligent function tools for workout analysis, program generation,
and routine management through the OpenAI Agents SDK.
"""

# Core data retrieval tools
from .core_tools import (
    get_workout_data,
    get_exercise_data,
    get_workout_by_id,
    get_workouts,
    get_routine_by_id,
    get_routines
)

# Advanced analysis tools
from .analysis_tools import (
    analyze_workout_patterns,
    detect_plateaus,
    assess_muscle_group_balance
)

# User profile and goals management
from .user_tools import (
    get_user_profile,
    update_user_profile,
    get_fitness_goals,
    set_fitness_goals,
    get_user_preferences,
    update_user_preferences
)

# Enhanced program generation tools
from .program_tools import (
    generate_workout_program,
    create_routine,
    create_workout_program
)

# Routine modification tools
from .modification_tools import (
    find_exercise_alternatives,
    swap_exercise_in_routine,
    optimize_routine_for_goal
)

# Complete tool exports for agent configuration
__all__ = [
    # Core data tools
    'get_workout_data',
    'get_exercise_data', 
    'get_workout_by_id',
    'get_workouts',
    'get_routine_by_id',
    'get_routines',
    
    # Analysis tools
    'analyze_workout_patterns',
    'detect_plateaus',
    'assess_muscle_group_balance',
    
    # User management tools
    'get_user_profile',
    'update_user_profile',
    'get_fitness_goals',
    'set_fitness_goals',
    'get_user_preferences',
    'update_user_preferences',
    
    # Program generation tools
    'generate_workout_program',
    'create_routine',
    'create_workout_program',
    
    # Modification tools
    'find_exercise_alternatives',
    'swap_exercise_in_routine',
    'optimize_routine_for_goal'
]