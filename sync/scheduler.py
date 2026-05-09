"""
SF Finance — Clip-Scheduler
Berechnet optimale Posting-Zeiten und trägt Clips in die Queue ein.

Optimale Posting-Zeiten für deutschsprachige Trading-Zielgruppe (CET/CEST):
  TikTok:          07:15, 12:30, 18:00, 21:00
  YouTube Shorts:  08:00, 17:30
  YouTube Long:    14:30

Regeln:
  - Minimum 6h Abstand zwischen TikTok-Posts (Anti-Spam-Schutz)
  - Minimum 24h Abstand zwischen YouTube-Posts
  - Nur Werktage für Long-form YouTube bevorzugt

Verwendung:
  python sync/scheduler.py [--clips-json api/clips.json] [--post-due]
"""

import json, os, argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone


# Posting-Fenster in UTC (CET = UTC+1 Winter, CEST = UTC+2 Sommer)
# Gaming-Zielgruppe: aktiv nachmittags, abends & nachts — Wochenende besonders stark
POSTING_WINDOWS = {
    "tiktok": [
        {"hour": 11, "minute": 0},   # 12:00 CET — Mittag
        {"hour": 15, "minute": 0},   # 16:00 CET — Nach Schule/Arbeit
        {"hour": 18, "minute": 0},   # 19:00 CET — Prime-Time Gaming
        {"hour": 20, "minute": 30},  # 21:30 CET — Late-Night Session
    ],
    "youtube_shorts": [
        {"hour": 14, "minute": 0},   # 15:00 CET — Nachmittag
        {"hour": 19, "minute": 0},   # 20:00 CET — Abend
    ],
    "youtube_long": [
        {"hour": 15, "minute": 0},   # 16:00 CET — Wochenende bevorzugt
    ],
}

MIN_GAP = {
    "tiktok": timedelta(hours=6),
    "youtube": timedelta(hours=24),
}


def get_next_posting_slot(
    platform: str,
    last_post_time: datetime | None,
    min_future_hours: float = 1.0
) -> datetime:
    """
    Berechnet den nächsten verfügbaren Posting-Zeitpunkt für eine Plattform.
    Berücksichtigt Mindestabstände und optimale Zeitfenster.
    """
    now = datetime.now(timezone.utc)
    min_time = now + timedelta(hours=min_future_hours)

    # Mindestabstand seit letztem Post einhalten
    if last_post_time:
        gap = MIN_GAP.get("youtube" if "youtube" in platform else "tiktok", timedelta(hours=6))
        min_time = max(min_time, last_post_time + gap)

    windows = POSTING_WINDOWS.get(platform, POSTING_WINDOWS["tiktok"])

    # Nächstes Fenster suchen (bis zu 7 Tage in die Zukunft)
    for days_ahead in range(8):
        candidate_date = (min_time + timedelta(days=days_ahead)).date()

        # YouTube Long: Wochenende bevorzugen für Gaming (Sa=5, So=6)
        if platform == "youtube_long" and candidate_date.weekday() < 5 and days_ahead < 3:
            # Werktage überspringen wenn Wochenende in den nächsten 3 Tagen
            next_weekend_in = 5 - candidate_date.weekday()
            if next_weekend_in <= 3:
                continue

        for window in sorted(windows, key=lambda w: (w["hour"], w["minute"])):
            candidate = datetime(
                candidate_date.year, candidate_date.month, candidate_date.day,
                window["hour"], window["minute"], 0,
                tzinfo=timezone.utc
            )
            if candidate >= min_time:
                return candidate

    # Fallback: morgen um 8 Uhr UTC
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)


def schedule_clips(clips_json_path: str = "api/clips.json") -> int:
    """
    Weist allen ungeschedulten Clips in der Queue Posting-Zeiten zu.
    Gibt die Anzahl der geschedulten Clips zurück.
    """
    clips_path = Path(clips_json_path)
    if not clips_path.exists():
        print(f"Fehler: {clips_json_path} nicht gefunden.")
        return 0

    with open(clips_path, encoding="utf-8") as f:
        clips_data = json.load(f)

    queue = clips_data.get("queue", [])
    posted = clips_data.get("posted", [])

    # Letzten Post-Zeitpunkt pro Plattform ermitteln
    all_clips = queue + posted
    last_tiktok = None
    last_youtube = None

    for clip in all_clips:
        tt = clip.get("tiktok_posted_at")
        yt = clip.get("youtube_posted_at")
        sched = clip.get("scheduled_at")

        if tt:
            dt = datetime.fromisoformat(tt.replace("Z", "+00:00"))
            if not last_tiktok or dt > last_tiktok:
                last_tiktok = dt
        if yt:
            dt = datetime.fromisoformat(yt.replace("Z", "+00:00"))
            if not last_youtube or dt > last_youtube:
                last_youtube = dt
        if sched and clip.get("status") == "scheduled":
            dt = datetime.fromisoformat(sched.replace("Z", "+00:00"))
            if "tiktok" in clip.get("platforms_to_post", {}):
                if not last_tiktok or dt > last_tiktok:
                    last_tiktok = dt
            if "youtube" in str(clip.get("platforms_to_post", {})):
                if not last_youtube or dt > last_youtube:
                    last_youtube = dt

    scheduled_count = 0
    for clip in queue:
        if clip.get("scheduled_at") or clip.get("status") == "posted":
            continue
        if clip.get("status") not in ("captioned", "processed"):
            continue

        files = clip.get("files", {})
        platforms_to_post = {}

        # TikTok-Slot
        if files.get("tiktok") or files.get("tiktok_captioned"):
            slot = get_next_posting_slot("tiktok", last_tiktok)
            platforms_to_post["tiktok"] = slot.strftime("%Y-%m-%dT%H:%M:%SZ")
            last_tiktok = slot

        # YouTube Shorts-Slot
        if files.get("youtube_shorts") or files.get("youtube_shorts_captioned"):
            slot = get_next_posting_slot("youtube_shorts", last_youtube)
            platforms_to_post["youtube_shorts"] = slot.strftime("%Y-%m-%dT%H:%M:%SZ")
            if not last_youtube or slot > last_youtube:
                last_youtube = slot

        # YouTube Long-Slot
        if files.get("youtube_long"):
            slot = get_next_posting_slot("youtube_long", last_youtube)
            platforms_to_post["youtube_long"] = slot.strftime("%Y-%m-%dT%H:%M:%SZ")
            if not last_youtube or slot > last_youtube:
                last_youtube = slot

        if platforms_to_post:
            # Frühester Slot = primäres scheduled_at
            earliest = min(platforms_to_post.values())
            clip["scheduled_at"] = earliest
            clip["platforms_to_post"] = platforms_to_post
            clip["status"] = "scheduled"
            scheduled_count += 1

            print(f"  📅 {clip['clip_id']}: TikTok {platforms_to_post.get('tiktok', '—')[:16]}, "
                  f"YT {platforms_to_post.get('youtube_shorts', platforms_to_post.get('youtube_long', '—'))[:16]}")

    clips_data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(clips_path, "w", encoding="utf-8") as f:
        json.dump(clips_data, f, indent=2, ensure_ascii=False)

    return scheduled_count


def post_due_now(clips_json_path: str = "api/clips.json", dry_run: bool = False) -> None:
    """Triggert das Posting aller fälligen Clips (delegiert an tiktok_post.py + youtube_post.py)."""
    from sync.tiktok_post import post_due_clips as tiktok_post
    from sync.youtube_post import post_due_clips as youtube_post

    print("\n=== Starte fällige Posts ===")
    tiktok_post(clips_json_path, dry_run)
    youtube_post(clips_json_path, dry_run)


def print_schedule(clips_json_path: str = "api/clips.json") -> None:
    """Gibt die aktuelle Posting-Queue aus."""
    clips_path = Path(clips_json_path)
    if not clips_path.exists():
        print("Keine clips.json gefunden.")
        return

    with open(clips_path, encoding="utf-8") as f:
        clips_data = json.load(f)

    queue = clips_data.get("queue", [])
    posted = clips_data.get("posted", [])

    print(f"\n{'='*60}")
    print(f"SF Finance Clip-Schedule")
    print(f"{'='*60}")
    print(f"\nQueue ({len(queue)} Clips):")
    for clip in sorted(queue, key=lambda c: c.get("scheduled_at", "9999")):
        status = clip.get("status", "?")
        sched = clip.get("scheduled_at", "unscheduled")[:16]
        hook = clip.get("hook", "?")[:50]
        tt_id = clip.get("tiktok_video_id", "—")
        yt_id = clip.get("youtube_video_id", "—")
        print(f"  [{status}] {sched} | {hook} | TT:{tt_id} YT:{yt_id}")

    print(f"\nGepostet ({len(posted)} Clips):")
    for clip in posted[-5:]:
        hook = clip.get("hook", "?")[:50]
        tt_id = clip.get("tiktok_video_id", "—")
        yt_id = clip.get("youtube_video_id", "—")
        posted_at = clip.get("tiktok_posted_at", "?")[:10]
        print(f"  [{posted_at}] {hook} | TT:{tt_id} YT:{yt_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SF Finance Clip-Scheduler")
    parser.add_argument("--clips-json", default="api/clips.json")
    parser.add_argument("--post-due", action="store_true",
                        help="Fällige Clips jetzt posten")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--show", action="store_true", help="Queue anzeigen")
    args = parser.parse_args()

    if args.show:
        print_schedule(args.clips_json)
    elif args.post_due:
        post_due_now(args.clips_json, args.dry_run)
    else:
        print("\n=== SF Finance Clip-Scheduler ===")
        count = schedule_clips(args.clips_json)
        print(f"✓ {count} Clips gescheduled.")
        print_schedule(args.clips_json)
