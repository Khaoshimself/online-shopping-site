from records.keys import Key, db_key_get_or_create

from ecdsa import SigningKey, VerifyingKey, NIST384p

cookie_key: Key = db_key_get_or_create("cookie_key")

private = SigningKey.from_string(cookie_key["private"].encode(), curve=NIST384p)
public = VerifyingKey.from_string(cookie_key["public"].encode(), curve=NIST384p)


def cookie_sign(cookie: str) -> str:
    return private.sign(cookie.encode()).decode()


def cookie_verify(cookie: str, signature: str) -> bool:
    return public.verify(signature=signature.encode(), data=cookie.encode())
