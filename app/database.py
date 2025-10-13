from bson import ObjectId
import pymongo
from os import environ
from typing import Any, Dict
from pymongo.collection import Collection
from pymongo.database import Database
from records.keys import Key
from records.users import User, UserType


class db:
    client: pymongo.MongoClient[Dict[str, Any]] = pymongo.MongoClient(
        f"mongodb://{environ.get("CONFIG_MONGODB_USERNAME","devroot")}:{environ.get("CONFIG_MONGODB_PASSWORD","devroot")}@{environ.get("CONFIG_MONGODB_IP","127.0.0.1")}:{environ.get("CONFIG_MONGODB_PORT","27017")}"
    )
    database: Database = client[environ.get("CONFIG_MONGODB_DATABASE", "project")]
    users: Collection[User] = database["users"]
    keys: Collection[Key] = database["keys"]


print(f"{db.client.HOST}:{db.client.PORT}")
print(db.client.list_database_names())
print(db.database.list_collection_names())
