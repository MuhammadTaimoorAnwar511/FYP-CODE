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

from pprint import pprint

# ------------------------------------------------------------------------------
# Configuration and Database Setup
# ------------------------------------------------------------------------------
load_dotenv() 
# Configuration variables
BASE_URL = os.getenv("BASE_URL")
CLOSEPNL_ENDPOINT= os.getenv("CLOSE_PNL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
TIME_ENDPOINT=os.getenv("TIME_ENDPOINT")
# MongoDB connection and collections
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
subscriptions_collection = db['subscriptions']
users_collection = db['users']
recv_window = "10000"

# ------------------------------------------------------------------------------
# Helper Functions (Single Responsibility)
# ------------------------------------------------------------------------------

def find_user_by_id(user_id_str):
    """
    Find and return a user document by its ID.
    """
    return users_collection.find_one({"_id": ObjectId(user_id_str)})

def get_subscriptions_by_symbol(symbol):
    """
    Retrieve all subscription documents matching the provided symbol.
    """
    return subscriptions_collection.find({"symbol": symbol})

def get_user_trade_collection(user_id):
    """
    Retrieve the user's trade collection based on the user ID.
    """
    collection_name = f"user_{user_id}"
    return db[collection_name]

#def find_open_trade(trade_collection, symbol, direction):
    # """
    # Find an open trade in the user's trade collection matching the cleaned symbol and direction.
    # """
    # clean_symbol = symbol.replace("/", "")
    # return trade_collection.find_one({
    #     "symbol": clean_symbol,
    #     "direction": direction,
    #     "status": "OPEN"
    # })

def find_open_trade(trade_collection, symbol, direction):
    """
    Find the latest open trade using find_one with sorting.
    """
    clean_symbol = symbol.replace("/", "")
    return trade_collection.find_one(
        {
            "symbol": clean_symbol,
            "direction": direction,
            "status": "OPEN"
        },
        sort=[("entry_time", -1)] 
    )

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

    #print(f"[DEBUG] Updating trade with: {update_fields}")

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

def get_server_timestamp(base_url: str) -> int:
    """
    Retrieve the server timestamp from the market time endpoint.
    """
    try:
        response = requests.get(f"{base_url}{TIME_ENDPOINT}")  
        if response.status_code == 200:
            return int(response.json()['result']['timeNano']) // 1_000_000
    except Exception as e:
        print("[WARNING] Fallback to local time due to error getting server time:", str(e))
    return int(time.time() * 1000)


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
    #timestamp = get_current_timestamp()
    timestamp = str(get_server_timestamp(base_url))
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

def process_response(response, direction):
    #print("\n[DEBUG] Entered process_response function")
    data = None

    #print(f"[DEBUG] Response Status Code: {response.status_code}\n")
    if response.status_code == 200:
        try:
            data = response.json()
            #print("[DEBUG] JSON response successfully decoded:")
            #pprint(data)
        except requests.exceptions.JSONDecodeError:
            print(f"[✖] JSON decode error. Response text:\n{response.text}")
            return "Error: Invalid API response format"
    else:
        print(f"[✖] Close Trade API failed.\nStatus Code: {response.status_code}\nResponse Text:\n{response.text}")
        return f"Error: API request failed ({response.status_code})"

    if not data:
        print("[✖] No data found in response.")
        return "Error: No valid response data"

    #print(f"\n[DEBUG] retCode in response: {data.get('retCode')}")
    if data.get("retCode") == 0:
        results = data.get("result", {}).get("list", [])
        print(f"[DEBUG] Number of trades in response: {len(results)}")

        if not results:
            print("[✖] No trades found in response 'result.list'")
            return "No trades found in API response"

        # Determine which trade 'side' to match based on user 'direction'
        if direction.upper() == "SHORT":
            match_side = "Buy"
        elif direction.upper() == "LONG":
            match_side = "Sell"
        else:
            print(f"[✖] Invalid direction value provided: {direction}")
            return f"Error: Invalid direction '{direction}'"

        #print(f"[DEBUG] Matching trades where side == '{match_side}' based on direction '{direction}'")

        # Filter trades
        filtered_trades = [t for t in results if t.get("side", "").lower() == match_side.lower()]
        #print(f"[DEBUG] Number of trades matching side '{match_side}': {len(filtered_trades)}")

        if not filtered_trades:
            print(f"[✖] No closed trades found matching direction: {direction}")
            return f"No closed trades found matching direction: {direction}"

        # Sort by updatedTime (latest first)
        sorted_trades = sorted(filtered_trades, key=lambda x: int(x.get("updatedTime", 0)), reverse=True)
        #print(f"\n[DEBUG] Sorted trades by updatedTime. Latest trade data:")
        #pprint(sorted_trades[0])

        latest_trade = sorted_trades[0]
        pnl = latest_trade.get("closedPnl")
        avg_entry_price = latest_trade.get("avgEntryPrice")
        symbol = latest_trade.get("symbol")
        side = latest_trade.get("side")
        avg_exit_price = latest_trade.get("avgExitPrice")

        print(f"\n[SUCCESS] Latest Trade Summary:")
        print(f"  Symbol         : {symbol}")
        print(f"  Direction      : {side}")
        print(f"  Avg Entry Price: {avg_entry_price}")
        print(f"  Avg Exit Price : {avg_exit_price}")
        print(f"  PnL            : {pnl}")

        return (
            f"Symbol: {symbol}, "
            f"Direction: {side}, "
            f"Avg Entry Price: {avg_entry_price}, "
            f"Avg Exit Price: {avg_exit_price}, "
            f"PnL: {pnl}"
        )
    else:
        print(f"[✖] retCode not 0. retMsg: {data.get('retMsg')}")
        return f"Error: {data.get('retMsg')}"

def update_balances(user_id, pnl, symbol):
    """
    Update bot_current_balance (min 0) and user_current_balance (can be negative)
    after trade closure.
    """
    try:
       
        subscription = subscriptions_collection.find_one({"user_id": str(user_id), "symbol": symbol})
        if subscription:
            current_bot_balance = subscription.get("bot_current_balance", 0)
            new_bot_balance = max(0, current_bot_balance + pnl)

            subscriptions_collection.update_one(
                {"_id": subscription["_id"]},
                {"$set": {"bot_current_balance": new_bot_balance}}
            )
        else:
            print(f"[⚠] Subscription not found for user_id: {user_id}, symbol: {symbol}")

        # ✅ Users collection: Assuming you have a global `users_collection`
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            current_user_balance = user.get("user_current_balance", 0)
            new_user_balance = current_user_balance + pnl

            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"user_current_balance": new_user_balance}}
            )
        else:
            print(f"[⚠] User not found in users_collection with ID: {user_id}")

        print(f" Balance update completed successfully for user_id: {user_id}")

    except Exception as e:
        print(f"[✖] Exception during balance update for user_id: {user_id} -> {str(e)}")


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
        return jsonify({"message": "Missing required parameters"}), 400

    # Step 1: Find ALL subscriptions for the provided symbol
    subscriptions = list(get_subscriptions_by_symbol(symbol))
    if not subscriptions:
        return jsonify({"message": f"No subscriptions found for the provided {symbol}"}), 404

    results = []

    for subscription in subscriptions:
        user_id = subscription.get("user_id")
        
        # Step 2: Get user document
        user = find_user_by_id(user_id)
        if not user:
            results.append({"user_id": user_id, "status": "error", "message": "User not found"})
            continue

        # Step 3: Get user's trade collection
        user_trade_collection = get_user_trade_collection(user_id)
        if user_trade_collection.name not in db.list_collection_names():
            results.append({"user_id": user_id, "status": "error", "message": "Trade collection not found"})
            continue

        # Step 4: Find open trade
        trade = find_open_trade(user_trade_collection, symbol, direction)
        if not trade:
            results.append({"user_id": user_id, "status": "error", "message": "Open trade not found"})
            continue

        # Step 5: Process trade closure
        try:
            entry_price = trade.get("entry_price")
            if not entry_price:
                results.append({"user_id": user_id, "status": "error", "message": "Entry price missing"})
                continue

           

            # Step 6: Fetch closed PnL from Bybit
            api_key = user.get("api_key")
            api_secret = user.get("secret_key")
            time.sleep(10)  # Maintain exchange sync delay if needed
            response = fetch_closed_pnl(api_key, api_secret, BASE_URL, CLOSEPNL_ENDPOINT, symbol, recv_window)
            result = process_response(response, direction)

            # Step 7: Parse PnL
            pnl_value = None
            if result.startswith("Symbol:"):
                try:
                    parts = result.split(", ")
                    parsed_data = {k.strip(): v.strip() for k, v in (item.split(":") for item in parts)}
                    pnl_value = float(parsed_data.get("PnL", 0))
                except Exception as e:
                    print(f"Error parsing PnL for user {user_id}: {str(e)}")
                    pnl_value = None
            else:
                print(f"Process response failed for user {user_id}: {result}")

            # Step 8: Update trade status
            exit_time = update_trade_status(user_trade_collection, trade["_id"], reason, pnl=pnl_value)

            # Step 9: Update balances
            if pnl_value is not None:
                update_balances(user_id, pnl_value, symbol)

            results.append({
                "user_id": user_id,
                "status": "success",
                "exit_time": exit_time.isoformat(),
                "pnl_result": result
            })

        except Exception as e:
            results.append({
                "user_id": user_id,
                "status": "error",
                "message": f"Error processing trade: {str(e)}"
            })

    return jsonify({
        "message": "Batch processing completed for close trade",
        "results": results
    }), 200