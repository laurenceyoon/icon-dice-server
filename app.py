from sanic import Sanic
from sanic.request import Request
from sanic.response import json, HTTPResponse
from sanic_session import InMemorySessionInterface
from dispatcher.user_dispatcher import UserDispatcher
from dispatcher.game_dispatcher import GameDispatcher

app = Sanic(__name__)
app.add_route(UserDispatcher.dispatch, '/users', methods=['POST'])
app.add_route(GameDispatcher.websocket_dispatch, '/game')
app.session_interface = InMemorySessionInterface()


@app.route('/')
async def index(_request: Request) -> HTTPResponse:
    return json({"Hello": "world"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
