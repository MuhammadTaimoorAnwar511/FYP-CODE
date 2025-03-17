from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app import mongo

botdetail_bp = Blueprint("botdetail", __name__)
CORS(botdetail_bp) 

@botdetail_bp.route("/detail", methods=["GET"])
def getbotdetail():
    botname = request.args.get("botname")  
    if not botname:
        return jsonify({"error": "botname parameter is required"}), 400

    collection_name = f"Analysis_{botname}"  # Append 'Analysis_' prefix
    collection = mongo.db[collection_name]  # Get collection from MongoDB

    # Fetch only required fields
    data = collection.find_one({}, {
        "_id": 0,
        "Total Trades": 1,
        "Losing Trades": 1,
        "Winning Trades": 1,
        "Max Losing Streak": 1,
        "Max Winning Streak": 1,
        "Win Rate (%)": 1,
        "ROI (%)":1
    })  

    if not data:
        return jsonify({"error": f"No data found for {botname}"}), 404

    return jsonify(data), 200
