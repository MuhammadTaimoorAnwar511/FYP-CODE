import requests
import time
import hmac
import hashlib

# API credentials
api_key = "FVxJssLNFyUgq5OTyt"
api_secret = "3PstkL6fJ6vkyTOPCPR0jIGOaoeQQdBv6sDl"

# API configuration
base_url = "https://api-demo.bybit.com"
endpoint = "/v5/account/wallet-balance"
params = {
    "accountType": "UNIFIED"  # Use "SPOT" or "CONTRACT" if needed
}

# Generate timestamp and recv_window
timestamp = str(int(time.time() * 1000))
recv_window = "5000"  # Default is 5000 milliseconds

# Create query string (sorted alphabetically)
query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])

# Generate signature
signature_payload = f"{timestamp}{api_key}{recv_window}{query_string}"
signature = hmac.new(
    api_secret.encode("utf-8"),
    signature_payload.encode("utf-8"),
    hashlib.sha256
).hexdigest()

# Request headers
headers = {
    "X-BAPI-API-KEY": api_key,
    "X-BAPI-TIMESTAMP": timestamp,
    "X-BAPI-RECV-WINDOW": recv_window,
    "X-BAPI-SIGN": signature
}

# Send GET request
response = requests.get(
    url=f"{base_url}{endpoint}",
    params=params,
    headers=headers
)

# Parse response
if response.status_code == 200:
    data = response.json()
    if 'result' in data and 'list' in data['result']:
        for account in data['result']['list']:
            for coin in account.get('coin', []):
                if coin['coin'] == 'USDT':
                    print(f"USDT Wallet Balance: {coin['walletBalance']}")
else:
    print("Error fetching balance:", response.json())
