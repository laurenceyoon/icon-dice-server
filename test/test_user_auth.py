import json
import unittest

import jwt
from jsonrpcclient.clients.http_client import HTTPClient

from app import app
from config import CONFIG
from dispatcher.user_dispatcher import UserDispatcher

http_client = HTTPClient(CONFIG.uri + '/users')
test_address = "hxbe258ceb872e08851f1f59694dac2558708ece11"
test_sig = "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA="


class TestUserAuth(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_index_returns_200(self):
        request, response = app.test_client.get('/')
        self.assertEqual(response.status, 200)

    def test_login_hash(self):
        response = http_client.request(method_name='login_hash', address=test_address)
        result = json.loads(response.text)['result']
        random_result = '0x9aa0330713174af486fb46144ed479bbee6054d448e6484d86e7507c780779b4'

        self.assertNotEqual(result, random_result)
        self.assertEqual(len(result), 64)

    def test_login(self):
        response = http_client.request(method_name='login', address=test_address, signature=test_sig)
        result = json.loads(response.text)['result']

        token = UserDispatcher.generate_jwt(test_address)

        self.assertEqual(result, token)

    def test_jwt_decode_address(self):
        key = 'secret'
        encoded = jwt.encode(
            payload={'address': test_address},
            key=key,
            algorithm='HS256')
        decoded = jwt.decode(encoded, key, algorithms='HS256')
        self.assertEqual(decoded['address'], test_address)
