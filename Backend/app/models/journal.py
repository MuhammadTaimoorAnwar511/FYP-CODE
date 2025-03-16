from app import mongo

# Define the default user document structure
user_data = {
    "User_Id": "",
    "Total_Signals": 0,
    "Signals_Closed_in_Profit": 0,
    "Signals_Closed_in_Loss": 0,
    "Current_Running_Signals": 0,
    "Avg_Profit_USDT": 0.0,
    "Avg_Loss_USDT": 0.0
}

# Insert into MongoDB
mongo.db.users.insert_one(user_data)
