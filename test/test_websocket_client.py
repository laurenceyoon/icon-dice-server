import asyncio
import hashlib
import unittest

import websockets
from secp256k1 import PrivateKey

from app import app
from config import CONFIG

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
        loop.run_until_complete(TestWebsocketClient.game())

    @staticmethod
    async def game():
        uri = CONFIG.ws_uri + '/game'
        async with websockets.connect(uri) as websocket:
            token = ''
            await websocket.send(token)
