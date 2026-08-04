#!/bin/bash
# SF Finance — Website-Bilder generieren
# Ausführen: bash assets/generate-images.sh

SKILL="$HOME/.claude/plugins/cache/glebis-skills/nano-banana/f19030eb2bdf/scripts/nano_banana.py"
OUT="$(dirname "$0")/img"

# Key aus .env laden falls nicht gesetzt
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$GEMINI_API_KEY" ] && [ -f "$SCRIPT_DIR/.env" ]; then
  export GEMINI_API_KEY=$(grep GEMINI_API_KEY "$SCRIPT_DIR/.env" | cut -d'=' -f2)
fi

if [ -z "$GEMINI_API_KEY" ]; then
  echo "❌ GEMINI_API_KEY nicht gesetzt."
  exit 1
fi

echo "🎨 Generiere 5 Website-Bilder..."

python3 "$SKILL" \
  "Cinematic hero background for a premium financial brand. Deep navy blue and royal blue atmosphere, dramatic gold light rays from above, abstract financial cityscape silhouette, luxury wealth, wide cinematic, no text, no logos, photorealistic" \
  --platform slides "$OUT/hero-bg.jpg" &

python3 "$SKILL" \
  "Premium financial trading chart on deep navy background. Glowing gold candlestick chart trending upward, abstract luxury finance, subtle blue grid, warm gold light, cinematic dark mood, no text, square" \
  --platform square "$OUT/pillar-trading.jpg" &

python3 "$SKILL" \
  "Abstract golden network of interconnected nodes on deep navy blue. Digital affiliate marketing growth, glowing gold nodes, blue connections, premium luxury digital style, no text, square" \
  --platform square "$OUT/pillar-affiliate.jpg" &

python3 "$SKILL" \
  "Abstract golden staircase rising upward on deep navy. Financial education growth concept, gold gradient steps, blue ambient light, premium luxury modern finance, no text, square" \
  --platform square "$OUT/pillar-education.jpg" &

python3 "$SKILL" \
  "Düsseldorf skyline at golden hour, Rhine river reflection, dramatic blue and gold city lights, premium moody photography, luxury financial district, wide landscape, photorealistic" \
  --platform blog "$OUT/about-dus.jpg" &

wait
echo "✅ Fertig! Bilder gespeichert in: $OUT"
ls -lh "$OUT"/*.jpg 2>/dev/null
