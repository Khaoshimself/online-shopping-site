import os

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None  # pymongo not installed yet or not needed

MONGO_URI = (
    f"mongodb://{os.environ.get("CONFIG_MONGODB_USERNAME","devroot")}:"
    f"{os.environ.get("CONFIG_MONGODB_PASSWORD","devroot")}@"
    f"{os.environ.get("CONFIG_MONGODB_IP","127.0.0.1")}:"
    f"{os.environ.get("CONFIG_MONGODB_PORT","27017")}"
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
