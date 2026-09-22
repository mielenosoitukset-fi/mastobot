import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

with patch("mastobot.database.DatabaseManager") as mock_database:
    import mastobot.bot as bot
    from mastobot.bot import (
        MAX_STATUS_LENGTH,
        SUBSCRIBE_INSTRUCTIONS,
        PostedState,
        append_subscribe_instructions,
        upcoming_within_days,
    )


class MastoBotTestCase(unittest.TestCase):

    def test__upcoming_within_days__returns_true_for_given_days_in_future(self):
        event_dt = datetime.fromisoformat("2023-04-15T12:30:00")
        test_dt = datetime.fromisoformat(f"2023-04-10T13:30:00")
        days = 4
        with self.subTest(event_dt=event_dt, test_dt=test_dt, within_days=days, returns=False):
            self.assertFalse(upcoming_within_days(event_dt, days, test_dt))
        days = 5
        with self.subTest(event_dt=event_dt, test_dt=test_dt, within_days=days, returns=True):
            self.assertTrue(upcoming_within_days(event_dt, days, test_dt))

    def test__upcoming_within_days__returns_true_for_upcoming_events_same_day(self):
        event_dt = datetime.fromisoformat("2023-04-15T12:30:00")
        test_dt = datetime.fromisoformat(f"2023-04-15T12:29:00")
        with self.subTest(event_dt=event_dt, test_dt=test_dt, returns=True):
            self.assertTrue(upcoming_within_days(event_dt, 0, test_dt))
        test_dt = datetime.fromisoformat(f"2023-04-15T12:30:00")
        with self.subTest(event_dt=event_dt, test_dt=test_dt, returns=False):
            self.assertFalse(upcoming_within_days(event_dt, 0, test_dt))

    def test__append_subscribe_instructions__embeds_instructions_in_status(self):
        status = "Testimielenosoitus\n17. lokakuuta 2026 klo 13:00"
        combined = append_subscribe_instructions(status)
        self.assertTrue(combined.startswith(status))
        self.assertIn(SUBSCRIBE_INSTRUCTIONS, combined)
        self.assertLessEqual(len(combined), MAX_STATUS_LENGTH)

    def test__append_subscribe_instructions__drops_instructions_when_status_too_long(self):
        status = "x" * MAX_STATUS_LENGTH
        self.assertEqual(append_subscribe_instructions(status), status)

    def _make_event(self, demo_id="demo123", **overrides):
        event = {
            "_id": demo_id,
            "title": "Testimielenosoitus",
            "date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "start_time": "13:00",
            "end_time": "15:00",
            "city": "Helsinki",
            "tags": ["ilmasto"],
            "cancelled": False,
        }
        event.update(overrides)
        return event

    def test__process_events__posts_single_status_with_embedded_instructions(self):
        with patch.object(bot, "post_to_mastodon", return_value=(True, {"id": "1"})) as mock_post, \
             patch.object(bot, "append_posted", return_value=None) as mock_append, \
             patch.object(bot.time, "sleep", return_value=None):
            posted = bot.process_events(
                [self._make_event()],
                PostedState(),
                client=None,
                dry_run=True,
                max_days=60,
            )

        self.assertEqual(posted, 1)
        mock_post.assert_called_once()
        status = mock_post.call_args[0][1]
        self.assertIn(SUBSCRIBE_INSTRUCTIONS, status)
        self.assertLessEqual(len(status), MAX_STATUS_LENGTH)
        mock_append.assert_called_once()

    def test__process_events__posts_one_status_per_event(self):
        with patch.object(bot, "post_to_mastodon", return_value=(True, {"id": "1"})) as mock_post, \
             patch.object(bot, "append_posted", return_value=None), \
             patch.object(bot.time, "sleep", return_value=None):
            posted = bot.process_events(
                [self._make_event("demo123"), self._make_event("demo456")],
                PostedState(),
                client=None,
                dry_run=True,
                max_days=60,
            )

        self.assertEqual(posted, 2)
        self.assertEqual(mock_post.call_count, 2)

    def test__handle_cancellations__does_not_attach_subscription_instructions(self):
        state = PostedState()
        state.announcements["demo123"] = {"link": "https://mielenosoitukset.fi/demonstration/demo123", "status_id": "abc"}
        with patch.object(bot, "post_to_mastodon", return_value=(True, {"id": "2"})) as mock_post, \
             patch.object(bot, "append_posted", return_value=None) as mock_append, \
             patch.object(bot.time, "sleep", return_value=None):
            cancelled = bot.handle_cancellations(
                [self._make_event(demo_id="demo123", cancelled=True)],
                state,
                client=None,
                dry_run=True,
            )

        self.assertEqual(cancelled, 1)
        mock_post.assert_called_once()
        status = mock_post.call_args[0][1]
        self.assertNotIn(SUBSCRIBE_INSTRUCTIONS, status)
        mock_append.assert_called_once()


if __name__ == "__main__":
    unittest.main()
