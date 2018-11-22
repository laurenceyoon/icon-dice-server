import json
import os
import time
from asyncio import Condition

import utils
from db_manager import db_manager

game_room = dict()
address_rooms = dict()
first_tx_result = ''
player_waiting_condition: Condition = None
tx_result_condition: Condition = None


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
        global player_waiting_condition
        if player_waiting_condition is None:
            player_waiting_condition = Condition()

        # ====== round1 ======
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
            async with player_waiting_condition:
                await player_waiting_condition.wait()
        # second player
        else:
            game_room_id, (opposite_address, _) = next(iter(game_room.items()))
            game_room.pop(game_room_id)

            GameDispatcher.save_response_to_both_players(game_room_id, my_address, opposite_address)
            async with player_waiting_condition:
                player_waiting_condition.notify()

        await ws.send(json.dumps(address_rooms[my_address]))

        # ====== round2 ======
        global tx_result_condition, first_tx_result
        if tx_result_condition is None:
            tx_result_condition = Condition()
        start_game_tx_hash = await ws.recv()

        # first player
        if not first_tx_result:
            while True:
                try:
                    response = utils.get_transaction_result(start_game_tx_hash)
                    first_tx_result = start_game_tx_hash
                    break
                except Exception:
                    time.sleep(0.5)
            async with tx_result_condition:
                await tx_result_condition.wait()
        # second player
        else:
            while True:
                try:
                    response = utils.get_transaction_result(start_game_tx_hash)
                    break
                except Exception:
                    time.sleep(0.5)
            async with tx_result_condition:
                tx_result_condition.notify()

        await ws.send('success')


    @staticmethod
    def save_response_to_both_players(game_room_id, my_address, opposite_address):
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
