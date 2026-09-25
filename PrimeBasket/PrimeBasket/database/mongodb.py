"""MongoDB connection, configured from the .env file (see PrimeBasket/settings.py,
which loads that file before this module is ever imported).

Previously this connected with hardcoded localhost:27017 values and no server
selection timeout, so MONGODB_URI / DATABASE_NAME / MONGODB_MAX_POOL_SIZE /
MONGODB_SERVER_SELECTION_TIMEOUT_MS in .env had no effect, and a request would
hang for pymongo's ~30s default instead of failing fast when MongoDB is down.
"""

import os

import pymongo

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "primebasket")
MAX_POOL_SIZE = int(os.environ.get("MONGODB_MAX_POOL_SIZE", "10"))
SERVER_SELECTION_TIMEOUT_MS = int(os.environ.get("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "3000"))

client = pymongo.MongoClient(
    MONGODB_URI,
    maxPoolSize=MAX_POOL_SIZE,
    serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
)

db = client[DATABASE_NAME]

users_collection = db["users"]
wishlist_collection = db["wishlist"]
cart_collection = db["cart"]
orders_collection = db["orders"]
reviews_collection = db["reviews"]
messages_collection = db["messages"]
newsletter_collection = db["newsletter"]
products_collection = db["products"]
categories_collection = db["categories"]
admins_collection = db["admins"]
