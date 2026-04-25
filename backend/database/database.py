import os
from pymongo import MongoClient

def get_db():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = MongoClient(mongo_url)
    return client.discord_bot_feedback