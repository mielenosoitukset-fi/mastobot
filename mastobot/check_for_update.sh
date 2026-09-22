#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_NAME="mastobot"

cd "$APP_DIR"

# Allow git operations when the repo is owned by another user (e.g. the
# service account) but this script is run as root from CI/deploy.
if ! git config --global --get-all safe.directory 2>/dev/null | grep -Fxq "$APP_DIR"; then
    git config --global --add safe.directory "$APP_DIR"
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "Error: $APP_DIR is not a git repository"
    exit 1
fi

branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$branch" = "HEAD" ]; then
    echo "Error: detached HEAD detected, refusing to auto-update"
    exit 1
fi

current_head="$(git rev-parse HEAD)"
newest_head="$(git ls-remote origin "refs/heads/$branch" | cut -f1)"

echo "Current: $current_head"
echo "Newest:  $newest_head"

if [ -z "$newest_head" ]; then
    echo "Error: could not resolve remote head for branch '$branch'"
    exit 1
fi

if [ "$current_head" != "$newest_head" ]; then
    echo "Update available — updating..."

    git fetch origin "$branch"
    git reset --hard "origin/$branch"
    git clean -fd

    if [ -f requirements.txt ]; then
        echo "Installing Python dependencies..."
        # Prefer the service venv when present (matches the deployed systemd unit)
        PIP_PYTHON="/usr/bin/python3"
        VENV_DIR=""
        if [ -x "$APP_DIR/../venv/bin/python" ]; then
            PIP_PYTHON="$APP_DIR/../venv/bin/python"
            VENV_DIR="$(dirname "$PIP_PYTHON")/.."
        fi
        "$PIP_PYTHON" -m pip install -r requirements.txt
        # Keep the venv owned by the service user when installed as root
        if [ "$(id -u)" = "0" ] && [ -n "$VENV_DIR" ] && [ -d "$VENV_DIR" ]; then
            venv_owner="$(stat -c %U "$VENV_DIR" 2>/dev/null || true)"
            if [ -n "$venv_owner" ]; then
                chown -R "$venv_owner" "$VENV_DIR"
            fi
        fi
    fi

    echo "Restarting service..."
    systemctl restart "$SERVICE_NAME"

    echo "Update complete."
else
    echo "Already up to date."
fi