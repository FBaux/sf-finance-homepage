# Red-Folder-Bot

Mo–Fr 06:30 (Berlin) Telegram-Nachricht mit den heutigen High-Impact-Events (ForexFactory), inkl. Prognose vs. Vorwert.
Kein Event → „Keine Red-Folder-Events heute“. Feed down → Warnung „manuell prüfen“.

Setup (einmalig):
1. Telegram: @BotFather → `/newbot` → Token kopieren. Dem Bot eine Nachricht schicken.
2. Chat-ID: `https://api.telegram.org/bot<TOKEN>/getUpdates` öffnen → `chat.id`.
3. GitHub → Settings → Secrets → Actions: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
4. Optional Variable `RED_FOLDER_COUNTRIES` (Default `USD`, z. B. `USD,EUR`).
5. Actions → „Red Folder Alert“ → „Run workflow“ zum Testen.

„bullish/bearish“ = erwartete Richtung für die **Währung** (Prognose vs. Vorwert), keine Marktprognose.
