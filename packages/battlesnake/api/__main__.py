"""DigitalOcean Function entrypoint for the Battlesnake bot.

Battlesnake registers a single base URL and appends the routes it needs
(GET /, POST /start, POST /move, POST /end). A DO Function is a single
`main(args)` entrypoint, so with `web: raw` we inspect the HTTP method and the
trailing sub-path and dispatch to the same handlers the local Flask server uses
(see logic.py, shared with server.py / main.py).
"""

import base64
import json

import logic


def _json(status: int, body):
    # A dict `body` is auto-serialized to JSON by the DO runtime.
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": body,
    }


def main(args):
    http = args.get("http", {})
    method = (http.get("method") or "GET").upper()
    path = (http.get("path") or "/") or "/"

    if method == "GET":  # Battlesnake info ping
        return _json(200, logic.info())

    raw = http.get("body", "") or ""
    if http.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    game_state = json.loads(raw) if raw else {}

    if path.endswith("/start"):
        logic.start(game_state)
        return _json(200, {"status": "ok"})
    if path.endswith("/move"):
        return _json(200, logic.move(game_state))
    if path.endswith("/end"):
        logic.end(game_state)
        return _json(200, {"status": "ok"})

    return _json(200, logic.info())  # base POST / unknown
