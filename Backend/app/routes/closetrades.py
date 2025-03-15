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


# Flask Blueprint
closetrades_bp = Blueprint('closetrades', __name__)
CORS(closetrades_bp)

@closetrades_bp.route('/close_trade', methods=['POST'])
def close_trade():
    # Get the JSON data from the request body
    data = request.get_json()
    symbol = data.get("symbol")
    direction = data.get("direction")
    reason = data.get("reason")
    
    # Step 1: Find the subscription using the provided symbol.
    # (Assumes the subscription symbol matches the provided symbol)
    subscription = subscriptions_collection.find_one({"symbol": symbol})
    if not subscription:
        return jsonify({"message": "Subscription not found for the provided symbol"}), 404
    
    # Step 2: Retrieve the user_id from the subscription.
    user_id = subscription.get("user_id")
    
    # Step 3: Access the user's trade collection using the user_id.
    user_collection_name = f"user_{user_id}"
    user_trade_collection = db[user_collection_name]
    
    # Additional check: Print whether the user collection exists.
    if user_collection_name in db.list_collection_names():
        print("User collection found.")
    else:
        print("User collection not found.")
    
    # Remove "/" from symbol for comparing with the symbol stored in user trade collection.
    clean_symbol = symbol.replace("/", "")
    
    # Step 4: Look for an open trade with matching symbol and direction.
    trade = user_trade_collection.find_one({
        "symbol": clean_symbol,
        "direction": direction,
        "status": "OPEN"
    })
    if not trade:
        return jsonify({"message": "Open trade not found for the provided symbol and direction"}), 404
    
    # Step 5: Retrieve the entry price.
    entry_price = trade.get("entry_price")
    
    # Optionally, update the trade to mark it as closed.
    exit_time = datetime.now(timezone.utc)
    user_trade_collection.update_one(
        {"_id": trade["_id"]},
        {"$set": {"status": reason, "exit_time": exit_time}}
    )
    
    # Return the result with entry_price and exit time.
    return jsonify({
        "message": "User trade closed successfully"
    }), 200
