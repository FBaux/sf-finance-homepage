# AI-TOOLING — Bewertung der „kostenlosen Alternativen"

Bewertung vom 08.08.2026. Grundlage: fünf Karten aus einem Creator-Carousel
(TikTok/Instagram, @digitalsaim), die je ein Bezahltool einer kostenlosen
Alternative gegenüberstellen. Geprüft wurde nicht, ob die Tools gut sind,
sondern ob sie zu dem passen, was dieses Repo tatsächlich braucht.

---

## Kurzfassung

| # | Kategorie | Paid (Carousel) | Free (Carousel) | Bedarf hier | Urteil |
|---|---|---|---|---|---|
| 02 | Image Creation | Midjourney $60 | Nano Banana | **ja, laufend** | **Läuft bereits** — `assets/generate-images.sh` |
| 03 | Cinematic Creation | Runway ML $76 | Stable Diffusion | nein | Kein Anwendungsfall im Repo |
| 04 | Video Generation | Higgsfield $49 | Hailuo | **später** | Erst wenn Social-Content startet — Free-Tier unbrauchbar |
| 05 | Presentation / Design | Canva $17 | Lovart | nein | Website ist handcodiert, keine Decks im Repo |
| 07 | Voice Generation | ElevenLabs $99 | MiniMax | **später** | Für Kursvertonung — Free-Tier unbrauchbar |

**Ergebnis:** Von fünf Alternativen ist genau eine für dieses Projekt
einsetzbar — und die ist bereits im Einsatz. Zwei sind später relevant, aber
dann nicht in der kostenlosen Variante. Zwei lösen ein Problem, das wir nicht
haben.

---

## Zwei Filter, an denen die meisten „$0"-Angaben scheitern

### 1. Kommerzielle Nutzungsrechte

fsfinance.de ist der Außenauftritt einer GbR. Jedes Bild, Video und Voiceover
auf dieser Seite ist kommerzielle Nutzung — auch ohne direkten Verkauf. Die
Free-Tiers der genannten Tools sind überwiegend Test-Kontingente ohne
kommerzielle Lizenz:

- **Hailuo / MiniMax:** Free-Tier ohne kommerzielle Rechte, mit Wasserzeichen,
  720p, Renders verfallen nach ca. drei Tagen. Kommerzielle Rechte erst ab
  Paid (~$9,99/Monat).
- **ElevenLabs:** Free-Tier ohne kommerzielle Lizenz, mit Attributionspflicht.
- **Lovart:** 100 Credits täglich, kein dauerhaftes Gratis-Kontingent.
- **Stable Diffusion:** je nach Modellversion. SD 1.5 / SDXL (CreativeML Open
  RAIL-M) kommerziell frei. SD 3 / 3.5 laufen unter der Stability AI Community
  License — kostenlos unter $1 Mio. Jahresumsatz, aber **mit Attributionspflicht**
  („Powered by Stability AI") bei Weitergabe.
- **Nano Banana** (Gemini Image, Google AI Studio): kommerzielle Nutzung im
  Free-Tier erlaubt, aber Google verwendet Ein- und Ausgaben zur
  Modellverbesserung, inklusive menschlicher Review. Für Website-Motive ohne
  vertrauliche Inhalte unkritisch — für Kundendaten oder unveröffentlichte
  Zahlen nicht.

### 2. EU AI Act, Artikel 50 — seit 02.08.2026 anwendbar

Die Transparenzpflichten gelten seit sechs Tagen. Relevant für uns:
KI-generierte Bild-, Audio- und Videoinhalte müssen als solche erkennbar sein —
in menschenlesbarer **und** maschinenlesbarer Form. Bußgeldrahmen bis
15 Mio. EUR oder 3 % des weltweiten Jahresumsatzes.

Vor dem 02.08.2026 erzeugte Inhalte müssen nicht rückwirkend gekennzeichnet
werden. Die bestehenden Bilder unter `assets/img/` stammen vom 04.08. bzw.
früher und fallen damit in die Übergangsregel — die Kommission empfiehlt
Kennzeichnung trotzdem.

Für eine Marke, deren Kernversprechen „Transparenz muss belegbar sein" lautet
(`src/components.jsx`, `Credibility`), ist das ohnehin keine reine
Rechtsfrage. Die Kennzeichnung ist hier Teil des Produkts.

---

## Bewertung im Einzelnen

### 02 — Image Creation: Nano Banana ✅ bereits im Einsatz

`assets/generate-images.sh` generiert seit dem Redesign fünf Website-Motive
(Hero, drei Säulen-Bilder, Düsseldorf-Aufnahme) über Nano Banana mit
`GEMINI_API_KEY`. Die Alternative aus dem Carousel ist also schon die gelebte
Praxis — Midjourney wurde hier nie gebraucht.

Offener Punkt aus `PLAN.md`: „Bilder auf WebP umstellen". Das ist ein
Konvertierungsschritt (`cwebp`/`sharp`), kein Tool-Thema. Die PNG-Dateien im
Repo sind teils über 1 MB, `logo_lion_shield_transparent.png` liegt bei 3,5 MB —
da liegt mehr Ladezeit begraben als in der Wahl des Bildgenerators.

### 03 — Cinematic Creation: Stable Diffusion ❌ kein Anwendungsfall

Die Karte ist inhaltlich schief: Stable Diffusion ist ein Bildmodell, nicht
„image to video". Gemeint ist vermutlich Stable Video Diffusion. Unabhängig
davon gibt es auf der Seite keine Stelle für cinematische Videos. Die offenen
Hero-Effekte aus `HANDOFF.md` — Ken-Burns, Gold-Beams-Canvas, Scroll-Parallax —
sind CSS und Canvas, kein generiertes Video. Ein Hintergrundvideo im Hero wäre
zudem ein Rückschritt bei Ladezeit und `prefers-reduced-motion`, das in
`components.jsx` bereits sauber respektiert wird.

### 04 — Video Generation: Hailuo ⏳ später, aber nicht kostenlos

Relevanz ist real, aber noch nicht akut: Die Sektion `ContentPreview` zeigt
drei Platzhalter-Kacheln mit Badge „Geplant", der Footer listet Instagram,
TikTok und YouTube als „(folgt)", und `sync/fetch_data.py` zieht bereits
Instagram- und TikTok-Kennzahlen (aktuell mit `available: false`, weil Tokens
fehlen). Sobald diese Kanäle starten, entsteht Bedarf an Kurzvideos.

Dann aber gilt: Free-Tier ohne kommerzielle Rechte und mit Wasserzeichen ist
für einen Markenkanal nicht nutzbar. Realistisch sind ~$10/Monat.

Anmerkung zum Carousel: **Hailuo und MiniMax sind dasselbe Unternehmen.**
Karte 04 und Karte 07 verkaufen denselben Anbieter als zwei unabhängige
Empfehlungen.

### 05 — Presentation / Design: Lovart ❌ kein Anwendungsfall

Die Website ist React plus handgeschriebenes CSS mit eigenen Design-Tokens
(`assets/css/styles.css`, Dark-Navy/Gold). Es gibt keine Präsentation und kein
Grafik-Asset im Repo, das aus einem Design-Tool käme. Ein KI-Design-Agent
würde hier gegen das bestehende Designsystem arbeiten, nicht dafür.

Falls später Pitch-Decks oder Social-Templates gebraucht werden, ist das ein
Thema außerhalb dieses Repos.

### 07 — Voice Generation: MiniMax ⏳ später, aber nicht kostenlos

Denkbarer Einsatz: Vertonung der Kursinhalte im Mitgliederbereich
(`mitglieder/kurs.html` lädt `trading-kurs.html` aus einem privaten
Supabase-Bucket). Bezahlte Kursinhalte mit synthetischer Stimme sind
kommerzielle Nutzung — Free-Tier scheidet aus.

Die Preisangabe der Karte ist irreführend: ElevenLabs kostet nicht $99, um
kommerzielle Rechte zu bekommen. Der Starter-Tarif liegt bei $5/Monat und
enthält sie bereits. Der ehrliche Vergleich lautet also **$5 mit Rechten gegen
$0 ohne Rechte**, nicht $99 gegen $0.

Unabhängig vom Tool: Bei einem Bildungsangebot im Finanzbereich sollte eine
synthetische Stimme gekennzeichnet sein — siehe Art. 50.

---

## Harte Grenze: keine KI-Bilder für Personen und Belege

Drei Stellen im Repo sehen nach einer Lücke aus, die man mit einem
Bildgenerator „schnell schließen" könnte. Alle drei sind bewusst offen:

1. **Gründerfotos** — `components.jsx`, `Team`: Platzhalter „Foto folgt — {Name}"
   für drei real existierende Personen. KI-generierte Porträts realer Gründer
   auf einer Impressumsseite sind eine Falschdarstellung, unabhängig vom AI Act.
2. **Testimonials** — im Code ausdrücklich als „replaces fabricated testimonials"
   markiert und durch die `Credibility`-Sektion ersetzt. Diese Entscheidung
   nicht rückgängig machen.
3. **Performance-Belege** — die `MetricTile`-Kacheln stehen auf „Noch nicht
   veröffentlicht" und „Verifizierung folgt". Belege sind Screenshots und
   Kontoauszüge, keine generierten Bilder.

Symbolbilder (Architektur, Skyline, abstrakte Charts) sind unproblematisch und
genau das, was `generate-images.sh` heute erzeugt.

---

## Empfehlung

**Jetzt:** nichts anschaffen. Der einzige laufende Bedarf — Bildgenerierung —
ist mit Nano Banana gedeckt, und das kostenlos und kommerziell zulässig.

**Wenn die Social-Kanäle starten:** ein Video-Tool im ~$10-Bereich (Hailuo
Standard oder vergleichbar) und, falls vertont wird, ElevenLabs Starter für
$5. Zusammen unter $15/Monat mit sauberen Rechten. Die Free-Tiers taugen zum
Ausprobieren, nicht zum Veröffentlichen.

**Vor der ersten Veröffentlichung von KI-Medien:** Kennzeichnungskonzept nach
Art. 50 festlegen — sichtbarer Hinweis am Asset plus Metadaten. Am besten als
fester Bestandteil des Risiko- und Affiliate-Hinweisblocks im Footer, wo die
bestehenden Transparenzhinweise bereits stehen.

---

## Nebenbefund

`HANDOFF.md`, `PLAN.md` und diese Datei liegen im Wurzelverzeichnis eines
GitHub-Pages-Repos, das aus dem Root ausliefert. Sie sind damit öffentlich
abrufbar (`fsfinance.de/PLAN.md`). Bisher steht dort nichts Vertrauliches,
aber es ist eine Eigenschaft, die man kennen sollte, bevor interne Notizen
dazukommen.

---

## Quellen

- [Hailuo/MiniMax Pricing und Lizenz](https://felloai.com/minimax-pricing/) ·
  [Hailuo 2.3 Pricing](https://magichour.ai/blog/hailuo-23-pricing)
- [ElevenLabs Free Plan Limits](https://aivoicereview.com/guides/elevenlabs-free-plan-limits) ·
  [ElevenLabs Lizenzleitfaden](https://www.licenseorg.com/blog/elevenlabs-licensing-guide-ai-voices)
- [Lovart Pricing](https://www.lovart.ai/pricing)
- [Stability AI Community License](https://stability.ai/license) ·
  [Stable Diffusion Output Rights](https://terms.law/ai-output-rights/stable-diffusion/)
- [Gemini Free-Tier Datennutzung](https://docs.bswen.com/blog/2026-03-23-gemini-free-tier-data-privacy/)
- [AI Act Art. 50 — Transparenzpflichten](https://artificialintelligenceact.eu/transparency-rules-article-50/) ·
  [Leitlinien der EU-Kommission](https://digital-strategy.ec.europa.eu/en/policies/guidelines-transparency-ai-generated-content) ·
  [Fristen und Bußgelder](https://datamatters.sidley.com/2026/06/24/eu-ai-act-transparency-obligations-preparing-for-compliance-by-2-august-2026/)
