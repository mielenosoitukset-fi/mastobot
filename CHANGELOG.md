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