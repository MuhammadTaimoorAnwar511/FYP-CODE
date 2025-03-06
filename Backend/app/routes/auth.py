from flask import Blueprint, request, jsonify
from app import bcrypt, mongo
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

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

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user_data = {
        "username": username,
        "email": email,
        "country": country,
        "password": hashed_password
    }

    mongo.db.users.insert_one(user_data)

    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Ensure both email and password are provided
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Find user by email only
    user = mongo.db.users.find_one({"email": email})

    # Check if user exists and verify password
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate JWT token using email as identity
    access_token = create_access_token(identity=email)

    return jsonify({
        "access_token": access_token
        # "user": {
        #     "username": user["username"],
        #     "email": user["email"],
        #     "country": user["country"]
        # }
    }), 200
