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
