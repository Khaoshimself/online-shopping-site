import os

try:
    from pymongo import MongoClient
    from bson import ObjectId
except Exception:
    MongoClient = None  # pymongo not installed yet or not needed
    ObjectId = None

MONGO_URI = (
    f"mongodb://{os.environ.get('CONFIG_MONGODB_USERNAME','devroot')}:"
    f"{os.environ.get('CONFIG_MONGODB_PASSWORD','devroot')}@"
    f"{os.environ.get('CONFIG_MONGODB_IP','127.0.0.1')}:"
    f"{os.environ.get('CONFIG_MONGODB_PORT','27017')}"
)
db = None  # stays None until we init (or if Mongo isn't running)


def init_db() -> bool:
    """Try to connect to Mongo. Returns True if connected."""
    global db
    if MongoClient is None:
        print("pymongo not installed")
        db = None
        return False
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        # Optional ping: client.admin.command("ping")
        db = client[os.environ.get("CONFIG_MONGODB_DATABASE", "project")]

        print(f"{client.HOST}:{db.client.PORT}")
        print(client.list_database_names())
        print(db.list_collection_names())
        return True
    except Exception as e:
        db = None
        print(e)
        return False


def get_items(limit: int = 100):
    """Return list of items from the database (as dictionaries)."""
    if db is None:
        return [] # return nothing if db isn't initialized
    try:
        cursor = db["items"].find().limit(limit)
        items = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON/templates
            items.append(doc)
        return items
    except Exception as e:
        print(e)
        return []


# this function creates a new mongoDB item
# it follows the ItemModel structure from usermodel.py
def create_item(name, description, price_cents, category, stock, image_urls, tags):
    """Create a new item in the database. Returns inserted_id if successful, None otherwise."""
    # the fields are:
    # _id: ObjectId
    # name: str
    # description: str
    # price_cents: int
    # category: ItemCategory
    # stock: int
    # image_urls: List[str]
    # tags: List[str]
    if db is None:
        print("Database not initialized")
        return None
    try:
        item = {
            "name": name,
            "description": description,
            "price_cents": price_cents,
            "category": category,
            "stock": stock,
            "image_urls": image_urls,
            "tags": tags
        }
        result = db["items"].insert_one(item)
        return result.inserted_id
    except Exception as e:
        print(e)

def update_item(item_id, update_fields):
    """Update an existing item in the database. Returns True if successful, False otherwise."""
    if db is None:
        print("Database not initialized")
        return False
    try:
        result = db["items"].update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_fields}
        )
        return result.modified_count > 0
    except Exception as e:
        print(e)
        return False

"""
from bson import ObjectId
import pymongo
from os import environ
from typing import Any, Dict
from pymongo.collection import Collection
from pymongo.database import Database
from app.records.keymodel import Key
from app.records.usermodel import UserModel,UserType


class db:
    client: pymongo.MongoClient[Dict[str, Any]] = pymongo.MongoClient(
        f"mongodb://{environ.get("CONFIG_MONGODB_USERNAME","devroot")}:{environ.get("CONFIG_MONGODB_PASSWORD","devroot")}@{environ.get("CONFIG_MONGODB_IP","127.0.0.1")}:{environ.get("CONFIG_MONGODB_PORT","27017")}"
    )
    database: Database = client[environ.get("CONFIG_MONGODB_DATABASE", "project")]
    users: Collection[UserModel] = database["users"]
    keys: Collection[Key] = database["keys"]


print(f"{db.client.HOST}:{db.client.PORT}")
print(db.client.list_database_names())
print(db.database.list_collection_names())

"""
