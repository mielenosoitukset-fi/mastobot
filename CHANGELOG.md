# Changelog

All notable changes to this project are documented here. Format loosely based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## UNRELEASED

- **Reduce subscription-instruction noise**: Subscription instructions are no longer posted as a
  separate reply toot under each announcement. They are now embedded in the event announcement
  itself, so followers no longer see an extra instruction post per event in their timeline. The
  instructions are still posted on announcements (and omitted on cancellations, since cancelled
  events cannot be subscribed to). If an event post would exceed the Mastodon status length limit,
  the instructions are skipped rather than failing the announcement.
- **Tests**: Fixed the broken `DatabaseManager` mock target in the test suite so tests can run, and
  added coverage for the embedded subscription instructions.
- **Auto-deploy on merge to `main`**: Added a GitHub Actions deploy workflow that runs the unit
  tests and then updates the production server via SSH (pulling `main`, installing dependencies and
  restarting the `mastobot` service). See the README for the required secrets and server setup.
- **`check_for_update.sh` hardening**: The update script now works when run as root against a repo
  owned by the service account (adds the `safe.directory` git exception itself) and installs Python
  dependencies into the `/opt/mastobot/venv` used by the deployed unit (falling back to
  `/usr/bin/python3` when no venv exists), keeping the venv owned by the service user.