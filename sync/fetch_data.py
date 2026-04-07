"""
SF Finance — API Data Sync
Läuft via GitHub Actions alle 30 Minuten.
Schreibt Ergebnisse nach api/data.json.

Benötigte GitHub Secrets:
  IG_ACCESS_TOKEN     — Instagram Graph API Long-Lived Token
  IG_USER_ID          — Instagram Business User ID (z.B. 17841400000000000)
  TRADOVATE_USER      — Tradovate Benutzername
  TRADOVATE_PASS      — Tradovate Passwort
  DIGISTORE24_API_KEY — Digistore24 API Key (aus Account-Einstellungen)
"""

import os, json, requests
from datetime import datetime, timezone

# ── INITIAL DATA STRUCTURE ──────────────────────────────────────────────────
data = {
    "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "tradovate": {
        "accountBalance": 0,
        "pnl": 0,
        "drawdown": 0.0,
        "available": False,
        "error": None
    },
    "instagram": {
        "followers": 0,
        "available": False,
        "error": None
    },
    "tiktok": {
        "followers": 0,
        "available": False,
        "error": "TikTok API erfordert Server-seitige OAuth-Genehmigung"
    },
    "digistore": {
        "monthlyRevenue": 0,
        "available": False,
        "error": None
    }
}

# ── INSTAGRAM GRAPH API ─────────────────────────────────────────────────────
IG_TOKEN   = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")

if IG_TOKEN and IG_USER_ID:
    try:
        r = requests.get(
            f"https://graph.facebook.com/v21.0/{IG_USER_ID}",
            params={"fields": "followers_count,username", "access_token": IG_TOKEN},
            timeout=15
        )
        r.raise_for_status()
        d = r.json()
        if "error" in d:
            data["instagram"]["error"] = d["error"].get("message", "Unbekannter Fehler")
        else:
            data["instagram"]["followers"] = d.get("followers_count", 0)
            data["instagram"]["available"] = True
            data["instagram"]["error"] = None

        # Token-Refresh (verhindert Ablauf nach 60 Tagen)
        requests.get(
            "https://graph.instagram.com/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": IG_TOKEN},
            timeout=10
        )
    except Exception as e:
        data["instagram"]["error"] = str(e)
        print(f"Instagram Fehler: {e}")
else:
    data["instagram"]["error"] = "IG_ACCESS_TOKEN oder IG_USER_ID nicht konfiguriert"

# ── TRADOVATE API ────────────────────────────────────────────────────────────
TV_USER = os.environ.get("TRADOVATE_USER", "")
TV_PASS = os.environ.get("TRADOVATE_PASS", "")

if TV_USER and TV_PASS:
    try:
        # Authenticate
        auth_r = requests.post(
            "https://live.tradovateapi.com/v1/auth/accesstokenrequest",
            json={
                "name": TV_USER,
                "password": TV_PASS,
                "appId": "SF Finance Dashboard",
                "appVersion": "1.0",
                "cids": 0,
                "sec": ""
            },
            timeout=15
        )
        auth_r.raise_for_status()
        auth_data = auth_r.json()

        if "accessToken" not in auth_data:
            raise ValueError(auth_data.get("errorText", "Kein Token erhalten"))

        token   = auth_data["accessToken"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get account list
        acc_r = requests.get(
            "https://live.tradovateapi.com/v1/account/list",
            headers=headers, timeout=10
        )
        acc_r.raise_for_status()
        accounts = acc_r.json()

        if accounts:
            account_id      = accounts[0]["id"]
            initial_balance = float(accounts[0].get("initialBalance") or 100000)

            # Get cash balance snapshot
            bal_r = requests.get(
                "https://live.tradovateapi.com/v1/cashBalance/getCashBalanceSnapshot",
                params={"accountId": account_id},
                headers=headers, timeout=10
            )
            bal_r.raise_for_status()
            bal = bal_r.json()

            realized   = float(bal.get("realizedPnL")  or 0)
            unrealized = float(bal.get("openPnL")       or 0)
            total_pnl  = round(realized + unrealized, 2)

            # Drawdown: current equity vs initial (simplified — max 10%)
            current_eq = initial_balance + total_pnl
            peak       = max(initial_balance, current_eq)
            drawdown   = round(max(0, (peak - current_eq) / peak * 100), 2) if peak > 0 else 0

            data["tradovate"]["pnl"]            = total_pnl
            data["tradovate"]["accountBalance"] = round(current_eq, 2)
            data["tradovate"]["drawdown"]       = drawdown
            data["tradovate"]["available"]      = True
            data["tradovate"]["error"]          = None

    except Exception as e:
        data["tradovate"]["error"] = str(e)
        print(f"Tradovate Fehler: {e}")
else:
    data["tradovate"]["error"] = "TRADOVATE_USER oder TRADOVATE_PASS nicht konfiguriert"

# ── DIGISTORE24 API ──────────────────────────────────────────────────────────
DS_KEY = os.environ.get("DIGISTORE24_API_KEY", "")

if DS_KEY:
    try:
        # Digistore24 REST API: Umsatz des laufenden Monats
        from datetime import date
        today      = date.today()
        date_from  = today.replace(day=1).isoformat()
        date_until = today.isoformat()

        r = requests.get(
            f"https://www.digistore24.com/api/call/{DS_KEY}/list_sales",
            params={"date_from": date_from, "date_until": date_until},
            timeout=15
        )
        r.raise_for_status()
        d = r.json()

        if d.get("result") == "success":
            sales = d.get("data", {}).get("sales", [])
            monthly_revenue = sum(
                float(s.get("earnings_net", 0)) for s in sales
                if s.get("status") in ("complete", "completed")
            )
            data["digistore"]["monthlyRevenue"] = round(monthly_revenue, 2)
            data["digistore"]["available"]      = True
            data["digistore"]["error"]          = None
        else:
            data["digistore"]["error"] = d.get("message", "API-Fehler")
    except Exception as e:
        data["digistore"]["error"] = str(e)
        print(f"Digistore24 Fehler: {e}")
else:
    data["digistore"]["error"] = "DIGISTORE24_API_KEY nicht konfiguriert"

# ── WRITE OUTPUT ─────────────────────────────────────────────────────────────
os.makedirs("api", exist_ok=True)
with open("api/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Sync abgeschlossen: {data['updated']}")
for k, v in data.items():
    if isinstance(v, dict) and "available" in v:
        status = "✓" if v["available"] else "✗"
        err    = f" ({v.get('error', '')})" if not v["available"] else ""
        print(f"  {status} {k}{err}")
