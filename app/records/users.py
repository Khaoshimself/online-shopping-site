import argon2
from bson.objectid import ObjectId
from uuid import uuid4
from typing import Optional, List

from pymongo.collection import Collection
from flask_login import UserMixin
from argon2 import PasswordHasher

# from _ import _ creates a copy of the object, so init_db doesn't work like that
import app.database

from app.records.usermodel import UserModel, UserType, CartItem

ph = PasswordHasher()

users: Collection[UserModel]


def _get_db():
    "Return usable db or None if Mongo isn't initialized"
    # If you have an init_db() helper and db is None, try to initialize once.
    if app.database.db is None and app.database.init_db:
        try:
            app.database.init_db()
        except Exception:
            pass
    return app.database.db


def get_users() -> Optional[Collection[UserModel]]:
    if _get_db() is None:
        return None
    users = app.database.db["users"]
    return users


def db_user_create(name: str, password: str) -> Optional[ObjectId]:

    u = get_users()
    if u is None:
        return None

    if u.find_one({"name": name}) is not None:
        print(f"user {name} exists")
        return None
    try:
        pw_hash = ph.hash(password)
        user = UserModel(
            name=name,
            password_hash=pw_hash,
            permissions=UserType.USER,
            activated=True,
            cart=[],
        )
        resp = u.insert_one(user)
        return resp.inserted_id
    except Exception as e:
        print(e)
        return None


def seed_admin() -> None:
    """Call this only when Mongo is running (e.g., a one-time CLI/route)."""
    u = get_users()
    if u is None:
        print("DB not available; skip admin seed.")
        return
    doc = u.find_one({"name": "admin"})
    if doc is None:
        _id = db_user_create("admin", "admin")
        if _id:
            u.update_one(
                {"_id": _id},
                {"$set": {"permissions": UserType.ADMIN}},
            )


class User(UserMixin):
    model: UserModel

    def __init__(self, model: UserModel):
        self.model = model

    # Flask-Login expects properties, not class-level flags
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_active(self) -> bool:
        return bool(self.model.get("activated", False))

    def get_id(self) -> str:
        return str(self.model["_id"])

    def get_name(self) -> str:
        return self.model["name"]

    def get_permissions(self) -> UserType:
        return self.model["permissions"]

    def get_cart(self) -> List[CartItem]:
        return self.model["cart"]
    def update_cart(self,new_cart: List[CartItem] ) -> bool:
        u = get_users()
        if u is None:
            return False
        u.update_one({"_id":self.model["_id"]}, {"$set": {"cart": new_cart}})
        return True

    def new_auth_token(self) -> Optional[str]:
        u = get_users()
        if u is None:
            return None
        token = "auth_" + str(uuid4())
        u.update_one({"_id": self.model["_id"]}, {"$set": {"auth_token": token}})
        return token

    def check_password(self, password: str) -> bool:
        try:
            return ph.verify(self.model["password_hash"], password)
        except argon2.exceptions.VerificationError:
            return False

    def update_password(self, password: str) -> None:
        u = get_users()
        if u is None:
            return None

        u.update_one(
            {"_id": self.model["_id"]},
            {"$set": {"password_hash": ph.hash(password)}},
        )

    def update_username(self, username: str) -> None:
        u = get_users()
        if u is None:
            return None

        u.update_one({"_id": self.model["_id"]}, {"$set": {"name": username}})

    def delete_user(self) -> None:
        u = get_users()
        if u is None:
            return None

        u.delete_one({"_id": self.model["_id"]})


def db_user_verify_login(name: str, password: str) -> Optional[User]:
    u = get_users()
    if u is None:
        return None

    user = u.find_one({"name": name})
    if user is not None:
        try:
            if ph.verify(user["password_hash"], password):
                ret = User(user)
                ret.new_auth_token()  # optional
                return ret
        except argon2.exceptions.VerificationError:
            return None
    return None


# Was getting DB issues so I commented it out
"""
import argon2
from bson.objectid import ObjectId
from uuid import uuid4

from flask_login import UserMixin

from app.database import db
from argon2 import PasswordHasher

from app.records.usermodel import UserModel, UserType

ph = PasswordHasher()


def db_user_create(name: str, password: str) -> ObjectId | None:
    if db.users.find_one({"name": name}) is not None:
        return None
    hash = ph.hash(password)
    user = UserModel(
        name=name,
        password_hash=hash,
        permissions=UserType.USER,
        activated=True,
        cart=[],
    )
    resp = db.users.insert_one(user)
    return resp.inserted_id


if db.users.find_one({"name": "admin"}) is None:
    id = db_user_create("admin", "admin")
    db.users.update_one({"_id": id}, {"$set": {"permissions": UserType.ADMIN}})


class User(UserMixin):
    model: UserModel

    def __init__(self, model: UserModel):
        self.model: UserModel = model
        self.is_active = self.model['activated']

    is_authenticated = True
    is_anonymous = False
    is_active = False

    def get_id(self):
        return str(self.model["_id"])

    def get_name(self):
        return self.model["name"]

    def get_permissions(self):
        return self.model["permissions"]

    def get_cart(self):
        return self.model["cart"]

    def new_auth_token(self) -> str:
        token = 'auth_' + str(uuid4())
        db.users.update_one({"_id": self.model["_id"]}, {"$set": {"auth_token": token}})
        return token

    def check_password(self, password: str) -> bool:
        try:
            return ph.verify(self.model["password_hash"],password)
        except argon2.exceptions.VerificationError:
            return False

    def update_password(self, password: str):
        db.users.update_one({"_id": self.model["_id"]},{"$set": {"password_hash": ph.hash(password)}})

    def update_username(self, username: str):
        db.users.update_one({"_id": self.model["_id"]},{"$set": {"name": username}})

    def delete_user(self):
        db.users.delete_one({"_id": self.model["_id"]})


def db_user_verify_login(name: str, password: str) -> User | None:
    user = db.users.find_one({"name": name})
    if user is not None and ph.verify(user["password_hash"], password):
        ret = User(user)
        ret.new_auth_token()
        return ret

    return None
"""
