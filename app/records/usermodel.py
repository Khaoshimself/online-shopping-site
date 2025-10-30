from typing import TypedDict, List
from enum import StrEnum

from bson import ObjectId


class UserType(StrEnum):
    ADMIN = "admin"
    USER = "user"


class CartItem(TypedDict):
    """Reference Items with a quantity"""

    item_id: ObjectId
    quantity: int


class UserModel(TypedDict):
    """Class for users in the database"""

    _id: ObjectId
    name: str
    password_hash: str
    permissions: UserType
    activated: bool
    auth_token: str
    cart: List[CartItem]
