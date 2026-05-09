"""
SF Finance — API Data Sync
Läuft via GitHub Actions alle 30 Minuten.
Schreibt Ergebnisse nach api/data.json.

Benötigte GitHub Secrets:
  IG_ACCESS_TOKEN      — Instagram Graph API Long-Lived Token
  IG_USER_ID           — Instagram Business User ID (z.B. 17841400000000000)
  TRADOVATE_USER       — Tradovate Benutzername
  TRADOVATE_PASS       — Tradovate Passwort
  DIGISTORE24_API_KEY  — Digistore24 API Key (aus Account-Einstellungen)
  TIKTOK_ACCESS_TOKEN  — TikTok API Token (für Clip-Analytics)
  YOUTUBE_TOKEN_JSON   — YouTube OAuth Token JSON (Base64-kodiert)
"""

import os, json, base64, requests
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
    },
    "clips": {
        "tiktok": {
            "total_clips_posted": 0,
            "last_30d_views": 0,
            "last_30d_likes": 0,
            "last_30d_shares": 0,
            "last_clip": None,
            "available": False,
            "error": None
        },
        "youtube": {
            "total_clips_posted": 0,
            "shorts_views_30d": 0,
            "channel_subscribers": 0,
            "last_clip": None,
            "available": False,
            "error": None
        }
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

# ── TIKTOK CLIP ANALYTICS ────────────────────────────────────────────────────
TT_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN", "")

if TT_TOKEN:
    try:
        # Liste der letzten Videos abrufen
        list_r = requests.post(
            "https://open.tiktokapis.com/v2/video/list/",
            headers={
                "Authorization": f"Bearer {TT_TOKEN}",
                "Content-Type": "application/json; charset=UTF-8"
            },
            json={"max_count": 20},
            timeout=15
        )
        list_r.raise_for_status()
        list_data = list_r.json()

        if list_data.get("error", {}).get("code") == "ok":
            videos = list_data.get("data", {}).get("videos", [])
            if videos:
                video_ids = [v["id"] for v in videos[:20]]

                # Stats für Videos abrufen
                stats_r = requests.post(
                    "https://open.tiktokapis.com/v2/video/query/",
                    headers={
                        "Authorization": f"Bearer {TT_TOKEN}",
                        "Content-Type": "application/json; charset=UTF-8"
                    },
                    json={
                        "filters": {"video_ids": video_ids},
                        "fields": ["id", "title", "view_count", "like_count",
                                   "share_count", "comment_count", "create_time"]
                    },
                    timeout=15
                )
                stats_r.raise_for_status()
                stats_data = stats_r.json()
                video_stats = stats_data.get("data", {}).get("videos", [])

                total_views = sum(v.get("view_count", 0) for v in video_stats)
                total_likes = sum(v.get("like_count", 0) for v in video_stats)
                total_shares = sum(v.get("share_count", 0) for v in video_stats)

                best = max(video_stats, key=lambda v: v.get("view_count", 0), default=None)

                data["clips"]["tiktok"] = {
                    "total_clips_posted": len(video_stats),
                    "last_30d_views": total_views,
                    "last_30d_likes": total_likes,
                    "last_30d_shares": total_shares,
                    "last_clip": {
                        "video_id": best["id"],
                        "title": best.get("title", "")[:80],
                        "views": best.get("view_count", 0),
                        "likes": best.get("like_count", 0),
                        "shares": best.get("share_count", 0)
                    } if best else None,
                    "available": True,
                    "error": None
                }
        else:
            data["clips"]["tiktok"]["error"] = list_data.get("error", {}).get("message", "API-Fehler")
    except Exception as e:
        data["clips"]["tiktok"]["error"] = str(e)
        print(f"TikTok Clip-Analytics Fehler: {e}")
else:
    data["clips"]["tiktok"]["error"] = "TIKTOK_ACCESS_TOKEN nicht konfiguriert"

# ── YOUTUBE CLIP ANALYTICS ───────────────────────────────────────────────────
YT_TOKEN_B64 = os.environ.get("YOUTUBE_TOKEN_JSON", "")

if YT_TOKEN_B64:
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        token_json = json.loads(base64.b64decode(YT_TOKEN_B64).decode())
        creds = Credentials.from_authorized_user_info(token_json)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube = build("youtube", "v3", credentials=creds)

        # Kanal-Stats
        ch_r = youtube.channels().list(part="statistics", mine=True).execute()
        ch_stats = ch_r.get("items", [{}])[0].get("statistics", {})
        subscribers = int(ch_stats.get("subscriberCount", 0))

        # Letzte 10 Videos
        search_r = youtube.search().list(
            part="snippet", forMine=True, type="video",
            order="date", maxResults=10
        ).execute()
        video_items = search_r.get("items", [])

        if video_items:
            video_ids_yt = [item["id"]["videoId"] for item in video_items]
            stats_r = youtube.videos().list(
                part="statistics,snippet", id=",".join(video_ids_yt)
            ).execute()
            yt_videos = stats_r.get("items", [])

            total_views_yt = sum(
                int(v.get("statistics", {}).get("viewCount", 0)) for v in yt_videos
            )
            best_yt = max(
                yt_videos,
                key=lambda v: int(v.get("statistics", {}).get("viewCount", 0)),
                default=None
            )

            data["clips"]["youtube"] = {
                "total_clips_posted": len(yt_videos),
                "shorts_views_30d": total_views_yt,
                "channel_subscribers": subscribers,
                "last_clip": {
                    "video_id": best_yt["id"],
                    "title": best_yt.get("snippet", {}).get("title", "")[:80],
                    "views": int(best_yt.get("statistics", {}).get("viewCount", 0)),
                    "likes": int(best_yt.get("statistics", {}).get("likeCount", 0))
                } if best_yt else None,
                "available": True,
                "error": None
            }
    except ImportError:
        data["clips"]["youtube"]["error"] = "google-api-python-client nicht installiert"
    except Exception as e:
        data["clips"]["youtube"]["error"] = str(e)
        print(f"YouTube Clip-Analytics Fehler: {e}")
else:
    data["clips"]["youtube"]["error"] = "YOUTUBE_TOKEN_JSON nicht konfiguriert"

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
    elif isinstance(v, dict):
        # Nested (clips)
        for sub_k, sub_v in v.items():
            if isinstance(sub_v, dict) and "available" in sub_v:
                status = "✓" if sub_v["available"] else "✗"
                err    = f" ({sub_v.get('error', '')})" if not sub_v["available"] else ""
                print(f"  {status} {k}.{sub_k}{err}")
