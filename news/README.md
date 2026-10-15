# Red-Folder-Bot

Telegram-Alerts für High-Impact-Events (ForexFactory „Red Folder“). Läuft als GitHub Action, kein Server.

| Wann | Was |
|---|---|
| Mo–Fr 06:30 | Tagesübersicht: Zeit, Event, Prognose vs. Vorwert, Richtung, Sperrzeit ±5 min |
| 10 min vor jedem Event | 🚨 Reminder „jetzt flat gehen“ |
| So abends | Wochenvorschau |
| Kein Event | „✅ Keine Red-Folder-Events heute“ → bleibt die Nachricht aus, ist der Bot kaputt |
| Feed down | „⚠️ manuell prüfen“ |

## Setup
1. Telegram: @BotFather → `/newbot` → Token. Dem Bot einmal schreiben.
2. Chat-ID: `https://api.telegram.org/bot<TOKEN>/getUpdates` → `chat.id`.
3. GitHub → Settings → Secrets and variables → Actions → Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
4. Test: Actions → „Red Folder Alert“ → Run workflow (Modus `daily` / `weekly`).

Optionale Variables (gleiche Seite, Tab „Variables“):
- `RED_FOLDER_COUNTRIES` – Default `USD`, z. B. `USD,EUR`
- `RED_FOLDER_BUFFER_MIN` – Sperrzeit ± Minuten, Default `5`
- `RED_FOLDER_LEAD_MIN` – Reminder-Vorlauf, Default `10`

## Hinweise
- „bullish/bearish“ = erwartete Richtung der **Währung** aus Prognose vs. Vorwert. Für Indizes oft invers (heiße Inflation → USD ↑, NQ/ES ↓).
- Reminder decken 07:45–23:45 Berlin (Sommer) ab; frühere Events nur in der Morgenübersicht.
- Tests: `python news/test_red_folder.py`
