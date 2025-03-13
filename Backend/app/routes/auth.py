from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app import bcrypt, mongo
from flask_jwt_extended import create_access_token
from datetime import timedelta
import re

auth_bp = Blueprint("auth", __name__)
CORS(auth_bp) 

# Password validation function
def is_strong_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character"
    return None  # Valid password

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    country = data.get("country")
    password = data.get("password")

    if not username or not email or not country or not password:
        return jsonify({"message": "All fields are required"}), 400

    if mongo.db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
        return jsonify({"message": "Username or Email already exists"}), 400

    password_error = is_strong_password(password)
    if password_error:
        return jsonify({"message": password_error}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user_data = {
        "username": username,
        "email": email,
        "country": country,
        "password": hashed_password,
        "Bots_Balance": 0,
        "User_Balance": 0,
        "exchange": None,
        "api_key": None,
        "secret_key": None,
    }

    mongo.db.users.insert_one(user_data)

    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = mongo.db.users.find_one({"email": email})

    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Set token expiry to 1 day explicitly
    access_token = create_access_token(identity=email, expires_delta=timedelta(days=1))

    return jsonify({"access_token": access_token}), 200
