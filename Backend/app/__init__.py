from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI") + os.getenv("MONGO_DB")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Import routes
from app.routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix="/auth")
from app.routes.profile import profile_bp
app.register_blueprint(profile_bp, url_prefix="/user")
from app.routes.exchange import exchange_bp
app.register_blueprint(exchange_bp, url_prefix="/exchange")
from app.routes.subscription import subscription_bp
app.register_blueprint(subscription_bp, url_prefix="/subscription") 
from app.routes.botdetail import botdetail_bp
app.register_blueprint(botdetail_bp, url_prefix="/bot") 

@app.route("/")
def home():
    return {"message": "Flask Backend is Running!"}
