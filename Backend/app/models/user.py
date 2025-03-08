from app import mongo

class User:
    @staticmethod
    def find_by_username_or_email(username, email):
        return mongo.db.users.find_one({"$or": [{"username": username}, {"email": email}]})

    @staticmethod
    def create_user(username, email, country, hashed_password):
        return mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "country": country,
            "password": hashed_password,
            "Balance": 0,
            "exchange": None,
            "api_key": None,
            "secret_key": None,
            "secret_phrase": None
        })

