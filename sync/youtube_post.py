"""
SF Finance — YouTube Data API v3 Upload
Lädt Clips auf YouTube (Shorts und Long-form) hoch.

Auth: OAuth 2.0 mit gespeichertem token.json (base64-kodiert in GitHub Secret).

Benötigte GitHub Secrets:
  YOUTUBE_TOKEN_JSON  — Base64-kodiertes token.json aus einmaligem OAuth-Flow
  YOUTUBE_CHANNEL_ID  — YouTube Kanal-ID (optional, für Analytics)

Einmaliges Setup (lokal ausführen):
  python sync/youtube_auth_setup.py

Verwendung:
  python sync/youtube_post.py [--dry-run] [--clips-json api/clips.json]
"""

import os, json, base64, time, tempfile
import requests
from pathlib import Path
from datetime import datetime, timezone


DEFAULT_TAGS = [
    "cod", "call of duty", "warzone", "gaming", "gamer",
    "fps", "shooter", "clutch", "highlight", "gameplay",
    "mtblucaz", "cod deutsch", "warzone deutsch"
]

YOUTUBE_CATEGORY_GAMING = "20"
YOUTUBE_CATEGORY_EDUCATION = "27"
YOUTUBE_CATEGORY_PEOPLE = "22"


def get_youtube_client():
    """Erstellt einen authentifizierten YouTube API Client."""
    token_json_b64 = os.environ.get("YOUTUBE_TOKEN_JSON", "")
    if not token_json_b64:
        raise EnvironmentError(
            "YOUTUBE_TOKEN_JSON nicht konfiguriert.\n"
            "Einmalig: python sync/youtube_auth_setup.py"
        )

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        token_json = json.loads(base64.b64decode(token_json_b64).decode())
        creds = Credentials.from_authorized_user_info(token_json)

        # Token refreshen wenn abgelaufen
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("  ✓ YouTube Token refreshed.")

        youtube = build("youtube", "v3", credentials=creds)
        return youtube

    except ImportError:
        raise ImportError("google-api-python-client nicht installiert. pip install -r requirements.txt")


def upload_video(
    youtube,
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    is_short: bool = False,
    privacy: str = "public",
    dry_run: bool = False
) -> str | None:
    """
    Lädt ein Video auf YouTube hoch.
    Gibt die Video-ID zurück.
    """
    from googleapiclient.http import MediaFileUpload

    file_size = Path(video_path).stat().st_size
    print(f"\nYouTube Upload: {Path(video_path).name}")
    print(f"  Titel: {title[:80]}")
    print(f"  Größe: {file_size / 1024 / 1024:.1f} MB")
    print(f"  Typ: {'Short' if is_short else 'Long-form'}")

    if dry_run:
        print("  [DRY-RUN] Kein echter Upload.")
        return f"dry_run_{Path(video_path).stem}"

    # YouTube Shorts: #Shorts in Beschreibung für bessere Auffindbarkeit
    if is_short and "#Shorts" not in description:
        description = f"{description}\n\n#Shorts"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": YOUTUBE_CATEGORY_GAMING,
            "defaultLanguage": "de",
            "defaultAudioLanguage": "de",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "madeForKids": False,
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        chunksize=1024 * 1024,  # 1 MB Chunks
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    # Resumable Upload mit Fortschrittsanzeige
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"  Upload: {progress}%")
        except Exception as e:
            print(f"  Upload-Fehler: {e}")
            raise

    video_id = response["id"]
    print(f"  ✓ YouTube veröffentlicht: https://youtube.com/watch?v={video_id}")
    return video_id


def build_description(clip: dict, channel_url: str = "") -> str:
    """Erstellt eine optimierte YouTube-Beschreibung für Gaming-Clips."""
    hook = clip.get("hook", "")

    desc_parts = [
        hook,
        "",
        "🎮 Mehr Clips & Highlights auf meinem Kanal!",
        "🔔 Abonnieren nicht vergessen!",
        "",
        "📲 TikTok: @mtb_lucaz",
    ]

    if channel_url:
        desc_parts.append(f"🌐 {channel_url}")

    desc_parts += [
        "",
        "#cod #callofduty #warzone #gaming #clutch #highlight #fps #shooter",
        "#mtblucaz #Shorts"
    ]

    return "\n".join(desc_parts)


def post_clip_to_youtube(clip: dict, youtube, dry_run: bool = False) -> dict:
    """Postet einen Clip auf YouTube (Shorts + ggf. Long-form). Gibt Video-IDs zurück."""
    hook = clip.get("hook", "Neuer Trading-Clip")
    description = build_description(clip)
    video_ids = {}

    # YouTube Shorts
    shorts_file = (
        clip.get("files", {}).get("youtube_shorts_captioned") or
        clip.get("files", {}).get("youtube_shorts")
    )

    if shorts_file and Path(shorts_file).exists():
        title = f"{hook[:95]} #Shorts"[:100]
        try:
            video_id = upload_video(
                youtube, shorts_file, title, description,
                DEFAULT_TAGS, is_short=True, dry_run=dry_run
            )
            if video_id:
                video_ids["youtube_shorts"] = video_id
        except Exception as e:
            print(f"  Shorts Upload Fehler: {e}")

    # YouTube Long-form (falls vorhanden)
    long_file = clip.get("files", {}).get("youtube_long")
    if long_file and Path(long_file).exists():
        title = f"{hook[:97]}..."[:100]
        try:
            video_id = upload_video(
                youtube, long_file, title, description,
                DEFAULT_TAGS, is_short=False, dry_run=dry_run
            )
            if video_id:
                video_ids["youtube_long"] = video_id
        except Exception as e:
            print(f"  Long-form Upload Fehler: {e}")

    return video_ids


def post_due_clips(clips_json_path: str = "api/clips.json", dry_run: bool = False) -> None:
    """Postet alle fälligen YouTube-Clips aus der Queue."""
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
        if c.get("status") in ("captioned", "processed", "scheduled", "posted_tiktok")
        and not c.get("youtube_video_id")
    ]

    # Nur fällige Clips (scheduled_at in der Vergangenheit)
    due_now = []
    for clip in due_clips:
        scheduled_at = clip.get("scheduled_at")
        if not scheduled_at or scheduled_at <= now.strftime("%Y-%m-%dT%H:%M:%SZ"):
            due_now.append(clip)

    if not due_now:
        print("Keine fälligen YouTube-Clips.")
        return

    print(f"\n=== YouTube Posting: {len(due_now)} fällige Clips ===")

    try:
        youtube = get_youtube_client()
    except (EnvironmentError, ImportError) as e:
        print(f"YouTube Auth Fehler: {e}")
        return

    for clip in due_now:
        try:
            video_ids = post_clip_to_youtube(clip, youtube, dry_run)

            if video_ids:
                # Primäre Video-ID setzen (Shorts haben Priorität)
                primary_id = video_ids.get("youtube_shorts") or video_ids.get("youtube_long")
                clip["youtube_video_id"] = primary_id
                clip["youtube_video_ids"] = video_ids
                clip["youtube_posted_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

                if clip.get("tiktok_video_id"):
                    clip["status"] = "posted"
                else:
                    clip["status"] = "posted_youtube"

                clip.setdefault("analytics", {})["youtube"] = {
                    "views": 0, "likes": 0, "last_fetched": None
                }
        except Exception as e:
            print(f"  Fehler bei {clip['clip_id']}: {e}")

        # Rate limiting: YouTube API Quota schonen
        if not dry_run and len(due_now) > 1:
            time.sleep(30)

    # Vollständig gepostete Clips in posted[] verschieben
    still_queued = []
    posted = clips_data.get("posted", [])
    for clip in queue:
        if clip.get("status") == "posted":
            posted.append(clip)
        else:
            still_queued.append(clip)

    clips_data["queue"] = still_queued
    clips_data["posted"] = posted
    clips_data["stats_summary"]["total_clips"] = len(posted)
    clips_data["updated"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(clips_path, "w", encoding="utf-8") as f:
        json.dump(clips_data, f, indent=2, ensure_ascii=False)

    print(f"✓ YouTube Posting abgeschlossen.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SF Finance YouTube Poster")
    parser.add_argument("--dry-run", action="store_true", help="Kein echter Upload")
    parser.add_argument("--clips-json", default="api/clips.json")
    args = parser.parse_args()

    post_due_clips(args.clips_json, args.dry_run)
