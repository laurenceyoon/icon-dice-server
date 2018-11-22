import logging

import jwt
from config import CONFIG
from db_manager import db_manager
import json

tokens = set()
# USERS = dict()


class GameDispatcher:
    @staticmethod
    async def game(request, ws):
        token = await ws.recv()
        tokens.add(token)
        logging.debug(f"received token: {token}")
        await ws.send('ok')

    @staticmethod
    async def hello(request, ws):
        hello = await ws.recv()
        print(hello)
        await ws.send('nickname')

    @staticmethod
    async def get_address_from_token(token: str):
        token_bytes = token.encode('utf-8')
        decoded = jwt.decode(token_bytes, CONFIG.jwt_key, algorithms='HS256')
        return decoded['address']
