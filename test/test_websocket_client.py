import asyncio
import base64
import hashlib
import json
import unittest

import websockets
from jsonrpcclient.clients.http_client import HTTPClient
from secp256k1 import PrivateKey

from app import app
from config import CONFIG

http_client = HTTPClient(CONFIG.http_uri + '/users')
PRIVATE_KEY = PrivateKey()
serialized_pub = PRIVATE_KEY.pubkey.serialize(compressed=False)
hashed_pub = hashlib.sha3_256(serialized_pub[1:]).digest()
test_address = "hx" + hashed_pub[-20:].hex()


class TestWebsocketClient(unittest.TestCase):
    def test_index_returns_200(self):
        request, response = app.test_client.get('/')
        self.assertEqual(response.status, 200)

    def test_websocket_hello(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(TestWebsocketClient.hello())

    @staticmethod
    async def hello():
        uri = CONFIG.ws_uri + '/hello'
        async with websockets.connect(uri) as websocket:
            await websocket.send('hello')
            nickname = await websocket.recv()
            print({nickname})

    def test_websocket_game(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.game())

    async def game(self):
        token = await self.get_token_from_login()

        uri = CONFIG.ws_uri + '/game'
        async with websockets.connect(uri) as websocket:
            await websocket.send(token)

    async def get_token_from_login(self):
        response = http_client.request(method_name='login_hash', address=test_address)
        random_result = json.loads(response.text)['result']
        random_bytes = bytes.fromhex(random_result[2:])
        signature_base64str = await self.sign(PRIVATE_KEY, random_bytes)
        response = http_client.request(method_name='login', address=test_address, signature=signature_base64str)
        token = json.loads(response.text)['result']
        return token

    async def sign(self, private_key: PrivateKey, random_bytes):
        raw_sig = private_key.ecdsa_sign_recoverable(msg=random_bytes,
                                                     raw=True,
                                                     digest=hashlib.sha3_256)
        serialized_sig, recover_id = private_key.ecdsa_recoverable_serialize(raw_sig)
        signature = serialized_sig + bytes((recover_id,))
        signature_base64str = base64.b64encode(signature).decode('utf-8')
        return signature_base64str
