import hashlib

import jwt
from secp256k1 import PublicKey

from config import CONFIG


async def verify_signature(address_bytes, random_bytes, sign_bytes, private_key):
    recoverable_sig = private_key.ecdsa_recoverable_deserialize(
        ser_sig=sign_bytes[:-1],
        rec_id=sign_bytes[-1]
    )
    raw_public_key = private_key.ecdsa_recover(
        msg=random_bytes,
        recover_sig=recoverable_sig,
        raw=True,
        digest=hashlib.sha3_256
    )
    public_key = PublicKey(raw_public_key)
    hash_pub = hashlib.sha3_256(public_key.serialize(compressed=False)[1:]).digest()
    expect_address = hash_pub[-20:]
    if expect_address != address_bytes:
        raise RuntimeError


def get_address_from_token(token: str):
    token_bytes = token.encode('utf-8')
    decoded = jwt.decode(token_bytes, CONFIG.jwt_key, algorithms='HS256')
    return decoded['address']


def generate_jwt(address):
    token = jwt.encode(
        payload={'address': address},
        key=CONFIG.jwt_key,
        algorithm='HS256').decode('utf-8')
    return token
