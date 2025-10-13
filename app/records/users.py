from bson.objectid import ObjectId
from typing import List, TypedDict
from enum import StrEnum

from database import db
from argon2 import PasswordHasher


class UserType(StrEnum):
    ADMIN = "admin"
    USER = "user"


class CartItem(TypedDict):
    """Reference Items with a quantity"""

    item_id: ObjectId
    quantity: int


class User(TypedDict):
    """Class for users in the database"""

    name: str
    password_hash: str
    permissions: UserType
    cart: List[CartItem]


ph = PasswordHasher()


def db_user_create(name: str, password: str) -> ObjectId | None:
    if db.users.find_one({"name": name}) is not None:
        return None
    hash = ph.hash(password)
    user = User(name=name, password_hash=hash, permissions=UserType.USER, cart=[])
    resp = db.users.insert_one(user)
    return resp.inserted_id


if db.users.find_one({"name": "admin"}) is None:
    id = db_user_create("admin", "admin")
    db.users.update_one({"_id": id}, {"$set": {"permissions": UserType.ADMIN}})
