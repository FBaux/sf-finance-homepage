import os, sys, unittest
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
import pine_list as p


def ev(date_, title, country="USD", impact="High"):
    return {"title": title, "country": country, "date": date_, "impact": impact, "forecast": "", "previous": ""}


ALL = (p.daily_range(date(2020, 1, 1))[0], p.daily_range(date(2030, 1, 1))[1])

XML = b"""<?xml version="1.0" encoding="windows-1252"?><weeklyevents>
<event><title>Bank Holiday</title><country>USD</country><date><![CDATA[11-11-2026]]></date><time><![CDATA[All Day]]></time></event>
<event><title>Treasury Refunding</title><country>USD</country><date><![CDATA[11-12-2026]]></date><time><![CDATA[Tentative]]></time></event>
<event><title>CPI m/m</title><country>USD</country><date><![CDATA[11-12-2026]]></date><time><![CDATA[1:30pm]]></time></event>
</weeklyevents>"""


class T(unittest.TestCase):
    def test_format_merge_sort_dedupe(self):
        raw = [
            ev("2026-11-12T08:30:00-05:00", "Core CPI m/m"),
            ev("2026-11-12T08:30:00-05:00", "CPI m/m"),
            ev("2026-11-12T08:30:00-05:00", "CPI y/y"),
            ev("2026-11-12T08:30:00-05:00", "CPI m/m"),
            ev("2026-11-10T14:00:00-05:00", "FOMC Statement"),
            ev("2026-11-06T08:30:00-05:00", "Non-Farm Employment Change"),
        ]
        self.assertEqual(p.lines(raw, *ALL), [
            "2026-11-06 14:30 NFP",
            "2026-11-10 20:00 FOMC Statement",
            "2026-11-12 14:30 Core CPI / CPI",
        ])

    def test_regex_and_no_commas(self):
        out = p.lines([ev("2026-11-12T10:00:00-05:00", "Retail Sales, ex Autos m/m")], *ALL)
        self.assertEqual(out, ["2026-11-12 16:00 Retail Sales ex Autos"])
        self.assertTrue(all(p.LINE_RE.match(l) for l in out))

    def test_only_usd_high(self):
        raw = [ev("2026-11-12T08:30:00-05:00", "CPI m/m", country="EUR"),
               ev("2026-11-12T08:30:00-05:00", "PPI m/m", impact="Medium"),
               ev("2026-11-12T08:30:00-05:00", "Bank Holiday", impact="Holiday")]
        self.assertEqual(p.lines(raw, *ALL), [])

    def test_dst_gap_weeks(self):
        raw = [
            ev("2026-10-29T08:30:00-04:00", "Advance GDP q/q"),   # EU schon Winterzeit, US noch Sommerzeit → 5h
            ev("2026-10-28T14:00:00-04:00", "FOMC Statement"),
            ev("2026-11-05T08:30:00-05:00", "Jobless Claims"),     # beide Winterzeit → 6h
            ev("2027-03-18T08:30:00-04:00", "CPI m/m"),            # US schon Sommerzeit, EU noch Winterzeit → 5h
            ev("2027-04-01T08:30:00-04:00", "PPI m/m"),            # beide Sommerzeit → 6h
        ]
        self.assertEqual(p.lines(raw, *ALL), [
            "2026-10-28 19:00 FOMC Statement",
            "2026-10-29 13:30 Advance GDP",
            "2026-11-05 14:30 Jobless Claims",
            "2027-03-18 13:30 CPI",
            "2027-04-01 14:30 PPI",
        ])

    def test_utc_input(self):
        self.assertEqual(p.lines([ev("2026-11-12T13:30:00+00:00", "CPI m/m")], *ALL), ["2026-11-12 14:30 CPI"])

    def test_untimed_excluded(self):
        raw = [ev("2026-11-03T10:16:00-05:00", "Congressional Elections"),   # Platzhalterzeit aus echtem Feed
               ev("2026-11-11T00:00:00-05:00", "Bank Holiday"),
               ev("2026-11-12T09:00:00-05:00", "Treasury Refunding"),
               ev("2026-11-12T08:30:00-05:00", "CPI m/m")]
        self.assertEqual(p.lines(raw, *ALL, p.untimed_titles(XML)), ["2026-11-12 14:30 CPI"])

    def test_untimed_titles_parses_xml(self):
        self.assertEqual(p.untimed_titles(XML), {("USD", "Bank Holiday"), ("USD", "Treasury Refunding")})
        self.assertEqual(p.untimed_titles(b""), set())

    def test_message_pre_block(self):
        msg = p.message(["2026-11-12 14:30 CPI", "2026-11-13 14:30 PPI"])
        self.assertEqual(msg, "<pre>2026-11-12 14:30 CPI\n2026-11-13 14:30 PPI</pre>")
        self.assertNotIn("`", msg)
        self.assertIsNone(p.message([]))

    def test_ranges(self):
        s, e = p.daily_range(date(2026, 11, 6))            # Freitag
        self.assertEqual((f"{s:%Y-%m-%d %H:%M}", f"{e:%Y-%m-%d}"), ("2026-11-06 00:00", "2026-11-09"))
        s, e = p.weekly_range(date(2026, 11, 8))           # Sonntag → Mo 9.–So 15.
        self.assertEqual((f"{s:%Y-%m-%d}", f"{e:%Y-%m-%d}"), ("2026-11-09", "2026-11-16"))
        s, _ = p.weekly_range(date(2026, 11, 9))           # verspäteter Lauf am Montag → diese Woche
        self.assertEqual(f"{s:%Y-%m-%d}", "2026-11-09")
        raw = [ev("2026-11-08T23:30:00+01:00", "X Speaks"), ev("2026-11-09T00:30:00+01:00", "Y Speaks"),
               ev("2026-11-16T00:00:00+01:00", "Z Speaks")]
        self.assertEqual([l[17:] for l in p.lines(raw, *p.weekly_range(date(2026, 11, 8)))], ["Y Speaks"])


if __name__ == "__main__":
    unittest.main()
