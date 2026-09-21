"""Local launcher: run the Battlesnake bot behind a Flask server (for ngrok).

The game logic lives in packages/battlesnake/api/logic.py so it can be shared,
unchanged, with the DigitalOcean Function. We add that directory to sys.path so
this launcher can import it directly.
"""

import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "packages", "battlesnake", "api"
    ),
)

import logic  # noqa: E402
from server import run_server  # noqa: E402


# Start server when `python main.py` is run
if __name__ == "__main__":
    run_server(
        {
            "info": logic.info,
            "start": logic.start,
            "move": logic.move,
            "end": logic.end,
        }
    )
