import pandas as pd
import numpy as np

# Load the Excel file
file_path = r"C:\Users\sanju\OneDrive\Desktop\merged_all_phases.xlsx"  # Update with the correct file path
df = pd.read_excel(file_path, dtype=str)  # Read all columns as strings

# Function to clean and convert numeric values properly
def clean_numeric(column):
    column = column.str.replace(r'[^\d]', '', regex=True)  # Remove non-numeric characters
    column = column.replace('', np.nan)  # Replace empty strings with NaN
    return pd.to_numeric(column, errors='coerce')  # Convert valid numbers, keep NaN

# Convert "कुल प्राप्त मत" column
if "कुल प्राप्त मत" in df.columns:
    df["कुल प्राप्त मत"] = clean_numeric(df["कुल प्राप्त मत"])

# Save the updated file
output_file = "merged_all_phases_fixed.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ Fixed number formatting! File saved as: {output_file}")
