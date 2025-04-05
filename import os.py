import os
import pandas as pd

# Define the folder containing the extracted Excel files
folder_path = r"C:\Users\sanju\OneDrive\Desktop\Till phase 9"  # Change this to the extracted folder path

# List all Excel files in the folder
excel_files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]

# Create an empty list to store dataframes
df_list = []

# Read and clean each Excel file
for file in excel_files:
    file_path = os.path.join(folder_path, file)
    
    try:
        df = pd.read_excel(file_path, dtype=str)  # Read the file (force all data to string to avoid type mismatches)
        
        # Standardize column names (remove extra spaces, convert to lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        # Append the dataframe to the list without removing missing values
        df_list.append(df)

        print(f"Processed: {file}")

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Merge all dataframes
if df_list:
    merged_df = pd.concat(df_list, ignore_index=True)
    
    # Drop duplicate rows if any (but keep missing values)
    merged_df.drop_duplicates(inplace=True)
    
    # Save the merged data with missing values intact
    output_file = "merged_all_phases.xlsx"
    merged_df.to_excel(output_file, index=False)
    
    print(f"\n✅ All phases merged successfully! File saved as: {output_file}")
else:
    print("❌ No valid files found to merge.")
