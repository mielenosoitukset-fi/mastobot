# mastobot-integrations

This repository contains the code for the Mielenosoitukset.fi Mastodon bot.

## Cutover From The Main Repo

The old in-app Mastobot used the main application MongoDB and stored state in:

- `posted_events`
- `mastobot_meta`
- `mastobot_subscriptions`

To avoid duplicate posts during cutover, the safest default is to keep using the
same MongoDB database in this standalone repo. That lets Mastobot see the exact
same historical state it used before the split.

If you must move Mastobot into a separate database later, run:

```bash
python3 scripts/migrate_state.py
```

That script copies the three state collections with idempotent `_id`-based
upserts, so rerunning it does not create duplicates.

If the standalone repo is pointed at the same source DB already, the script will
detect that and simply report that the existing state will be reused directly.

## Setup

### 1. Copy the example configuration file

```bash
cp example.config.yaml config.yaml
```

### 2. Edit the configuration

```bash
nano config.yaml
```

Important:
- `MONGO_URI` / `MONGO_DBNAME` should point to the current production bot state
  before you delete the old main-repo copy.
- The systemd service reads its config from `MASTOBOT_CONFIG=/etc/mastobot/config.yaml`.

### 3. Create a dedicated system user

```bash
sudo adduser --system --group --home /opt/mastobot mastobot
```

### 4. Create the required directories

```bash
sudo mkdir -p /opt/mastobot/current
sudo mkdir -p /etc/mastobot
sudo mkdir -p /var/log/mastobot
sudo mkdir -p /var/lib/mastobot

sudo chown mastobot:mastobot /opt/mastobot
sudo chown mastobot:mastobot /opt/mastobot/current
sudo chown mastobot:mastobot /etc/mastobot
sudo chown mastobot:mastobot /var/log/mastobot
sudo chown mastobot:mastobot /var/lib/mastobot
```

### 5. Copy the project files

```bash
sudo cp -a . /opt/mastobot/current/
sudo chown -R mastobot:mastobot /opt/mastobot/current
```

### 6. Move the configuration file into place

```bash
sudo mv config.yaml /etc/mastobot/config.yaml
sudo chown mastobot:mastobot /etc/mastobot/config.yaml
```

### 7. Install and start the systemd service (optional)

```bash
sudo cp mastobot.service /etc/systemd/system/mastobot.service
sudo chown root:root /etc/systemd/system/mastobot.service

sudo systemctl daemon-reload
sudo systemctl enable --now mastobot
```

### 7.5. Optional migration / preflight

If you are reusing the same DB as the old bot, verify that first:

```bash
python3 scripts/migrate_state.py --verify-only
```

If you are moving to a different database, copy the state before first start:

```bash
python3 scripts/migrate_state.py
```

### 8. View logs

```bash
journalctl -u mastobot -f
```

## Automatic deployment (GitHub Actions)

Every merge to `main` (and manual `workflow_dispatch` runs) deploys to production:

1. The `test` job runs the unit tests (`python -m unittest discover -s tests`).
2. The `deploy` job SSHes into the production server and runs
   `mastobot/check_for_update.sh`, which pulls the new `main`, installs any
   changed Python dependencies and restarts the `mastobot` service. The service
   is restarted even when the checkout is already up to date, so re-running a
   workflow after a partially failed deploy still applies the update.

### Required GitHub secrets

Configure these in the repository settings (Settings → Secrets and variables →
Actions):

- `MASTOBOT_DEPLOY_HOST` – production server hostname/IP.
- `MASTOBOT_DEPLOY_USER` – SSH user for the deploy (defaults to `root` if unset).
- `MASTOBOT_DEPLOY_KEY` – private SSH key accepted on the server for that user.

### Server prerequisites

- `/opt/mastobot/current` is a git clone of this repository with `origin`
  pointing at `github.com/mielenosoitukset-fi/mastobot`, checked out on `main`.
- The deploy SSH key is in the deploy user's `~/.ssh/authorized_keys`.
- The deploy user must be able to write to `/opt/mastobot/current`, install the
  Python requirements and restart the `mastobot` service (running the deploy as
  `root` satisfies all of these). The `safe.directory` git exception for
  `/opt/mastobot/current` is added automatically by `check_for_update.sh`.

## Directory layout

```
/opt/mastobot/current      -> application code
/etc/mastobot/config.yaml  -> configuration
/var/log/mastobot          -> log files
/var/lib/mastobot          -> persistent data (if needed)
```
