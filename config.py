import hashlib

from secp256k1 import PrivateKey, PublicKey


class CONFIG:
    db_path = './.db_user'
    http_uri = 'http://127.0.0.1:8000'
    ws_uri = 'ws://127.0.0.1:8000'
    jwt_key = 'thisissecret'
    v3_uri = 'https://bicon.net.solidwallet.io/api/v3'
    contract_address = 'cx6a84c2f001b8f58564a4411c4403294cd8cd9caf’'
    private_key = PrivateKey()
    address = hashlib.sha3_256(private_key.pubkey.serialize(compressed=False)[1:]).digest()[-20:]
