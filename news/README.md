# Red-Folder-Bot

Telegram-Alerts für High-Impact-Events (ForexFactory „Red Folder“). Läuft als GitHub Action, kein Server.

| Wann | Was |
|---|---|
| Mo–Fr 07:00 | Tagesübersicht: Zeit, Event, Prognose vs. Vorwert, Richtung, Sperrzeit ±5 min |
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
- `RED_FOLDER_COUNTRIES` – Default `ALL` (alle Währungen), z. B. `USD,EUR` zum Einschränken
- `RED_FOLDER_BUFFER_MIN` – Sperrzeit ± Minuten, Default `5`
- `RED_FOLDER_LEAD_MIN` – Reminder-Vorlauf, Default `10`

## Pünktlich triggern (cron-job.org)
GitHub-Cron ist oft Stunden verspätet. Deshalb triggert cron-job.org den Workflow minutengenau.

1. GitHub → Settings (Profil) → Developer settings → Fine-grained tokens → Generate:
   Repository access *Only* `sf-finance-homepage`, Permission **Actions: Read and write**. Ablaufdatum notieren!
2. cron-job.org → Konto → je Job: URL
   `https://api.github.com/repos/FBaux/sf-finance-homepage/actions/workflows/red-folder.yml/dispatches`,
   Methode **POST**, Zeitzone **Europe/Berlin**, Header
   `Authorization: Bearer <TOKEN>`, `Accept: application/vnd.github+json`, Body:

| Job | Zeit (Berlin) | Body |
|---|---|---|
| Daily | Mo–Fr 07:00 | `{"ref":"main","inputs":{"mode":"daily"}}` |
| Remind 1–4 | Mo–Fr 07:45, 11:45, 15:45, 19:45 | `{"ref":"main","inputs":{"mode":"remind"}}` |
| Weekly | So 18:00 | `{"ref":"main","inputs":{"mode":"weekly"}}` |

3. Test: Daily-Job „Test run“ → Antwort **204** = ok.
4. GitHub → Settings → Secrets and variables → Actions → Variables: `RED_FOLDER_EXTERNAL_CRON` = `true`
   (schaltet die verspäteten GitHub-Crons ab, sonst kommen Nachrichten doppelt).

## Hinweise
- „bullish/bearish“ = erwartete Richtung der **Währung** aus Prognose vs. Vorwert. Für Indizes oft invers (heiße Inflation → USD ↑, NQ/ES ↓).
- Reminder decken 07:45–23:45 Berlin ab; frühere Events nur in der Morgenübersicht.
- Token läuft ab → Bot verstummt. Vor Ablauf neuen Token in cron-job.org eintragen.
- Tests: `python news/test_red_folder.py`
