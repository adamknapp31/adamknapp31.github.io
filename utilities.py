import os
from pymongo import MongoClient

DB_NAME = "movie_recommendation_system"

# Variables for MongoDB connection
SERVER = "127.0.0.1:27017"
DATABASE_NAME = "movie_recommendation_system"

def setup_mongo_connection():
    # Load environment variables from .env file
    # (Ensure you have a method or package to do this if needed)

    # Retrieve MongoDB credentials and server details from environment variables
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')

    # Construct MongoDB URI based on the presence of a username and password
    if MONGO_USER and MONGO_PASSWORD:
        mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{SERVER}/{DATABASE_NAME}?authSource=admin"
    else:
        mongo_uri = f"mongodb://{SERVER}/{DATABASE_NAME}"

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Attempt to fetch server information as a connection check
        return client
    except Exception as e:
        print(f"Failed to connect to MongoDB. Error: {e}")
        return None
