import math
from collections import deque
from typing import Any, NamedTuple


class Point(NamedTuple):
    x: int
    y: int


class NextMoveStatus:
    def __init__(
        self, point: Point, direction: str, deadend: bool = False, risk: bool = False
    ):
        self.point = point
        self.direction = direction
        self.deadend = deadend
        self.risk = risk
        self.kill_possibility = False
        self.space = 0
        self.food_distance: int | None = None
        self.longest_path: int = 0

    def get_space_category(self, length: int) -> int:
        if self.space < length * 0.8:
            return 0
        if self.space >= length * 0.8 and self.space < length * 1.4:
            return 1
        return 2

    def __str__(self) -> str:
        return f"({self.direction.upper()} deadend: {self.deadend}, risk: {self.risk}, space: {self.space})"

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
        self.body = [Point(f["x"], f["y"]) for f in input["body"]]
        self.neck = Point(input["body"][1]["x"], input["body"][1]["y"])

        self.double_tail = False
        if len(self.body) > 1 and self.body[-1] == self.body[-2]:
            self.double_tail = True


class BoardObject:
    def __init__(self, input: dict[str, Any]):

        self.height = input["height"]
        self.width = input["width"]
        self.food = {Point(f["x"], f["y"]) for f in input["food"]}
        self.snakes = [SnakeObject(elem) for elem in input["snakes"]]

        self.obstacles: set[Point] = set()
        for sn in self.snakes:
            # we get body without last item because it is:
            # - either tail that will be emptry the next turn
            # or it is double tail, and so two last items are the same and we can use just one
            self.obstacles.update(sn.body[:-1])

    def bfs(
        self, start: Point, max_visited: int = 10000
    ) -> tuple[int, int | None, int]:
        """it returns: (visited cell amount, the closest food distance, the longest path)"""

        class CellDescr(NamedTuple):
            distance: int
            is_food: bool

        visited: dict[Point, CellDescr] = {}

        queue: deque = deque()
        queue.append((start, 0))

        while len(queue) > 0 and len(visited) < max_visited:
            cell, pos = queue.popleft()
            if cell in visited:
                continue

            is_food = cell in self.food

            ns = self.neighbours(cell)
            ns_empty = [(n, pos + 1) for n in ns if n not in self.obstacles]

            queue.extend(ns_empty)
            visited[cell] = CellDescr(pos, is_food)

        if len(visited) == 0:
            return (0, None, 0)

        food: list[int] = [elem.distance for elem in visited.values() if elem.is_food]
        closest_food: int | None = min(food, default=None)

        longest_path: int = max(visited.values(), key=lambda e: e.distance).distance

        return len(visited), closest_food, longest_path

    def onboard(self, p: Point) -> bool:
        if p.x < 0 or p.x >= self.width:
            return False
        if p.y < 0 or p.y >= self.height:  # noqa: SIM103
            return False
        return True

    def next_moves(self, snake: SnakeObject) -> set[NextMoveStatus]:
        res: set[NextMoveStatus] = set()

        p = Point(snake.head.x - 1, snake.head.y)
        if self.onboard(p):
            state = NextMoveStatus(p, "left")
            res.add(state)

        p = Point(snake.head.x + 1, snake.head.y)
        if self.onboard(p):
            state = NextMoveStatus(p, "right")
            res.add(state)

        p = Point(snake.head.x, snake.head.y + 1)
        if self.onboard(p):
            state = NextMoveStatus(p, "up")
            res.add(state)

        p = Point(snake.head.x, snake.head.y - 1)
        if self.onboard(p):
            state = NextMoveStatus(p, "down")
            res.add(state)

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


def move_fn(board: BoardObject, me: SnakeObject):

    available_moves = board.next_moves(me)

    for move in available_moves:
        if move.point in board.obstacles:
            move.deadend = True

    # mark cells as risky if big oponents head can move into
    oponents_heads = {
        snake.head
        for snake in board.snakes
        if snake.head != me.head and snake.length >= me.length
    }  # snakes other then me

    risky: set[Point] = set()
    for h in oponents_heads:
        neighs = board.neighbours(h)
        risky.update(neighs)

    for move in available_moves:
        if move.point in risky:
            move.risk = True

    # calculate space available for each of the moves
    for move in available_moves:
        if move.deadend == True:
            continue
        space, closest_food, longest_path = board.bfs(move.point)  # , me.length * 2
        move.space = space
        move.food_distance = closest_food
        move.longest_path = longest_path

    safe_moves: list[NextMoveStatus] = [
        move for move in available_moves if move.deadend == False and move.risk == False
    ]

    need_food: bool = False

    if me.health < 55:
        need_food = True
    else:
        for s in board.snakes:
            if s.id == me.id:
                continue
            if s.length >= me.length:
                need_food = True

    # filter only those where food is, it which are safe and which have enough space to not die
    if need_food:
        food_moves = [
            move
            for move in safe_moves
            if move.food_distance is not None
            and move.get_space_category(me.length) >= 1
        ]

        if len(food_moves) > 0:
            ordered_food = sorted(
                food_moves,
                key=lambda e: (
                    e.food_distance if e.food_distance is not None else 100000
                ),
            )
            return {"move": ordered_food[0].direction}

    ordered_moves = sorted(
        available_moves,
        key=lambda e: e.longest_path,
        reverse=True,
    )

    # todo:
    # remember to not go for foor that enemy can reach first
    # if just two left - try to attack
    # todo: if you see that space is constrained - follow the longest available path
    # stay way from ends of the grid, move closer to the center
    # follow your tail

    for move in ordered_moves:
        if move.deadend == False and move.risk == False:
            return {"move": move.direction}
    for move in ordered_moves:
        if move.deadend == False and move.risk == True:
            return {"move": move.direction}

    return {"move": "up", "shout": "no moves"}


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


# if False or me.health < 50 and len(board.food) > 0:
#     closest_food = next(iter(board.food))
#     min_dist = BoardObject.dist(me.head, closest_food)
#     for f in board.food:
#         dist = BoardObject.dist(me.head, f)
#         if dist < min_dist:
#             min_dist = dist
#             closest_food = f

#     if closest_food.x < me.head.x:
#         next_move = "left"
#     if closest_food.x > me.head.x:
#         next_move = "right"
#     if closest_food.y < me.head.y:
#         next_move = "down"
#     if closest_food.y > me.head.y:
#         next_move = "up"
