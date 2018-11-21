import base64
import hashlib
import os

import jwt
from jsonrpcserver.aio import AsyncMethods
from sanic import response
from secp256k1 import PublicKey, PrivateKey

from config import CONFIG
from db_manager import DBManager

db_manager = DBManager(CONFIG.db_path)
methods = AsyncMethods()
PRIVATE_KEY = PrivateKey()
USERS_RANDOM = dict()  # {address_bytes: random_bytes}


class UserDispatcher:
    @staticmethod
    async def dispatch(request):
        dispatch_response = await methods.dispatch(request.json)
        return response.json(dispatch_response, status=dispatch_response.http_status)

    @staticmethod
    @methods.add
    async def login_hash(**kwargs):
        """
        :param kwargs:
        address: "hxbe258ceb872e08851f1f59694dac2558708ece11"
        :return:
        result: "0x1fcf7c34dc875681761bdaa5d75d770e78e8166b5c4f06c226c53300cbe85f57"
        """
        address = kwargs.get('address')
        address_bytes = bytes.fromhex(address[2:])
        random = os.urandom(32)
        USERS_RANDOM[address_bytes] = random
        return '0x' + random.hex()

    @staticmethod
    @methods.add
    async def login(**kwargs):
        """
        :param kwargs:
        address: "hxbe258ceb872e08851f1f59694dac2558708ece11",
        signature: "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA="
        :return:
        result: "0x48757af881f76c858890fb41934bee228ad50a71707154a482826c39b8560d4b"
        """
        address = kwargs.get('address')
        signature = kwargs.get('signature')

        address_bytes = bytes.fromhex(address[2:])
        sign_bytes = base64.b64decode(signature.encode('utf-8'))

        await UserDispatcher.verify_signature(address_bytes, sign_bytes)
        token = UserDispatcher.generate_jwt(address)
        db_manager.add_token(address, token)
        return token

    @staticmethod
    async def verify_signature(address_bytes, sign_bytes):
        random_bytes = USERS_RANDOM[address_bytes]
        recoverable_sig = PRIVATE_KEY.ecdsa_recoverable_deserialize(
            ser_sig=sign_bytes[:-1],
            rec_id=sign_bytes[-1]
        )
        raw_public_key = PRIVATE_KEY.ecdsa_recover(
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

    @staticmethod
    def generate_jwt(address):
        key = 'secret'
        token = jwt.encode(
            payload={'address': address},
            key=key,
            algorithm='HS256').decode('utf-8')
        return token
