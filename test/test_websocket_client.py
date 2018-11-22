import asyncio
from threading import Thread
import unittest

import websockets
from jsonrpcclient.clients.http_client import HTTPClient

import utils
from app import app
from config import CONFIG

http_client = HTTPClient(CONFIG.http_uri + '/users')
address1, private_key1 = utils.create_new_address_and_privkey()
address2, private_key2 = utils.create_new_address_and_privkey()


class TestWebsocketClient(unittest.TestCase):
    def test_index_returns_200(self):
        request, response = app.test_client.get('/')
        self.assertEqual(response.status, 200)

    def test_websocket_hello(self):
        loop = asyncio.new_event_loop()
        nickname = loop.run_until_complete(self.hello())

        self.assertEqual(nickname, 'nickname')

    async def hello(self):
        uri = CONFIG.ws_uri + '/hello'
        async with websockets.connect(uri) as websocket:
            await websocket.send('hello')
            nickname = await websocket.recv()

        return nickname

    def test_websocket_game(self):
        thread1 = Thread(target=self._run, args=(address1, private_key1, ))
        thread1.start()

        thread2 = Thread(target=self._run, args=(address2, private_key2, ))
        thread2.start()

        thread1.join()
        thread2.join()

    def _run(self, address, private_key):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.game(address, private_key))
        loop.run_forever()

    async def game(self, address, private_key):
        token = await utils.get_token_from_login_process(address, private_key)
        print(f"token type? {type(token)}")

        uri = CONFIG.ws_uri + '/game'
        async with websockets.connect(uri) as websocket:
            await websocket.send(token)
            response = await websocket.recv()
            print(f"got response! {response}")

        async def _stop():
            loop.stop()

        loop = asyncio.get_event_loop()
        loop.create_task(_stop())

        return response

