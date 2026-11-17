"""USD-Red-Folder-Liste zum Einfügen in die TradingView-Strategie.

Format je Zeile: JJJJ-MM-TT HH:MM Name  (Europe/Berlin, gleiche Minute zusammengefasst mit " / ")
"""
import html, re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")
LINE_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2} [^,]+$")
CLOCK_RE = re.compile(r"^\d{1,2}:\d{2}(am|pm)$", re.I)
SUFFIX_RE = re.compile(r"\s+(m/m|q/q|y/y)$", re.I)
RENAME = {
    "Non-Farm Employment Change": "NFP",
    "ADP Non-Farm Employment Change": "ADP NFP",
    "Average Hourly Earnings": "Avg Hourly Earnings",
    "FOMC Meeting Minutes": "FOMC Minutes",
    "Federal Funds Rate": "Fed Funds Rate",
    "Core PCE Price Index": "Core PCE",
    "PCE Price Index": "PCE",
    "Unemployment Claims": "Jobless Claims",
}
UNTIMED_WORDS = ("election", "tentative", "all day")


def short_name(title):
    t = SUFFIX_RE.sub("", title.strip())
    t = RENAME.get(t, t).replace(",", " ")
    return re.sub(r"\s+", " ", t).strip()


def untimed_titles(xml_bytes):
    """(country, title) aller Events, deren XML-Zeit keine Uhrzeit ist (All Day, Tentative, …)."""
    if not xml_bytes:
        return set()
    out = set()
    for ev in ET.fromstring(xml_bytes).iter("event"):
        t = (ev.findtext("time") or "").strip()
        if not CLOCK_RE.match(t):
            out.add(((ev.findtext("country") or "").strip(), (ev.findtext("title") or "").strip()))
    return out


def has_fixed_time(e, t, untimed=frozenset()):
    # FF kodiert „All Day“ im JSON mit Platzhalterzeit (z. B. 10:16) → echte Releases liegen auf 5-Minuten-Raster
    return (t.minute % 5 == 0
            and not any(w in e["title"].lower() for w in UNTIMED_WORDS)
            and (e.get("country"), e["title"]) not in untimed)


def lines(raw, start, end, untimed=frozenset()):
    groups = {}
    for e in raw:
        if e.get("impact") != "High" or e.get("country", "").upper() != "USD":
            continue
        t = datetime.fromisoformat(e["date"]).astimezone(BERLIN).replace(second=0, microsecond=0)
        if not (start <= t < end) or not has_fixed_time(e, t, untimed):
            continue
        names = groups.setdefault(t, [])
        n = short_name(e["title"])
        if n and n not in names:
            names.append(n)
    out = [f"{t:%Y-%m-%d %H:%M} {' / '.join(n)}" for t, n in sorted(groups.items()) if n]
    assert all(LINE_RE.match(l) for l in out), out
    return out


def message(pine_lines):
    """Telegram-HTML: <pre> → Tippen kopiert nur den Text, ohne Backticks."""
    return f"<pre>{html.escape(chr(10).join(pine_lines))}</pre>" if pine_lines else None


def week_monday(d):
    return d - timedelta(days=d.weekday())


def _midnight(d):
    return datetime(d.year, d.month, d.day, tzinfo=BERLIN)


def daily_range(today):
    """Heute bis Ende der laufenden Woche (Mo–So)."""
    return _midnight(today), _midnight(week_monday(today) + timedelta(days=7))


def weekly_range(today):
    """Kommende Woche Mo–So (Sonntagslauf → ab morgen; verspäteter Montagslauf → diese Woche)."""
    mon = week_monday(today + timedelta(days=1))
    return _midnight(mon), _midnight(mon + timedelta(days=7))
