from flask import Blueprint, request, jsonify
from app.models.subscription import Subscription
from bson import ObjectId
from app import mongo
from flask_cors import CORS
from flask import Blueprint,request, jsonify
from urllib.parse import urljoin
from datetime import datetime, UTC
from bson import ObjectId
import hmac
import requests
import hashlib
import base64


subscription_bp = Blueprint("subscription", __name__)
CORS(subscription_bp) 

###
@subscription_bp.route("/create", methods=["POST"])
def create_subscription():
    data = request.get_json()
    bot_name = data.get("bot_name")
    user_id = data.get("user_id")
    balance_allocated = data.get("balance_allocated")
    
    if not bot_name or not user_id or not balance_allocated:
        return jsonify({"error": "Missing required fields"}), 400
    
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if required fields are present and not null
    if not all([user.get("exchange"), user.get("api_key"), user.get("secret_key")]):
        return jsonify({"error": "User must have exchange, api_key, and secret_key set"}), 400
    
    # Update user balance
    new_balance = user.get("Balance", 0) + balance_allocated
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"Balance": new_balance}})
    
        # Generate symbol by replacing "_" with "/"
    symbol = bot_name.replace("_", "/")

    subscription_id = mongo.db.subscriptions.insert_one({
        "bot_name": bot_name,
        "symbol": symbol,
        "user_id": user_id,
        "balance_allocated": balance_allocated
    }).inserted_id
    
    return jsonify({"message": "Subscription created successfully", "subscription_id": str(subscription_id)}), 201

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
    new_balance = max(user.get("Balance", 0) - balance_allocated, 0)  # Ensure balance never goes negative
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"Balance": new_balance}})

    # Delete the subscription
    result = mongo.db.subscriptions.delete_one({"user_id": user_id, "bot_name": bot_name})

    return jsonify({"message": "Subscription deleted"}), 200
