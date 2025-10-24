import argon2
from bson.objectid import ObjectId
from uuid import uuid4
from typing import Optional

from flask_login import UserMixin
from argon2 import PasswordHasher

# Import db and optional init helper
from app.database import db as _db
try:
    from app.database import init_db  # if you added it; otherwise ignore
except Exception:
    init_db = None  # type: ignore

from app.records.usermodel import UserModel, UserType

ph = PasswordHasher()


def _get_db():
    "Return usable db or None if Mongo isn't initialized"
    # If you have an init_db() helper and db is None, try to initialize once.
    if _db is None and init_db:
        try:
            init_db()
        except Exception:
            pass
    return _db


def db_user_create(name: str, password: str) -> Optional[ObjectId]:
    d = _get_db()
    if d is None:
        # DB not available; skip silently or raise RuntimeError
        return None
    if d.users.find_one({"name": name}) is not None:
        return None
    pw_hash = ph.hash(password)
    user = UserModel(
        name=name,
        password_hash=pw_hash,
        permissions=UserType.USER,
        activated=True,
        cart=[],
    )
    resp = d.users.insert_one(user)
    return resp.inserted_id


def seed_admin() -> None:
    """Call this only when Mongo is running (e.g., a one-time CLI/route)."""
    d = _get_db()
    if d is None:
        print("DB not available; skip admin seed.")
        return
    doc = d.users.find_one({"name": "admin"})
    if doc is None:
        _id = db_user_create("admin", "admin")
        if _id:
            d.users.update_one(
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

    def get_permissions(self):
        return self.model["permissions"]

    def get_cart(self):
        return self.model["cart"]

    def new_auth_token(self) -> Optional[str]:
        d = _get_db()
        if d is None:
            return None
        token = "auth_" + str(uuid4())
        d.users.update_one({"_id": self.model["_id"]}, {"$set": {"auth_token": token}})
        return token

    def check_password(self, password: str) -> bool:
        try:
            return ph.verify(self.model["password_hash"], password)
        except argon2.exceptions.VerificationError:
            return False

    def update_password(self, password: str) -> None:
        d = _get_db()
        if d is None:
            return
        d.users.update_one(
            {"_id": self.model["_id"]},
            {"$set": {"password_hash": ph.hash(password)}},
        )

    def update_username(self, username: str) -> None:
        d = _get_db()
        if d is None:
            return
        d.users.update_one({"_id": self.model["_id"]}, {"$set": {"name": username}})

    def delete_user(self) -> None:
        d = _get_db()
        if d is None:
            return
        d.users.delete_one({"_id": self.model["_id"]})


def db_user_verify_login(name: str, password: str) -> Optional[User]:
    d = _get_db()
    if d is None:
        return None
    user = d.users.find_one({"name": name})
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