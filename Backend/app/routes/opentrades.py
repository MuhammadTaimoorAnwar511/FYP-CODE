import os
import time
import hmac
import hashlib
import json
import math
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

# ------------------------------------------------------------------------------
# Environment and Database Setup
# ------------------------------------------------------------------------------
load_dotenv()  # Load environment variables from .env file

BASE_URL = os.getenv("BASE_URL")
TIME_ENDPOINT = os.getenv("TIME_ENDPOINT")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
Tickers = os.getenv("Tickers")
INSTUMENTS_INFO=os.getenv("INSTUMENTS_INFO")
POSITION_LIST=os.getenv("POSITION_LIST")
SET_LEVERAGE=os.getenv("SET_LEVERAGE")
CREATE_ORDER=os.getenv("CREATE_ORDER")
recv_window = '5000'
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# MongoDB collections
subscriptions_collection = db['subscriptions']
users_collection = db['users']

# ------------------------------------------------------------------------------
# Flask Blueprint Setup
# ------------------------------------------------------------------------------
opentrades_bp = Blueprint('opentrades', __name__)
CORS(opentrades_bp)

# ------------------------------------------------------------------------------
# API Utility Functions
# ------------------------------------------------------------------------------
def get_server_timestamp(base_url: str) -> int:
    """
    Retrieve the server timestamp from the market time endpoint.
    """
    try:
        response = requests.get(f"{base_url}{TIME_ENDPOINT}")
        if response.status_code == 200:
            data = response.json()
            return int(data["result"]["timeNano"]) // 1_000_000
        return int(time.time() * 1000)
    except Exception:
        return int(time.time() * 1000)

def sign_payload(api_secret: str, timestamp: str, api_key: str, recv_window: str, json_payload: str) -> str:
    """
    Sign the payload using HMAC SHA256.
    """
    payload = f"{timestamp}{api_key}{recv_window}{json_payload}"
    return hmac.new(api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

def send_post_request(base_url: str, endpoint: str, api_key: str, api_secret: str, recv_window: str, params: dict):
    """
    Send a POST request to the given endpoint with a signed payload.
    """
    timestamp = str(get_server_timestamp(base_url))
    sorted_params = dict(sorted(params.items()))
    json_payload = json.dumps(sorted_params, separators=(',', ':'))
    signature = sign_payload(api_secret, timestamp, api_key, recv_window, json_payload)
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
        "Content-Type": "application/json"
    }
    return requests.post(f"{base_url}{endpoint}", data=json_payload, headers=headers)

def generate_signature(api_key: str, api_secret: str, query_str: str, timestamp: str, recv_window: str) -> str:
    """
    Generate a signature for GET requests.
    """
    return hmac.new(api_secret.encode(), f'{timestamp}{api_key}{recv_window}{query_str}'.encode(), hashlib.sha256).hexdigest()

# ------------------------------------------------------------------------------
# Market Data Utility Functions
# ------------------------------------------------------------------------------
def get_current_price(base_url: str, symbol: str):
    """
    Get the current market price for the given symbol.
    """
    try:
        response = requests.get(f"{base_url}{Tickers}", params={"category": "linear", "symbol": symbol})
        if response.status_code == 200:
            return float(response.json()['result']['list'][0]['lastPrice'])
        return None
    except Exception:
        return None

def get_instrument_info(base_url: str, symbol: str):
    """
    Retrieve instrument information for the given symbol.
    """
    try:
        response = requests.get(f"{base_url}{INSTUMENTS_INFO}", params={"category": "linear", "symbol": symbol})
        if response.status_code == 200:
            return response.json()['result']['list'][0]
        return None
    except Exception:
        return None

def get_symbol_info(base_url: str, symbol: str):
    """
    Get lot size filter details for the given symbol.
    """
    info = get_instrument_info(base_url, symbol)
    return info.get("lotSizeFilter") if info else None

def get_max_allowed_leverage(base_url: str, symbol: str):
    """
    Retrieve the maximum allowed leverage for the given symbol.
    """
    info = get_instrument_info(base_url, symbol)
    return info["leverageFilter"]["maxLeverage"] if info and "leverageFilter" in info else "50"

def format_quantity(qty: float, step: float) -> str:
    """
    Format the order quantity based on the step size.
    """
    decimals = int(round(-math.log(step, 10))) if step < 1 else 0
    formatted = f"{qty:.{decimals}f}"
    return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted

def calculate_order_quantity(base_url: str, symbol: str, usdt_amount: float):
    """
    Calculate the order quantity based on USDT amount and current market price.
    """
    lot_size_filter = get_symbol_info(base_url, symbol)
    if not lot_size_filter:
        return None
    qty_step = float(lot_size_filter['qtyStep'])
    min_qty = float(lot_size_filter['minOrderQty'])
    price = get_current_price(base_url, symbol)
    if not price or price <= 0:
        return None
    raw_qty = usdt_amount / price
    adjusted_qty = max(round(raw_qty / qty_step) * qty_step, min_qty)
    return format_quantity(adjusted_qty, qty_step) if adjusted_qty * price >= 20 else None

def get_position_info(symbol: str, api_key: str, api_secret: str, base_url: str):
    """
    Retrieve position information for the given symbol.
    """
    endpoint = POSITION_LIST
    params = {'category': "linear", 'symbol': symbol}
    query_str = '&'.join([f'{k}={v}' for k, v in params.items()])
    timestamp = str(int(time.time() * 1000))

    sign = generate_signature(api_key, api_secret, query_str, timestamp, recv_window)
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': sign,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    return requests.get(f'{base_url}{endpoint}?{query_str}', headers=headers).json()

# ------------------------------------------------------------------------------
# Trading Action Functions
# ------------------------------------------------------------------------------
def set_leverage_action(base_url: str, api_key: str, api_secret: str, recv_window: str, symbol: str, desired_max_leverage=None):
    """
    Set the leverage for a given symbol.
    """
    if not desired_max_leverage:
        desired_max_leverage = get_max_allowed_leverage(base_url, symbol)
    params = {
        "category": "linear",
        "symbol": symbol,
        "buyLeverage": desired_max_leverage,
        "sellLeverage": desired_max_leverage
    }
    return send_post_request(base_url,SET_LEVERAGE,api_key, api_secret, recv_window, params)

def create_market_order_action(base_url: str, api_key: str, api_secret: str, recv_window: str, symbol: str, direction: str, stop_loss, take_profit, usdt_amount: float, position_idx: int = 0):
    """
    Create a market order based on the given parameters.
    """
    qty = calculate_order_quantity(base_url, symbol, usdt_amount)
    if not qty:
        return None
    params = {
        "category": "linear",
        "symbol": symbol,
        "side": "Buy" if direction.lower() == "long" else "Sell",
        "orderType": "Market",
        "qty": qty,
        "positionIdx": position_idx
    }
    if take_profit:
        params["takeProfit"] = str(take_profit)
    if stop_loss:
        params["stopLoss"] = str(stop_loss)
    return send_post_request(base_url, CREATE_ORDER , api_key, api_secret, recv_window, params)

def store_position_data_to_mongo(user_id: str, position_data: dict):
    """
    Store the given position data into the user's MongoDB collection.
    """
    collection = db[f"user_{user_id}"]
    collection.insert_one(position_data)

# ------------------------------------------------------------------------------
# Trade Calculation Functions
# ------------------------------------------------------------------------------
def validate_direction(direction: str):
    """
    Validate the trade direction.
    """
    if direction.lower() not in ["long", "short"]:
        raise ValueError("Direction must be 'long' or 'short'")

def compute_usdt_amount(balance: float, percentage: float, multiplier: float) -> float:
    """
    Compute the USDT amount for the trade.
    """
    return (balance * (percentage / 100)) * multiplier

# ------------------------------------------------------------------------------
# Request Parsing and Data Building Helpers
# ------------------------------------------------------------------------------
def parse_trade_data(req) -> dict:
    """
    Parse the trade data from the incoming request.
    """
    return req.get_json() or {}

def fetch_subscriptions_by_symbol(symbol: str):
    """
    Fetch all subscriptions for a given symbol.
    """
    return list(subscriptions_collection.find({"symbol": symbol}))

def find_user_by_id(user_id_str: str):
    """
    Retrieve a user document by its ID.
    """
    return users_collection.find_one({"_id": ObjectId(user_id_str)})

def build_trade_info(trade_data: dict, sub: dict, user: dict) -> dict:
    """
    Build the trade information dictionary using trade data, subscription, and user details.
    """
    return {
        "symbol": trade_data.get("symbol").replace("/", ""),
        "direction": trade_data.get("direction", "").lower(),
        "stop_loss": round(float(trade_data.get("stop_loss", 0)), 2),
        "take_profit": round(float(trade_data.get("take_profit", 0)), 2),
        "investment_per_trade": float(trade_data.get("investment_per_trade", 0)),
        "amount_multiplier": int(float(trade_data.get("amount_multiplier", 0))),
        "user_id": sub.get("user_id"),
        "bot_initial_balance": sub.get("bot_initial_balance",0),
        "api_key": user.get("api_key"),
        "secret_key": user.get("secret_key")
    }

# ------------------------------------------------------------------------------
# Flask Route: Open Trade
# ------------------------------------------------------------------------------
@opentrades_bp.route('/open_trade', methods=['POST'])
def open_trade():
    """
    Process the open trade request:
      1. Parse the incoming trade data.
      2. Validate the symbol and fetch subscriptions.
      3. For each subscription, validate direction, compute trade amount,
         set leverage, create a market order, and store the position.
    """
    trade_data = parse_trade_data(request)
    if not trade_data.get("symbol"):
        return jsonify({"error": "Missing symbol"}), 400

    subscriptions = fetch_subscriptions_by_symbol(trade_data["symbol"])
    if not subscriptions:
        return jsonify({"error": "No subscriptions found"}), 404

    results = []
    for sub in subscriptions:
        user_id = sub.get("user_id")
        user = find_user_by_id(user_id)
        if not user:
            continue

        info = build_trade_info(trade_data, sub, user)
        try:
            validate_direction(info["direction"])
        except ValueError as e:
            results.append({"user_id": user_id, "status": "failed", "error": str(e)})
            continue

        usdt_amount = compute_usdt_amount(info["bot_initial_balance"], info["investment_per_trade"], info["amount_multiplier"])

        try:
            leverage_resp = set_leverage_action(BASE_URL, info["api_key"], info["secret_key"],recv_window, info["symbol"])
            if leverage_resp.status_code != 200:
                results.append({
                    "user_id": user_id,
                    "status": "failed",
                    "error": "Leverage error",
                    "response": leverage_resp.json()
                })
                continue
        except Exception as e:
            results.append({"user_id": user_id, "status": "failed", "error": str(e)})
            continue

        try:
            order_resp = create_market_order_action(
                BASE_URL,
                info["api_key"],
                info["secret_key"],
                recv_window,
                info["symbol"],
                info["direction"],
                info["stop_loss"],
                info["take_profit"],
                usdt_amount
            )
            if order_resp and order_resp.status_code == 200:
                order_data = order_resp.json()  # Define order_data properly
                order_id = order_data.get("result", {}).get("orderId")  # Extract orderId
                results.append({"user_id": user_id, "status": "success", "order": order_resp.json()})
                position_data = get_position_info(info["symbol"], info["api_key"], info["secret_key"], BASE_URL)
                if position_data["retCode"] == 0 and position_data["result"]["list"]:
                    pos = position_data["result"]["list"][0]
                    record = {
                        "user_id": user_id,
                        "orderId": order_id,
                        "symbol": pos['symbol'],
                        "direction": 'LONG' if pos['side'] == 'Buy' else 'SHORT',
                        "entry_time": datetime.fromtimestamp(int(pos['createdTime']) / 1000, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "entry_price": float(pos['avgPrice']),
                        "stop_loss": float(pos['stopLoss']) if pos['stopLoss'] else None,
                        "take_profit": float(pos['takeProfit']) if pos['takeProfit'] else None,
                        "leverage": pos['leverage'],
                        "initial_margin": float(pos['positionIM']),
                        "status": "OPEN",
                        "PNL": None,
                        "exit_time": None
                    }
                    store_position_data_to_mongo(user_id, record)
            else:
                results.append({"user_id": user_id, "status": "failed", "order": order_resp.json() if order_resp else None})
        except Exception as e:
            results.append({"user_id": user_id, "status": "failed", "error": str(e)})

    return jsonify({"message": f"Processed {len(results)} user(s)", "results": results}), 200
