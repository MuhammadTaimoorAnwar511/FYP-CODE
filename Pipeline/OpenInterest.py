import requests
import pandas as pd
from datetime import timedelta
import os
import csv


def fetch_open_interest_for_range_1H(start_time_utc, end_time_utc, limit, symbol):
    # List to hold all results
    all_data = []
    seen_timestamps = set() 
    
    # Initialize variables
    current_start_time = start_time_utc
    
    while current_start_time < end_time_utc:
        #print(f"Current start time: {current_start_time}")  
        
        # Convert start and end times to timestamps in milliseconds
        begin = int(current_start_time.timestamp() * 1000)
        
        # Ensure we do not exceed the end time
        next_end_time = current_start_time + timedelta(hours=limit)
        
        # If next_end_time exceeds the end_time_utc, set it to end_time_utc
        if next_end_time > end_time_utc:
            next_end_time = end_time_utc
        
        end = int(next_end_time.timestamp() * 1000)
        
        # Define the API endpoint and parameters
        url = 'https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history'
        params = {
            'instId': symbol, 
            'period': '1H',
            'begin': str(begin),
            'end': str(end),
            'limit': str(limit)
        }
        
        # Send the GET request to the API
        response = requests.get(url, params=params)
        data = response.json()
        
        # Check if the response contains data
        if data['code'] == '0' and data['data']:
            # Convert the data into a pandas DataFrame
            df = pd.DataFrame(data['data'], columns=['ts', 'oi', 'oiCcy', 'oiUsd'])

            # Keep only the timestamp and open interest in USD
            df = df[['ts', 'oiUsd']]

            # Convert the timestamp to a readable datetime format (milliseconds to seconds) in UTC
            df['ts'] = pd.to_datetime(df['ts'].astype(int), unit='ms', utc=True)

            # Remove duplicates for current batch based on timestamp (if any)
            df = df[~df['ts'].isin(seen_timestamps)]
            
            # If new data is found, append it to the list and update seen timestamps
            if not df.empty:
                all_data.append(df)
                seen_timestamps.update(df['ts'])

                # Update current_start_time for the next chunk (ensure no overlap)
                current_start_time = pd.to_datetime(df['ts'].iloc[-1]) + timedelta(hours=1)
            else:
                # If no new data, increment the current_start_time by 1 hour manually
                #print(f"No new data for {current_start_time}. Incrementing by 1 hour.")
                current_start_time += timedelta(hours=1)
        else:
            # If no data found for this range, break out of the loop
            print("No data found or error fetching data for this range.")
            break
    
    # Combine all chunks into one DataFrame
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)

        # Sort the data by timestamp (ascending order)
        df_all_sorted = df_all.sort_values(by='ts', ascending=True)

        # Remove duplicates if any (in case they are present after pagination)
        df_all_sorted = df_all_sorted.drop_duplicates(subset=['ts'], keep='last')

        # Reset index to start from 0
        df_all_sorted.reset_index(drop=True, inplace=True)

        # Print the sorted DataFrame with readable human time and relevant columns
        pd.set_option('display.max_rows', None)  # Set this to None to display all rows
        pd.set_option('display.max_columns', None)  # Optionally, set this to None for all columns
        print(df_all_sorted[['ts', 'oiUsd']])
        # Return the sorted DataFrame with the relevant columns
        return df_all_sorted[['ts', 'oiUsd']]
    else:
        print('No data retrieved or an error occurred.')
        return None

def fetch_open_interest_for_range_4H(start_time_utc, end_time_utc, limit, symbol):
    #print(f"Fetching 4H data for {symbol} from {start_time_utc} to {end_time_utc}")
    
    # List to hold all results
    all_data = []
    seen_timestamps = set() 
    
    # Initialize variables
    current_start_time = start_time_utc
    
    while current_start_time < end_time_utc:
        #print(f"Current start time: {current_start_time}")
        
        # Convert start and end times to timestamps in milliseconds
        begin = int(current_start_time.timestamp() * 1000)
        
        # Ensure we do not exceed the end time
        next_end_time = current_start_time + timedelta(hours=limit)
        
        # If next_end_time exceeds the end_time_utc, set it to end_time_utc
        if next_end_time > end_time_utc:
            next_end_time = end_time_utc
        
        end = int(next_end_time.timestamp() * 1000)
        
        # Define the API endpoint and parameters
        url = 'https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history'
        params = {
            'instId': symbol, 
            'period': '4H',
            'begin': str(begin),
            'end': str(end),
            'limit': str(limit)
        }

        # Send the GET request to the API
        response = requests.get(url, params=params)
        data = response.json()

        # Check if the response contains data
        if data['code'] == '0' and data['data']:
            # Convert the data into a pandas DataFrame
            df = pd.DataFrame(data['data'], columns=['ts', 'oi', 'oiCcy', 'oiUsd'])

            # Keep only the timestamp and open interest in USD
            df = df[['ts', 'oiUsd']]

            # Convert the timestamp to a readable datetime format (milliseconds to seconds) in UTC
            df['ts'] = pd.to_datetime(df['ts'].astype(int), unit='ms', utc=True)

            # Remove duplicates for current batch based on timestamp (if any)
            df = df[~df['ts'].isin(seen_timestamps)]
            
            # If new data is found, append it to the list and update seen timestamps
            if not df.empty:
                all_data.append(df)
                seen_timestamps.update(df['ts'])

                # Update current_start_time for the next chunk (ensure no overlap)
                current_start_time = pd.to_datetime(df['ts'].iloc[-1]) + timedelta(hours=4)
            else:
                # If no new data, increment the current_start_time by 4 hours manually
                #print(f"No new data for {current_start_time}. Incrementing by 4 hours.")
                current_start_time += timedelta(hours=4)
        else:
            # If no data found for this range, break out of the loop
            print("No data found or error fetching data for this range.")
            break
    
    # Combine all chunks into one DataFrame
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)

        # Sort the data by timestamp (ascending order)
        df_all_sorted = df_all.sort_values(by='ts', ascending=True)

        # Remove duplicates if any (in case they are present after pagination)
        df_all_sorted = df_all_sorted.drop_duplicates(subset=['ts'], keep='last')

        # Reset index to start from 0
        df_all_sorted.reset_index(drop=True, inplace=True)

        # Print the sorted DataFrame with readable human time and relevant columns
        pd.set_option('display.max_rows', None)  # Set this to None to display all rows
        pd.set_option('display.max_columns', None)  # Optionally, set this to None for all columns
        print(df_all_sorted[['ts', 'oiUsd']])
        # Return the sorted DataFrame with the relevant columns
        return df_all_sorted[['ts', 'oiUsd']]
    else:
        print('No data retrieved or an error occurred.')
        return None

def fetch_open_interest_for_range_1D(start_time_utc, end_time_utc, limit, symbol):
    start_time_utc=start_time_utc.replace(hour=16, minute=0, second=0, microsecond=0)
    print(f"Fetching 1D data for {symbol} from {start_time_utc} to {end_time_utc}")
        
    # List to hold all results
    all_data = []
    seen_timestamps = set() 
    
    # Initialize variables
    current_start_time = start_time_utc
    
    while current_start_time < end_time_utc:
        #print(f"Current start time: {current_start_time}")
        
        # Convert start and end times to timestamps in milliseconds
        begin = int(current_start_time.timestamp() * 1000)
        
        # Ensure we do not exceed the end time
        next_end_time = min(current_start_time + timedelta(days=limit), end_time_utc)
        end = int(next_end_time.timestamp() * 1000)
        
        # Define the API endpoint and parameters
        url = 'https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history'
        params = {
            'instId': symbol,  # Use the symbol passed as a parameter
            'period': '1D',
            'begin': str(begin),
            'end': str(end),
            'limit': str(limit)
        }

        # Send the GET request to the API
        response = requests.get(url, params=params)
        data = response.json()

        # Check if the response contains data
        if data['code'] == '0' and data['data']:
            # Convert the data into a pandas DataFrame
            df = pd.DataFrame(data['data'], columns=['ts', 'oi', 'oiCcy', 'oiUsd'])

            # Keep only the timestamp and open interest in USD
            df = df[['ts', 'oiUsd']]

            # Convert the timestamp to a readable datetime format (milliseconds to seconds) in UTC
            df['ts'] = pd.to_datetime(df['ts'].astype(int), unit='ms', utc=True)

            # Remove duplicates for current batch based on timestamp (if any)
            df = df[~df['ts'].isin(seen_timestamps)]
            
            # Append the data for this chunk to the all_data list
            all_data.append(df)
            
            # Update seen_timestamps with the newly added timestamps from this batch
            seen_timestamps.update(df['ts'])

            # Update current_start_time for the next chunk (ensure no overlap)
            if not df.empty:
                current_start_time = pd.to_datetime(df['ts'].iloc[-1]) + timedelta(days=1)
            else:
                # If no data found, manually increment current_start_time by 1 day
                #print(f"No new data for {current_start_time}. Incrementing by 1 day.")
                current_start_time += timedelta(days=1)
                current_start_time = current_start_time.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # Combine all chunks into one DataFrame
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)

        # Sort the data by timestamp (ascending order)
        df_all_sorted = df_all.sort_values(by='ts', ascending=True)

        # Remove duplicates if any (in case they are present after pagination)
        df_all_sorted = df_all_sorted.drop_duplicates(subset=['ts'], keep='last')

        # Reset index to start from 0
        df_all_sorted.reset_index(drop=True, inplace=True)

        # Print the sorted DataFrame with readable human time and relevant columns
        pd.set_option('display.max_rows', None)  # Set this to None to display all rows
        pd.set_option('display.max_columns', None)  # Optionally, set this to None for all columns
        print(df_all_sorted[['ts', 'oiUsd']])
        # Return the sorted DataFrame with the relevant columns
        return df_all_sorted[['ts', 'oiUsd']]
    else:
        print('No data retrieved or an error occurred.')
        return None

def extract_symbol_and_interval(file_name):
    # Split the file name (assuming format: SYMBOL_INTERVAL.csv)
    symbol, interval_with_extension = file_name.split('_')
    interval = interval_with_extension.split('.')[0]  # Remove the .csv extension
    symbol = symbol + '-USDT-SWAP'  # Append '-USDT-SWAP' to the symbol
    return symbol, interval

def process_csv_and_find_empty_cells(file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Check if the "Open Interest (USD)" column exists
    if "Open Interest (USD)" not in df.columns:
        print(f"Column 'Open Interest (USD)' not found in {file_path}.")
        return None, None
    
    # Find the first and last empty cells in the "Open Interest (USD)" column
    first_empty_idx = df['Open Interest (USD)'].isna().idxmax()  # First empty cell index
    last_empty_idx = df['Open Interest (USD)'].isna()[::-1].idxmax()  # Last empty cell index
    
    # Get corresponding times for the first and last empty cells
    # No need for 'unit="ms"' if Open Time is already a datetime string
    start_time = pd.to_datetime(df['Open Time'].iloc[first_empty_idx], utc=True)
    end_time = pd.to_datetime(df['Open Time'].iloc[last_empty_idx], utc=True)
    
    return start_time, end_time

def update_open_interest_in_csv(file_path, symbol, interval, open_interest_data):

    # Ensure open_interest_data is valid
    if open_interest_data is None or not isinstance(open_interest_data, pd.DataFrame) or open_interest_data.empty:
        print("Error: The Open Interest data is not available or is empty.")
        return

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Check if the "Open Interest (USD)" column exists
    if "Open Interest (USD)" not in df.columns:
        print(f"Column 'Open Interest (USD)' not found in {file_path}.")
        return

    # Ensure 'Open Time' is parsed as datetime, and strip off the timezone
    df['Open Time'] = pd.to_datetime(df['Open Time'], errors='coerce').dt.tz_localize(None).dt.floor('h')  # Use 'h' instead of 'H'

    # Ensure 'ts' column in open_interest_data is parsed as datetime, and strip off the timezone
    open_interest_data['ts'] = pd.to_datetime(open_interest_data['ts'], errors='coerce').dt.tz_localize(None).dt.floor('h')  # Use 'h' instead of 'H'

    # Check if there are any NaT (Not a Time) entries after parsing
    if df['Open Time'].isna().any():
        print(f"Error: Some 'Open Time' entries could not be parsed. Please check the format.")
        return
    if open_interest_data['ts'].isna().any():
        print(f"Error: Some 'ts' entries in Open Interest data could not be parsed. Please check the format.")
        return

    # Check if the interval is supported
    if interval in ['1h', '4h']:
        # Exact timestamp match for 1h and 4h intervals
        open_interest_mapping = open_interest_data.set_index('ts')['oiUsd']
    elif interval == '1d':
        # Use only the date part for 1d interval
        df['Date'] = df['Open Time'].dt.date  # Extract date part for matching
        open_interest_data['Date'] = open_interest_data['ts'].dt.date
        open_interest_mapping = open_interest_data.set_index('Date')['oiUsd']
    else:
        print(f"Interval {interval} not supported for this operation.")
        return

    # Identify rows with missing Open Interest values
    missing_data_indices = df[df['Open Interest (USD)'].isna()].index

    if len(missing_data_indices) == 0:
        print(f"No empty Open Interest cells found in {file_path}.")
        return

    # Update the missing Open Interest values
    for idx in missing_data_indices:
        if interval in ['1h', '4h']:
            row_time = df.at[idx, 'Open Time']  # Exact timestamp match
            #print(f"Attempting to match timestamp: {row_time}")
            if row_time in open_interest_mapping:
                # Cast the Open Interest value to float before assignment
                df.at[idx, 'Open Interest (USD)'] = float(open_interest_mapping[row_time])
                #print(f"Updated Open Interest for {row_time}: {open_interest_mapping[row_time]}")
            else:
                print(f"No matching Open Interest data for {row_time}")
        elif interval == '1d':
            row_date = df.at[idx, 'Date']  # Match based on date only
            #print(f"Attempting to match date: {row_date}")
            if row_date in open_interest_mapping:
                # Cast the Open Interest value to float before assignment
                df.at[idx, 'Open Interest (USD)'] = float(open_interest_mapping[row_date])
                #print(f"Updated Open Interest for {row_date}: {open_interest_mapping[row_date]}")
            else:
                print(f"No matching Open Interest data for {row_date}")

    # Drop the auxiliary 'Date' column for 1D interval
    if interval == '1d' and 'Date' in df.columns:
        df.drop(columns=['Date'], inplace=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv(file_path, index=False)
    print(f"Updated Open Interest (USD) for {symbol} with {interval} interval in {file_path}.")

def check_for_empty_open_interest(file_path):
    # Open the CSV and check for any missing values in the 'Open Interest (USD)' column
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Open Interest (USD)'] == '' or row['Open Interest (USD)'] == 'NA':
                return True  # Found an empty or 'NA' value, return True
    return False  # No empty cells found

def process_and_update_files():
    for file_name in FILE_NAMES:
        file_path = os.path.join(COMBINED_DIR, file_name)
        
        symbol, interval = extract_symbol_and_interval(file_name)
        
        # Process CSV and check if there are any missing Open Interest values
        has_empty_cells = check_for_empty_open_interest(file_path)
        
        if not has_empty_cells:
            #print(f"No missing Open Interest data for {file_name}, skipping this file.")
            print(f"Data Already Up to date in {file_name}, skipping this file.")
            continue  # Skip to the next file if there are no missing values in Open Interest
        
        # If there are missing Open Interest cells, proceed with processing
        start_time, end_time = process_csv_and_find_empty_cells(file_path)
        
        if start_time and end_time:
            print(f"==========================================================")
            print(f"For {file_name} (symbol: {symbol}, interval: {interval}):")
            print(f"Start Time: {start_time}")
            print(f"End Time: {end_time}")
            
            # Fetch open interest data for the correct interval
            if interval == "1d":
                start_time = start_time - timedelta(days=1)
                end_time = end_time + timedelta(hours=16)
                open_interest_data = fetch_open_interest_for_range_1D(start_time, end_time, limit=4, symbol=symbol)

                #update_open_interest_in_csv(file_path, symbol, interval, start_time, end_time, open_interest_data)
            elif interval == "1h":
                start_time = start_time - timedelta(hours=1)
                end_time = end_time + timedelta(hours=1)
                open_interest_data = fetch_open_interest_for_range_1H(start_time, end_time, limit=20, symbol=symbol)

                #update_open_interest_in_csv(file_path, symbol, interval, start_time, end_time, open_interest_data)
            elif interval == "4h":
                end_time = end_time + timedelta(hours=4)
                open_interest_data = fetch_open_interest_for_range_4H(start_time, end_time, limit=20, symbol=symbol)
                #update_open_interest_in_csv(file_path, symbol, interval, start_time, end_time, open_interest_data)
            else:
                print(f"Unsupported interval: {interval}")
                continue

        update_open_interest_in_csv(file_path, symbol, interval, open_interest_data)

# Directory and file names
COMBINED_DIR = "../Data"
FILE_NAMES = [
    "BTC_1d.csv", "BTC_1h.csv", "BTC_4h.csv",
    "BNB_1d.csv", "BNB_1h.csv", "BNB_4h.csv", 
    "ETH_1d.csv", "ETH_1h.csv", "ETH_4h.csv",
    "PEPE_1d.csv", "PEPE_1h.csv", "PEPE_4h.csv",
    "SOL_1d.csv","SOL_1h.csv", "SOL_4h.csv", 
]

# Main execution
if __name__ == "__main__":
    process_and_update_files()