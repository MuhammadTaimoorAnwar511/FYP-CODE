from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from bson.objectid import ObjectId
from app import mongo

profile_bp = Blueprint("profile", __name__)
CORS(profile_bp) 

@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    email = get_jwt_identity()  # Extract the email from the JWT token
    user = mongo.db.users.find_one({"email": email}, {"password": False})  # Only exclude password

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Convert ObjectId to string for JSON serialization
    user["_id"] = str(user["_id"])

    return jsonify(user), 200
