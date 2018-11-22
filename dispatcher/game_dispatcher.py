import os
from asyncio import Condition

import utils
from db_manager import db_manager

game_room = dict()
address_rooms = dict()
waiting_condition: Condition = Condition()


class GameDispatcher:
    @staticmethod
    async def hello(request, ws):
        hello = await ws.recv()
        print(hello)
        await ws.send('nickname')

    @staticmethod
    async def game(request, ws):
        # round1
        token = await ws.recv()
        my_address = utils.get_address_from_token(token)
        address_rooms.pop(my_address, None)

        # first player
        if not game_room:
            game_room_id = '0x' + os.urandom(32).hex()
            game_room[game_room_id] = (my_address, None)
            async with waiting_condition:
                await waiting_condition.wait()
        # second player
        else:
            game_room_id, (opposite_address, _) = next(iter(game_room.items()))
            game_room.pop(game_room_id)

            await GameDispatcher.save_both_player_data(game_room_id, my_address, opposite_address)
            async with waiting_condition:
                waiting_condition.notify()

        await ws.send(address_rooms[my_address])

    @staticmethod
    async def save_both_player_data(game_room_id, my_address, opposite_address):
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
