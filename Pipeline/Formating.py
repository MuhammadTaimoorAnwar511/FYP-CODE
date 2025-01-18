import os
import pandas as pd

# Directory containing the CSV files
COMBINED_DIR = "../Data"

# List of CSV files to process
FILE_NAMES = [
    "BNB_1d.csv", "BNB_1h.csv", "BNB_4h.csv",
    "BTC_1d.csv", "BTC_1h.csv", "BTC_4h.csv",
    "ETH_1d.csv", "ETH_1h.csv", "ETH_4h.csv",
    "PEPE_1d.csv", "PEPE_1h.csv", "PEPE_4h.csv",
    "SOL_1d.csv", "SOL_1h.csv", "SOL_4h.csv",
]

def remove_duplicates(file_path):
    """Removes duplicate rows in a CSV file."""
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        initial_row_count = len(df)
        df = df.drop_duplicates(keep='first')
        final_row_count = len(df)
        df.to_csv(file_path, index=False)
        print(f"Removed {initial_row_count - final_row_count} duplicate rows from {file_path}.")
    else:
        print(f"File {file_path} does not exist. Skipping.")

def add_columns(df):
    """Adds missing columns 'FearGreedIndex' and 'TwitterIndex' to the DataFrame."""
    if "FearGreedIndex" not in df.columns:
        df["FearGreedIndex"] = ""  # Empty values
    if "TwitterIndex" not in df.columns:
        df["TwitterIndex"] = ""  # Empty values
    return df

def format_timestamps(df, file_name):
    """Formats the 'Open Time' column for daily files to include '00:00:00'."""
    if "_1d.csv" in file_name and 'Open Time' in df.columns:
        df['Open Time'] = df['Open Time'].astype(str).apply(
            lambda x: f"{x} 00:00:00" if " " not in x else x
        )
    return df

def reorder_columns(df):
    """Reorders columns to match the desired order."""
    column_order = [
        "Open Time", "Open", "High", "Low", "Close", "Quote Asset Volume",
        "Open Interest (USD)", "LSRatio", "FearGreedIndex", "TwitterIndex"
    ]
    return df[column_order]

def needs_formatting(df, file_name):
    """Checks if the file needs timestamp formatting."""
    if "_1d.csv" in file_name and 'Open Time' in df.columns:
        return any(" " not in str(x) for x in df['Open Time'])
    return False

def process_file(file_name):
    """Processes a single CSV file to modify and update content."""
    file_path = os.path.join(COMBINED_DIR, file_name)

    if not os.path.exists(file_path):
        print(f"File {file_name} does not exist. Skipping.")
        return

    try:
        df = pd.read_csv(file_path)

        # Check if 'FearGreedIndex' and 'TwitterIndex' columns exist and timestamp needs formatting
        if "FearGreedIndex" in df.columns and "TwitterIndex" in df.columns and not needs_formatting(df, file_name):
            print(f"File {file_name} is already in the correct format. Skipping.")
            return

        # Add missing columns
        df = add_columns(df)

        # Format timestamps
        df = format_timestamps(df, file_name)

        # Reorder columns
        df = reorder_columns(df)

        # Save updated file
        df.to_csv(file_path, index=False)
        print(f"Successfully updated {file_name}.")

        # Remove duplicates
        remove_duplicates(file_path)

    except Exception as e:
        print(f"Error processing {file_name}: {e}")


def process_files():
    """Processes all CSV files in the list."""
    for file_name in FILE_NAMES:
        process_file(file_name)

# Process the files
process_files()
