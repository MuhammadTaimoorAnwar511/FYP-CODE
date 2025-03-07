from app import mongo
from bson import ObjectId

class Subscription:
    @staticmethod
    def find_by_userid(user_id):
        return mongo.db.subscriptions.find_one({"user_id": user_id})

    @staticmethod
    def create_subscription(bot_name, user_id, balance_allocated):
        result = mongo.db.subscriptions.insert_one({
            "bot_name": bot_name,
            "user_id": user_id,
            "balance_allocated": balance_allocated
        })
        return str(result.inserted_id)
