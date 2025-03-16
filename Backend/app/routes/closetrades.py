import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

# ------------------------------------------------------------------------------
# Configuration and Database Setup
# ------------------------------------------------------------------------------
load_dotenv() 
# Configuration variables
BASE_URL = os.getenv("BASE_URL")
CLOSEPNL= os.getenv("CLOSE_PNL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# MongoDB connection and collections
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
subscriptions_collection = db['subscriptions']
users_collection = db['users']

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

def update_trade_status(trade_collection, trade_id, reason):
    """
    Update a trade document to mark it as closed with a given reason.
    """
    exit_time = datetime.now(timezone.utc)
    trade_collection.update_one(
        {"_id": trade_id},
        {"$set": {"status": reason, "exit_time": exit_time}}
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
# Flask Blueprint Setup
# ------------------------------------------------------------------------------
closetrades_bp = Blueprint('closetrades', __name__)
CORS(closetrades_bp)

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
    log_user_keys(user)

    # Step 3: Retrieve the user's trade collection.
    user_trade_collection = get_user_trade_collection(user_id)
    if user_trade_collection.name not in db.list_collection_names():
        print("User trade collection not found.")

    # Step 4: Find an open trade matching the symbol and direction.
    trade = find_open_trade(user_trade_collection, symbol, direction)
    if not trade:
        return jsonify({"message": "Open trade not found for the provided symbol and direction"}), 404

    # Step 5: Update the trade status to mark it as closed.
    exit_time = update_trade_status(user_trade_collection, trade["_id"], reason)

    # Return a successful response.
    return jsonify({
        "message": "User trade closed successfully",
        "exit_time": exit_time.isoformat()
    }), 200
