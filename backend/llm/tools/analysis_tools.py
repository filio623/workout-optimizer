"""
Advanced analysis tools for workout pattern recognition and performance insights.
Provides intelligent analysis capabilities for progressive overload tracking,
plateau detection, and workout optimization.
"""

import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from agents import function_tool
from backend.services.workout_analyzer import WorkoutAnalyzer
from backend.services.exercise_analyzer import exercise_analyzer
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

@function_tool
def analyze_workout_patterns(time_period: str = "3 months") -> Dict[str, Any]:
    """Analyze workout patterns to identify trends, consistency, and optimization opportunities.
    
    Performs comprehensive analysis of workout data to identify:
    - Training frequency patterns
    - Volume trends over time
    - Exercise variety and rotation
    - Consistency metrics
    - Potential areas for improvement
    
    Args:
        time_period: Time period to analyze. Examples: "3 months", "6 months", "1 year"
    
    Returns:
        dict: Comprehensive analysis including frequency, volume, variety, and recommendations
    
    Example:
        >>> analyze_workout_patterns("6 months")
    """
    logger.info(f"🔧 Tool called: analyze_workout_patterns with time_period={time_period}")
    
    analyzer = WorkoutAnalyzer()
    
    # Filter data by time period
    cutoff_date = datetime.now() - timedelta(days=90)  # Default 3 months
    if "6 months" in time_period.lower():
        cutoff_date = datetime.now() - timedelta(days=180)
    elif "1 year" in time_period.lower():
        cutoff_date = datetime.now() - timedelta(days=365)
    elif "1 month" in time_period.lower():
        cutoff_date = datetime.now() - timedelta(days=30)
    
    # Filter workouts
    recent_workouts = analyzer.workouts_df[
        pd.to_datetime(analyzer.workouts_df['start_time']) >= cutoff_date
    ]
    
    # Frequency analysis
    workout_count = len(recent_workouts)
    days_analyzed = (datetime.now() - cutoff_date).days
    avg_workouts_per_week = (workout_count / days_analyzed) * 7
    
    # Volume analysis (if exercises data available)
    volume_analysis = {}
    if not analyzer.exercises_df.empty:
        recent_exercises = analyzer.exercises_df[
            pd.to_datetime(analyzer.exercises_df['workout_date']) >= cutoff_date.date()
        ]
        
        # Exercise frequency
        exercise_counts = recent_exercises['title'].value_counts()
        most_frequent = exercise_counts.head(5).to_dict()
        
        # Muscle group distribution
        muscle_group_counts = recent_exercises['primary_muscle_group'].value_counts()
        muscle_distribution = muscle_group_counts.to_dict()
        
        volume_analysis = {
            "most_frequent_exercises": most_frequent,
            "muscle_group_distribution": muscle_distribution,
            "total_exercises_performed": len(recent_exercises),
            "unique_exercises": recent_exercises['title'].nunique()
        }
    
    # Consistency analysis
    recent_workouts['workout_date'] = pd.to_datetime(recent_workouts['start_time']).dt.date
    workout_dates = recent_workouts['workout_date'].tolist()
    
    # Calculate gaps between workouts
    gaps = []
    if len(workout_dates) > 1:
        sorted_dates = sorted(workout_dates)
        for i in range(1, len(sorted_dates)):
            gap = (sorted_dates[i] - sorted_dates[i-1]).days
            gaps.append(gap)
    
    consistency_metrics = {
        "avg_days_between_workouts": np.mean(gaps) if gaps else 0,
        "max_gap_days": max(gaps) if gaps else 0,
        "min_gap_days": min(gaps) if gaps else 0,
        "consistency_score": min(100, (avg_workouts_per_week / 4) * 100)  # Assuming 4 workouts/week is optimal
    }
    
    # Generate recommendations
    recommendations = []
    
    if avg_workouts_per_week < 2:
        recommendations.append("Consider increasing workout frequency to at least 2-3 times per week for better results")
    elif avg_workouts_per_week > 6:
        recommendations.append("High training frequency detected - ensure adequate recovery between sessions")
    
    if volume_analysis.get("unique_exercises", 0) < 10:
        recommendations.append("Limited exercise variety detected - consider adding more exercises for better muscle development")
    
    if consistency_metrics["max_gap_days"] > 7:
        recommendations.append("Inconsistent training pattern detected - try to maintain regular workout schedule")
    
    return {
        "analysis_period": time_period,
        "frequency_analysis": {
            "total_workouts": workout_count,
            "avg_workouts_per_week": round(avg_workouts_per_week, 1),
            "days_analyzed": days_analyzed
        },
        "volume_analysis": volume_analysis,
        "consistency_analysis": consistency_metrics,
        "recommendations": recommendations,
        "summary": f"Analyzed {workout_count} workouts over {days_analyzed} days with {round(avg_workouts_per_week, 1)} workouts per week on average"
    }

@function_tool
def detect_plateaus(exercise_name: str = None, time_period: str = "2 months") -> Dict[str, Any]:
    """Detect training plateaus in specific exercises or overall progress.
    
    Analyzes workout data to identify when progress has stagnated and suggests
    strategies for breaking through plateaus.
    
    Args:
        exercise_name: Specific exercise to analyze (optional). If None, analyzes all exercises.
        time_period: Time period to analyze for plateau detection.
    
    Returns:
        dict: Plateau analysis with identified stagnant exercises and breakthrough strategies
    
    Example:
        >>> detect_plateaus("Bench Press", "3 months")
        >>> detect_plateaus()  # Analyze all exercises
    """
    logger.info(f"🔧 Tool called: detect_plateaus with exercise_name={exercise_name}")
    
    analyzer = WorkoutAnalyzer()
    
    # Filter by time period
    cutoff_date = datetime.now() - timedelta(days=60)  # Default 2 months
    if "3 months" in time_period.lower():
        cutoff_date = datetime.now() - timedelta(days=90)
    elif "1 month" in time_period.lower():
        cutoff_date = datetime.now() - timedelta(days=30)
    
    # Get sets data for analysis
    if analyzer.sets_df.empty:
        return {"error": "No sets data available for plateau analysis"}
    
    recent_sets = analyzer.sets_df[
        pd.to_datetime(analyzer.sets_df['workout_date']) >= cutoff_date.date()
    ]
    
    plateau_results = []
    
    # Analyze specific exercise or all exercises
    exercises_to_analyze = [exercise_name] if exercise_name else recent_sets['exercise_title'].unique()
    
    for exercise in exercises_to_analyze:
        if exercise is None:
            continue
            
        exercise_sets = recent_sets[recent_sets['exercise_title'] == exercise]
        
        if len(exercise_sets) < 5:  # Need at least 5 sets for meaningful analysis
            continue
        
        # Focus on weighted exercises for plateau detection
        weighted_sets = exercise_sets[exercise_sets['weight_kg'].notna()]
        
        if len(weighted_sets) < 3:
            continue
        
        # Sort by date to track progression
        weighted_sets = weighted_sets.sort_values('workout_date')
        
        # Calculate progression metrics
        weights = weighted_sets['weight_kg'].tolist()
        dates = weighted_sets['workout_date'].tolist()
        
        # Check for plateau (no improvement in last 3-4 workouts)
        if len(weights) >= 4:
            recent_weights = weights[-4:]
            max_recent = max(recent_weights)
            
            # If max weight in recent sessions hasn't improved
            if all(w <= max_recent for w in recent_weights[-3:]):
                plateau_duration = len([w for w in recent_weights if w == max_recent])
                
                # Generate breakthrough strategies
                strategies = []
                strategies.append("Consider a deload week (reduce weight by 10-15%)")
                strategies.append("Try different rep ranges (if doing 8-12, try 5-6 or 15-20)")
                strategies.append("Add pause reps or tempo variations")
                strategies.append("Switch to a similar exercise variation")
                strategies.append("Increase training frequency for this movement")
                
                plateau_results.append({
                    "exercise": exercise,
                    "plateau_detected": True,
                    "current_max_weight_kg": max_recent,
                    "plateau_duration_sessions": plateau_duration,
                    "last_workout_date": str(dates[-1]),
                    "breakthrough_strategies": strategies
                })
    
    # Overall assessment
    total_exercises_analyzed = len(exercises_to_analyze)
    plateaued_exercises = len(plateau_results)
    plateau_percentage = (plateaued_exercises / total_exercises_analyzed * 100) if total_exercises_analyzed > 0 else 0
    
    general_recommendations = []
    if plateau_percentage > 50:
        general_recommendations.append("High plateau rate detected - consider periodization or program change")
        general_recommendations.append("Review recovery, nutrition, and sleep quality")
        general_recommendations.append("Consider working with a trainer for form assessment")
    elif plateau_percentage > 25:
        general_recommendations.append("Some plateaus detected - normal part of training progression")
        general_recommendations.append("Focus on consistent progression in non-plateaued exercises")
    
    return {
        "analysis_period": time_period,
        "exercises_analyzed": total_exercises_analyzed,
        "plateaued_exercises": plateaued_exercises,
        "plateau_percentage": round(plateau_percentage, 1),
        "plateau_details": plateau_results,
        "general_recommendations": general_recommendations,
        "summary": f"Analyzed {total_exercises_analyzed} exercises, found {plateaued_exercises} with potential plateaus ({plateau_percentage:.1f}%)"
    }

@function_tool
def assess_muscle_group_balance() -> Dict[str, Any]:
    """Assess muscle group training balance to identify imbalances and suggest corrections.
    
    Analyzes the distribution of training volume across different muscle groups
    to identify potential imbalances that could lead to injury or aesthetic issues.
    
    Returns:
        dict: Balance analysis with imbalances identified and correction recommendations
    
    Example:
        >>> assess_muscle_group_balance()
    """
    logger.info(f"🔧 Tool called: assess_muscle_group_balance")
    
    analyzer = WorkoutAnalyzer()
    
    if analyzer.exercises_df.empty:
        return {"error": "No exercise data available for balance analysis"}
    
    # Analyze last 3 months for current balance
    cutoff_date = datetime.now() - timedelta(days=90)
    recent_exercises = analyzer.exercises_df[
        pd.to_datetime(analyzer.exercises_df['workout_date']) >= cutoff_date.date()
    ]
    
    # Count exercises by muscle group
    muscle_group_counts = recent_exercises['primary_muscle_group'].value_counts()
    total_exercises = len(recent_exercises)
    
    # Calculate percentages
    muscle_group_percentages = {}
    for muscle_group, count in muscle_group_counts.items():
        if muscle_group and pd.notna(muscle_group):
            muscle_group_percentages[muscle_group] = round((count / total_exercises) * 100, 1)
    
    # Define ideal ranges for muscle group balance
    ideal_ranges = {
        "chest": (8, 15),
        "back": (12, 20),
        "shoulders": (8, 15),
        "arms": (10, 18),
        "legs": (20, 30),
        "core": (5, 12),
        "glutes": (8, 15)
    }
    
    # Identify imbalances
    imbalances = []
    recommendations = []
    
    for muscle_group, (min_pct, max_pct) in ideal_ranges.items():
        current_pct = muscle_group_percentages.get(muscle_group, 0)
        
        if current_pct < min_pct:
            imbalances.append({
                "muscle_group": muscle_group,
                "type": "undertrained",
                "current_percentage": current_pct,
                "ideal_range": f"{min_pct}-{max_pct}%",
                "deficit": min_pct - current_pct
            })
            recommendations.append(f"Increase {muscle_group} training - currently {current_pct}%, should be {min_pct}-{max_pct}%")
        
        elif current_pct > max_pct:
            imbalances.append({
                "muscle_group": muscle_group,
                "type": "overtrained",
                "current_percentage": current_pct,
                "ideal_range": f"{min_pct}-{max_pct}%",
                "excess": current_pct - max_pct
            })
            recommendations.append(f"Reduce {muscle_group} training frequency - currently {current_pct}%, should be {min_pct}-{max_pct}%")
    
    # Check for common imbalance patterns
    push_muscles = muscle_group_percentages.get("chest", 0) + muscle_group_percentages.get("shoulders", 0)
    pull_muscles = muscle_group_percentages.get("back", 0)
    
    if push_muscles > pull_muscles * 1.3:
        recommendations.append("Push/Pull imbalance detected - increase back/pulling exercises")
    
    # Balance score (0-100)
    balance_score = 100
    for imbalance in imbalances:
        if imbalance["type"] == "undertrained":
            balance_score -= imbalance["deficit"] * 2
        else:
            balance_score -= imbalance["excess"] * 1.5
    
    balance_score = max(0, balance_score)
    
    return {
        "analysis_period": "Last 3 months",
        "total_exercises_analyzed": total_exercises,
        "muscle_group_distribution": muscle_group_percentages,
        "balance_score": round(balance_score, 1),
        "imbalances_detected": len(imbalances),
        "imbalance_details": imbalances,
        "recommendations": recommendations,
        "summary": f"Balance score: {balance_score:.1f}/100 with {len(imbalances)} imbalances detected"
    }

# Export all tools for easy importing
__all__ = [
    'analyze_workout_patterns',
    'detect_plateaus',
    'assess_muscle_group_balance'
]