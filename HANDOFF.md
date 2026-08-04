# HANDOFF — DayDom Website

## Entscheidung vom 04.08.2026

**Dieser Ordner ist die einzige Website der DayDom Performance Group.** Es gibt keinen zweiten Zweig mehr, der gepflegt wird.

Entschieden von Fabian, Begründung vollständig in `~/Claude/_ops/entscheidung-website.md`.

### Was verworfen wurde

Der Relaunch-Entwurf vom 19.07.2026 („Website 2.0", Zielrepo `gamefabe68-debug/website2.0`, nie deployt). Er lag verstreut in `~/Downloads/` und liegt jetzt vollständig unter:

```
~/Archiv/2026-08_stillgelegt/daydom-website/relaunch-entwurf-19-07/
```

Kurzform der Begründung: das hier laufende Repo **ist** dieser Relaunch, portiert beim Redesign v3 am 21.07. Gleiche Design-Tokens, gleiche Schriften, gleiche Sektionsfolge — nur die Ink-Palette wurde bewusst von warmem Fast-Schwarz auf Dark-Navy gedreht. Der Entwurf konnte dafür keine Unterseiten, keinen Mitgliederbereich, kein Mobil-Layout und keine Barrierefreiheit. Übernahme hätte 12–20 Stunden gekostet, die verbliebenen Einzelteile nachzuziehen kostet 2–4.

### Was aus dem Entwurf noch fehlt

Bewusst offen gelassen, jederzeit einzeln nachziehbar. Quelldateien im Archivpfad oben unter `react-integration-setup/website/`:

| Feature | Quelldatei | Aufwand |
|---|---|---|
| Testimonials-Carousel | `Testimonials.jsx` | ~2 h, wartet auf echte Kundenstimmen |
| Ken-Burns-Hero (`@keyframes dd-kb`, 26 s) | `Hero.jsx` | ~1 h |
| Gold-Beams-Canvas | `Hero.jsx` | ~1 h |
| Scroll-Parallax | `Hero.jsx`, `Sections.jsx` | ~1 h |

Nicht übernehmen: `tweaks-panel.jsx` ist ein Entwicklungswerkzeug, `image-slot.js` funktioniert nur im ursprünglichen Design-Tool, die SocialRail kollidiert mit dem Mobil-Layout.

---

## Arbeiten an diesem Repo

- **Build:** `npm run build` — esbuild bündelt `src/App.jsx` nach `assets/js/bundle.js`.
- **Nach jedem Build den Cache-Busting-Zähler in `index.html` erhöhen**, sowohl `bundle.js?v=N` als auch `styles.css?v=N`. Ohne das bekommen Besucher die alte Fassung ausgeliefert.
- **Deployment:** GitHub Pages aus `FBaux/sf-finance-homepage`, Domain über `CNAME`.
- `.github/workflows/sync.yml` committet alle 30 Minuten API-Daten. Beim Rebasen damit rechnen.
- Beim Bauen von Scroll-Reveals nie `opacity:0` als Grundzustand setzen, nur als Keyframe-Overlay — sonst bleibt der Inhalt unsichtbar, falls der Trigger nicht feuert.
