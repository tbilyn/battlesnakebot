import math
import random
import typing


def dist(p1: typing.Dict, p2: typing.Dict) -> float:
    return math.hypot(p2["x"] - p1["x"], p2["y"] - p1["y"])


def is_cell_valid(p: dict, board_width: int, board_height: int) -> bool:
    if p["x"] < 0 or p["x"] >= board_width:
        return False
    if p["y"] < 0 or p["y"] >= board_height:  # noqa: SIM103
        return False
    return True


def cell_in_list(p: dict, list: list[dict]) -> bool:
    for a in list:
        if p["x"] == a["x"] and p["y"] == a["y"]:
            return True
    return False


def get_valid_neighboring_cells(
    p: dict, board_width: int, board_height: int
) -> list[dict]:
    left_cell = {"x": p["x"] - 1, "y": p["y"]}
    right_cell = {"x": p["x"] + 1, "y": p["y"]}
    top_cell = {"x": p["x"], "y": p["y"] + 1}
    down_cell = {"x": p["x"], "y": p["y"] - 1}
    res = []
    if is_cell_valid(left_cell, board_width, board_height):
        res.append(left_cell)
    if is_cell_valid(right_cell, board_width, board_height):
        res.append(right_cell)
    if is_cell_valid(top_cell, board_width, board_height):
        res.append(top_cell)
    if is_cell_valid(down_cell, board_width, board_height):
        res.append(down_cell)
    return res


last_move = ""



# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    global last_move

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    body = game_state["you"]["body"]
    head = game_state["you"]["head"]
    my_length = game_state["you"]["length"]
    my_health = game_state["you"]["health"]

    if head["x"] == 0:
        is_move_safe["left"] = False
    if head["x"] == board_width - 1:
        is_move_safe["right"] = False
    if head["y"] == 0:
        is_move_safe["down"] = False
    if head["y"] == board_height - 1:
        is_move_safe["up"] = False

    left_cell = {"x": head["x"] - 1, "y": head["y"]}
    right_cell = {"x": head["x"] + 1, "y": head["y"]}
    top_cell = {"x": head["x"], "y": head["y"] + 1}
    down_cell = {"x": head["x"], "y": head["y"] - 1}

    opponents = game_state["board"]["snakes"]

    opponents_unsafe_heads = [
        op["head"] for op in opponents if op["length"] >= my_length and not(op['head']['x'] == head['x'] and op['head']['y'] == head['y'])
    ]
    # print("=========")
    # print("head:")
    # print(head)
    # print(opponents_unsafe_heads)
    all_obstacles = [p for op in opponents for p in op["body"]]
    all_obstacles += body

    if cell_in_list(left_cell, all_obstacles):
        is_move_safe["left"] = False
    if cell_in_list(right_cell, all_obstacles):
        is_move_safe["right"] = False
    if cell_in_list(top_cell, all_obstacles):
        is_move_safe["up"] = False
    if cell_in_list(down_cell, all_obstacles):
        is_move_safe["down"] = False

    # prevent possible head collisions with bigger snakes
    if is_move_safe["left"]:
        neighboars = get_valid_neighboring_cells(left_cell, board_width, board_height)
        for n in neighboars:
            if cell_in_list(n, opponents_unsafe_heads):
                is_move_safe["left"] = False
                break
    if is_move_safe["right"]:
        neighboars = get_valid_neighboring_cells(right_cell, board_width, board_height)
        for n in neighboars:
            if cell_in_list(n, opponents_unsafe_heads):
                is_move_safe["right"] = False
                break
    if is_move_safe["up"]:
        neighboars = get_valid_neighboring_cells(top_cell, board_width, board_height)
        for n in neighboars:
            if cell_in_list(n, opponents_unsafe_heads):
                is_move_safe["up"] = False
                break
    if is_move_safe["down"]:
        neighboars = get_valid_neighboring_cells(down_cell, board_width, board_height)
        for n in neighboars:
            if cell_in_list(n, opponents_unsafe_heads):
                is_move_safe["down"] = False
                break

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    next_move = random.choice(safe_moves)

    food = game_state["board"]["food"]

    if len(food) > 0 and my_health < 75:
        closest_food = food[0]
        min_dist = dist(head, closest_food)
        for f in food:
            d = dist(head, f)
            if d < min_dist:
                min_dist = d
                closest_food = f

        if closest_food["x"] < head["x"] and is_move_safe["left"]:
            next_move = "left"
        if closest_food["x"] > head["x"] and is_move_safe["right"]:
            next_move = "right"
        if closest_food["y"] < head["y"] and is_move_safe["down"]:
            next_move = "down"
        if closest_food["y"] > head["y"] and is_move_safe["up"]:
            next_move = "up"

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}

