"""Red-Folder-Events (ForexFactory, Impact High) per Telegram melden.

Modi:  daily (Default) – Tagesübersicht morgens
       remind          – Ping LEAD_MIN Minuten vor jedem Event
       weekly          – Wochenvorschau (Sonntag)
"""
import html, json, os, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FEED = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
TZ = ZoneInfo(os.getenv("TZ_NAME", "Europe/Berlin"))
COUNTRIES = {c.strip().upper() for c in os.getenv("COUNTRIES", "ALL").split(",") if c.strip()} - {"ALL"}  # leer = alle Währungen
SEND_HOUR = int(os.getenv("SEND_HOUR", "7"))
BUFFER = int(os.getenv("BUFFER_MIN", "5"))   # Sperrzeit ± Minuten ums Event
LEAD = int(os.getenv("LEAD_MIN", "10"))      # Reminder x Minuten vorher
REMIND_SPAN = timedelta(hours=4)             # jeder Reminder-Lauf deckt 4h ab
REMIND_OFFSET = timedelta(minutes=40)        # Fenster startet 40 min nach Cron → Puffer für Cron-Verzögerung
INVERSE = ("unemployment", "jobless", "claims")  # höher = schlecht für die Währung
WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def http(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0 red-folder-bot"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def send(text):
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        sys.exit("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID fehlen (GitHub → Settings → Secrets → Actions).")
    body = urllib.parse.urlencode({"chat_id": chat, "text": text, "parse_mode": "HTML",
                                   "disable_web_page_preview": "true"}).encode()
    http(f"https://api.telegram.org/bot{token}/sendMessage", body)


def fetch():
    try:
        return json.loads(http(FEED))
    except Exception as ex:
        send(f"⚠️ <b>Red-Folder-Bot:</b> Kalender nicht abrufbar ({type(ex).__name__}). "
             "Heute MANUELL auf forexfactory.com prüfen!")
        raise


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


def red(events):
    """High-Impact-Events der gewählten Länder als sortierte (lokale Zeit, Event)-Liste."""
    out = [(datetime.fromisoformat(e["date"]).astimezone(TZ), e) for e in events
           if e.get("impact") == "High" and (not COUNTRIES or e.get("country", "").upper() in COUNTRIES)]
    return sorted(out, key=lambda x: x[0])


def scope():
    return ", ".join(sorted(COUNTRIES)) if COUNTRIES else "alle Währungen"


def day_label(d):
    return f"{WEEKDAYS[d.weekday()]}, {d:%d.%m.}"


def hm(t, today=None):
    return f"{t:%H:%M}" if today is None or t.date() == today else f"{WEEKDAYS[t.weekday()]} {t:%H:%M}"


def event_lines(t, e, today=None):
    lines = [f"<b>{hm(t, today)}</b> · {e['country']} · {html.escape(e['title'])}"]
    if e.get("forecast") or e.get("previous"):
        lines.append(f"    Prognose {html.escape(e.get('forecast') or '–')} | Vorher {html.escape(e.get('previous') or '–')}")
    lines.append(f"    {expectation(e)}")
    return lines


def blocks(events, today=None):
    """Zeitfenster ±BUFFER, überlappende zusammengefasst."""
    out = []
    for t, _ in events:
        s, e = t - timedelta(minutes=BUFFER), t + timedelta(minutes=BUFFER)
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return " · ".join(f"{hm(s, today)}–{e:%H:%M}" for s, e in out)


def build_daily(events, today):
    """Heute + kommende Nacht bis SEND_HOUR (Asien-Session)."""
    tomorrow = today + timedelta(days=1)
    events = [x for x in events if x[0].date() == today or (x[0].date() == tomorrow and x[0].hour < SEND_HOUR)]
    if not events:
        return f"✅ <b>Keine Red-Folder-Events heute</b> ({day_label(today)}, {scope()})"
    lines = [f"🔴 <b>Red Folder heute</b> ({day_label(today)}, {scope()})", ""]
    for t, e in events:
        lines += event_lines(t, e, today)
    lines += ["", f"⛔ Sperrzeit: {blocks(events, today)}", f"🔔 Reminder kommt {LEAD} min vorher (07:45–23:45)."]
    return "\n".join(lines)


def build_weekly(events, today):
    events = [x for x in events if x[0].date() >= today]
    if not events:
        return (f"📅 <b>Wochenvorschau:</b> keine kommenden Red-Folder-Events im Feed ({scope()}). "
                "Montag früh kommt die Tagesübersicht.")
    by_day = defaultdict(list)
    for t, e in events:
        by_day[t.date()].append((t, e))
    lines = ["📅 <b>Red Folder diese Woche</b>"]
    for d in sorted(by_day):
        lines += ["", f"<b>{day_label(d)}</b>"]
        lines += [f"  {t:%H:%M} · {e['country']} · {html.escape(e['title'])}" for t, e in by_day[d]]
    return "\n".join(lines)


def build_reminder(t, group):
    lines = [f"🚨 <b>In {LEAD} min: Red Folder</b> ({t:%H:%M})", ""]
    for _, e in group:
        lines += event_lines(t, e)
    lines += ["", "→ Jetzt flat gehen / keine neuen Trades."]
    return "\n".join(lines)


def remind_window(now_utc):
    """Fenster, für das dieser Lauf zuständig ist (aus der Cron-Zeit, nicht der Startzeit → robust gegen Verzögerung)."""
    sched = os.getenv("CRON_SCHEDULE", "")
    if os.getenv("GITHUB_EVENT_NAME") == "schedule" and sched:
        minute, hour = (int(x) for x in sched.split()[:2])
        start = now_utc.replace(hour=hour, minute=minute, second=0, microsecond=0) + REMIND_OFFSET
        if start - now_utc > timedelta(hours=12):  # Lauf über Mitternacht verzögert
            start -= timedelta(days=1)
        return start, start + REMIND_SPAN
    return now_utc, now_utc + REMIND_SPAN


def reminders(events, start, end):
    groups = defaultdict(list)
    for t, e in events:
        groups[t].append((t, e))
    lead = timedelta(minutes=LEAD)
    return [(t - lead, t, g) for t, g in sorted(groups.items()) if start <= t - lead < end]


def run_remind(events):
    now = datetime.now(timezone.utc)
    start, end = remind_window(now)
    due = reminders(events, start, end)
    print(f"Fenster {start:%H:%M}–{end:%H:%M} UTC, {len(due)} Reminder")
    for at, t, group in due:
        if datetime.now(timezone.utc) >= t:
            continue
        wait = (at - datetime.now(timezone.utc)).total_seconds()
        if wait > 0:
            time.sleep(wait)
        send(build_reminder(t, group))


def wait_for_send_hour():
    """GitHub-Cron startet nachts (oft Stunden verspätet) → bis SEND_HOUR Ortszeit schlafen."""
    now = datetime.now(TZ)
    target = now.replace(hour=SEND_HOUR, minute=0, second=0, microsecond=0)
    if now < target:
        print(f"Warte bis {target:%H:%M}")
        time.sleep((target - now).total_seconds())


def main(mode="daily"):
    if mode == "daily" and os.getenv("GITHUB_EVENT_NAME") == "schedule":
        wait_for_send_hour()
    events = red(fetch())
    if mode == "remind":
        return run_remind(events)
    today = datetime.now(TZ).date()
    msg = build_weekly(events, today) if mode == "weekly" else build_daily(events, today)
    print(msg)
    send(msg)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "daily")
