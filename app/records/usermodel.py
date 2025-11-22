from typing import TypedDict, List
from enum import StrEnum

from bson import ObjectId


class UserType(StrEnum):
    ADMIN = "admin"
    USER = "user"


class CartItem(TypedDict):
    """Reference Items with a quantity (stored in DB)."""

    item_id: ObjectId
    quantity: int


# separate version including full item details (uses ItemModel)
class CartItemFull(CartItem, total=False):
    item: "ItemModel"


class UserModel(TypedDict):
    """Class for users in the database"""

    _id: ObjectId
    name: str
    password_hash: str
    permissions: UserType
    activated: bool
    auth_token: str
    cart: List[CartItem]


class ItemCategory(StrEnum):
    PRODUCE = "produce"
    DAIRY = "dairy"
    BAKERY = "bakery"
    FROZEN = "frozen"
    PANTRY = "pantry"
    DELI = "deli"
    MEAT = "meat"
    SEAFOOD = "seafood"
    DRUGSTORE = "drugstore"
    OTHER = "other"


class ItemModel(TypedDict, total=False):
    """Grocery store item stored in the DB. price is stored in cents to avoid floats."""

    _id: ObjectId
    name: str
    description: str
    price_cents: int
    category: ItemCategory
    stock: int
    image_urls: List[str]
    tags: List[str]
    # on_sale: bool
    # sale_price_cents: int
    # created_at: datetime
    # updated_at: datetime # maybe implement these later

