import os
import pandas as pd

# Define the directory and file names
COMBINED_DIR = "../Data"
FILE_NAMES = [
    "BNB_1d.csv", "BNB_1h.csv", "BNB_4h.csv",
    "BTC_1d.csv", "BTC_1h.csv", "BTC_4h.csv",
    "ETH_1d.csv", "ETH_1h.csv", "ETH_4h.csv",
    "PEPE_1d.csv", "PEPE_1h.csv", "PEPE_4h.csv",
    "SOL_1d.csv", "SOL_1h.csv", "SOL_4h.csv",
]

# Loop through each file
for file_name in FILE_NAMES:
    file_path = os.path.join(COMBINED_DIR, file_name)

    # Check if the file exists
    if os.path.exists(file_path):
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Update the TwitterIndex column with the value 50.0 if not already set
            if 'TwitterIndex' in df.columns:
                if not (df['TwitterIndex'] == 50.0).all():
                    df['TwitterIndex'] = 50.0

                    # Save the updated DataFrame back to the same file
                    df.to_csv(file_path, index=False)
                    print(f"Updated and saved: {file_name}")
                else:
                    print(f"Skipped {file_name}: All values in 'TwitterIndex' are already 50.0")
            else:
                print(f"Column 'TwitterIndex' not found in {file_name}")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
    else:
        print(f"File not found: {file_name}")
