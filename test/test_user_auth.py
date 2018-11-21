import base64
import hashlib
import json
import unittest

import jwt
from jsonrpcclient.clients.http_client import HTTPClient
from secp256k1 import PrivateKey

from app import app
from config import CONFIG
from dispatcher.user_dispatcher import UserDispatcher

http_client = HTTPClient(CONFIG.uri + '/users')

PRIVATE_KEY = PrivateKey()
serialized_pub = PRIVATE_KEY.pubkey.serialize(compressed=False)
hashed_pub = hashlib.sha3_256(serialized_pub[1:]).digest()
test_address = "hx" + hashed_pub[-20:].hex()


class TestUserAuth(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_index_returns_200(self):
        request, response = app.test_client.get('/')
        self.assertEqual(response.status, 200)

    def test_login(self):
        # test_login_hash
        response = http_client.request(method_name='login_hash', address=test_address)
        result = json.loads(response.text)['result']
        random_bytes = bytes.fromhex(result[2:])
        random_result_example = '0x9aa0330713174af486fb46144ed479bbee6054d448e6484d86e7507c780779b4'

        self.assertNotEqual(result, random_result_example)
        self.assertEqual(len(result), 66)

        # test_login
        signature_base64str = self.sign(PRIVATE_KEY, random_bytes)
        response = http_client.request(method_name='login', address=test_address, signature=signature_base64str)
        result = json.loads(response.text)['result']

        token = UserDispatcher.generate_jwt(test_address)

        self.assertEqual(result, token)

    def sign(self, private_key: PrivateKey, random_bytes):
        raw_sig = private_key.ecdsa_sign_recoverable(msg=random_bytes,
                                                     raw=True,
                                                     digest=hashlib.sha3_256)
        serialized_sig, recover_id = private_key.ecdsa_recoverable_serialize(raw_sig)
        signature = serialized_sig + bytes((recover_id,))
        signature_base64str = base64.b64encode(signature).decode('utf-8')
        return signature_base64str

    def test_jwt_decode_address(self):
        key = 'secret'
        encoded = jwt.encode(
            payload={'address': test_address},
            key=key,
            algorithm='HS256')
        decoded = jwt.decode(encoded, key, algorithms='HS256')
        self.assertEqual(decoded['address'], test_address)
