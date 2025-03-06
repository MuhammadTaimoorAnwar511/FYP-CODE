import os
from dotenv import load_dotenv
from app import app

# Load environment variables
load_dotenv()

# Get port from .env or default to 5000
port = int(os.getenv("PORT"))

if __name__ == "__main__":
    app.run(debug=True, port=port)
