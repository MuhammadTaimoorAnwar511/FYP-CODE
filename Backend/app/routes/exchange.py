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

exchange_bp = Blueprint('exchange', __name__)
CORS(exchange_bp) 

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

    def test_connection(self):
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
                return True
            return False
        except:
            return False

@exchange_bp.route('/TestConnection', methods=['POST'])
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
        if client.test_connection():
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@exchange_bp.route("/SaveConnection", methods=["PUT"])
@jwt_required()
def update_exchange():
    email = get_jwt_identity()  # Extract the email from the JWT token
    user = mongo.db.users.find_one({"email": email})
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json  # Get JSON data from the request body
    
    # Extract API credentials
    api_key = data.get("apiKey")
    api_secret = data.get("apiSecret")
    passphrase = data.get("phrase")

    if not all([api_key, api_secret, passphrase]):
        return jsonify({"message": "Missing required API credentials"}), 400

    # Create client instance and test connection
    client = OKXClient(api_key, api_secret, passphrase)
    if not client.test_connection():
        return jsonify({"message": "API connection test failed"}), 400

    # If test is successful, save connection
    update_data = {
        "exchange": data.get("selectedExchange"),
        "api_key": api_key,
        "secret_key": api_secret,
        "secret_phrase": passphrase,
    }
    
    mongo.db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_data})
    
    return jsonify({"message": "Exchange details updated successfully"}), 200

@exchange_bp.route('/DeleteConnection', methods=['DELETE'])
@jwt_required()
def DeleteConnection():
    try:
        user_email = get_jwt_identity()  # Extract user email from JWT token
        
        # Find user by email
        user = mongo.db.users.find_one({"email": user_email})
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Check if the user is subscribed to any bot
        active_subscriptions = list(mongo.db.subscriptions.find({"user_id": user["_id"]}))
        if active_subscriptions:
            subscribed_bots = [sub["bot_name"] for sub in active_subscriptions]
            return jsonify({
                "error": "Unsubscribe bots first.",
                "subscribed_bots": subscribed_bots
            }), 400

        # Update the user’s exchange connection fields to null
        update_result = mongo.db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "exchange": None,
                "api_key": None,
                "secret_key": None,
                "secret_phrase": None
            }}
        )

        return jsonify({"message": "Exchange connection deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
