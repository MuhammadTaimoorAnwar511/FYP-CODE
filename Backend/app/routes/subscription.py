from flask import Blueprint, request, jsonify
from app.models.subscription import Subscription
from bson import ObjectId
from app import mongo
from flask_cors import CORS
from flask import request, jsonify
from urllib.parse import urljoin
from datetime import datetime, UTC
from bson import ObjectId
import hmac
import requests
import hashlib
import base64


subscription_bp = Blueprint("subscription", __name__)
CORS(subscription_bp) 

class OKXClient:
    def __init__(self, api_key, api_secret, passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
        self.is_demo = True  # Only allow demo trading

    def _get_timestamp(self):
        return datetime.now(UTC).isoformat(timespec='milliseconds').replace("+00:00", "Z")

    def _sign(self, timestamp, method, request_path, body=''):
        message = str(timestamp) + method.upper() + request_path + str(body)
        mac = hmac.new(
            bytes(self.api_secret, 'utf-8'), 
            bytes(message, 'utf-8'), 
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')

    def get_balance(self):
        method = 'GET'
        request_path = '/api/v5/account/balance'
        url = urljoin(self.base_url, request_path)
        
        timestamp = self._get_timestamp()
        signature = self._sign(timestamp, method, request_path)
        
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        
        if self.is_demo:
            headers['x-simulated-trading'] = '1'  # Ensure demo trading is enforced
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data['code'] == '0':
                return data['data']  # Return balance data
            return None
        except Exception as e:
            return {'error': str(e)}

@subscription_bp.route('/Checkbalance', methods=['POST'])
def balance():
    data = request.get_json()
    if not data or not all(k in data for k in ('api_key', 'api_secret', 'passphrase')):
        return jsonify({'error': 'Missing required API credentials'}), 400
    
    client = OKXClient(
        api_key=data['api_key'],
        api_secret=data['api_secret'],
        passphrase=data['passphrase']
    )
    
    try:
        balance_data = client.get_balance()
        if balance_data:
            # Extract USDT balance
            usdt_balance = next(
                (item["eq"] for item in balance_data[0]["details"] if item["ccy"] == "USDT"),
                "0"  # Default to "0" if USDT is not found
            )
            return jsonify({'success': True, 'USDT_balance': usdt_balance})
        else:
            return jsonify({'success': False, 'error': 'Failed to retrieve balance'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_bp.route("/create", methods=["POST"])
def create_subscription():
    data = request.get_json()
    bot_name = data.get("bot_name")
    user_id = data.get("user_id")  # This is a string from the request
    balance_allocated = data.get("balance_allocated")

    if not all([bot_name, user_id, balance_allocated]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user_object_id = ObjectId(user_id)
        balance_allocated = float(balance_allocated)  # Convert balance to float
    except:
        return jsonify({"error": "Invalid input format"}), 400

    # Check if user exists
    user = mongo.db.users.find_one({"_id": user_object_id})
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Ensure user has connected exchange credentials
    required_fields = ["exchange", "api_key", "secret_key", "secret_phrase"]
    if any(field not in user or user[field] is None for field in required_fields):
        return jsonify({"error": "First connect exchange"}), 400

    # Fetch user's current USDT balance from OKX
    client = OKXClient(
        api_key=user["api_key"],
        api_secret=user["secret_key"],
        passphrase=user["secret_phrase"]
    )

    balance_data = client.get_balance()
    if not balance_data or "error" in balance_data:
        return jsonify({"error": "Failed to fetch balance from exchange"}), 500

    usdt_balance = next(
        (item["eq"] for item in balance_data[0]["details"] if item["ccy"] == "USDT"),
        "0"  # Default to "0" if USDT is not found
    )
    usdt_balance = float(usdt_balance)

    # Get user's currently allocated balance
    current_allocated_balance = user.get("Balance", 0)

    # Check if the user has enough balance to allocate
    required_balance = current_allocated_balance + balance_allocated
    if required_balance > usdt_balance:
        shortfall = required_balance - usdt_balance
        return jsonify({
            "usdt_balance": usdt_balance,
            "currently_allocated": current_allocated_balance,
            "requested_allocation": balance_allocated,
            "shortfall": shortfall,
            "error": f"Your total allocated balance ({current_allocated_balance} USDT) + requested allocation ({balance_allocated} USDT) exceeds your available balance ({usdt_balance} USDT). You need at least {shortfall} more USDT."
        }), 400

    # Update user's allocated balance
    new_balance = current_allocated_balance + balance_allocated
    mongo.db.users.update_one({"_id": user_object_id}, {"$set": {"Balance": new_balance}})

    # Create subscription
    subscription_id = Subscription.create_subscription(bot_name, user_object_id, balance_allocated)

    return jsonify({"message": "Subscription created", "subscription_id": str(subscription_id)}), 201

@subscription_bp.route("/delete/<user_id>/<bot_name>", methods=["DELETE"])
def delete_subscription(user_id, bot_name):
    try:
        user_object_id = ObjectId(user_id)
    except:
        return jsonify({"error": "Invalid user_id format"}), 400

    # Find the subscription to get the allocated balance
    subscription = mongo.db.subscriptions.find_one({"user_id": user_object_id, "bot_name": bot_name})

    if not subscription:
        return jsonify({"error": "No subscription found for this user and bot"}), 404

    balance_allocated = subscription.get("balance_allocated", 0)

    # Find the user to update balance
    user = mongo.db.users.find_one({"_id": user_object_id})
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Deduct balance from user
    new_balance = max(user.get("Balance", 0) - balance_allocated, 0)  # Ensure balance never goes negative
    mongo.db.users.update_one({"_id": user_object_id}, {"$set": {"Balance": new_balance}})

    # Delete the subscription
    result = mongo.db.subscriptions.delete_one({"user_id": user_object_id, "bot_name": bot_name})

    return jsonify({"message": "Subscription deleted"}), 200

# Check if user is subscribed to a specific bot
@subscription_bp.route("/status", methods=["POST"])
def check_subscription_status():
    data = request.get_json()  # Get data from the request body
    user_id = data.get("user_id")
    bot_name = data.get("bot_name")

    if not all([user_id, bot_name]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user_object_id = ObjectId(user_id)
    except:
        return jsonify({"error": "Invalid user_id format"}), 400

    # Query the database to check if the user is subscribed to the bot
    subscription = mongo.db.subscriptions.find_one({"user_id": user_object_id, "bot_name": bot_name})

    if subscription:
        return jsonify({"subscribed": True}), 200
    else:
        return jsonify({"subscribed": False}), 200
