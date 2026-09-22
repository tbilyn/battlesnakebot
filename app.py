import math
import time
from collections import deque
from typing import Any, NamedTuple

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


class Point(NamedTuple):
    x: int
    y: int


class NextMoveStatus:
    def __init__(self, move: str, deadend: bool = False, risk: bool = False):
        self.move = move
        self.deadend = deadend
        self.risk = risk
        self.kill_possibility = False
        self.space = 0
        self.food_distance = 0

    def __str__(self) -> str:
        return f"({self.move.upper()} deadend: {self.deadend}, risk: {self.risk}, space: {self.space})"

    def __repr__(self) -> str:
        return self.__str__()


class GameObject:
    def __init__(self, input: dict[str, Any]):
        self.id = input["id"]


class SnakeObject:
    def __init__(self, input: dict[str, Any]):
        self.id = input["id"]

        self.health = input["health"]
        self.length = input["length"]

        self.head = Point(input["head"]["x"], input["head"]["y"])
        self.body = {Point(f["x"], f["y"]) for f in input["body"]}
        self.neck = Point(input["body"][1]["x"], input["body"][1]["y"])


class BoardObject:
    def __init__(self, input: dict[str, Any]):

        self.height = input["height"]
        self.width = input["width"]
        self.food = {Point(f["x"], f["y"]) for f in input["food"]}
        self.snakes = [SnakeObject(elem) for elem in input["snakes"]]

        self.obstacles: set[Point] = set()
        for sn in self.snakes:
            self.obstacles.update(sn.body)

    def bfs(self, start: Point, max_visited: int = 10000) -> int:
        queue: deque = deque()
        queue.append(start)
        visited: set[Point] = set()
        while len(queue) > 0 and len(visited) < max_visited:
            cell = queue.popleft()
            if cell in visited:
                continue
            ns = self.neighbours(cell)
            ns_empty = [n for n in ns if n not in self.obstacles]
            # print(ns_empty)
            queue.extend(ns_empty)
            visited.add(cell)
        return len(visited)

    def onboard(self, p: Point) -> bool:
        if p.x < 0 or p.x >= self.width:
            return False
        if p.y < 0 or p.y >= self.height:  # noqa: SIM103
            return False
        return True

    def next_moves(self, snake: SnakeObject) -> dict[Point, NextMoveStatus]:
        res: dict[Point, NextMoveStatus] = {}

        p = Point(snake.head.x - 1, snake.head.y)
        if self.onboard(p):
            state = NextMoveStatus("left")
            res[p] = state

        p = Point(snake.head.x + 1, snake.head.y)
        if self.onboard(p):
            state = NextMoveStatus("right")
            res[p] = state

        p = Point(snake.head.x, snake.head.y + 1)
        if self.onboard(p):
            state = NextMoveStatus("up")
            res[p] = state

        p = Point(snake.head.x, snake.head.y - 1)
        if self.onboard(p):
            state = NextMoveStatus("down")
            res[p] = state

        return res

    def neighbours(self, p: Point) -> set[Point]:
        res: set[Point] = set()
        n = Point(p.x - 1, p.y)
        if self.onboard(n):
            res.add(n)

        n = Point(p.x + 1, p.y)
        if self.onboard(n):
            res.add(n)

        n = Point(p.x, p.y - 1)
        if self.onboard(n):
            res.add(n)

        n = Point(p.x, p.y + 1)
        if self.onboard(n):
            res.add(n)

        return res

    @staticmethod
    def dist(p1: Point, p2: Point) -> float:
        return math.hypot(p2.x - p1.x, p2.y - p1.y)


def move(board: BoardObject, me: SnakeObject):
    # print("---")
    # print(f"head: {me.head}")
    available_moves = board.next_moves(me)

    for point, state in available_moves.items():
        if point in board.obstacles:
            state.deadend = True

    # mark cells as risky if big oponents head can move into
    oponents_heads = {
        snake.head
        for snake in board.snakes
        if snake.head != me.head and snake.length >= me.length
    }  # snakes other then me

    risky: set[Point] = set()
    for h in oponents_heads:
        neighs = board.neighbours(h)
        # print(f"   oponent head: {h}: {neighs}")
        risky.update(neighs)

    for point, state in available_moves.items():
        if point in risky:
            state.risk = True

    # calculate space available for each of the moves
    for point in available_moves:
        if available_moves[point].deadend == True:
            continue
        space = board.bfs(point)  # , me.length * 2
        available_moves[point].space = space
        # if space < me.length:
        #     available_moves[point].deadend = True

    # print(available_moves)

    if False or me.health < 50 and len(board.food) > 0:
        closest_food = next(iter(board.food))
        min_dist = BoardObject.dist(me.head, closest_food)
        for f in board.food:
            dist = BoardObject.dist(me.head, f)
            if dist < min_dist:
                min_dist = dist
                closest_food = f

        if closest_food.x < me.head.x:
            next_move = "left"
        if closest_food.x > me.head.x:
            next_move = "right"
        if closest_food.y < me.head.y:
            next_move = "down"
        if closest_food.y > me.head.y:
            next_move = "up"

    ordered_moves = sorted(
        [(k, v) for k, v in available_moves.items()],
        key=lambda e: e[1].space,
        reverse=True,
    )

    # print(ordered_moves)

    for p, s in ordered_moves:
        if s.deadend == False and s.risk == False:
            return {"move": s.move}
    for p, s in ordered_moves:
        if s.deadend == False and s.risk == True:
            return {"move": s.move}

    return {"move": "up", "shout": "no moves"}


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

    res = move(board, snake)

    end_time = time.perf_counter()
    elapsed_time_ms = (end_time - start_time) * 1000

    print(f"{body["turn"]}\t - MOVE: " + res["move"] + f"\t\t\t{elapsed_time_ms:.6f}ms")
    return JSONResponse(res)


app = Starlette(
    debug=True,
    routes=[
        Route("/", index, methods=["GET"]),
        Route("/start", game_start, methods=["POST"]),
        Route("/end", game_end, methods=["POST"]),
        Route("/move", game_move, methods=["POST"]),
    ],
)

if __name__ == "__main__":
    # snake1 = SnakeObject(
    #     {"body": }
    # )
    board = BoardObject(
        {
            "id": 1,
            "width": 6,
            "height": 6,
            "food": [],
            "snakes": [
                {
                    "id": 1,
                    "health": 10,
                    "length": 3,
                    # "body": [{"x": 2, "y": 2}, {"x": 3, "y": 2}, {"x": 3, "y": 3}, {"x": 1, "y": 1}, {"x": 1, "y": 2}],
                    "body": [
                        {"x": 3, "y": 0},
                        {"x": 2, "y": 0},
                        {"x": 1, "y": 0},
                        {"x": 0, "y": 0},
                        {"x": 0, "y": 1},
                        {"x": 0, "y": 2},
                        {"x": 1, "y": 2},
                        {"x": 2, "y": 2},
                        {"x": 4, "y": 2},
                        {"x": 5, "y": 2},
                        {"x": 3, "y": 1},  # head
                    ],
                    "head": {"x": 3, "y": 1},
                }
            ],
        }
    )

    print("2,1: " + str(board.bfs(Point(2, 1), 5)))
    print("3,2: " + str(board.bfs(Point(3, 2), 5)))
    print("4,1: " + str(board.bfs(Point(4, 1), 5)))
