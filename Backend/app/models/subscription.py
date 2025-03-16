from app import mongo
from bson import ObjectId

class Subscription:
    @staticmethod
    def find_by_userid(user_id):
        return mongo.db.subscriptions.find_one({"user_id": user_id})

    @staticmethod
    def create_subscription(bot_name, user_id, bot_initial_balance,symbol,bot_current_balance):
        result = mongo.db.subscriptions.insert_one({
            "bot_name": bot_name,
            "symbol": symbol,
            "user_id": user_id,
            "bot_initial_balance": bot_initial_balance,
            "bot_current_balance": bot_current_balance
        })
        return str(result.inserted_id)