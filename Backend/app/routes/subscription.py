import os
from dotenv import load_dotenv
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
from flask_jwt_extended import jwt_required, get_jwt_identity


# Load environment variables from .env file
load_dotenv()

# Get the values of Bybit API details from the .env file
BASE_URL = os.getenv("BASE_URL")
WALLETENDPOINT = os.getenv("WALLETENDPOINT")
TIME_ENDPOINT = os.getenv("TIME_ENDPOINT")

subscription_bp = Blueprint("subscription", __name__)
CORS(subscription_bp)


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
    response = requests.get(f"{BASE_URL}{WALLETENDPOINT}", params=params, headers=headers)
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
@jwt_required()
def create_subscription():
    """Create a new subscription after verifying API credentials and checking balance."""
    user_id = get_jwt_identity()  # ✅ Get user _id from token
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    bot_name = data.get("bot_name")
    bot_initial_balance = data.get("bot_initial_balance")

    if not bot_name or bot_initial_balance is None:
        return jsonify({"error": "Missing required fields"}), 400

    api_key = user.get("api_key")
    api_secret = user.get("secret_key")

    if not all([user.get("exchange"), api_key, api_secret]):
        return jsonify({"error": "User must have exchange, api_key, and secret_key set"}), 400

    usdt_balance = get_usdt_balance(api_key, api_secret)  # Fetch actual balance from Bybit API
    if usdt_balance == -1:
        return jsonify({"error": "Invalid API key or secret"}), 401

    balance_allocated_to_bots = user.get("balance_allocated_to_bots", 0)
    new_balance = balance_allocated_to_bots + bot_initial_balance

    if new_balance > usdt_balance:
        additional_required = new_balance - usdt_balance
        return jsonify({
            "error": f"You need additional {additional_required:.2f} USDT to subscribe to {bot_name} "
                     f"because you already allocated {balance_allocated_to_bots:.2f} USDT to bots."
        }), 400

    # Proceed with subscription creation
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"balance_allocated_to_bots": new_balance}})
    
    new_user_current_balance = user.get("user_current_balance", 0) + bot_initial_balance
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"user_current_balance": new_user_current_balance}})

    symbol = bot_name.replace("_", "/")
    subscription_id = mongo.db.subscriptions.insert_one({
        "bot_name": bot_name,
        "symbol": symbol,
        "user_id": str(user_id),
        "bot_initial_balance": bot_initial_balance,
        "bot_current_balance": bot_initial_balance
    }).inserted_id

    return jsonify({
        "message": f"{symbol} Subscription created successfully, USDT balance: {usdt_balance:.2f}",
        "subscription_id": str(subscription_id),
        "symbol": symbol,
        "usdt_balance": usdt_balance,
        "balance_allocated_to_bots": new_balance,
        "user_current_balance": new_user_current_balance
    }), 201

@subscription_bp.route("/status", methods=["POST"])
@jwt_required()
def check_subscription_status():
    user_id = get_jwt_identity()  # ✅ Get user _id from token
    data = request.get_json()
    bot_name = data.get("bot_name")

    if not bot_name:
        return jsonify({"error": "Missing bot_name field"}), 400

    # Query the database using user_id from token
    subscription = mongo.db.subscriptions.find_one({
        "user_id": str(user_id),
        "bot_name": bot_name
    })

    return jsonify({"subscribed": bool(subscription)}), 200


@subscription_bp.route("/delete/<user_id>/<bot_name>", methods=["DELETE"])
def delete_subscription(user_id, bot_name):
    
    # Query the subscription using user_id as a string
    subscription = mongo.db.subscriptions.find_one({"user_id": user_id, "bot_name": bot_name})

    if not subscription:
        return jsonify({"error": "No subscription found for this user and bot"}), 404

    bot_initial_balance = subscription.get("bot_initial_balance", 0)

    # Find the user to update balance
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})  
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Deduct balance from user
    new_balance = max(user.get("balance_allocated_to_bots", 0) - bot_initial_balance, 0)  
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"balance_allocated_to_bots": new_balance}})


    new_user_current_balance = user.get("user_current_balance", 0) - bot_initial_balance
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"user_current_balance": new_user_current_balance}})

    # Delete the subscription
    result = mongo.db.subscriptions.delete_one({"user_id": user_id, "bot_name": bot_name})

    return jsonify({"message": f"{bot_name} Bot Subscription deleted"}), 200
