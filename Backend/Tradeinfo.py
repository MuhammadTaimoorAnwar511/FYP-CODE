import time
import hashlib
import hmac
import requests
import urllib.parse

# API Credentials and Setup
api_key = "FVxJssLNFyUgq5OTyt"
api_secret = "3PstkL6fJ6vkyTOPCPR0jIGOaoeQQdBv6sDl"
base_url = "https://api-demo.bybit.com"

# Request parameters
endpoint = "/v5/position/closed-pnl"
params = {
    "category": "linear",
    "symbol": "BTCUSDT"
}

# Timestamp and Recv Window
timestamp = str(int(time.time() * 1000))
recv_window = "5000"

# Generate signature
query_string = urllib.parse.urlencode(params)
string_to_sign = f"{timestamp}{api_key}{recv_window}{query_string}"
signature = hmac.new(
    bytes(api_secret, "utf-8"),
    string_to_sign.encode("utf-8"),
    hashlib.sha256
).hexdigest()

# Construct headers
headers = {
    "X-BAPI-API-KEY": api_key,
    "X-BAPI-TIMESTAMP": timestamp,
    "X-BAPI-RECV-WINDOW": recv_window,
    "X-BAPI-SIGN": signature
}

# Full request URL
url = f"{base_url}{endpoint}?{query_string}"

# Send GET request
response = requests.get(url, headers=headers)
data = response.json()

# Debug: print status code and full response (optional)
print("Status Code:", response.status_code)
#print("Response JSON:", data)

# Extract and display required fields if the API call was successful
if data.get("retCode") == 0:
    # Assuming the closed pnl records are in the 'list' key under 'result'
    results = data.get("result", {}).get("list", [])
    for trade in results:
        symbol = trade.get("symbol")
        direction = trade.get("side")
        avg_entry_price = trade.get("avgEntryPrice")
        pnl = trade.get("closedPnl")
        print(f"Symbol: {symbol}, Direction: {direction}, Avg Entry Price: {avg_entry_price}, PnL: {pnl}")
else:
    print("Error:", data.get("retMsg"))
