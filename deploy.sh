#!/usr/bin/env bash
# Deploy on the server. Run as root from the repo dir, right after `git pull`:
#   ./deploy.sh
# Assumes the systemd unit and nginx site are symlinked to the repo files
# (Option A), so the pull already updated them in place — no copying needed.
set -euo pipefail

cd /apps/battlesnakebots

# Sync Python deps into the venv (installs new/updated, no-op if unchanged).
# Runs before the chmod so freshly installed files are made app-readable too.
.venv/bin/pip install -r requirements.txt

# Ensure www-data (the app user) can read everything root just pulled,
# regardless of root's umask. Capital X = traverse dirs / keep executables,
# without marking plain files executable. Ownership stays root (read-only to app).
chmod -R a+rX /apps/battlesnakebots

# Pick up any change to battlesnakebot.service (no-op if unchanged).
systemctl daemon-reload

# Validate nginx BEFORE reloading; if the pulled config is broken,
# set -e stops here and the running nginx keeps serving the old config.
nginx -t
systemctl reload nginx

# Restart the app to pick up code / unit changes.
systemctl restart battlesnakebots

# Show the result.
systemctl --no-pager --lines=0 status battlesnakebots
echo "Deploy complete."
