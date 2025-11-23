import pandas as pd
import numpy as np
from typing import List, Dict
from pprint import pprint
import json

"""
  MyNetDiary Excel Parser
  Parses MyNetDiary Excel exports and aggregates into daily nutrition summaries
"""

def pandas_to_json_serializable(obj):
    """Convert pandas types to JSON-serializable Python types"""
    if pd.isna(obj):
        return None
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeTZDtype)):
        return obj.isoformat()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def clean_nan_values(data):
    """Recursively clean NaN values from nested dict/list structures"""
    if isinstance(data, list):
        return [clean_nan_values(item) for item in data]
    elif isinstance(data, dict):
        return {key: clean_nan_values(value) for key, value in data.items()}
    elif pd.isna(data):
        return None
    elif isinstance(data, float) and (np.isnan(data) or np.isinf(data)):
        return None
    else:
        return data

class MyNetDiaryParser:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.daily_data = []

    def parse(self) -> List[Dict]:
        """
        Main method to parse the MyNetDiary Excel file and return daily summaries
        Returns:
            List[Dict]: List of daily nutrition summaries
        """
        self._read_excel()
        self._aggregate_daily()
        return self.daily_data
    
    def _read_excel(self):
        # Read the Excel file into a DataFrame
        self.df = pd.read_excel(self.file_path, engine='xlrd')
        print(f"Excel file read successfully with {len(self.df)} rows.")
    
    def _aggregate_daily(self) -> pd.DataFrame:
        df = self.df.copy()

        df['Date & Time'] = pd.to_datetime(df['Date & Time'])

        grouped_dates = df.groupby(df['Date & Time'].dt.date)

        for date, group in grouped_dates:
            # Convert pandas DataFrame to native Python types for JSON serialization
            raw_data_dict = group.to_dict('records')
            # Convert all pandas types to JSON-serializable Python types
            raw_data_serialized = json.loads(json.dumps(raw_data_dict, default=pandas_to_json_serializable))
            # Clean any remaining NaN values
            raw_data = clean_nan_values(raw_data_serialized)

            daily_summary = {
                'log_date': date,
                'calories': float(group['Calories, cals'].sum()),
                'protein_g': float(group['Protein, g'].sum()),
                'carbs_g': float(group['Total Carbs, g'].sum()),
                'fats_g': float(group['Total Fat, g'].sum()),
                'fiber_g': float(group['Dietary Fiber, g'].sum()),
                'source': 'mynetdiary',
                'raw_data': raw_data  # Dump all columns as JSON (fully serializable)
            }
            self.daily_data.append(daily_summary)


if __name__ == "__main__":

    parser = MyNetDiaryParser('../sample_data/my_net_diary/MyNetDiary_Year_2024.xls')
    daily_summaries = parser.parse()

    pprint (daily_summaries)