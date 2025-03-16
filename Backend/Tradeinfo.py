import os
import time
import math
import hashlib
import hmac
import requests
import urllib.parse
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# Environment and Database Setup
# ------------------------------------------------------------------------------
load_dotenv()  

BASE_URL = os.getenv("BASE_URL")
CLOSEPNL= os.getenv("CLOSE_PNL")
# ------------------------------------------------------------------------------
# API Credentials and Setup
# ------------------------------------------------------------------------------
API_KEY = "FVxJssLNFyUgq5OTyt"
API_SECRET = "3PstkL6fJ6vkyTOPCPR0jIGOaoeQQdBv6sDl"
RECV_WINDOW = "5000"

# ------------------------------------------------------------------------------
# CLOSING TRADE Utility Functions
# ------------------------------------------------------------------------------

def get_current_timestamp() -> str:
    """
    Return the current timestamp in milliseconds as a string.
    """
    return str(int(time.time() * 1000))

def generate_signature(api_secret: str, timestamp: str, api_key: str, recv_window: str, params: dict) -> tuple[str, str]:
    ...

    """
    Generate HMAC SHA256 signature and return it along with the URL-encoded query string.
    """
    query_string = urllib.parse.urlencode(params)
    string_to_sign = f"{timestamp}{api_key}{recv_window}{query_string}"
    signature = hmac.new(
        api_secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return signature, query_string

def build_headers(api_key: str, timestamp: str, recv_window: str, signature: str) -> dict:
    """
    Construct headers required for the API request.
    """
    return {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature
    }

def fetch_closed_pnl(api_key: str, api_secret: str, base_url: str, endpoint: str, symbol: str, recv_window: str):
    """
    Build the request URL with the hardcoded "linear" category and send a GET request.
    
    Returns:
        response (requests.Response): The API response.
    """
    params = {
        "category": "linear",  # Hardcoded category
        "symbol": symbol
    }
    timestamp = get_current_timestamp()
    signature, query_string = generate_signature(api_secret, timestamp, api_key, recv_window, params)
    headers = build_headers(api_key, timestamp, recv_window, signature)
    url = f"{base_url}{endpoint}?{query_string}"
    return requests.get(url, headers=headers)

def truncate_to_one_decimal(value: float) -> float:
    """
    Truncate a float value to one decimal place without rounding.
    
    For example, 84258.89 becomes 84258.8.
    """
    return math.floor(value * 10) / 10

def process_response(response, target_avg_entry_price: float):
    """
    Process the API response and print only the trade that has an average entry price 
    matching the target up to one decimal place (using truncation).
    
    Args:
        response: The API response object.
        target_avg_entry_price (float): The target average entry price.
    """
    data = response.json()
    print("Status Code:", response.status_code)
    if data.get("retCode") == 0:
        results = data.get("result", {}).get("list", [])
        found_trade = False
        # Truncate the target value to one decimal place for comparison
        target_truncated = truncate_to_one_decimal(target_avg_entry_price)
        for trade in results:
            avg_entry_price = trade.get("avgEntryPrice")
            try:
                if avg_entry_price is not None:
                    # Truncate the trade's avgEntryPrice to one decimal place
                    trade_truncated = truncate_to_one_decimal(float(avg_entry_price))
                    if trade_truncated == target_truncated:
                        symbol = trade.get("symbol")
                        direction = trade.get("side")
                        pnl = trade.get("closedPnl")
                        print(f"Symbol: {symbol}, Direction: {direction}, Avg Entry Price: {avg_entry_price}, PnL: {pnl}")
                        found_trade = True
            except ValueError:
                continue
        if not found_trade:
            print(f"No trade found with Avg Entry Price matching {target_truncated} (truncated)")
    else:
        print("Error:", data.get("retMsg"))

# ------------------------------------------------------------------------------
# 
# ------------------------------------------------------------------------------

def main():
    """
    Main function to execute the closed PnL data retrieval and process the response
    for a specific average entry price using truncation to one decimal.
    """
    SYMBOL = "BTCUSDT"
    target_avg_entry_price = 84302.8 
    response = fetch_closed_pnl(API_KEY, API_SECRET, BASE_URL, CLOSEPNL, SYMBOL, RECV_WINDOW)
    # Set the target average entry price.
    # For example, 84258.81097561 will be truncated to 84258.8 for comparison.
 
    process_response(response, target_avg_entry_price)

if __name__ == "__main__":
    main()
