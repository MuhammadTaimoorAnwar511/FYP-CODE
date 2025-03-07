from flask import Blueprint, request, jsonify
from app.models.subscription import Subscription
from bson import ObjectId
from app import mongo

subscription_bp = Blueprint("subscription", __name__)

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

    # Create subscription if user exists
    subscription_id = Subscription.create_subscription(bot_name, user_object_id, balance_allocated)
    
    return jsonify({"message": "Subscription created", "subscription_id": str(subscription_id)}), 201


