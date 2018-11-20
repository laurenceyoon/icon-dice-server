USERS = dict()


class GameDispatcher:
    @staticmethod
    async def websocket_dispatch(request, ws):
        request = await ws.recv()
        pass
