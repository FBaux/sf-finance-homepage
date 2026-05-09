"""
SF Finance — TikTok Content Posting API v2
Lädt Clips automatisch auf TikTok hoch (Direct Post).

Auth-Flow: OAuth 2.0 mit Auto-Token-Refresh via GitHub Secrets API.

Benötigte GitHub Secrets:
  TIKTOK_ACCESS_TOKEN   — OAuth Access Token (24h Gültigkeit, wird auto-refreshed)
  TIKTOK_REFRESH_TOKEN  — OAuth Refresh Token (365 Tage)
  TIKTOK_CLIENT_KEY     — App Client Key (aus TikTok Developer Console)
  TIKTOK_CLIENT_SECRET  — App Client Secret
  GITHUB_TOKEN          — Für Secrets-Update (wird automatisch gesetzt)

Einmalige Setup-Schritte:
  1. App auf developers.tiktok.com erstellen
  2. Scopes: video.upload, video.publish, video.list aktivieren
  3. Lokal OAuth-Dance einmalig durchführen → Access + Refresh Token
  4. Tokens als GitHub Secrets hinterlegen

Verwendung:
  python sync/tiktok_post.py [--dry-run]
"""

import os, json, math, time, base64, hashlib, hmac
import requests
from pathlib import Path
from datetime import datetime, timezone


TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"
CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB pro Chunk

DEFAULT_HASHTAGS = [
    "#trading", "#daytrading", "#proptrading", "#fsfinance",
    "#finance", "#trader", "#forex", "#aktien", "#geldverdienen"
]


def refresh_access_token(client_key: str, client_secret: str, refresh_token: str) -> dict:
    """Tauscht den Refresh Token gegen einen neuen Access Token."""
    r = requests.post(
        f"{TIKTOK_API_BASE}/oauth/token/",
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=30
    )
    r.raise_for_status()
    data = r.json()

    if "error" in data:
        raise ValueError(f"Token-Refresh fehlgeschlagen: {data.get('error_description', data['error'])}")

    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", refresh_token),
        "expires_in": data.get("expires_in", 86400)
    }


def update_github_secret(secret_name: str, secret_value: str, github_token: str) -> bool:
    """Aktualisiert ein GitHub Actions Secret via REST API."""
    # Repo-Infos aus GITHUB_REPOSITORY ermitteln
    repo = os.environ.get("GITHUB_REPOSITORY", "fbaux/sf-finance-homepage")
    api_base = "https://api.github.com"

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    try:
        # Public Key für Verschlüsselung holen
        pk_r = requests.get(
            f"{api_base}/repos/{repo}/actions/secrets/public-key",
            headers=headers, timeout=10
        )
        pk_r.raise_for_status()
        pk_data = pk_r.json()

        # Secret mit NaCl/libsodium verschlüsseln
        from base64 import b64encode
        try:
            from nacl import encoding, public

            public_key = public.PublicKey(pk_data["key"].encode(), encoding.Base64Encoder())
            sealed_box = public.SealedBox(public_key)
            encrypted = sealed_box.encrypt(secret_value.encode())
            encrypted_b64 = b64encode(encrypted).decode()
        except ImportError:
            # Fallback ohne pynacl (Warnung ausgeben)
            print(f"  ⚠ pynacl nicht installiert — Secret {secret_name} nicht aktualisiert.")
            print(f"  Bitte manuell in GitHub Settings > Secrets aktualisieren.")
            return False

        # Secret aktualisieren
        update_r = requests.put(
            f"{api_base}/repos/{repo}/actions/secrets/{secret_name}",
            headers=headers,
            json={
                "encrypted_value": encrypted_b64,
                "key_id": pk_data["key_id"]
            },
            timeout=10
        )
        update_r.raise_for_status()
        return True

    except Exception as e:
        print(f"  Secret-Update Fehler: {e}")
        return False


def initialize_upload(access_token: str, video_path: str, title: str,
                      privacy: str = "PUBLIC_TO_EVERYONE") -> dict:
    """Initialisiert den TikTok Video-Upload und gibt Upload-Infos zurück."""
    file_size = Path(video_path).stat().st_size
    chunk_count = math.ceil(file_size / CHUNK_SIZE)

    payload = {
        "post_info": {
            "title": title,
            "privacy_level": privacy,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": CHUNK_SIZE,
            "total_chunk_count": chunk_count,
        }
    }

    r = requests.post(
        f"{TIKTOK_API_BASE}/post/publish/video/init/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        },
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    data = r.json()

    if data.get("error", {}).get("code") != "ok":
        raise ValueError(f"Init-Fehler: {data.get('error', {})}")

    return data["data"]


def upload_video_chunks(upload_url: str, video_path: str) -> bool:
    """Lädt das Video in Chunks hoch."""
    file_size = Path(video_path).stat().st_size
    chunk_count = math.ceil(file_size / CHUNK_SIZE)

    print(f"  Upload: {file_size / 1024 / 1024:.1f} MB in {chunk_count} Chunks")

    with open(video_path, "rb") as f:
        for chunk_idx in range(chunk_count):
            chunk_data = f.read(CHUNK_SIZE)
            start = chunk_idx * CHUNK_SIZE
            end = min(start + len(chunk_data) - 1, file_size - 1)

            r = requests.put(
                upload_url,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Content-Length": str(len(chunk_data))
                },
                data=chunk_data,
                timeout=120
            )

            if r.status_code not in (200, 206):
                print(f"  Chunk {chunk_idx + 1} Fehler: HTTP {r.status_code}")
                return False

            progress = (chunk_idx + 1) / chunk_count * 100
            print(f"  Chunk {chunk_idx + 1}/{chunk_count} ({progress:.0f}%)")

    return True


def poll_publish_status(access_token: str, publish_id: str, max_wait: int = 120) -> dict:
    """Wartet auf Verarbeitungsstatus nach dem Upload."""
    for attempt in range(max_wait // 5):
        time.sleep(5)
        r = requests.post(
            f"{TIKTOK_API_BASE}/post/publish/status/fetch/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8"
            },
            json={"publish_id": publish_id},
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
        status = data.get("data", {}).get("status", "")

        print(f"  Status: {status}")
        if status in ("PUBLISH_COMPLETE", "SUCCESS"):
            return data["data"]
        if status in ("FAILED", "ERROR"):
            raise ValueError(f"TikTok Publish fehlgeschlagen: {data}")

    raise TimeoutError("TikTok Verarbeitung timed out nach 120s")


def post_clip_to_tiktok(clip: dict, access_token: str, dry_run: bool = False) -> str | None:
    """Postet einen einzelnen Clip auf TikTok. Gibt die Video-ID zurück."""
    hook = clip.get("hook", "Neuer Trading-Clip")
    hashtags = " ".join(DEFAULT_HASHTAGS[:6])
    title = f"{hook[:100]} {hashtags}"[:2200]

    # Captioned-Version bevorzugen, sonst processed
    video_file = (
        clip.get("files", {}).get("tiktok_captioned") or
        clip.get("files", {}).get("tiktok")
    )

    if not video_file or not Path(video_file).exists():
        print(f"  Video-Datei nicht gefunden: {video_file}")
        return None

    print(f"\nTikTok Upload: {clip['clip_id']}")
    print(f"  Titel: {title[:80]}...")
    print(f"  Datei: {video_file} ({Path(video_file).stat().st_size / 1024 / 1024:.1f} MB)")

    if dry_run:
        print("  [DRY-RUN] Kein echter Upload.")
        return f"dry_run_{clip['clip_id']}"

    # Upload initialisieren
    upload_info = initialize_upload(access_token, video_file, title)
    publish_id = upload_info["publish_id"]
    upload_url = upload_info["upload_url"]

    # Chunks hochladen
    success = upload_video_chunks(upload_url, video_file)
    if not success:
        print(f"  Upload fehlgeschlagen.")
        return None

    # Status abwarten
    result = poll_publish_status(access_token, publish_id)
    video_id = result.get("publicaly_available_post_id", [None])[0]
    print(f"  ✓ TikTok veröffentlicht: {video_id}")
    return str(video_id)


def post_due_clips(clips_json_path: str = "api/clips.json", dry_run: bool = False) -> None:
    """Postet alle fälligen TikTok-Clips aus der Queue."""
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
    access_token = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
    refresh_token = os.environ.get("TIKTOK_REFRESH_TOKEN", "")
    github_token = os.environ.get("GITHUB_TOKEN", "")

    if not access_token and not refresh_token:
        print("TIKTOK_ACCESS_TOKEN und TIKTOK_REFRESH_TOKEN nicht konfiguriert.")
        print("Einmalig OAuth-Setup erforderlich → sync/tiktok_auth_setup.py")
        return

    # Token refreshen wenn nötig
    if refresh_token and client_key and client_secret:
        print("Refreshe TikTok Access Token...")
        try:
            tokens = refresh_access_token(client_key, client_secret, refresh_token)
            access_token = tokens["access_token"]

            # Neuen Refresh Token in GitHub Secrets speichern
            if github_token and tokens.get("refresh_token") != refresh_token:
                update_github_secret("TIKTOK_ACCESS_TOKEN", access_token, github_token)
                update_github_secret("TIKTOK_REFRESH_TOKEN", tokens["refresh_token"], github_token)
                print("  ✓ Tokens in GitHub Secrets aktualisiert.")
        except Exception as e:
            print(f"  Token-Refresh Fehler: {e}")
            if not access_token:
                return

    clips_path = Path(clips_json_path)
    if not clips_path.exists():
        print(f"Fehler: {clips_json_path} nicht gefunden.")
        return

    with open(clips_path, encoding="utf-8") as f:
        clips_data = json.load(f)

    now = datetime.now(timezone.utc)
    queue = clips_data.get("queue", [])

    due_clips = [
        c for c in queue
        if c.get("status") in ("captioned", "processed", "scheduled")
        and c.get("platforms_to_post", {}).get("tiktok", True)
        and not c.get("tiktok_video_id")
    ]

    # Scheduled_at Filter: nur fällige Clips
    due_now = []
    for clip in due_clips:
        scheduled_at = clip.get("scheduled_at")
        if not scheduled_at or scheduled_at <= now.strftime("%Y-%m-%dT%H:%M:%SZ"):
            due_now.append(clip)

    print(f"\n=== TikTok Posting: {len(due_now)} fällige Clips ===")

    for clip in due_now:
        try:
            video_id = post_clip_to_tiktok(clip, access_token, dry_run)
            if video_id:
                clip["tiktok_video_id"] = video_id
                clip["tiktok_posted_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                clip["status"] = "posted_tiktok"
                clip.setdefault("analytics", {})["tiktok"] = {
                    "views": 0, "likes": 0, "shares": 0, "last_fetched": None
                }
        except Exception as e:
            print(f"  Fehler bei {clip['clip_id']}: {e}")

        # Rate limiting: min. 60s zwischen Uploads
        if not dry_run and len(due_now) > 1:
            time.sleep(60)

    # Gepostete Clips in posted[] verschieben
    still_queued = []
    posted = clips_data.get("posted", [])
    for clip in queue:
        if clip.get("tiktok_video_id") and clip.get("youtube_video_id"):
            posted.append(clip)
        else:
            still_queued.append(clip)

    clips_data["queue"] = still_queued
    clips_data["posted"] = posted
    clips_data["updated"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(clips_path, "w", encoding="utf-8") as f:
        json.dump(clips_data, f, indent=2, ensure_ascii=False)

    print(f"✓ TikTok Posting abgeschlossen.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SF Finance TikTok Poster")
    parser.add_argument("--dry-run", action="store_true", help="Kein echter Upload")
    parser.add_argument("--clips-json", default="api/clips.json")
    args = parser.parse_args()

    post_due_clips(args.clips_json, args.dry_run)
