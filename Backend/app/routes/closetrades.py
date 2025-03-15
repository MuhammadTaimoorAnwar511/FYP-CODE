import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import CORS

from pymongo import MongoClient
from bson import ObjectId

import requests
import time
import hmac
import hashlib
import json
import math
from datetime import datetime, timezone

# Flask Blueprint
closetrades_bp = Blueprint('closetrades', __name__)
CORS(closetrades_bp)

@closetrades_bp.route('/close_trade', methods=['POST'])
def close_trade():
    return jsonify({"message": "User trade close successfully"}), 200