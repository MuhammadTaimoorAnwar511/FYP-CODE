import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import hmac
import hashlib
import base64
from datetime import datetime, UTC
from urllib.parse import urljoin
from flask_cors import CORS
from app import mongo
from bson.objectid import ObjectId
import time
from bson import ObjectId

# Load environment variables from .env file
load_dotenv()

# Get the values of Bybit API details from the .env file
BASE_URL = os.getenv("BASE_URL")
WALLETENDPOINT = os.getenv("WALLETENDPOINT")
TIME_ENDPOINT = os.getenv("TIME_ENDPOINT")

exchange_bp = Blueprint('exchange', __name__)
CORS(exchange_bp) 

def get_server_timestamp():
    """Fetch the correct server timestamp from Bybit to avoid time drift issues."""
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
    
    timestamp = str(get_server_timestamp())  # Use Bybit's server time
    recv_window = "10000"  

    query_string = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))

    signature_payload = f"{timestamp}{api_key}{recv_window}{query_string}"
    signature = hmac.new(
        api_secret.encode("utf-8"),
        signature_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

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
    return -1  # Default if USDT balance is not found

@exchange_bp.route('/TestConnection', methods=['POST'])
@jwt_required()
def test_connection():
    user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"success": False, "error": "Unauthorized user"}), 403

    data = request.get_json()
    api_key = data.get("api_key")
    api_secret = data.get("api_secret")

    if not api_key or not api_secret:
        return jsonify({"success": False, "error": "API key and secret are required"}), 400

    usdt_balance = get_usdt_balance(api_key, api_secret)

    if usdt_balance == -1:  # Invalid API key or secret
        return jsonify({"success": False, "error": "Invalid API key or secret"}), 401

    return jsonify({"success": True, "usdt_balance": usdt_balance})

@exchange_bp.route("/SaveConnection", methods=["PUT"])
@jwt_required()
def update_exchange():
    user_id = get_jwt_identity()  # Now using _id from token
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    data = request.json

    # Extract API credentials and selected exchange
    api_key = data.get("apiKey")
    api_secret = data.get("apiSecret")
    selected_exchange = data.get("selectedExchange")

    if not selected_exchange:
        return jsonify({"success": False, "message": "Exchange name is required"}), 400

    if not api_key:
        return jsonify({"success": False, "message": "API key is missing"}), 400

    if not api_secret:
        return jsonify({"success": False, "message": "API secret is missing"}), 400

    # Test API credentials
    usdt_balance = get_usdt_balance(api_key, api_secret)

    if usdt_balance == -1:
        return jsonify({
            "success": False,
            "message": "Invalid API key or secret. Please check your credentials and try again."
        }), 401

    if usdt_balance == 0:
        return jsonify({
            "success": False,
            "message": "Valid API credentials, but your USDT balance is zero."
        }), 200

    # Update user data in MongoDB
    update_data = {
        "exchange": selected_exchange,
        "api_key": api_key,
        "secret_key": api_secret
    }
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    return jsonify({
        "success": True,
        "message": f"Exchange '{selected_exchange}' connected successfully!",
        "usdt_balance": usdt_balance
    }), 200


@exchange_bp.route('/DeleteConnection', methods=['DELETE'])
@jwt_required()
def delete_connection():
    try:
        user_id = get_jwt_identity()  # _id from JWT token
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        if not user:
            return jsonify({"message": "User not found"}), 404

        user_id_str = str(user["_id"])  # For comparing in subscriptions (if stored as string)

        # Check if user is subscribed to any bots
        active_subscriptions = list(mongo.db.subscriptions.find({"user_id": user_id_str}))
        if active_subscriptions:
            subscribed_bots = [sub.get("bot_name", "Unknown") for sub in active_subscriptions]
            return jsonify({
                "error": "Unsubscribe from the following bots first.",
                "subscribed_bots": subscribed_bots
            }), 400

        # Clear exchange connection info
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "exchange": None,
                "api_key": None,
                "secret_key": None
            }}
        )

        return jsonify({"message": "Exchange connection deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
