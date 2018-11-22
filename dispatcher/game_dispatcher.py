import jwt
from config import CONFIG
from db_manager import db_manager

USERS = dict()


class GameDispatcher:
    @staticmethod
    async def websocket_dispatch(request, ws):
        request = await ws.recv()
        address = GameDispatcher.get_address_from_token(request.get('token'))
        db_manager.get_nickname_by_address(address)
        pass

    @staticmethod
    async def get_address_from_token(token: str):
        token_bytes = token.encode('utf-8')
        decoded = jwt.decode(token_bytes, CONFIG.jwt_key, algorithms='HS256')
        return decoded['address']
