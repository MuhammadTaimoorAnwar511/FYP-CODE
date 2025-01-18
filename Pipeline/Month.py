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

# Define the variables for months, hours, and days
months = 12
h_1 = months * 30 * 24  # Total hours in 30-day months
d = months * 30  # Total days in 30-day months
h_4 = (months * 30 * 24) // 4  # Total 4-hour periods in 30-day months

# Add 3 extra days manually
d += 3
h_1 += 3 * 24  
h_4 += 3 * 6  
# Print the results to the console
print(f"Total 1-hour periods in {months} months (30-day months + 3 extra days): {h_1}")
print(f"Total 4-hour periods in {months} months (30-day months + 3 extra days): {h_4}")
print(f"Total days in {months} months (30-day months + 3 extra days): {d}")

# Store the values in variables
values = {
    "h_1": h_1,
    "h_4": h_4,
    "d": d
}

# Loop through each file and check the number of rows
for file_name in FILE_NAMES:
    file_path = os.path.join(COMBINED_DIR, file_name)
    
    # Read the CSV file
    try:
        df = pd.read_csv(file_path)
        
        # Count the rows excluding the header
        row_count = len(df)
        print(f"File: {file_name}, Rows : {row_count - 1}")
        
        # Check and remove rows if there are too many data points
        if "1d" in file_name:
            if row_count - 1 > d:  # Subtract 1 for header row
                df = df.tail(d)  # Keep only the most recent 'd' rows
                print(f"Removed {row_count - 1 - d} rows from the top.")
        elif "1h" in file_name:
            if row_count - 1 > h_1:  # Subtract 1 for header row
                df = df.tail(h_1)  # Keep only the most recent 'h_1' rows
                print(f"Removed {row_count - 1 - h_1} rows from the top.")
        elif "4h" in file_name:
            if row_count - 1 > h_4:  # Subtract 1 for header row
                df = df.tail(h_4)  # Keep only the most recent 'h_4' rows
                print(f"Removed {row_count - 1 - h_4} rows from the top.")
        
        # Save the modified file
        df.to_csv(file_path, index=False)
        print(f"File {file_name} updated and saved.")
    
    except Exception as e:
        print(f"Error reading or modifying {file_name}: {e}")
