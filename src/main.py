import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from bot import BoardObject, SnakeObject, move_fn
from oldbot import move as old_move


def index(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "apiversion": "1",
            "author": "tbilyn",  # Battlesnake Username
            "color": "#29CEB8",
            "head": "default",
            "tail": "default",
        }
    )


def game_start(request: Request) -> Response:
    print("GAME START")
    return Response(status_code=200)


def game_end(request: Request) -> Response:
    print("GAME OVER")
    return Response(status_code=200)


async def game_move(request: Request) -> JSONResponse:
    """Game logic"""
    start_time = time.perf_counter()
    body = await request.json()

    snake = SnakeObject(body["you"])
    board = BoardObject(body["board"])

    res = move_fn(board, snake)

    end_time = time.perf_counter()
    elapsed_time_ms = (end_time - start_time) * 1000

    print(f"{body['turn']}\t - MOVE: " + res["move"] + f"\t\t\t{elapsed_time_ms:.6f}ms")
    return JSONResponse(res)


# old bot


def old_on_info(request: Request):
    return JSONResponse(
        {
            "apiversion": "1",
            "author": "tbilyn",  # TODO: Your Battlesnake Username
            "color": "#29CEB8",  # TODO: Choose color
            "head": "default",  # TODO: Choose head
            "tail": "default",  # TODO: Choose tail
        }
    )


def old_on_start(request: Request):
    print("GAME START")
    return Response(status_code=200)


def old_on_end(request: Request):
    print("GAME START")
    return Response(status_code=200)


async def old_on_move(request: Request):

    body = await request.json()
    return JSONResponse(old_move(body))


app = Starlette(
    debug=True,
    routes=[
        Route("/new", index, methods=["GET"]),
        Route("/new/start", game_start, methods=["POST"]),
        Route("/new/end", game_end, methods=["POST"]),
        Route("/new/move", game_move, methods=["POST"]),
        Route("/", old_on_info, methods=["GET"]),
        Route("/start", old_on_start, methods=["POST"]),
        Route("/end", old_on_end, methods=["POST"]),
        Route("/move", old_on_move, methods=["POST"]),
    ],
)
