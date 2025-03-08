from flask import Blueprint, request, jsonify
from app.models.subscription import Subscription
from bson import ObjectId
from app import mongo
from flask_cors import CORS

subscription_bp = Blueprint("subscription", __name__)
CORS(subscription_bp) 
from flask import request, jsonify
from bson import ObjectId

@subscription_bp.route("/create", methods=["POST"])
def create_subscription():
    data = request.get_json()
    bot_name = data.get("bot_name")
    user_id = data.get("user_id")  # This is a string from the request
    balance_allocated = data.get("balance_allocated")

    if not all([bot_name, user_id, balance_allocated]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Convert user_id string to ObjectId
        user_object_id = ObjectId(user_id)
    except:
        return jsonify({"error": "Invalid user_id format"}), 400

    # Check if the user exists in the users collection
    user = mongo.db.users.find_one({"_id": user_object_id})
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Check if the required fields are present and not null for the user
    if any(field not in user or user[field] is None for field in ["exchange", "api_key", "secret_key", "secret_phrase"]):
        return jsonify({"error": "First Connect exchange"}), 400

    # Create subscription if all conditions are met
    subscription_id = Subscription.create_subscription(bot_name, user_object_id, balance_allocated)
    
    return jsonify({"message": "Subscription created", "subscription_id": str(subscription_id)}), 201

@subscription_bp.route("/delete/<user_id>/<bot_name>", methods=["DELETE"])
def delete_subscription(user_id, bot_name):
    try:
        user_object_id = ObjectId(user_id)
    except:
        return jsonify({"error": "Invalid user_id format"}), 400

    # Delete the subscription for the given user ID and bot name
    result = mongo.db.subscriptions.delete_one({"user_id": user_object_id, "bot_name": bot_name})

    if result.deleted_count == 0:
        return jsonify({"error": "No subscription found for this user and bot"}), 404

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
