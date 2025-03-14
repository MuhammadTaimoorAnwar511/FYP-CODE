import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS

from pymongo import MongoClient
from bson import ObjectId
from bson.objectid import ObjectId

import requests
import time
import hmac
import hashlib
import json
import math
# Load environment variables from .env file
load_dotenv()

# --------------------------------------------------------------------------
# Environment Variables and MongoDB Connection
# --------------------------------------------------------------------------
BASE_URL = os.getenv("BASE_URL")
ENDPOINT = os.getenv("ENDPOINT")
TIME_ENDPOINT = os.getenv("TIME_ENDPOINT")

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Collections
subscriptions_collection = db['subscriptions']
users_collection = db['users']

# --------------------------------------------------------------------------
# Blueprint Configuration
# --------------------------------------------------------------------------
trades_bp = Blueprint('trades', __name__)
CORS(trades_bp)

# --------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------
def parse_trade_data(req) -> dict:

    trade_data = req.get_json()
    return trade_data if trade_data else {}

def fetch_subscriptions_by_symbol(symbol: str) -> list:

    return list(subscriptions_collection.find({"symbol": symbol}))

def find_user_by_id(user_id_str: str) -> dict:

    try:
        user_obj_id = ObjectId(user_id_str)
    except:
        return None  # Invalid user ID format
    return users_collection.find_one({"_id": user_obj_id})

def build_trade_info(trade_data: dict, subscription: dict, user_record: dict) -> dict:

    return {
        "symbol": trade_data.get("symbol").replace("/", ""),
        "direction": trade_data.get("direction", "").lower(),
        "stop_loss": round(float(trade_data.get("stop_loss", 0)), 2),
        "take_profit": round(float(trade_data.get("take_profit", 0)), 2),
        "investment_per_trade": float(trade_data.get("investment_per_trade", 0)),
        "amount_multiplier": int(float(trade_data.get("amount_multiplier", 0))),
        "user_id": subscription.get("user_id"),
        "balance_allocated": subscription.get("balance_allocated", 0),
        "api_key": user_record.get("api_key"),
        "secret_key": user_record.get("secret_key"),
    }

# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@trades_bp.route('/open_trade', methods=['POST'])
def open_trade():

    try:
        # Parse incoming data
        trade_data = parse_trade_data(request)
        if not trade_data:
            return jsonify({"error": "No JSON data received"}), 400

        # Ensure a symbol is provided
        symbol = trade_data.get("symbol")
        if not symbol:
            return jsonify({"error": "Missing symbol in request"}), 400

        # Retrieve all subscriptions for this symbol
        subscriptions = fetch_subscriptions_by_symbol(symbol)
        if not subscriptions:
            return jsonify({"error": "No subscriptions found for this symbol"}), 404

        all_trades = []
        # Build trade info for each subscription
        for subscription in subscriptions:
            user_id_str = subscription.get("user_id")
            if not user_id_str:
                continue  # Skip if no user ID

            user_record = find_user_by_id(user_id_str)
            if not user_record:
                continue  # Skip if user not found

            trade_info = build_trade_info(trade_data, subscription, user_record)
            all_trades.append(trade_info)


        if not all_trades:
            return jsonify({"error": "No valid user subscriptions processed"}), 400

        return jsonify({
            "message": f"Trade opened for {len(all_trades)} user(s)",
            "trades": all_trades
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@trades_bp.route('/close_trade', methods=['POST'])
def close_trade():
    """
    Close a trade (placeholder endpoint).
    
    Returns:
        JSON response confirming that a trade has been closed.
    """
    print("User trade close successfully")
    return jsonify({
        "message": "User trade close successfully"
    }), 200
