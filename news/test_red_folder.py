import os, sys, unittest
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import red_folder as r

RAW = [
    {"title": "CPI m/m", "country": "USD", "date": "2026-10-15T08:30:00-04:00", "impact": "High", "forecast": "0.3%", "previous": "0.2%"},
    {"title": "Unemployment Claims", "country": "USD", "date": "2026-10-15T08:30:00-04:00", "impact": "High", "forecast": "225K", "previous": "218K"},
    {"title": "FOMC Member Speaks", "country": "USD", "date": "2026-10-15T14:00:00-04:00", "impact": "High", "forecast": "", "previous": ""},
    {"title": "German ZEW", "country": "EUR", "date": "2026-10-15T05:00:00-04:00", "impact": "High", "forecast": "1", "previous": "2"},
    {"title": "Retail Sales & Co", "country": "USD", "date": "2026-10-16T08:30:00-04:00", "impact": "High", "forecast": "0.3%", "previous": "0.4%"},
    {"title": "Crude Oil Inventories", "country": "USD", "date": "2026-10-15T10:30:00-04:00", "impact": "Medium", "forecast": "1M", "previous": "2M"},
]
EV = r.red(RAW)


class T(unittest.TestCase):
    def setUp(self):
        for k in ("GITHUB_EVENT_NAME", "CRON_SCHEDULE"):
            os.environ.pop(k, None)

    def test_filter(self):
        self.assertEqual([e["title"] for _, e in EV],
                         ["CPI m/m", "Unemployment Claims", "FOMC Member Speaks", "Retail Sales & Co"])
        self.assertEqual(f"{EV[0][0]:%H:%M}", "14:30")

    def test_expectation(self):
        self.assertIn("USD-bullish", r.expectation(RAW[0]))
        self.assertIn("USD-bearish", r.expectation(RAW[1]))
        self.assertIn("keine Prognose", r.expectation(RAW[2]))
        self.assertIn("↓", r.expectation(RAW[4]))

    def test_daily(self):
        msg = r.build_daily(EV, date(2026, 10, 15))
        self.assertIn("Do, 15.10.", msg)
        self.assertIn("Sperrzeit: 14:25–14:35 · 19:55–20:05", msg)
        self.assertNotIn("Retail", msg)
        self.assertIn("Keine Red-Folder", r.build_daily(EV, date(2026, 10, 14)))

    def test_escape(self):
        w = r.build_weekly(EV, date(2026, 10, 11))
        self.assertIn("&amp;", w)
        self.assertIn("Fr, 16.10.", w)
        self.assertIn("keine kommenden", r.build_weekly(EV, date(2026, 10, 17)))

    def test_reminders_grouped_and_windowed(self):
        start = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
        due = r.reminders(EV, start, start + timedelta(hours=4))
        self.assertEqual(len(due), 1)                  # CPI + Claims zusammengefasst, 18:00 UTC außerhalb
        self.assertEqual(len(due[0][2]), 2)
        self.assertEqual(f"{due[0][0].astimezone(timezone.utc):%H:%M}", "12:20")

    def test_remind_window_uses_cron_not_start_time(self):
        os.environ.update(GITHUB_EVENT_NAME="schedule", CRON_SCHEDULE="5 13 * * 1-5")
        late = datetime(2026, 10, 15, 13, 50, tzinfo=timezone.utc)  # 45 min verspätet
        s, e = r.remind_window(late)
        self.assertEqual((f"{s:%H:%M}", f"{e:%H:%M}"), ("13:45", "17:45"))

    def test_daily_dst_dedupe(self):
        os.environ["GITHUB_EVENT_NAME"] = "schedule"
        summer = datetime.now(r.TZ).utcoffset() == timedelta(hours=2)
        os.environ["CRON_SCHEDULE"] = "0 5 * * 1-5"
        self.assertEqual(r.due_daily(), summer)
        os.environ["CRON_SCHEDULE"] = "0 6 * * 1-5"
        self.assertEqual(r.due_daily(), not summer)


if __name__ == "__main__":
    unittest.main()
