import os
import time
import hmac
import math
import hashlib
import requests
import urllib.parse
from bson import ObjectId
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

# ------------------------------------------------------------------------------
# Configuration and Database Setup
# ------------------------------------------------------------------------------
load_dotenv() 
# Configuration variables
BASE_URL = os.getenv("BASE_URL")
CLOSEPNL_ENDPOINT= os.getenv("CLOSE_PNL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# MongoDB connection and collections
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
subscriptions_collection = db['subscriptions']
users_collection = db['users']
recv_window = "5000"

# ------------------------------------------------------------------------------
# Helper Functions (Single Responsibility)
# ------------------------------------------------------------------------------

def find_user_by_id(user_id_str):
    """
    Find and return a user document by its ID.
    """
    return users_collection.find_one({"_id": ObjectId(user_id_str)})

def get_subscription_by_symbol(symbol):
    """
    Retrieve a subscription document matching the provided symbol.
    """
    return subscriptions_collection.find_one({"symbol": symbol})

def get_user_trade_collection(user_id):
    """
    Retrieve the user's trade collection based on the user ID.
    """
    collection_name = f"user_{user_id}"
    return db[collection_name]

def find_open_trade(trade_collection, symbol, direction):
    """
    Find an open trade in the user's trade collection matching the cleaned symbol and direction.
    """
    clean_symbol = symbol.replace("/", "")
    return trade_collection.find_one({
        "symbol": clean_symbol,
        "direction": direction,
        "status": "OPEN"
    })

def update_trade_status(trade_collection, trade_id, reason, pnl=None):
    """
    Update a trade document to mark it as closed with a given reason,
    exit time, and optional PNL.
    """
    exit_time = datetime.now(timezone.utc)
    update_fields = {}

    if reason:
        update_fields["status"] = reason
    update_fields["exit_time"] = exit_time

    if pnl is not None:
        update_fields["PNL"] = pnl 

    if not update_fields:
        raise ValueError("No fields to update. Update path is empty.")

    print(f"[DEBUG] Updating trade with: {update_fields}")

    trade_collection.update_one(
        {"_id": trade_id},
        {"$set": update_fields}
    )
    return exit_time

def log_user_keys(user):
    """
    Log API and secret keys of the user if available.
    """
    if user:
        print("User API Key:", user.get("api_key"))
        print("User Secret Key:", user.get("secret_key"))
    else:
        print("User not found in the user collection.")

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
    symbol = symbol.replace("/", "")
    params = {
        "category": "linear", 
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
    Process the API response and return the trade that has an average entry price 
    matching the target up to one decimal place (using truncation).
    
    Args:
        response: The API response object.
        target_avg_entry_price (float): The target average entry price.
        
    Returns:
        str: Trade summary or message.
    """
    data = response.json()
    if data.get("retCode") == 0:
        results = data.get("result", {}).get("list", [])
        target_truncated = truncate_to_one_decimal(target_avg_entry_price)
        for trade in results:
            avg_entry_price = trade.get("avgEntryPrice")
            try:
                if avg_entry_price is not None:
                    trade_truncated = truncate_to_one_decimal(float(avg_entry_price))
                    if trade_truncated == target_truncated:
                        symbol = trade.get("symbol")
                        direction = trade.get("side")
                        pnl = trade.get("closedPnl")
                        return f"Symbol: {symbol}, Direction: {direction}, Avg Entry Price: {avg_entry_price}, PnL: {pnl}"
            except ValueError:
                continue
        return f"No trade found with Avg Entry Price matching {target_truncated} (truncated)"
    else:
        return f"Error: {data.get('retMsg')}"

# ------------------------------------------------------------------------------
# Flask Blueprint Setup
# ------------------------------------------------------------------------------
closetrades_bp = Blueprint('closetrades', __name__)
CORS(closetrades_bp)

# -------------------------------------------------------------------
# close_trade Route
# -------------------------------------------------------------------
@closetrades_bp.route('/close_trade', methods=['POST'])
def close_trade():
    data = request.get_json()
    symbol = data.get("symbol")
    direction = data.get("direction")
    reason = data.get("reason")

    if not symbol or not direction or not reason:
        return jsonify({"message": "Missing required parameters."}), 400

    # Step 1: Find the subscription for the provided symbol.
    subscription = get_subscription_by_symbol(symbol)
    if not subscription:
        return jsonify({"message": "Subscription not found for the provided symbol"}), 404

    # Step 2: Get the user document and log API keys.
    user_id = subscription.get("user_id")
    user = find_user_by_id(user_id)
    #log_user_keys(user)

    # Step 3: Retrieve the user's trade collection.
    user_trade_collection = get_user_trade_collection(user_id)
    if user_trade_collection.name not in db.list_collection_names():
        print("User trade collection not found.")

    # Step 4: Find an open trade matching the symbol and direction.
    trade = find_open_trade(user_trade_collection, symbol, direction)
    if not trade:
        return jsonify({"message": "Open trade not found for the provided symbol and direction"}), 404

    # Step 5: Extract entry_price from the trade
    entry_price = trade.get("entry_price")
    if not entry_price:
        return jsonify({"message": "Entry price not found in trade document"}), 500

    target_avg_entry_price = float(entry_price)

    # Step 6: Fetch closed PnL from Bybit
    api_key = user.get("api_key")
    api_secret = user.get("secret_key")

    response = fetch_closed_pnl(api_key, api_secret, BASE_URL, CLOSEPNL_ENDPOINT, symbol, recv_window)
    result = process_response(response, target_avg_entry_price)

    # Step 7: Parse the result string to extract PnL
    pnl_value = None
    if result.startswith("Symbol:"):
        try:
            parts = result.split(", ")
            parsed_data = {k.strip(): v.strip() for k, v in (item.split(":") for item in parts)}
            pnl_value = float(parsed_data.get("PnL", 0))
        except Exception as e:
            print("Error parsing PnL value from result:", str(e))
    else:
        print("process_response returned:", result)

    # Step 8: Update trade status and include PnL if available
    exit_time = update_trade_status(user_trade_collection, trade["_id"], reason, pnl=pnl_value)

    # Step 9: Return response
    return jsonify({
        "message": "User trade closed successfully",
        "exit_time": exit_time.isoformat(),
        "pnl_result": result
    }), 200
