import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
journal_collection = db['journals']

# Flask Blueprint setup
journal_bp = Blueprint("journal", __name__)
CORS(journal_bp)

@journal_bp.route("/data", methods=["POST"])
@jwt_required()
def journal():
    try:
        # Get user_id from JWT (already set as _id during login)
        user_id = get_jwt_identity()

        # Fetch user by _id
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        user_balance = user.get("user_current_balance", 0.0)

        # Fetch journal data
        journal_data = journal_collection.find_one({"User_Id": str(user_id)})

        if journal_data:
            response = {
                "success": True,
                "message": "Journal data fetched successfully",
                "user": {
                    "user_id": str(user_id),
                    "current_balance": user_balance
                },
                "journal": {
                    "total_signals": journal_data.get("Total_Signals", 0),
                    "signals_closed_in_profit": journal_data.get("Signals_Closed_in_Profit", 0),
                    "signals_closed_in_loss": journal_data.get("Signals_Closed_in_Loss", 0),
                    "current_running_signals": journal_data.get("Current_Running_Signals", 0),
                    "average_profit_usdt": journal_data.get("Avg_Profit_USDT", 0.0),
                    "average_loss_usdt": journal_data.get("Avg_Loss_USDT", 0.0)
                }
            }
            return jsonify(response), 200
        else:
            return jsonify({
                "success": False,
                "message": "No journal data found for the user",
                "user": {
                    "user_id": str(user_id),
                    "current_balance": user_balance
                }
            }), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@journal_bp.route("/opentrades", methods=["POST"])
@jwt_required()
def opentrades():
    try:
        # Step 1: Extract user_id from JWT token
        user_id = get_jwt_identity()

        # Step 2: Find user info using _id
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Step 3: Determine user's trade collection name
        user_trade_collection = db[f"user_{user_id}"]

        # Step 4: Fetch trades with status OPEN
        open_trades_cursor = user_trade_collection.find({"status": "OPEN"})
        open_trades = []
        for trade in open_trades_cursor:
            trade["_id"] = str(trade["_id"])  # Convert ObjectId to string
            open_trades.append(trade)

        # Step 5: Build response
        response = {
            "success": True,
            "message": "Open trades fetched successfully",
            "user": {
                "user_id": str(user_id),
                "email": user.get("email")
            },
            "open_trades": open_trades
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@journal_bp.route("/closetrades", methods=["POST"])
@jwt_required()
def closetrades():
    try:
        # Step 1: Extract user_id from JWT token
        user_id = get_jwt_identity()

        # Step 2: Fetch user info using user_id
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Step 3: Get user's trades collection
        user_trade_collection = db[f"user_{user_id}"]

        # Step 4: Query for closed trades (TP or SL), sorted by exit_time descending
        closed_trades_cursor = user_trade_collection.find(
            {"status": {"$in": ["TP", "SL"]}}
        ).sort("exit_time", -1)

        closed_trades = []
        for trade in closed_trades_cursor:
            trade["_id"] = str(trade["_id"])
            closed_trades.append(trade)

        # Step 5: Build response
        response = {
            "success": True,
            "message": "Closed trades fetched successfully",
            "user": {
                "user_id": str(user_id),
                "email": user.get("email")
            },
            "closed_trades": closed_trades
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@journal_bp.route("/currentbalance", methods=["POST"])
@jwt_required()
def currentbalance():
    try:
        # Step 1: Extract user_id from JWT token
        user_id = get_jwt_identity()

        # Step 2: Find user info using _id
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Step 3: Retrieve the user's current balance and allocated balance
        balance = user.get("user_current_balance", 0)
        balance_allocated_to_bots = user.get("balance_allocated_to_bots", 0)
        
        # Determine the color based on the comparison
        if balance < balance_allocated_to_bots:
            color = "red"
        else:
            color = "green"
        
        # Return the balance and color
        return jsonify({
            "success": True,
            "user_current_balance": balance,
            "color": color
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
        