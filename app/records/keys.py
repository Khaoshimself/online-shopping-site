from typing import TypedDict
from ecdsa import SigningKey, VerifyingKey, NIST384p

from database import db


class Key(TypedDict):
    name: str
    private: str
    public: str


def db_key_create(name: str) -> Key | None:
    if db.keys.find_one({"name": name}) is not None:
        return None
    sk: SigningKey = SigningKey.generate(curve=NIST384p)
    vk: VerifyingKey = sk.verifying_key
    vk.precompute()
    key = Key(
        name=name, private=sk.to_string().decode(), public=vk.to_string().decode()
    )
    db.keys.insert_one(key)


def db_key_get_or_create(name: str) -> Key:
    key = db.keys.find_one({"name": name})
    if key is None:
        key = db_key_create(name=name)
    assert key is not None
    return key
