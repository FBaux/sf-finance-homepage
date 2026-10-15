"""Morgens die heutigen Red-Folder-Events (ForexFactory, Impact High) per Telegram melden."""
import html, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FEED = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
TZ = ZoneInfo(os.getenv("TZ_NAME", "Europe/Berlin"))
COUNTRIES = {c.strip().upper() for c in os.getenv("COUNTRIES", "USD").split(",") if c.strip()}
INVERSE = ("unemployment", "jobless", "claims")  # höher = schlecht für die Währung
WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def http(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0 red-folder-bot"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def send(text):
    token, chat = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
    body = urllib.parse.urlencode({"chat_id": chat, "text": text, "parse_mode": "HTML",
                                   "disable_web_page_preview": "true"}).encode()
    http(f"https://api.telegram.org/bot{token}/sendMessage", body)


def num(v):
    m = re.search(r"-?\d+(\.\d+)?", (v or "").replace(",", ""))
    return float(m.group()) if m else None


def expectation(e):
    f, p = num(e.get("forecast")), num(e.get("previous"))
    if f is None or p is None:
        return "keine Prognose – Richtung offen, volatil"
    if f == p:
        return "Prognose = Vorwert → neutral"
    up = f > p
    good = up != any(k in e["title"].lower() for k in INVERSE)
    return f"{'↑' if up else '↓'} erwartet → {e['country']}-{'bullish' if good else 'bearish'}"


def todays_events(events, today):
    out = []
    for e in events:
        if e.get("impact") != "High" or e.get("country", "").upper() not in COUNTRIES:
            continue
        t = datetime.fromisoformat(e["date"]).astimezone(TZ)
        if t.date() == today:
            out.append((t, e))
    return sorted(out, key=lambda x: x[0])


def build(events, today):
    head = f"{WEEKDAYS[today.weekday()]}, {today:%d.%m.}"
    if not events:
        return f"✅ <b>Keine Red-Folder-Events heute</b> ({head}, {', '.join(sorted(COUNTRIES))})"
    lines = [f"🔴 <b>Red Folder heute</b> ({head})", ""]
    for t, e in events:
        lines.append(f"<b>{t:%H:%M}</b> · {e['country']} · {html.escape(e['title'])}")
        if e.get("forecast") or e.get("previous"):
            lines.append(f"    Prognose {e.get('forecast') or '–'} | Vorher {e.get('previous') or '–'}")
        lines.append(f"    {expectation(e)}")
    lines += ["", "⚠️ Vor den Events flat sein – Prop-Firm-Regel checken."]
    return "\n".join(lines)


def due():
    """Cron läuft 2x (CET/CEST); nur der Lauf senden, der gerade 6:30 Ortszeit trifft."""
    sched = os.getenv("CRON_SCHEDULE", "")
    if os.getenv("GITHUB_EVENT_NAME") != "schedule" or not sched:
        return True
    utc_hour = int(sched.split()[1])
    offset_h = datetime.now(TZ).utcoffset() // timedelta(hours=1)
    return (utc_hour + offset_h) % 24 == int(os.getenv("SEND_HOUR", "6"))


def main():
    if not due():
        print("Nicht dran (DST-Duplikat) – skip.")
        return
    today = datetime.now(TZ).date()
    try:
        events = json.loads(http(FEED))
    except Exception as ex:
        send(f"⚠️ <b>Red-Folder-Bot:</b> Kalender nicht abrufbar ({type(ex).__name__}). "
             "Heute MANUELL auf forexfactory.com prüfen!")
        raise
    msg = build(todays_events(events, today), today)
    print(msg)
    send(msg)


if __name__ == "__main__":
    sys.exit(main())
