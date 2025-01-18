import requests
import os
from datetime import datetime, timezone, timedelta
import pandas as pd

# Function to convert a datetime object to a Unix timestamp in milliseconds
def to_unix_timestamp(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    # Ensure the timestamp is in UTC
    date_obj = date_obj.replace(tzinfo=timezone.utc)
    return int(date_obj.timestamp() * 1000)

# Function to fetch candlestick data for a specific date range
def fetch_candlestick_data(symbol, start_date, end_date, interval='1d'):
    base_url = "https://fapi.binance.com"
    endpoint = "/fapi/v1/klines"
    

    # Ensure that PEPE symbol is correctly formatted with 'USDT'
    if symbol == "PEPE":
        binance_symbol = "1000PEPEUSDT"
    else:
        binance_symbol = f"{symbol}USDT"
    
    # Convert start and end dates to Unix timestamps in milliseconds
    start_time = to_unix_timestamp(start_date)
    end_time = to_unix_timestamp(end_date)
    
    # Set up the parameters for the API request
    params = {
        'symbol': binance_symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 1000  # Limit can be adjusted as needed, Binance allows a max of 1000
    }
    
    # Send GET request to Binance API
    response = requests.get(base_url + endpoint, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data for {binance_symbol} at interval {interval}: {response.status_code}")
        return None

# Function to process each symbol and interval
# Function to process each symbol and interval
def process_symbol_and_interval(symbol, interval, csv_file):
    # Read the existing data from the CSV file
    df = pd.read_csv(csv_file)
    
    # Extract the last Open Time
    last_open_time = df['Open Time'].iloc[-1]
    
    # Convert the last Open Time to a datetime object
    last_date = datetime.strptime(last_open_time, '%Y-%m-%d %H:%M:%S')
    
    # Calculate the start date (next interval after the last entry)
    if interval == "1h":
        start_date = (last_date + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    elif interval == "4h":
        start_date = (last_date + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
    
    # Set the dynamic end date to the current UTC time
    current_utc_time = datetime.now(timezone.utc)
    if interval == "1h":
        adjusted_time = current_utc_time - timedelta(hours=1)
    elif interval == "4h":
        adjusted_time = current_utc_time - timedelta(hours=4)
    else:
        adjusted_time = current_utc_time - timedelta(days=1)

    adjusted_time = adjusted_time.replace(minute=59, second=59)
    end_date = adjusted_time.strftime('%Y-%m-%d %H:%M:%S')

    print(f"Start Date for {symbol} ({interval}): {start_date}")
    print(f"End Date for {symbol} ({interval}): {end_date}")
    
    # Fetch the candlestick data for the specific date range
    candlestick_data = fetch_candlestick_data(symbol, start_date, end_date, interval)
    
    if candlestick_data:
        print(f"Appending data for {symbol} at interval {interval}...")
        
        # Prepare the new data for appending
        new_data = []
        for candle in candlestick_data:
            open_time = datetime.fromtimestamp(candle[0] / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            new_data.append({
                'Open Time': open_time,
                'Open': candle[1],
                'High': candle[2],
                'Low': candle[3],
                'Close': candle[4],
                'Quote Asset Volume': candle[7]
            })
        
        # Create a DataFrame for the new data
        new_df = pd.DataFrame(new_data)
        
        # Concatenate the new data with the existing DataFrame
        updated_df = pd.concat([df, new_df]).drop_duplicates(subset='Open Time').reset_index(drop=True)
        
        # Save the updated DataFrame back to the CSV file
        updated_df.to_csv(csv_file, index=False)
        
        print(f"Data for {symbol} ({interval}) has been appended successfully.")
    else:
        print(f"No new data fetched for {symbol} at interval {interval}.")

# Main execution
if __name__ == "__main__":
    # Define symbols and intervals arrays
    symbols = ["BNB","BTC","ETH","PEPE","SOL"]  # Symbols without 'USDT' appended
    intervals = ["1h", "4h", "1d"]  # Add more intervals as needed
    COMBINED_DIR = "../Data"
    
    # List of corresponding CSV files for each symbol and interval
    FILE_NAMES = [
    "BNB_1d.csv", "BNB_1h.csv", "BNB_4h.csv",
    "BTC_1d.csv", "BTC_1h.csv", "BTC_4h.csv",
    "ETH_1d.csv", "ETH_1h.csv", "ETH_4h.csv",
    "PEPE_1d.csv", "PEPE_1h.csv", "PEPE_4h.csv",
    "SOL_1d.csv", "SOL_1h.csv", "SOL_4h.csv",
    ]
    
    for symbol in symbols:
        for interval in intervals:
            # Determine the corresponding CSV file for the symbol and interval
            file_name = f"{symbol}_{interval}.csv"
            file_path = os.path.join(COMBINED_DIR, file_name)
            
            # Check if the file exists before processing
            if os.path.exists(file_path):
                process_symbol_and_interval(symbol, interval, file_path)
            else:
                print(f"File {file_path} does not exist. Skipping.")
