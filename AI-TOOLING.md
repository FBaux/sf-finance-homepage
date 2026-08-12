# AI-TOOLING — Bewertung der „kostenlosen Alternativen"

Bewertung vom 08.08.2026. Grundlage: zehn Karten aus zwei Creator-Carousels
(@digitalsaim und @theromanknox), die je ein Bezahltool einer kostenlosen
Alternative gegenüberstellen. Geprüft wurde nicht, ob die Tools gut sind,
sondern ob sie zu dem passen, was dieses Repo tatsächlich braucht.

---

## Kurzfassung

| Kategorie | Free-Alternative | Bedarf hier | Urteil |
|---|---|---|---|
| Image Creation | Nano Banana | **ja, laufend** | **Läuft bereits** — `assets/generate-images.sh` |
| Image Generation | Google Flow | ja, laufend | Gleiche Modellfamilie, nur mit Oberfläche — kein Zugewinn |
| Video Generation | Hailuo | später | Free-Tier ohne kommerzielle Rechte |
| Video Generation | ArtFlow | später | Free-Tier mit Wasserzeichen |
| Voice Generation | MiniMax | später | Free-Tier ohne kommerzielle Rechte |
| Voice Cloning | FishAudio | **fraglich** | Open-Source-Modell ist **non-commercial** lizenziert |
| Avatar Creation | Hedra | **fraglich** | Free-Tier ohne kommerzielle Rechte + Deepfake-Recht |
| AI Avatar | HeyGen | **fraglich** | 3 Videos/Monat, Wasserzeichen + Deepfake-Recht |
| Presentation / Design | Lovart | nein | Website ist handcodiert, keine Decks im Repo |
| Cinematic Creation | Stable Diffusion | nein | Kein Anwendungsfall |

**Ergebnis:** Von zehn Alternativen ist genau eine ohne Einschränkung
einsetzbar — und die ist bereits im Einsatz. Zwei sind später relevant, dann
aber nicht in der kostenlosen Variante. Drei berühren Persönlichkeitsrechte
und sind keine reine Budgetfrage. Vier lösen ein Problem, das wir nicht haben.

---

## Warnung vorweg: die Zahlen der Carousels sind nicht belastbar

Die beiden Carousels widersprechen sich gegenseitig bei denselben Produkten:

| Produkt | @digitalsaim | @theromanknox | Tatsächlich |
|---|---|---|---|
| **HeyGen** | „Paid, $39/Monat" | „**Free**, $0/Monat" | Beides halb wahr: Free-Tier existiert, aber 3 Videos/Monat, 720p, Wasserzeichen, nicht kommerziell. Creator ab $29. |
| **ElevenLabs** | „$99/Monat" | „$6/Monat" | Starter ab $5/Monat, enthält bereits kommerzielle Rechte. Die $99 sind der Pro-Tarif. |
| **Higgsfield** | „$49/Monat" | „$19/Monat" | Je nach Tarifstufe — beide Karten greifen eine andere heraus. |

Dasselbe Produkt steht einmal auf der teuren und einmal auf der kostenlosen
Seite. Die Zahlen sind ausgewählte Tarifstufen, keine Vergleichsbasis. Für
eine Budgetplanung taugen sie nicht.

Zwei weitere sachliche Fehler: **Hailuo und MiniMax sind derselbe Anbieter**,
werden aber als zwei unabhängige Empfehlungen geführt. Und **Google Flow ist
kein Bildgenerator**, sondern Googles Filmmaking-Oberfläche auf Basis von
Veo 3.1, in der ImageFX und Whisk aufgegangen sind.

---

## Zwei Filter, an denen die meisten „$0"-Angaben scheitern

### 1. Kommerzielle Nutzungsrechte

fsfinance.de ist der Außenauftritt einer GbR. Jedes Asset dort ist
kommerzielle Nutzung — auch ohne direkten Verkauf. Die Free-Tiers sind
überwiegend Test-Kontingente ohne kommerzielle Lizenz:

| Tool | Free-Tier | Kommerzielle Rechte ab |
|---|---|---|
| Hailuo / MiniMax | Wasserzeichen, 720p, Renders verfallen nach ~3 Tagen | ~$9,99/Monat |
| ElevenLabs | keine kommerzielle Lizenz, Attributionspflicht | $5/Monat (Starter) |
| FishAudio (Dienst) | „personal use only" | $11/Monat (Plus) |
| FishAudio (fish-speech) | **CC-BY-NC-SA 4.0 — non-commercial** | nur per Einzelvereinbarung |
| Hedra | Wasserzeichen, nicht kommerziell | $15/Monat (Basic) |
| HeyGen | 3 Videos/Monat, 720p, Wasserzeichen | $29/Monat (Creator) |
| ArtFlow | 100 Credits/Monat, Wasserzeichen | $8/Monat (mit Attribution) |
| Google Flow | nutzbar, aber „Made with Veo"-Wasserzeichen im Export | Google-AI-Abo |
| Lovart | 100 Credits täglich | Starter aufwärts |
| Stable Diffusion | SD 1.5/SDXL frei; SD 3/3.5 unter $1 Mio. Umsatz frei | Attributionspflicht bei Weitergabe |
| Nano Banana | **kommerziell erlaubt**, aber Google trainiert auf den Eingaben | Paid-Tier für Datenschutz |

Der Sonderfall ist **FishAudio**: Das offene Modell `fish-speech` steht unter
CC-BY-NC-SA 4.0 und ist damit ausdrücklich nicht für kommerzielle Nutzung
lizenziert. „Open Source" heißt hier nicht „frei verwendbar". Wer das für
einen bezahlten Kurs einsetzt, verletzt die Lizenz.

### 2. EU AI Act, Artikel 50 — seit 02.08.2026 anwendbar

KI-generierte Bild-, Audio- und Videoinhalte müssen als solche erkennbar sein,
menschenlesbar **und** maschinenlesbar. Bußgeldrahmen bis 15 Mio. EUR oder 3 %
des weltweiten Jahresumsatzes. Vor dem 02.08.2026 erzeugte Inhalte fallen
unter die Übergangsregel; die bestehenden Bilder in `assets/img/` sind damit
nicht rückwirkend betroffen.

---

## Avatare und Voice Cloning sind eine andere Kategorie

Die fünf neuen Karten verschieben das Thema von „Bilder generieren" zu
„Personen nachbilden". Das ist rechtlich etwas völlig anderes.

**Ein KI-Avatar, der eine reale Person als Sprecher zeigt, ist ein Deepfake im
Sinne von Art. 50 Abs. 4 AI Act — auch dann, wenn es das eigene Gesicht ist,
die Person zugestimmt hat und der Inhalt inhaltlich stimmt.** Dasselbe gilt für
eine geklonte Stimme. Die Kennzeichnungspflicht greift unabhängig von der
Einwilligung: Die Einwilligung regelt das Persönlichkeitsrecht, die
Kennzeichnung die Transparenz gegenüber dem Publikum. Beides ist nötig, keins
ersetzt das andere.

Dazu kommen, unverändert neben dem AI Act: §§ 22, 23 KUG (Recht am eigenen
Bild), Art. 6 und 9 DSGVO bei biometrischen Daten, §§ 823 ff. BGB.

Praktisch heißt das für eine GbR mit drei Gründern: Bevor Gesicht oder Stimme
eines Gründers geklont wird, braucht es eine dokumentierte, widerrufbare
Einwilligung dieser Person — und zwar für den konkreten Verwendungszweck. Ein
mündliches „mach mal" reicht nicht, wenn der Avatar später in bezahlten
Kursinhalten oder Werbung auftaucht.

---

## Harte Grenze: keine KI-Personen als Lückenfüller

Drei Stellen im Repo sehen nach einer Lücke aus, die ein Avatar-Tool
„schnell schließen" könnte. Alle drei sind bewusst offen:

1. **Gründerfotos** — `components.jsx`, `Team`: Platzhalter
   „Foto folgt — {Name}" für drei real existierende Personen. Ein generiertes
   Porträt oder ein Avatar-Standbild an dieser Stelle ist eine
   Falschdarstellung auf einer Seite, die ins Impressum verlinkt. Drei
   Handyfotos vor einer neutralen Wand lösen das Problem in zwanzig Minuten
   und kosten nichts.
2. **Testimonials** — im Code ausdrücklich als „replaces fabricated
   testimonials" markiert und durch die `Credibility`-Sektion ersetzt. Ein
   Avatar-Video mit einer erfundenen Kundenstimme wäre exakt das, was diese
   Entscheidung verhindern sollte — und im Finanzumfeld zusätzlich ein
   Wettbewerbsverstoß.
3. **Performance-Belege** — die `MetricTile`-Kacheln stehen auf „Noch nicht
   veröffentlicht" und „Verifizierung folgt". Belege sind Screenshots und
   Kontoauszüge.

Symbolbilder (Architektur, Skyline, abstrakte Charts) bleiben unproblematisch
und sind genau das, was `generate-images.sh` heute erzeugt.

---

## Bewertung im Einzelnen

### Bildgenerierung: Nano Banana ✅ / Google Flow ➖

`assets/generate-images.sh` generiert seit dem Redesign fünf Website-Motive
über Nano Banana mit `GEMINI_API_KEY`. Google Flow bündelt unter anderem
Nano Banana 2 in einer Oberfläche — es ist dieselbe Modellfamilie, nur mit
GUI statt Skript. Für einen reproduzierbaren Build ist das Skript im Repo die
bessere Lösung: versioniert, nachvollziehbar, ohne Wasserzeichen im Export.
GPT Image löst hier nichts, was nicht schon gelöst wäre.

Offener Punkt aus `PLAN.md` bleibt „Bilder auf WebP umstellen" — ein
Konvertierungsschritt, kein Tool-Thema. `logo_lion_shield_transparent.png`
liegt bei 3,5 MB; da steckt mehr Ladezeit drin als in der Wahl des Generators.

### Videogenerierung: Hailuo / ArtFlow ⏳

Relevanz ist real, aber noch nicht akut: `ContentPreview` zeigt drei
Platzhalter mit Badge „Geplant", der Footer listet Instagram, TikTok und
YouTube als „(folgt)", und `sync/fetch_data.py` zieht bereits IG- und
TikTok-Kennzahlen (aktuell `available: false`, weil Tokens fehlen). Sobald die
Kanäle starten, entsteht Bedarf an Kurzvideos — dann aber in einer Variante
ohne Wasserzeichen und mit Rechten. Realistisch $8–10/Monat.

### Voice Cloning: FishAudio ⚠️

Denkbarer Einsatz: Vertonung der Kursinhalte im Mitgliederbereich
(`mitglieder/kurs.html` lädt `trading-kurs.html` aus einem privaten
Supabase-Bucket). Zwei getrennte Probleme:

- **Lizenz:** Das offene Modell ist non-commercial. Der gehostete Dienst
  erlaubt kommerzielle Nutzung erst ab $11/Monat. Bezahlte Kursinhalte sind
  eindeutig kommerziell.
- **Recht:** Eine geklonte Gründerstimme in einem Bildungsprodukt ist
  kennzeichnungspflichtig und braucht dokumentierte Einwilligung.

ElevenLabs Starter kostet $5 und löst zumindest das Lizenzproblem sauberer.

### Avatare: Hedra / HeyGen / Synthesia ⚠️

Beide „kostenlosen" Optionen sind Trial-Tarife: Hedra mit Wasserzeichen und
ohne kommerzielle Rechte, HeyGen mit 3 Videos pro Monat in 720p. Für einen
Markenkanal unbrauchbar. Kommerziell nutzbar wird es ab $15 (Hedra Basic)
bzw. $29 (HeyGen Creator).

Die eigentliche Frage ist aber nicht der Preis. Laut `components.jsx` ist ein
Gründer ausdrücklich für „Content-Produktion" zuständig. Eine echte Aufnahme
dieser Person ist billiger als jedes Avatar-Abo, braucht keine
Deepfake-Kennzeichnung, keine Einwilligungsdokumentation — und passt zu einer
Marke, die mit „Struktur statt Inszenierung" wirbt. Ein Avatar löst hier ein
Problem, das wir nicht haben, und schafft zwei neue.

Sinnvoll wäre ein Avatar-Tool am ehesten für **Lokalisierung**: bestehende,
echt aufgenommene Kursinhalte in weitere Sprachen bringen. Das steht aktuell
auf keiner Roadmap.

### Design und Cinematic: Lovart / Stable Diffusion ❌

Unverändert kein Anwendungsfall. Die Website ist React plus handgeschriebenes
CSS mit eigenen Design-Tokens; es gibt kein Deck und kein Asset im Repo, das
aus einem Design-Tool käme. Die offenen Hero-Effekte aus `HANDOFF.md`
(Ken-Burns, Gold-Beams-Canvas, Parallax) sind CSS und Canvas, kein generiertes
Video — ein Hintergrundvideo wäre zudem ein Rückschritt bei Ladezeit und beim
`prefers-reduced-motion`-Handling, das in `components.jsx` sauber umgesetzt ist.

---

## Empfehlung

**Jetzt:** nichts anschaffen. Der einzige laufende Bedarf — Bildgenerierung —
ist mit Nano Banana gedeckt, kostenlos und kommerziell zulässig.

**Wenn die Social-Kanäle starten:** ein Video-Tool im $8–10-Bereich, bei Bedarf
ElevenLabs Starter für $5. Zusammen unter $15/Monat mit sauberen Rechten. Die
Free-Tiers taugen zum Ausprobieren, nicht zum Veröffentlichen.

**Avatare und Voice Cloning:** vorerst nicht. Erst wenn es einen konkreten
Anlass gibt, der mit einer echten Aufnahme nicht lösbar ist — realistisch:
Mehrsprachigkeit. Vorher zu klären: Einwilligung der betroffenen Gründer,
schriftlich und zweckgebunden.

**Vor der ersten Veröffentlichung von KI-Medien:** Kennzeichnungskonzept nach
Art. 50 festlegen — sichtbarer Hinweis am Asset plus Metadaten. Sinnvoller Ort
ist der bestehende Risiko- und Affiliate-Hinweisblock im Footer, wo die
Transparenzhinweise ohnehin stehen.

Diese Bewertung ist eine technische und organisatorische Einschätzung, keine
Rechtsberatung. Bevor Gesicht oder Stimme eines Gründers geklont wird, gehört
das anwaltlich geprüft.

---

## Nebenbefund

`HANDOFF.md`, `PLAN.md` und diese Datei liegen im Wurzelverzeichnis eines
GitHub-Pages-Repos, das aus dem Root ausliefert. Sie sind damit öffentlich
abrufbar (`fsfinance.de/PLAN.md`). Bisher steht dort nichts Vertrauliches,
aber es ist eine Eigenschaft, die man kennen sollte, bevor interne Notizen
dazukommen.

---

## Quellen

**Tarife und Lizenzen**

- [Hailuo/MiniMax Pricing](https://felloai.com/minimax-pricing/) ·
  [Hailuo 2.3 Pricing](https://magichour.ai/blog/hailuo-23-pricing)
- [ElevenLabs Free Plan Limits](https://aivoicereview.com/guides/elevenlabs-free-plan-limits) ·
  [ElevenLabs Lizenzleitfaden](https://www.licenseorg.com/blog/elevenlabs-licensing-guide-ai-voices)
- [FishAudio — Is Free Voice Cloning Really Free](https://fish.audio/blog/is-free-voice-cloning-really-free-2026-guide/) ·
  [fish-speech Lizenz (CC-BY-NC-SA)](https://www.spheron.network/blog/deploy-open-source-tts-gpu-cloud-2026/)
- [Hedra Pricing](https://www.hedra.com/pricing) ·
  [Hedra Review 2026](https://fluxnote.io/guides/hedra-ai-review)
- [HeyGen Pricing 2026](https://konabayev.com/blog/heygen-pricing/) ·
  [HeyGen Free Trial Limits](https://avatar-video-ai.com/blog/heygen-ai-review)
- [ArtFlow Pricing](https://www.saasworthy.com/product/artflow-ai/pricing) ·
  [ArtFlow Review](https://aichief.com/ai-tools/artflow-ai/)
- [Google Flow Pricing und Free Tier](https://whiskailabs.net/google-flow-ai-pricing/) ·
  [Google Flow Guide](https://whiskailabs.net/google-flow-ai-filmmaking-tool-veo-guide-2026/)
- [Lovart Pricing](https://www.lovart.ai/pricing)
- [Stability AI Community License](https://stability.ai/license) ·
  [Stable Diffusion Output Rights](https://terms.law/ai-output-rights/stable-diffusion/)
- [Gemini Free-Tier Datennutzung](https://docs.bswen.com/blog/2026-03-23-gemini-free-tier-data-privacy/)

**Rechtlicher Rahmen**

- [AI Act Art. 50 — Transparenzpflichten](https://artificialintelligenceact.eu/transparency-rules-article-50/) ·
  [Leitlinien der EU-Kommission](https://digital-strategy.ec.europa.eu/en/policies/guidelines-transparency-ai-generated-content)
- [Fristen und Bußgelder](https://datamatters.sidley.com/2026/06/24/eu-ai-act-transparency-obligations-preparing-for-compliance-by-2-august-2026/)
- [Deepfake-Kennzeichnung nach Art. 50 Abs. 4](https://www.crispycontent.de/blog/deepfake-kennzeichnung-ki-verordnung-artikel-50-compliance-bewegtbild) ·
  [Deepfake-Recht — KUG, DSGVO, StGB](https://deepfake-recht.de/) ·
  [Haufe: Kennzeichnungspflicht ab August 2026](https://www.haufe.de/recht/kanzleimanagement/kennzeichnungspflicht-fuer-ki-inhalte-gilt-ab-august-2026_222_681220.html)
