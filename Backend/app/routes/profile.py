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
    user_id = get_jwt_identity() 

    # Convert user_id string to ObjectId for MongoDB query
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)}, {"password": False})

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Convert ObjectId to string for JSON response
    user["_id"] = str(user["_id"])

    return jsonify(user), 200