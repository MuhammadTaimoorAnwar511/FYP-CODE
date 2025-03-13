from flask import Blueprint, request, jsonify
from app.models.subscription import Subscription
from bson import ObjectId
from app import mongo
from flask_cors import CORS
from flask import Blueprint,request, jsonify
from urllib.parse import urljoin
from datetime import datetime, UTC
import hmac
import requests
import hashlib
import base64
import time

subscription_bp = Blueprint("subscription", __name__)
CORS(subscription_bp)

# Bybit API details
BASE_URL = "https://api-demo.bybit.com"
ENDPOINT = "/v5/account/wallet-balance"
TIME_ENDPOINT = "/v5/market/time"

def get_server_timestamp():
    """Fetch the correct server timestamp from Bybit."""
    try:
        response = requests.get(f"{BASE_URL}{TIME_ENDPOINT}")
        if response.status_code == 200:
            data = response.json()
            return int(data["result"]["timeNano"]) // 1_000_000  
    except Exception as e:
        print(f"Error fetching server time: {e}")
    return int(time.time() * 1000)  # Fallback to local time

def get_usdt_balance(api_key, api_secret):
    """Fetch only USDT wallet balance from Bybit API."""
    params = {"accountType": "UNIFIED"}
    timestamp = str(get_server_timestamp())
    recv_window = "10000"
    query_string = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
    signature_payload = f"{timestamp}{api_key}{recv_window}{query_string}"
    signature = hmac.new(api_secret.encode("utf-8"), signature_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature
    }
    response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and 'list' in data['result']:
            for account in data['result']['list']:
                for coin in account.get('coin', []):
                    if coin['coin'] == 'USDT':
                        return float(coin['walletBalance'])  
    return -1

@subscription_bp.route("/test_connection", methods=["POST"])
def test_connection():
    """Validate API key and fetch USDT balance."""
    data = request.get_json()
    api_key = data.get("api_key")
    api_secret = data.get("api_secret")
    if not api_key or not api_secret:
        return jsonify({"success": False, "error": "API key and secret are required"}), 400
    usdt_balance = get_usdt_balance(api_key, api_secret)
    if usdt_balance == -1:
        return jsonify({"success": False, "error": "Invalid API key or secret"}), 401
    return jsonify({"success": True, "usdt_balance": usdt_balance})

@subscription_bp.route("/create", methods=["POST"])
def create_subscription():
    """Create a new subscription after verifying API credentials and checking balance."""
    data = request.get_json()
    bot_name = data.get("bot_name")
    user_id = data.get("user_id")
    balance_allocated = data.get("balance_allocated")

    if not bot_name or not user_id or balance_allocated is None:
        return jsonify({"error": "Missing required fields"}), 400

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    api_key = user.get("api_key")
    api_secret = user.get("secret_key")

    if not all([user.get("exchange"), api_key, api_secret]):
        return jsonify({"error": "User must have exchange, api_key, and secret_key set"}), 400

    usdt_balance = get_usdt_balance(api_key, api_secret)  # Fetch actual balance from Bybit API
    if usdt_balance == -1:
        return jsonify({"error": "Invalid API key or secret"}), 401

    bots_balance = user.get("Bots_Balance", 0)  # Current allocated balance
    new_balance = bots_balance + balance_allocated  # Updated bot balance

    # **Check if balance allocation is allowed**
    if new_balance > usdt_balance:
        additional_required = new_balance - usdt_balance
        return jsonify({
            "error": f"You need additional {additional_required:.2f} USDT to subscribe to {bot_name} "
                     f"because you already allocated {bots_balance:.2f} USDT to bots."
        }), 400

    # **Proceed with subscription creation**
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"Bots_Balance": new_balance}})
    
    new_user_balance = user.get("User_Balance", 0) + balance_allocated
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"User_Balance": new_user_balance}})

    symbol = bot_name.replace("_", "/")
    subscription_id = mongo.db.subscriptions.insert_one({
        "bot_name": bot_name,
        "symbol": symbol,
        "user_id": user_id,
        "balance_allocated": balance_allocated
    }).inserted_id

    return jsonify({
        "message": f"{symbol} Subscription created successfully, USDT balance: {usdt_balance:.2f}",
        "subscription_id": str(subscription_id),
        "symbol": symbol,
        "usdt_balance": usdt_balance,
        "Bots_Balance": new_balance,
        "User_Balance": new_user_balance
    }), 201



# @subscription_bp.route("/create", methods=["POST"])
# def create_subscription():
#     """Create a new subscription after verifying API credentials."""
#     data = request.get_json()
#     bot_name = data.get("bot_name")
#     user_id = data.get("user_id")
#     balance_allocated = data.get("balance_allocated")
    
#     if not bot_name or not user_id or not balance_allocated:
#         return jsonify({"error": "Missing required fields"}), 400
    
#     user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         return jsonify({"error": "User not found"}), 404
    
#     api_key = user.get("api_key")
#     api_secret = user.get("secret_key")
    
#     if not all([user.get("exchange"), api_key, api_secret]):
#         return jsonify({"error": "User must have exchange, api_key, and secret_key set"}), 400
    
#     usdt_balance = get_usdt_balance(api_key, api_secret)
#     if usdt_balance == -1:
#         return jsonify({"error": "Invalid API key or secret"}), 401
    
#     new_balance = user.get("Bots_Balance", 0) + balance_allocated
#     mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"Bots_Balance": new_balance}})
    
#     # Update User_Balance similarly
#     new_user_balance = user.get("User_Balance", 0) + balance_allocated  
#     mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"User_Balance": new_user_balance}})


#     symbol = bot_name.replace("_", "/")
#     subscription_id = mongo.db.subscriptions.insert_one({
#         "bot_name": bot_name,
#         "symbol": symbol,
#         "user_id": user_id,
#         "balance_allocated": balance_allocated
#     }).inserted_id
    
#     return jsonify({
#         "message": f"{symbol} Subscription created successfully, USDT balance: {usdt_balance}",
#         "subscription_id": str(subscription_id),
#         "symbol": symbol,
#         "usdt_balance": usdt_balance
#     }), 201

# Check if user is subscribed to a specific bot
@subscription_bp.route("/status", methods=["POST"])
def check_subscription_status():
    data = request.get_json() 
    user_id = data.get("user_id")  # Keep as a string
    bot_name = data.get("bot_name")

    if not all([user_id, bot_name]):
        return jsonify({"error": "Missing required fields"}), 400

    # Query the database with user_id as a string
    subscription = mongo.db.subscriptions.find_one({"user_id": user_id, "bot_name": bot_name})

    return jsonify({"subscribed": bool(subscription)}), 200
###
@subscription_bp.route("/delete/<user_id>/<bot_name>", methods=["DELETE"])
def delete_subscription(user_id, bot_name):
    # Query the subscription using user_id as a string
    subscription = mongo.db.subscriptions.find_one({"user_id": user_id, "bot_name": bot_name})

    if not subscription:
        return jsonify({"error": "No subscription found for this user and bot"}), 404

    balance_allocated = subscription.get("balance_allocated", 0)

    # Find the user to update balance
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})  # Only convert here if needed
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Deduct balance from user
    new_balance = max(user.get("Bots_Balance", 0) - balance_allocated, 0)  
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"Bots_Balance": new_balance}})


    new_user_balance = max(user.get("User_Balance", 0) - balance_allocated, 0)  
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"User_Balance": new_user_balance}})

    # Delete the subscription
    result = mongo.db.subscriptions.delete_one({"user_id": user_id, "bot_name": bot_name})

    return jsonify({"message": "Subscription deleted"}), 200
