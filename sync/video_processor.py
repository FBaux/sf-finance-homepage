"""
SF Finance — Video-Prozessor
Schneidet Clips aus Rohmaterial, konvertiert Formate und optimiert für Plattformen.

Plattform-Spezifikationen:
  TikTok / YouTube Shorts: 9:16 Vertikal, 1080x1920px, max 60s, H.264
  YouTube Long-form: 16:9, 1920x1080px, H.264

Verwendung:
  python sync/video_processor.py [--input video.mp4] [--clips-json api/clips.json]
"""

import os, json, subprocess, tempfile, shutil
from pathlib import Path
from datetime import datetime, timezone


PLATFORMS = {
    "tiktok": {
        "width": 1080, "height": 1920,
        "max_duration": 59,
        "bitrate": "8M",
        "audio_bitrate": "128k",
        "fps": 30,
    },
    "youtube_shorts": {
        "width": 1080, "height": 1920,
        "max_duration": 59,
        "bitrate": "8M",
        "audio_bitrate": "128k",
        "fps": 30,
    },
    "youtube_long": {
        "width": 1920, "height": 1080,
        "max_duration": 3600,
        "bitrate": "10M",
        "audio_bitrate": "192k",
        "fps": 30,
    },
}


def detect_crop_center(video_path: str, timestamp: float = 5.0) -> tuple[int, int]:
    """
    Erkennt das Gesicht/Hauptmotiv im Video und gibt den Crop-Mittelpunkt zurück.
    Fallback: Bildmitte.
    """
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None, None

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            # Größtes Gesicht nehmen
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            cx = x + w // 2
            return cx, frame.shape[0] // 2  # X-Mitte des Gesichts, Y = Bildmitte

    except ImportError:
        pass
    except Exception as e:
        print(f"  Gesichtserkennung Fehler: {e}")

    return None, None


def build_crop_filter(src_width: int, src_height: int, target_width: int, target_height: int,
                      cx: int = None) -> str:
    """Erstellt den FFmpeg crop+scale Filter für das gewünschte Seitenverhältnis."""
    src_ratio = src_width / src_height
    target_ratio = target_width / target_height

    if src_ratio > target_ratio:
        # Quelle ist breiter → vertikal cropppen (links/rechts abschneiden)
        new_w = int(src_height * target_ratio)
        new_h = src_height
        x_offset = cx - new_w // 2 if cx else (src_width - new_w) // 2
        x_offset = max(0, min(x_offset, src_width - new_w))
        crop = f"crop={new_w}:{new_h}:{x_offset}:0"
    else:
        # Quelle ist schmaler → horizontal croppen (oben/unten abschneiden)
        new_w = src_width
        new_h = int(src_width / target_ratio)
        y_offset = (src_height - new_h) // 2
        crop = f"crop={new_w}:{new_h}:0:{y_offset}"

    return f"{crop},scale={target_width}:{target_height}"


def get_video_info(video_path: str) -> dict:
    """Gibt Breite, Höhe und Dauer des Videos zurück."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", video_path],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)
        video_stream = next(
            (s for s in info.get("streams", []) if s.get("codec_type") == "video"), {}
        )
        return {
            "width": video_stream.get("width", 1920),
            "height": video_stream.get("height", 1080),
            "duration": float(info.get("format", {}).get("duration", 0))
        }
    except Exception as e:
        print(f"  ffprobe Fehler: {e}")
        return {"width": 1920, "height": 1080, "duration": 0}


def extract_and_process_clip(
    source_video: str,
    start: float,
    end: float,
    output_path: str,
    platform: str,
    normalize_audio: bool = True
) -> bool:
    """
    Extrahiert einen Clip und konvertiert ihn für die Zielplattform.
    Gibt True zurück bei Erfolg.
    """
    spec = PLATFORMS.get(platform, PLATFORMS["tiktok"])
    duration = min(end - start, spec["max_duration"])

    src_info = get_video_info(source_video)
    cx, _ = detect_crop_center(source_video, start + duration / 2)

    crop_filter = build_crop_filter(
        src_info["width"], src_info["height"],
        spec["width"], spec["height"],
        cx
    )

    # Audio-Normalisierung auf -14 LUFS (TikTok-Standard)
    audio_filter = "loudnorm=I=-14:TP=-1.5:LRA=11" if normalize_audio else "acopy"

    vf_filter = f"{crop_filter},fps={spec['fps']}"

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", source_video,
        "-t", str(duration),
        "-vf", vf_filter,
        "-af", audio_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-b:v", spec["bitrate"],
        "-maxrate", spec["bitrate"],
        "-bufsize", f"{int(spec['bitrate'][:-1]) * 2}M",
        "-c:a", "aac",
        "-b:a", spec["audio_bitrate"],
        "-movflags", "+faststart",
        output_path
    ]

    print(f"  FFmpeg: {start:.1f}s–{start+duration:.1f}s → {Path(output_path).name}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"  FFmpeg Fehler: {result.stderr[-500:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  FFmpeg Timeout nach 300s")
        return False
    except Exception as e:
        print(f"  Fehler: {e}")
        return False


def process_all_clips(clips_json_path: str = "api/clips.json",
                      output_dir: str = "processed") -> list[dict]:
    """
    Verarbeitet alle Kandidaten aus clips.json und erstellt plattformspezifische Clip-Dateien.
    Gibt Liste der verarbeiteten Clips zurück.
    """
    clips_path = Path(clips_json_path)
    if not clips_path.exists():
        print(f"Fehler: {clips_json_path} nicht gefunden. Erst clip_analyzer.py ausführen.")
        return []

    with open(clips_path, encoding="utf-8") as f:
        clips_data = json.load(f)

    source_video = clips_data.get("source_video", "")
    candidates = clips_data.get("candidates", [])

    if not source_video or not candidates:
        print("Keine Clip-Kandidaten gefunden.")
        return []

    # Source-Video suchen (im Repo-Root oder in /tmp)
    source_path = None
    for search_path in [source_video, f"/tmp/{source_video}", f"input/{source_video}"]:
        if Path(search_path).exists():
            source_path = search_path
            break

    if not source_path:
        print(f"Quell-Video nicht gefunden: {source_video}")
        print("Tipp: Lege das Video nach /tmp/ oder input/ ab")
        return []

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    processed = []

    print(f"\n=== Verarbeite {len(candidates)} Clip-Kandidaten ===")

    for i, candidate in enumerate(candidates, 1):
        start = float(candidate.get("start", 0))
        end = float(candidate.get("end", start + 60))
        platform = candidate.get("platform", "both")
        hook = candidate.get("hook", f"Clip {i}")[:50]

        clip_id = f"clip_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{i:03d}"
        print(f"\nClip {i}/{len(candidates)}: {clip_id} ({start:.0f}s–{end:.0f}s)")

        clip_files = {}

        # Plattformen bestimmen
        platforms_to_process = []
        if platform in ("tiktok", "both"):
            platforms_to_process.append("tiktok")
        if platform in ("youtube_shorts", "both"):
            platforms_to_process.append("youtube_shorts")
        if platform in ("youtube_long",):
            platforms_to_process.append("youtube_long")
        if not platforms_to_process:
            platforms_to_process = ["tiktok", "youtube_shorts"]

        for plat in platforms_to_process:
            out_file = str(Path(output_dir) / f"{clip_id}_{plat}.mp4")
            success = extract_and_process_clip(source_path, start, end, out_file, plat)
            if success:
                clip_files[plat] = out_file
                print(f"  ✓ {plat}: {out_file}")
            else:
                print(f"  ✗ {plat}: Fehler")

        if clip_files:
            processed.append({
                "clip_id": clip_id,
                "hook": hook,
                "start": start,
                "end": end,
                "files": clip_files,
                "score": candidate.get("score", 0),
                "why_viral": candidate.get("why_viral", ""),
                "status": "processed",
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            })

    # Queue in clips.json aktualisieren
    clips_data["queue"] = processed + clips_data.get("queue", [])
    clips_data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(clips_path, "w", encoding="utf-8") as f:
        json.dump(clips_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ {len(processed)} Clips verarbeitet und in Queue eingetragen.")
    return processed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SF Finance Video-Prozessor")
    parser.add_argument("--input", help="Quell-Video-Datei (überschreibt clips.json Eintrag)")
    parser.add_argument("--clips-json", default="api/clips.json", help="Pfad zu clips.json")
    parser.add_argument("--output-dir", default="processed", help="Ausgabe-Verzeichnis")
    args = parser.parse_args()

    if args.input:
        # Direkte Verarbeitung mit übergebenem Video
        info = get_video_info(args.input)
        print(f"Video: {args.input} ({info['width']}x{info['height']}, {info['duration']:.1f}s)")

    process_all_clips(args.clips_json, args.output_dir)
