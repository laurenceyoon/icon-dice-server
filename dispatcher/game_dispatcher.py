import json
import os
import time
from asyncio import Condition

import utils
from db_manager import db_manager

game_room = dict()
address_rooms = dict()
first_start_game_result = ''
first_reveal_game_result = ''
condition_player_waiting: Condition = None
condition_start_game: Condition = None
condition_reveal_game: Condition = None


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
        # ============================ round1 ============================
        global condition_player_waiting
        if condition_player_waiting is None:
            condition_player_waiting = Condition()

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
            async with condition_player_waiting:
                await condition_player_waiting.wait()
        # second player
        else:
            game_room_id, (opposite_address, _) = next(iter(game_room.items()))
            game_room.pop(game_room_id)

            GameDispatcher.save_response_to_both_players(game_room_id, my_address, opposite_address)
            async with condition_player_waiting:
                condition_player_waiting.notify()

        await ws.send(json.dumps(address_rooms[my_address]))

        # ============================ round2 ============================
        global condition_start_game, first_start_game_result
        if condition_start_game is None:
            condition_start_game = Condition()
        start_game_tx_hash = await ws.recv()

        # first player
        if not first_start_game_result:
            result = await GameDispatcher.get_result_loop(start_game_tx_hash)
            first_start_game_result = start_game_tx_hash
            async with condition_start_game:
                await condition_start_game.wait()
        # second player
        else:
            result = await GameDispatcher.get_result_loop(start_game_tx_hash)
            async with condition_start_game:
                condition_start_game.notify()

        first_start_game_result = ''  # clear memory
        await ws.send(result)

        # ============================ round3 ============================
        global first_reveal_game_result, condition_reveal_game
        if condition_reveal_game is None:
            condition_reveal_game = Condition()
        reveal_game_tx_hash = await ws.recv()

        # first player
        if not first_reveal_game_result:
            result = await GameDispatcher.get_result_loop(reveal_game_tx_hash)
            first_reveal_game_result = reveal_game_tx_hash
            async with condition_reveal_game:
                await condition_reveal_game.wait()
        # second player
        else:
            result = await GameDispatcher.get_result_loop(reveal_game_tx_hash)
            async with condition_reveal_game:
                condition_reveal_game.notify()

        first_reveal_game_result = ''  # clear memory
        await ws.send(result)

        # TODO end game request!!!

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

    @staticmethod
    async def get_result_loop(start_game_tx_hash):
        while True:
            try:
                response = utils.get_transaction_result(start_game_tx_hash)
                break
            except Exception:
                time.sleep(0.5)
        return 'success'
