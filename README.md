# Battlesnake bot

A Python Battlesnake that runs two ways from one shared logic module
(`packages/battlesnake/api/logic.py`):

- **Locally** behind a Flask server + ngrok (for development).
- **On DigitalOcean Functions** via App Platform git-push auto-deploy.

## Layout

```
project.yml                      DigitalOcean Functions project config
packages/battlesnake/api/
  logic.py                       the bot's game logic (stdlib only, shared)
  __main__.py                    DO Function entrypoint (HTTP dispatch -> logic)
server.py                        Flask wrapper used for local runs
main.py                          local launcher (python main.py)
requirements.txt                 Flask (local only)
Dockerfile                       optional container hosting
```

## Run locally (Flask + ngrok)

```powershell
pip install -r requirements.txt
python main.py            # serves on http://0.0.0.0:8000
ngrok http 8000           # in a second terminal
```

Use the ngrok HTTPS URL as your Battlesnake URL when creating a game at
play.battlesnake.com.

## Deploy to DigitalOcean Functions (App Platform)

The DO Function reuses `logic.py` and dispatches on the HTTP method + trailing
sub-path (`web: raw`), so all four Battlesnake routes (`/`, `/start`, `/move`,
`/end`) reach the single `api` function. No `doctl` needed for git-push deploys.

1. Push this repo to GitHub.
2. DO control panel -> **Apps** -> **Create App** -> connect the GitHub repo +
   branch, and enable **Autodeploy**.
3. When DO detects resources, add a **Functions** component; set its **source
   directory** to the repo root (where `project.yml` lives).
4. Deploy. Find the live URL under **App -> Settings -> Functions component ->
   Functions table** (each function name links to its URL), e.g.
   `https://<app>.ondigitalocean.app/.../battlesnake/api`.
5. Use that URL as your Battlesnake URL at play.battlesnake.com. Every push now
   redeploys automatically.

### Notes

- **Cold starts:** Battlesnake enforces a per-move deadline (~500 ms). A cold DO
  function can occasionally exceed it and the engine substitutes a default move.
  Fine for casual play; self-host the Flask/Docker version if it matters.
- Keep **Flask out of** `packages/battlesnake/api/` — the function is stdlib-only,
  so there is no `requirements.txt` there and the serverless build stays fast.
