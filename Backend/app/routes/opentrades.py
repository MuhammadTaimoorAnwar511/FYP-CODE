import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS

from pymongo import MongoClient
from bson import ObjectId

import requests
import time
import hmac
import hashlib
import json
import math
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

# Environment Variables and MongoDB Connection
BASE_URL = os.getenv("BASE_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Collections
subscriptions_collection = db['subscriptions']
users_collection = db['users']

# Flask Blueprint
opentrades_bp = Blueprint('opentrades', __name__)
CORS(opentrades_bp)

# -------------------- Utility Functions --------------------
def get_server_timestamp(base_url: str) -> int:
    try:
        response = requests.get(f"{base_url}/v5/market/time")
        if response.status_code == 200:
            data = response.json()
            return int(data["result"]["timeNano"]) // 1_000_000
        return int(time.time() * 1000)
    except Exception:
        return int(time.time() * 1000)

def sign_payload(api_secret, timestamp, api_key, recv_window, json_payload):
    payload = f"{timestamp}{api_key}{recv_window}{json_payload}"
    return hmac.new(api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

def send_post_request(base_url, endpoint, api_key, api_secret, recv_window, params):
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
    #'orderId' can be get here from response
    return requests.post(f"{base_url}{endpoint}", data=json_payload, headers=headers)

def get_current_price(base_url, symbol):
    try:
        response = requests.get(f"{base_url}/v5/market/tickers", params={"category": "linear", "symbol": symbol})
        if response.status_code == 200:
            return float(response.json()['result']['list'][0]['lastPrice'])
        return None
    except:
        return None

def get_instrument_info(base_url, symbol):
    try:
        response = requests.get(f"{base_url}/v5/market/instruments-info", params={"category": "linear", "symbol": symbol})
        if response.status_code == 200:
            return response.json()['result']['list'][0]
        return None
    except:
        return None

def get_symbol_info(base_url, symbol):
    info = get_instrument_info(base_url, symbol)
    return info.get("lotSizeFilter") if info else None

def get_max_allowed_leverage(base_url, symbol):
    info = get_instrument_info(base_url, symbol)
    return info["leverageFilter"]["maxLeverage"] if info and "leverageFilter" in info else "50"

def format_quantity(qty, step):
    decimals = int(round(-math.log(step, 10))) if step < 1 else 0
    formatted = f"{qty:.{decimals}f}"
    return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted

def validate_direction(direction):
    if direction.lower() not in ["long", "short"]:
        raise ValueError("Direction must be 'long' or 'short'")

def compute_usdt_amount(balance, percentage, multiplier):
    return (balance * (percentage / 100)) * multiplier

def set_leverage_action(base_url, api_key, api_secret, recv_window, symbol, desired_max_leverage=None):
    if not desired_max_leverage:
        desired_max_leverage = get_max_allowed_leverage(base_url, symbol)
    params = {
        "category": "linear",
        "symbol": symbol,
        "buyLeverage": desired_max_leverage,
        "sellLeverage": desired_max_leverage
    }
    return send_post_request(base_url, "/v5/position/set-leverage", api_key, api_secret, recv_window, params)

def calculate_order_quantity(base_url, symbol, usdt_amount):
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

def create_market_order_action(base_url, api_key, api_secret, recv_window, symbol, direction, stop_loss, take_profit, usdt_amount, position_idx=0):
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
    return send_post_request(base_url, "/v5/order/create", api_key, api_secret, recv_window, params)

def generate_signature(api_key, api_secret, query_str, timestamp, recv_window):
    return hmac.new(api_secret.encode(), f'{timestamp}{api_key}{recv_window}{query_str}'.encode(), hashlib.sha256).hexdigest()

def get_position_info(symbol, api_key, api_secret, base_url):
    endpoint = '/v5/position/list'
    params = {'category': "linear", 'symbol': symbol}
    query_str = '&'.join([f'{k}={v}' for k, v in params.items()])
    timestamp = str(int(time.time() * 1000))
    recv_window = '5000'
    sign = generate_signature(api_key, api_secret, query_str, timestamp, recv_window)
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': sign,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    return requests.get(f'{base_url}{endpoint}?{query_str}', headers=headers).json()

def store_position_data_to_mongo(user_id: str, position_data: dict):
    collection = db[f"user_{user_id}"]
    collection.insert_one(position_data)

# -------------------- Helper Functions --------------------
def parse_trade_data(req): return req.get_json() or {}
def fetch_subscriptions_by_symbol(symbol): return list(subscriptions_collection.find({"symbol": symbol}))
def find_user_by_id(user_id_str): return users_collection.find_one({"_id": ObjectId(user_id_str)})
def build_trade_info(trade_data, sub, user):
    return {
        "symbol": trade_data.get("symbol").replace("/", ""),
        "direction": trade_data.get("direction", "").lower(),
        "stop_loss": round(float(trade_data.get("stop_loss", 0)), 2),
        "take_profit": round(float(trade_data.get("take_profit", 0)), 2),
        "investment_per_trade": float(trade_data.get("investment_per_trade", 0)),
        "amount_multiplier": int(float(trade_data.get("amount_multiplier", 0))),
        "user_id": sub.get("user_id"),
        "balance_allocated": sub.get("balance_allocated", 0),
        "api_key": user.get("api_key"),
        "secret_key": user.get("secret_key")
    }

# -------------------- Routes --------------------
@opentrades_bp.route('/open_trade', methods=['POST'])
def open_trade():
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
        if not user: continue
        info = build_trade_info(trade_data, sub, user)
        try: validate_direction(info["direction"])
        except ValueError as e:
            results.append({"user_id": user_id, "status": "failed", "error": str(e)})
            continue
        usdt_amount = compute_usdt_amount(info["balance_allocated"], info["investment_per_trade"], info["amount_multiplier"])
        try:
            leverage_resp = set_leverage_action(BASE_URL, info["api_key"], info["secret_key"], "5000", info["symbol"])
            if leverage_resp.status_code != 200:
                results.append({"user_id": user_id, "status": "failed", "error": "Leverage error", "response": leverage_resp.json()})
                continue
        except Exception as e:
            results.append({"user_id": user_id, "status": "failed", "error": str(e)})
            continue
        try:
            order_resp = create_market_order_action(BASE_URL, info["api_key"], info["secret_key"], "5000", info["symbol"], info["direction"], info["stop_loss"], info["take_profit"], usdt_amount)
            if order_resp and order_resp.status_code == 200:
                order_data = order_resp.json()  # ✅ Now we define order_data properly
                order_id = order_data.get("result", {}).get("orderId")  # ✅ Extract orderId
                results.append({"user_id": user_id, "status": "success", "order": order_resp.json()})
                position_data = get_position_info(info["symbol"], info["api_key"], info["secret_key"], BASE_URL)
                if position_data["retCode"] == 0 and position_data["result"]["list"]:
                    pos = position_data["result"]["list"][0]
                    record = {
                        "user_id": user_id,
                        "orderId":order_id,
                        "symbol": pos['symbol'],
                        "direction": 'LONG' if pos['side'] == 'Buy' else 'SHORT',
                        "entry_time": datetime.fromtimestamp(int(pos['createdTime']) / 1000, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "entry_price": float(pos['avgPrice']),
                        "stop_loss": float(pos['stopLoss']) if pos['stopLoss'] else None,
                        "take_profit": float(pos['takeProfit']) if pos['takeProfit'] else None,
                        "leverage": pos['leverage'],
                        "initial_margin": float(pos['positionIM']),
                        "status": "OPEN",
                        "PNL":None,
                        "exit_time":None
                    }
                    store_position_data_to_mongo(user_id, record)
            else:
                results.append({"user_id": user_id, "status": "failed", "order": order_resp.json() if order_resp else None})
        except Exception as e:
            results.append({"user_id": user_id, "status": "failed", "error": str(e)})
    return jsonify({"message": f"Processed {len(results)} user(s)", "results": results}), 200

