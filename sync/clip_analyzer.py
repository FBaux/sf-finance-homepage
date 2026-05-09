"""
SF Finance — KI-gestützte Clip-Erkennung
Analysiert Rohmaterial mit Whisper (Transkription) und Claude API (Viral-Scoring).
Schreibt Ergebnisse nach api/clips.json.

Benötigte Umgebungsvariablen:
  ANTHROPIC_API_KEY — Claude API Key für Segment-Analyse
  INPUT_VIDEO       — Pfad zur Eingabevideo-Datei

Verwendung:
  python sync/clip_analyzer.py --input video.mp4 [--dry-run]
"""

import os, json, argparse, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path


def transcribe_video(video_path: str) -> list[dict]:
    """Transkribiert Video mit Whisper und gibt Segmente mit Timestamps zurück."""
    try:
        import whisper
        print(f"Lade Whisper-Modell (base)...")
        model = whisper.load_model("base")
        print(f"Transkribiere: {video_path}")
        result = model.transcribe(
            video_path,
            language="de",
            word_timestamps=True,
            verbose=False
        )
        return result.get("segments", [])
    except ImportError:
        print("Whisper nicht installiert. Nutze Fallback-Transkription.")
        return []
    except Exception as e:
        print(f"Transkriptions-Fehler: {e}")
        return []


def score_segment(segment_text: str, start: float, duration: float) -> float:
    """
    Berechnet Virality-Score eines Segments basierend auf:
    - Deutschen Finance-Trigger-Keywords
    - Segment-Position (Anfang = Bonus)
    - Satzlänge (kurze, prägnante Sätze = höherer Score)
    """
    text_lower = segment_text.lower()

    # High-value Finance & Trading Keywords (Deutsch)
    hook_keywords = [
        "krass", "unglaublich", "fehler", "verlust", "gewinn", "pump",
        "breakout", "ich zeige", "schaut mal", "das ist der trick",
        "niemand redet darüber", "so verdiene ich", "warum ich",
        "100%", "200%", "+", "k€", "€ in", "geheimnis",
        "prop trading", "funded", "challenge", "drawdown",
        "das wäre mein schlimmster", "diese eine sache",
    ]

    keyword_score = sum(2.0 if kw in text_lower else 0 for kw in hook_keywords)

    # Kurze, impactvolle Segmente bevorzugen (15–60 Sekunden ideal)
    if 15 <= duration <= 60:
        length_score = 3.0
    elif 10 <= duration <= 90:
        length_score = 1.5
    else:
        length_score = 0.5

    # Hook-Bonus: Segmente am Anfang des Videos (< 120s) sind stärker
    position_score = 2.0 if start < 120 else (1.0 if start < 300 else 0)

    # Fragesätze und Ausrufezeichen signalisieren Engagement
    engagement_score = (
        text_lower.count("?") * 0.5 +
        text_lower.count("!") * 0.5
    )

    return round(keyword_score + length_score + position_score + engagement_score, 2)


def analyze_with_claude(segments: list[dict], video_path: str) -> list[dict]:
    """
    Nutzt Claude API um die besten 3–5 Clip-Kandidaten aus allen Segmenten zu identifizieren.
    Gibt eine Liste von Clip-Kandidaten mit Start/End-Timestamps zurück.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ANTHROPIC_API_KEY nicht gesetzt — nutze lokales Keyword-Scoring.")
        return select_clips_locally(segments)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        # Transkript für Claude aufbereiten
        transcript_text = "\n".join([
            f"[{s['start']:.1f}s–{s['end']:.1f}s]: {s['text'].strip()}"
            for s in segments
        ])

        prompt = f"""Du bist ein Social-Media-Experte für deutschsprachige Finance/Trading-Inhalte.

Analysiere dieses Video-Transkript und identifiziere die 3–5 besten Segmente für virale TikTok/YouTube-Shorts-Clips.

TRANSKRIPT:
{transcript_text}

Kriterien für virale Clips:
1. Starker Hook in den ersten 3 Sekunden ("Das ist mein größter Fehler...", Zahlen, Provokationen)
2. Einzigartiger Mehrwert oder Geheimtipp
3. Emotionale Sprache (Überraschung, Motivation, Warnung)
4. Klarer Anfang und Ende (kein mitten im Satz)
5. Ideal 30–90 Sekunden lang

Antworte NUR mit diesem JSON (kein anderer Text):
{{
  "clips": [
    {{
      "start": <Startzeit in Sekunden>,
      "end": <Endzeit in Sekunden>,
      "hook": "<Der erste Satz / Hook des Clips>",
      "why_viral": "<Kurze Begründung warum dieser Clip viral geht>",
      "score": <Virality-Score 1-10>,
      "platform": "<tiktok|youtube_shorts|both>"
    }}
  ]
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        # JSON aus der Antwort extrahieren
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx >= 0:
            result = json.loads(response_text[start_idx:end_idx])
            clips = result.get("clips", [])
            print(f"Claude hat {len(clips)} Clip-Kandidaten identifiziert.")
            return clips

    except Exception as e:
        print(f"Claude API Fehler: {e} — nutze lokales Scoring als Fallback.")

    return select_clips_locally(segments)


def select_clips_locally(segments: list[dict]) -> list[dict]:
    """Fallback: Wählt Clips basierend auf lokalem Keyword-Scoring."""
    if not segments:
        return []

    # Segmente in ~60-Sekunden-Blöcke gruppieren
    clip_candidates = []
    current_block = []
    block_start = 0.0

    for seg in segments:
        current_block.append(seg)
        block_duration = seg["end"] - block_start

        if block_duration >= 45 or seg == segments[-1]:
            block_text = " ".join(s["text"] for s in current_block)
            score = score_segment(block_text, block_start, block_duration)

            clip_candidates.append({
                "start": block_start,
                "end": seg["end"],
                "hook": current_block[0]["text"].strip()[:100],
                "why_viral": f"Keyword-Score: {score}",
                "score": min(score, 10.0),
                "platform": "both"
            })

            block_start = seg["end"]
            current_block = []

    # Top 5 nach Score sortieren
    clip_candidates.sort(key=lambda x: x["score"], reverse=True)
    return clip_candidates[:5]


def get_video_duration(video_path: str) -> float:
    """Gibt die Videodauer in Sekunden zurück."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except Exception:
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="SF Finance Clip-Analyzer")
    parser.add_argument("--input", help="Pfad zur Eingabevideo-Datei")
    parser.add_argument("--dry-run", action="store_true", help="Kein Schreiben nach clips.json")
    args = parser.parse_args()

    video_path = args.input or os.environ.get("INPUT_VIDEO", "")
    if not video_path or not Path(video_path).exists():
        print(f"Fehler: Video-Datei nicht gefunden: {video_path}")
        return

    print(f"\n=== SF Finance Clip-Analyzer ===")
    print(f"Video: {video_path}")
    duration = get_video_duration(video_path)
    print(f"Dauer: {duration:.1f}s ({duration/60:.1f} Minuten)")

    # Schritt 1: Transkription
    print("\n[1/3] Transkribiere Video mit Whisper...")
    segments = transcribe_video(video_path)
    print(f"  → {len(segments)} Segmente erkannt")

    # Schritt 2: Clip-Analyse mit Claude
    print("\n[2/3] Analysiere Segmente auf Viral-Potential...")
    clips = analyze_with_claude(segments, video_path)
    print(f"  → {len(clips)} Clip-Kandidaten gefunden")

    # Schritt 3: clips.json aktualisieren
    clips_data = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_video": str(Path(video_path).name),
        "video_duration": round(duration, 1),
        "candidates": clips,
        "queue": [],
        "posted": [],
        "stats_summary": {
            "total_clips": 0,
            "total_tiktok_views": 0,
            "total_youtube_views": 0,
            "best_performing_clip_id": None
        }
    }

    if args.dry_run:
        print("\n[DRY-RUN] clips.json würde enthalten:")
        print(json.dumps(clips_data, indent=2, ensure_ascii=False))
    else:
        print("\n[3/3] Schreibe Ergebnisse nach api/clips.json...")
        os.makedirs("api", exist_ok=True)

        # Bestehende posted-Clips und stats erhalten
        clips_path = Path("api/clips.json")
        if clips_path.exists():
            try:
                existing = json.loads(clips_path.read_text(encoding="utf-8"))
                clips_data["queue"] = existing.get("queue", [])
                clips_data["posted"] = existing.get("posted", [])
                clips_data["stats_summary"] = existing.get("stats_summary", clips_data["stats_summary"])
            except Exception:
                pass

        with open("api/clips.json", "w", encoding="utf-8") as f:
            json.dump(clips_data, f, indent=2, ensure_ascii=False)
        print(f"  → Gespeichert: api/clips.json")

    print("\n=== Clip-Analyse abgeschlossen ===")
    for i, clip in enumerate(clips, 1):
        print(f"  Clip {i}: {clip['start']:.0f}s–{clip['end']:.0f}s | Score: {clip['score']} | {clip['hook'][:60]}...")


if __name__ == "__main__":
    main()
