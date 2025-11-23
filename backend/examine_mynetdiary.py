"""
Quick script to examine MyNetDiary Excel file structure
This helps us understand the data format before building the parser
"""
import pandas as pd

# Read the Excel file
file_path = "../sample_data/my_net_diary/MyNetDiary_Year_2024.xls"

print("🔍 Examining MyNetDiary Excel file...\n")

# Read the file
df = pd.read_excel(file_path, engine='xlrd')

print("=" * 80)
print("FILE STRUCTURE")
print("=" * 80)
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"\nColumn names:\n{df.columns.tolist()}\n")

print("=" * 80)
print("FIRST 5 ROWS (Sample Data)")
print("=" * 80)
print(df.head())

print("\n" + "=" * 80)
print("DATA TYPES")
print("=" * 80)
print(df.dtypes)

print("\n" + "=" * 80)
print("LAST 5 ROWS (To see format consistency)")
print("=" * 80)
print(df.tail())

print("\n" + "=" * 80)
print("MISSING DATA CHECK")
print("=" * 80)
print(df.isnull().sum())

print("\n✅ Examination complete!")
