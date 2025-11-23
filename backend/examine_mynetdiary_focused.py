"""
Focused examination of key MyNetDiary columns
"""
import pandas as pd

file_path = "../sample_data/my_net_diary/MyNetDiary_Year_2024.xls"
df = pd.read_excel(file_path, engine='xlrd')

print("🎯 Examining KEY nutrition columns...\n")

# Define the columns we actually care about
key_columns = [
    'Date & Time',
    'Meal',
    'Name',
    'Amount',
    'Calories, cals',
    'Protein, g',
    'Total Carbs, g',
    'Total Fat, g',
    'Dietary Fiber, g',
    'Total Sugars, g',
    'Sodium, mg',
]

# Extract just these columns
focused_df = df[key_columns]

print("=" * 100)
print("SAMPLE DATA (First 10 entries)")
print("=" * 100)
print(focused_df.head(10).to_string())

print("\n" + "=" * 100)
print("DAILY AGGREGATION EXAMPLE (Jan 8, 2024)")
print("=" * 100)

# Group by date and show daily totals
daily = df.groupby(df['Date & Time'].dt.date).agg({
    'Calories, cals': 'sum',
    'Protein, g': 'sum',
    'Total Carbs, g': 'sum',
    'Total Fat, g': 'sum',
}).round(1)

print(daily.head())

print("\n" + "=" * 100)
print("UNIQUE MEALS")
print("=" * 100)
print(df['Meal'].unique())

print("\n" + "=" * 100)
print("DATE RANGE")
print("=" * 100)
print(f"First entry: {df['Date & Time'].min()}")
print(f"Last entry: {df['Date & Time'].max()}")
print(f"Total days covered: {(df['Date & Time'].max() - df['Date & Time'].min()).days} days")
print(f"Total food entries: {len(df)}")
