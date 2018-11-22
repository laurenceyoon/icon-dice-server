import json
import os
from asyncio import Condition

import utils
from db_manager import db_manager

game_room = dict()
address_rooms = dict()
waiting_condition: Condition = None


class GameDispatcher:
    @staticmethod
    async def hello(request, ws):
        hello = await ws.recv()
        if isinstance(hello, bytes):
            hello = hello.decode('utf-8')

        print(hello)
        await ws.send('nickname')

    @staticmethod
    async def game(request, ws):
        global waiting_condition
        if waiting_condition is None:
            waiting_condition = Condition()
        # round1
        token = await ws.recv()
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        await ws.send(token)

        print(f"token received: {token}")
        my_address = utils.get_address_from_token(token)
        address_rooms.pop(my_address, None)

        # first player
        if not game_room:
            game_room_id = '0x' + os.urandom(32).hex()
            game_room[game_room_id] = (my_address, None)
            print()
            async with waiting_condition:
                print(f"waiting!")
                await waiting_condition.wait()
        # second player
        else:
            game_room_id, (opposite_address, _) = next(iter(game_room.items()))
            game_room.pop(game_room_id)

            GameDispatcher.save_both_player_data(game_room_id, my_address, opposite_address)
            async with waiting_condition:
                print(f"notify!")
                waiting_condition.notify()

        print(f"lock이 풀렸습니다")
        await ws.send(json.dumps(address_rooms[my_address]))

    @staticmethod
    def save_both_player_data(game_room_id, my_address, opposite_address):
        my_nickname = db_manager.get_nickname_by_address(my_address)
        opposite_nickname = db_manager.get_nickname_by_address(opposite_address)
        address_rooms[my_address] = {
            'game_room_id': game_room_id,
            'opposite_address': opposite_address,
            'opposite_nickname': opposite_nickname
        }
        address_rooms[opposite_address] = {
            'game_room_id': game_room_id,
            'opposite_address': my_address,
            'opposite_nickname': my_nickname
        }
