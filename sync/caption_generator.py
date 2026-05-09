"""
SF Finance — Caption & Overlay-Generator
Erstellt eingebrannte Untertitel (TikTok-Stil) und Branding-Overlays für Clips.

Overlays:
  - Wort-für-Wort Untertitel (Großbuchstaben, zentriert, Bottom Third)
  - "@fsfinance" Handle oben links
  - CTA-Banner am Ende ("Folge mir für mehr Trading-Tipps!")
  - Optionale Fortschrittsleiste

Verwendung:
  python sync/caption_generator.py [--clips-json api/clips.json] [--output-dir captioned]
"""

import os, json, subprocess, tempfile
from pathlib import Path
from datetime import datetime, timezone


def transcribe_clip(clip_path: str, language: str = "de") -> list[dict]:
    """Transkribiert einen einzelnen Clip und gibt Wort-Timestamps zurück."""
    try:
        import whisper
        model = whisper.load_model("tiny")  # tiny für Clips ausreichend und schneller
        result = model.transcribe(
            clip_path,
            language=language,
            word_timestamps=True,
            verbose=False
        )
        # Wort-Level Timestamps extrahieren
        words = []
        for seg in result.get("segments", []):
            for word_info in seg.get("words", []):
                words.append({
                    "word": word_info["word"].strip().upper(),
                    "start": word_info["start"],
                    "end": word_info["end"]
                })
        return words
    except ImportError:
        print("Whisper nicht verfügbar — Caption-Overlay übersprungen.")
        return []
    except Exception as e:
        print(f"  Transkriptions-Fehler: {e}")
        return []


def words_to_srt(words: list[dict], max_words_per_line: int = 3) -> str:
    """Konvertiert Wort-Timestamps in SRT-Format (Gruppen von max_words_per_line)."""
    if not words:
        return ""

    srt_lines = []
    idx = 1
    i = 0

    while i < len(words):
        group = words[i:i + max_words_per_line]
        start = group[0]["start"]
        end = group[-1]["end"]
        text = " ".join(w["word"] for w in group)

        # SRT Timestamp-Format: HH:MM:SS,mmm
        def to_srt_time(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        srt_lines.append(f"{idx}")
        srt_lines.append(f"{to_srt_time(start)} --> {to_srt_time(end)}")
        srt_lines.append(text)
        srt_lines.append("")

        idx += 1
        i += max_words_per_line

    return "\n".join(srt_lines)


def add_captions_ffmpeg(
    input_path: str,
    output_path: str,
    srt_content: str,
    handle: str = "@fsfinance",
    cta_text: str = "Folge mir für mehr Trading-Tipps! 📈",
    add_progress_bar: bool = False
) -> bool:
    """
    Fügt Captions und Branding-Overlays per FFmpeg ein.
    Nutzt ASS-Format für bessere Styling-Kontrolle (TikTok-Stil: bold, groß, zentriert).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # SRT-Datei schreiben
        srt_path = os.path.join(tmp_dir, "captions.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        # ASS-Stil: Gold (#FFD700) auf dunklem Hintergrund, TikTok-Stil
        ass_style = (
            "Style: Default,Arial Black,52,&H00FFD700,&H000000FF,&H80000000,&H00000000,"
            "1,0,0,0,100,100,0,0,1,3,2,2,10,10,60,1"
        )

        # Videodauer ermitteln für CTA-Timing
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", input_path],
                capture_output=True, text=True, check=True
            )
            duration = float(json.loads(result.stdout)["format"]["duration"])
        except Exception:
            duration = 60.0

        cta_start = max(0, duration - 4)

        # FFmpeg drawtext für Handle (@fsfinance) oben links
        handle_filter = (
            f"drawtext=text='{handle}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":fontsize=36:fontcolor=white:x=20:y=20"
            f":shadowcolor=black:shadowx=2:shadowy=2"
        )

        # CTA-Banner am Ende
        cta_filter = (
            f"drawtext=text='{cta_text}'"
            f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":fontsize=34:fontcolor=white:x=(w-text_w)/2:y=h-100"
            f":shadowcolor=black:shadowx=2:shadowy=2"
            f":enable='between(t,{cta_start},{duration})'"
        )

        # Fortschrittsbalken (optional)
        progress_filter = (
            f"drawbox=x=0:y=h-8:w='iw*t/{duration}':h=8:color=#FFD700:t=fill"
            if add_progress_bar else ""
        )

        # Video-Filter zusammenstellen
        vf_parts = [
            f"subtitles={srt_path}:force_style='{ass_style}'",
            handle_filter,
            cta_filter,
        ]
        if progress_filter:
            vf_parts.append(progress_filter)

        vf = ",".join(vf_parts)

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "copy",
            "-movflags", "+faststart",
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"  FFmpeg Caption-Fehler: {result.stderr[-300:]}")
                # Fallback: Video ohne Captions kopieren
                shutil.copy2(input_path, output_path)
                return False
            return True
        except Exception as e:
            print(f"  Caption-Fehler: {e}")
            import shutil
            shutil.copy2(input_path, output_path)
            return False


def process_clip_captions(
    clip_info: dict,
    output_dir: str = "captioned",
    add_progress_bar: bool = False
) -> dict:
    """Fügt Captions und Overlays zu allen Plattform-Varianten eines Clips hinzu."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    clip_id = clip_info["clip_id"]
    captioned_files = {}

    for platform, file_path in clip_info.get("files", {}).items():
        if not Path(file_path).exists():
            print(f"  Datei nicht gefunden: {file_path}")
            continue

        print(f"\n  Caption: {clip_id} ({platform})")

        # Clip transkribieren
        words = transcribe_clip(file_path)
        srt_content = words_to_srt(words) if words else ""

        if not srt_content:
            print(f"  Keine Transkription — kopiere ohne Captions.")
            import shutil
            out_path = str(Path(output_dir) / f"{clip_id}_{platform}_captioned.mp4")
            shutil.copy2(file_path, out_path)
            captioned_files[platform] = out_path
            continue

        out_path = str(Path(output_dir) / f"{clip_id}_{platform}_captioned.mp4")
        success = add_captions_ffmpeg(
            file_path, out_path, srt_content,
            add_progress_bar=add_progress_bar
        )

        if success:
            print(f"  ✓ Captioned: {out_path}")
        else:
            print(f"  ⚠ Caption fehlgeschlagen, Original verwendet: {out_path}")

        captioned_files[platform] = out_path

    return captioned_files


def process_all_captions(
    clips_json_path: str = "api/clips.json",
    output_dir: str = "captioned"
) -> None:
    """Verarbeitet alle Clips in der Queue und fügt Captions hinzu."""
    clips_path = Path(clips_json_path)
    if not clips_path.exists():
        print(f"Fehler: {clips_json_path} nicht gefunden.")
        return

    with open(clips_path, encoding="utf-8") as f:
        clips_data = json.load(f)

    queue = clips_data.get("queue", [])
    pending = [c for c in queue if c.get("status") == "processed"]

    print(f"\n=== Caption-Generator: {len(pending)} Clips ===")

    for clip in pending:
        captioned = process_clip_captions(clip, output_dir)
        if captioned:
            clip["files"].update(captioned)
            clip["status"] = "captioned"
            clip["captioned_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    clips_data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(clips_path, "w", encoding="utf-8") as f:
        json.dump(clips_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ {len(pending)} Clips mit Captions versehen.")


if __name__ == "__main__":
    import argparse, shutil
    parser = argparse.ArgumentParser(description="SF Finance Caption-Generator")
    parser.add_argument("--clips-json", default="api/clips.json")
    parser.add_argument("--output-dir", default="captioned")
    parser.add_argument("--progress-bar", action="store_true", help="Fortschrittsbalken hinzufügen")
    args = parser.parse_args()

    process_all_captions(args.clips_json, args.output_dir)
