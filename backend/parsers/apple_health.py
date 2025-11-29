from typing import List, Dict
from datetime import datetime
import json
from pathlib import Path

class AppleHealthParser:
    """Parse Apple Health JSON export files and extract health metrics."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                self.health_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {file_path}") from e
        
        if "data" not in self.health_data:
            raise ValueError("Invalid Apple Health data format: 'data' key not found.")
        if "metrics" not in self.health_data["data"]:
            raise ValueError("Invalid Apple Health data format: 'metrics' key not found.")
        
    def parse(self) -> Dict[str, List[Dict]]:
        """Main entry point to parse the Apple Health data file."""
        return {
            "daily_metrics": self._parse_daily_metrics(),
            "raw_metrics": self._parse_raw_metrics(),
            "workouts": self._parse_workouts(),
        }
    
    def _parse_daily_metrics(self) -> List[Dict]:
        """Parse daily aggregated health metrics from Apple Health data."""
        # Implementation goes here
        metrics = self.health_data["data"]["metrics"]

        daily_data = {}

        for metric in metrics:
            metric_name = metric["name"]
            print(f"Processing metric: {metric_name}")
            metric_units = metric.get("units")

            for data_point in metric["data"]:
                date_str = data_point["date"]
                date = self._parse_date(date_str)

                if date not in daily_data:
                    daily_data[date] = {}

                if metric_name == "heart_rate":
                    daily_data[date][metric_name] = {
                        "min": data_point.get("Min"),
                        "max": data_point.get("Max"),
                        "avg": data_point.get("Avg"),
                        "units": metric_units,
                        "source": data_point.get("source")
                    }
                else:
                    daily_data[date][metric_name] = {
                        "value": data_point.get("qty"),
                        "units": metric_units,
                        "source": data_point.get("source")
                    }

        column_mapping = {
            "step_count": "steps",
            "weight_body_mass": "weight_lbs",
            "active_energy": "active_calories",
            "resting_heart_rate": "resting_heart_rate",
            "walking_running_distance": "distance_miles",
            "apple_exercise_time": "exercise_minutes",
            "apple_stand_time": "stand_minutes"
        }

        result = []

        for date, metric_values in daily_data.items():
            row = {
                "metric_date": date,
                "steps": None,
                "weight_lbs": None,
                "active_calories": None,
                "resting_heart_rate": None,
                "distance_miles": None,
                "exercise_minutes": None,
                "stand_minutes": None,
                "workout_minutes": None,  # Will calculate from workouts later
                "additional_metrics": {}
            }
            for metric_name, metric_data in metric_values.items():
                if metric_name in column_mapping:
                    db_column = column_mapping[metric_name]
                    row[db_column] = metric_data.get("value")
                else:
                    row["additional_metrics"][metric_name] = metric_data

            result.append(row)

        return result


    def _parse_raw_metrics(self) -> List[Dict]:
        """
        Parse raw health metrics from Apple Health data.
        Extracts time-series data from workouts (heart rate samples, steps, energy, recovery).
        """
        workouts = self.health_data["data"].get("workouts", [])
        raw_metrics = []

        for workout in workouts:
            workout_id = workout.get("id")

            # Extract heart rate time-series
            heart_rate_data = workout.get("heartRateData", [])
            for hr_point in heart_rate_data:
                raw_metrics.append({
                    "metric_date": self._parse_datetime(hr_point.get("date")),
                    "metric_type": "heart_rate",
                    "value": hr_point.get("Avg"),
                    "unit": hr_point.get("units", "bpm"),
                    "source": hr_point.get("source"),
                    "source_metadata": {
                        "workout_id": workout_id,
                        "min": hr_point.get("Min"),
                        "max": hr_point.get("Max"),
                        "avg": hr_point.get("Avg")
                    }
                })

            # Extract step count time-series
            step_data = workout.get("stepCount", [])
            for step_point in step_data:
                raw_metrics.append({
                    "metric_date": self._parse_datetime(step_point.get("date")),
                    "metric_type": "step_count",
                    "value": step_point.get("qty"),
                    "unit": step_point.get("units", "steps"),
                    "source": step_point.get("source"),
                    "source_metadata": {
                        "workout_id": workout_id
                    }
                })

            # Extract active energy time-series
            energy_data = workout.get("activeEnergy", [])
            for energy_point in energy_data:
                raw_metrics.append({
                    "metric_date": self._parse_datetime(energy_point.get("date")),
                    "metric_type": "active_energy",
                    "value": energy_point.get("qty"),
                    "unit": energy_point.get("units", "kcal"),
                    "source": energy_point.get("source"),
                    "source_metadata": {
                        "workout_id": workout_id
                    }
                })

            # Extract heart rate recovery time-series
            hr_recovery_data = workout.get("heartRateRecovery", [])
            for recovery_point in hr_recovery_data:
                raw_metrics.append({
                    "metric_date": self._parse_datetime(recovery_point.get("date")),
                    "metric_type": "heart_rate_recovery",
                    "value": recovery_point.get("Avg"),
                    "unit": recovery_point.get("units", "bpm"),
                    "source": recovery_point.get("source"),
                    "source_metadata": {
                        "workout_id": workout_id,
                        "min": recovery_point.get("Min"),
                        "max": recovery_point.get("Max"),
                        "avg": recovery_point.get("Avg")
                    }
                })

        return raw_metrics

    def _parse_workouts(self) -> List[Dict]:
        """
        Parse workout sessions from Apple Health data.
        Extracts workout summaries and metadata for storage in workout_cache table.
        """
        workouts = self.health_data["data"].get("workouts", [])
        parsed_workouts = []

        for workout in workouts:
            # Parse start/end times
            start_time = self._parse_datetime(workout.get("start"))
            end_time = self._parse_datetime(workout.get("end"))

            # Calculate duration in minutes
            duration_seconds = workout.get("duration", 0)
            duration_minutes = int(duration_seconds / 60) if duration_seconds else None

            # Extract calories burned
            calories_burned = None
            active_energy = workout.get("activeEnergyBurned", {})
            if isinstance(active_energy, dict):
                calories_burned = active_energy.get("qty")

            # Extract distance
            distance = None
            distance_data = workout.get("distance", {})
            if isinstance(distance_data, dict):
                distance = distance_data.get("qty")

            # Calculate average heart rate if available
            avg_heart_rate = None
            heart_rate_data = workout.get("heartRateData", [])
            if heart_rate_data:
                avg_values = [hr.get("Avg") for hr in heart_rate_data if hr.get("Avg")]
                if avg_values:
                    avg_heart_rate = sum(avg_values) / len(avg_values)

            parsed_workouts.append({
                "source": "apple_health",
                "source_workout_id": workout.get("id"),
                "workout_date": start_time,
                "title": workout.get("name"),
                "duration_minutes": duration_minutes,
                "calories_burned": int(calories_burned) if calories_burned else None,
                "total_sets": None,  # Not available in Apple Health
                "total_volume_kg": None,  # Not available in Apple Health
                "exercise_count": None,  # Not available in Apple Health
                "muscle_groups": None,  # Not available in Apple Health
                "workout_data": workout  # Store full workout JSON
            })

        return parsed_workouts

    def _parse_date(self, date_str: str) -> datetime:
        """Helper method to parse date strings to date objects (daily aggregates)."""
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
        return formatted_date.date()

    def _parse_datetime(self, date_str: str) -> datetime:
        """Helper method to parse date strings to datetime objects (timestamps)."""
        if not date_str:
            return None
        # Parse the datetime with timezone, then remove timezone info (database expects naive)
        dt_with_tz = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
        return dt_with_tz.replace(tzinfo=None)

if __name__ == "__main__":
    parser = AppleHealthParser('/Users/jamesfilios/Software_Projects/Workout_Optimizer/sample_data/apple_health/HealthAutoExport-2023-11-16-2025-11-23.json')
    data = parser.parse()
    #print (data)

    