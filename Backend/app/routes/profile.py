from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from flask_cors import CORS

profile_bp = Blueprint("profile", __name__)
CORS(profile_bp) 

@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    email = get_jwt_identity()  # Extract the email from the JWT token
    user = mongo.db.users.find_one({"email": email}, {"_id": 0, "password": 0})  # Exclude password and _id

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user), 200  # Return user details
