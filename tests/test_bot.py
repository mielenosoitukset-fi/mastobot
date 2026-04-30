import unittest
from datetime import datetime
from unittest.mock import patch
with patch('DatabaseManager.DatabaseManager') as mock:
    from mastobot.bot import upcoming_within_days


class MastoBotTestCase(unittest.TestCase):

    def test__upcoming_within_days__returns_true_for_given_days_in_future(self):
        event_dt = datetime.fromisoformat("2023-04-15T12:30:00")
        test_dt = datetime.fromisoformat(f"2023-04-10T13:30:00")
        days=4
        with self.subTest(event_dt=event_dt, test_dt=test_dt, within_days=days, returns=False):
            self.assertFalse(upcoming_within_days(event_dt, days, test_dt))
        days=5
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


if __name__ == '__main__':
    unittest.main()
