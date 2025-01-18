import requests
from datetime import datetime, timezone
import pandas as pd
import os

def find_empty_feargreed_times(combined_dir, file_names):
    start_times = []
    end_times = []
    
    for file_name in file_names:
        file_path = os.path.join(combined_dir, file_name)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Ensure the 'FearGreedIndex' column exists
        if 'FearGreedIndex' in df.columns:
            # Find rows where 'FearGreedIndex' is empty (NaN)
            empty_cells = df[df['FearGreedIndex'].isna()]
            
            # If there are empty cells, get the start and end times
            if not empty_cells.empty:
                # Get the start time (first empty cell)
                start_time = empty_cells.iloc[0]['Open Time']
                
                # Get the end time (last empty cell)
                end_time = empty_cells.iloc[-1]['Open Time']
                
                # Add the start and end times to the lists
                start_times.append(start_time)
                end_times.append(end_time)

    # Calculate the overall start and end times
    if start_times and end_times:
        overall_start_time = min(start_times)
        overall_end_time = max(end_times)
        
        # Check and format times if needed
        def ensure_correct_format(timestamp):
            if timestamp.endswith("00:00:00"):
                return timestamp
            return f"{timestamp.split()[0]} 00:00:00"

        overall_start_time = ensure_correct_format(overall_start_time)
        overall_end_time = ensure_correct_format(overall_end_time)
        
        return overall_start_time, overall_end_time

    # Return None if no empty times found
    return None, None

def timestamp_to_human_readable_utc(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Function to fetch the Fear and Greed Index data in a range and sort it
def fetch_fear_and_greed_index_in_range(start_time, end_time):
    # Convert the start and end times to Unix timestamps
    start_timestamp = int(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    end_timestamp = int(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())

    # API URL
    url = "https://api.alternative.me/fng/"

    # Define the query parameters
    params = {
        "limit": 100,  # Get up to 100 records
        "format": "json"  # Data format
    }

    # Send the GET request to the API
    response = requests.get(url, params=params)

    # Initialize a list to store filtered data
    filtered_data = []

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            # Iterate over the data and filter by the given date range
            for entry in data["data"]:
                timestamp = int(entry["timestamp"])

                # Filter based on the time range
                if start_timestamp <= timestamp <= end_timestamp:
                    value = entry["value"]
                    human_readable_time = timestamp_to_human_readable_utc(timestamp)
                    # Add entry to filtered data (avoiding duplicates)
                    if not any(d["timestamp"] == human_readable_time for d in filtered_data):
                        filtered_data.append({
                            "value": value,
                            "timestamp": human_readable_time
                        })

            # Sort the filtered data by timestamp in ascending order
            filtered_data.sort(key=lambda x: x["timestamp"])

            print("Data fetched successfully")
        else:
            print("Error: No data found in the response.")
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}")

    return filtered_data

# Function to display data in the required format
def display_data(data):
    print("Timestamp,Value")
    for entry in data:
        print(f'{entry["timestamp"]},{entry["value"]}')

# Define the directory and file names
COMBINED_DIR = "../Data"
FILE_NAMES = [
    "BNB_1d.csv", "BNB_1h.csv", "BNB_4h.csv",
    "BTC_1d.csv", "BTC_1h.csv", "BTC_4h.csv",
    "ETH_1d.csv", "ETH_1h.csv", "ETH_4h.csv",
    "PEPE_1d.csv", "PEPE_1h.csv", "PEPE_4h.csv",
    "SOL_1d.csv", "SOL_1h.csv", "SOL_4h.csv",
]
def update_fear_greed_index(combined_dir, file_names, api_data):
    # Iterate over each file
    for file_name in file_names:
        file_path = os.path.join(combined_dir, file_name)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Ensure 'FearGreedIndex' column exists, create if missing
        if 'FearGreedIndex' not in df.columns:
            df['FearGreedIndex'] = None
        
        # Ensure the 'FearGreedIndex' column is of numeric type
        df['FearGreedIndex'] = pd.to_numeric(df['FearGreedIndex'], errors='coerce')
        
        # Iterate through the API data and update the corresponding rows in the DataFrame
        for entry in api_data:
            api_date = entry["timestamp"].split(" ")[0]  # Extract the date part
            api_value = float(entry["value"])  # Ensure value is a float
            
            # Update rows where 'Open Time' matches the API date
            df.loc[df['Open Time'].str.startswith(api_date), 'FearGreedIndex'] = api_value
        
        # Save the updated DataFrame back to the same CSV file
        df.to_csv(file_path, index=False)
        print(f"Updated file: {file_name}")

# Main function
def main():
    # Get the overall start and end times
    overall_start_time, overall_end_time = find_empty_feargreed_times(COMBINED_DIR, FILE_NAMES)
    print(f"Returned Overall Start Time: {overall_start_time}")
    print(f"Returned Overall End Time: {overall_end_time}")
    
    # Check if start and end times are None
    if overall_start_time is None or overall_end_time is None:
        print("No missing values found. Skipping API fetch and file update.")
        return
    
    # Fetch data from the API
    api_data = fetch_fear_and_greed_index_in_range(overall_end_time, overall_start_time)
    
    # Update the CSV files
    update_fear_greed_index(COMBINED_DIR, FILE_NAMES, api_data)

# Entry point for the script
if __name__ == "__main__":
    main()
