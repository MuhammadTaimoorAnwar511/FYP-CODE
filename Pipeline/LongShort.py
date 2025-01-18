import os
import pandas as pd
import requests
from datetime import datetime, timezone

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

# Convert timestamp in milliseconds to human-readable UTC format
def timestamp_to_human_readable_utc(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Function to fetch Long/Short ratio for a given time range and symbol
def Fetch_Long_Short_Ratio(start_time, end_time, symbol, interval):
    # Check if start_time and end_time are numeric (float64), convert them to strings
    if isinstance(start_time, (float, int)):
        start_time = datetime.fromtimestamp(start_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(end_time, (float, int)):
        end_time = datetime.fromtimestamp(end_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # Convert the start and end times to timestamp (milliseconds), ensuring they are in UTC
    start_timestamp = int(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000)

    # API request URL
    url = "https://api.bybit.com/v5/market/account-ratio"

    # Define the query parameters for a chunk
    params = {
        "category": "linear",  # USDT Perpetual contract
        "symbol": symbol,      # Symbol
        "period": interval,    # Interval passed as parameter
        "limit": 500           # Optional limit on data size (max 500)
    }

    # Initialize variables to handle chunked requests
    all_data = []
    current_start_timestamp = start_timestamp
    chunk_size = 10 * 24 * 60 * 60 * 1000  # Define the chunk size for each request (in milliseconds)

    # Loop through the time range in chunks
    while current_start_timestamp < end_timestamp:
        current_end_timestamp = min(current_start_timestamp + chunk_size, end_timestamp)

        # Update the start and end time for the API request
        params['startTime'] = str(current_start_timestamp)
        params['endTime'] = str(current_end_timestamp)

        # Send the GET request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if data["retCode"] == 0:
                # Add the current page data to the all_data list
                all_data.extend(data["result"]["list"])
            else:
                print("Error:", data["retMsg"])
                break
        else:
            print("Failed to fetch data. Status Code:", response.status_code)
            break

        # Move to the next time chunk
        current_start_timestamp = current_end_timestamp

    # Sort the result based on the timestamp
    sorted_data = sorted(all_data, key=lambda x: x["timestamp"])

    # Remove duplicates, keeping the first occurrence
    unique_data = []
    seen_timestamps = set()
    for entry in sorted_data:
        if entry["timestamp"] not in seen_timestamps:
            unique_data.append(entry)
            seen_timestamps.add(entry["timestamp"])

    return unique_data

# Function to write the Long/Short ratio data to the CSV file
def Write_to_csv(file_path, fetched_data):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Check if there are any empty cells in the 'LSRatio' column
    if df["LSRatio"].isnull().sum() == 0:
        #print(f"{file_path}: No empty cells in LSRatio. Skipping file.")
        print(f"Data Already Up to date in {file_path}: Skipping file.")
        
        return
    
    if "LSRatio" not in df.columns:
        df["LSRatio"] = None  # Add the LSRatio column if not present

    for entry in fetched_data:
        timestamp = int(entry['timestamp'])
        try:
            buy_ratio = float(entry['buyRatio'])
            sell_ratio = float(entry['sellRatio'])
            # Calculate Long/Short Ratio
            long_short_ratio = buy_ratio / sell_ratio if sell_ratio != 0 else None
            long_short_ratio = round(long_short_ratio, 4) if long_short_ratio is not None else None
        except ValueError:
            long_short_ratio = None  # Handle any conversion errors if values are not valid numbers

        # Convert timestamp to human-readable UTC
        human_readable_time = timestamp_to_human_readable_utc(timestamp)

        # Match the timestamp with the Open Time column and update LSRatio
        match = df[df["Open Time"] == human_readable_time]
        if not match.empty:
            df.loc[df["Open Time"] == human_readable_time, "LSRatio"] = long_short_ratio

    # Save the updated CSV file
    df.to_csv(file_path, index=False)
    print(f"Updated LSRatio values written to {file_path}")

def Check_LSRatio_Missing(df):
    """
    Checks the 'LSRatio' column in the DataFrame for missing values.
    Returns the start and end times for missing values if found, or None if no missing values exist.
    """
    # Check if the 'LSRatio' column exists and has missing values
    if "LSRatio" not in df.columns or df["LSRatio"].isnull().sum() == 0:
        return None, None  # No missing values or column not found
    
    # Find the first and last missing values in 'LSRatio'
    missing_indices = df[df["LSRatio"].isnull()].index
    start_time = df.loc[missing_indices[0], "Open Time"]
    end_time = df.loc[missing_indices[-1], "Open Time"]
    
    return start_time, end_time

# Process each CSV file
for file_name in FILE_NAMES:
    file_path = os.path.join(COMBINED_DIR, file_name)
    if os.path.exists(file_path):
        # Extract symbol and interval from file name
        symbol, interval = file_name.split('_')
        if symbol == 'PEPE':
            symbol = '1000' + symbol

        symbol = symbol + 'USDT'
        interval = interval.split('.')[0]

        # Load the CSV into a DataFrame
        df = pd.read_csv(file_path)
        
        # Check for missing LSRatio values and get the start and end times
        start_time, end_time = Check_LSRatio_Missing(df)
        if start_time is None or end_time is None:
            print(f"No missing values in 'LSRatio' for {file_name}. Skipping.")
            continue  # Skip to the next file if no missing values

        # Print the determined time range
        print(f"Fetching 'LSRatio' from {start_time} to {end_time} in {file_name}.")

        # Fetch Long/Short Ratio data
        fetched_data = Fetch_Long_Short_Ratio(start_time, end_time, symbol, interval)

        # Write the fetched data to the CSV
        Write_to_csv(file_path, fetched_data)
    else:
        print(f"{file_name}: File not found in directory.")
