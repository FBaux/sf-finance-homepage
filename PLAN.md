# PLAN — Homepage (fsfinance.de)

**Ziel:** Außenauftritt der DayDom Performance Group. Eine Website, gepflegt an einem Ort.

---

## Aktueller Stand (04.08.2026)

- **Live** auf fsfinance.de seit 21.07.2026 (Redesign v3, Dark-Navy/Gold).
- Hosting: GitHub Pages, Repo `FBaux/sf-finance-homepage`, `CNAME` → fsfinance.de.
- Build: React 18 + esbuild. `npm run build` bündelt `src/App.jsx` nach `assets/js/bundle.js`.
- Unterseiten: `vergleich.html`, `impressum.html`, `datenschutz.html`, `mitglieder/`, `admin/`, `dashboard/`, `kontenliste/`.
- `.github/workflows/sync.yml` zieht alle 30 Minuten API-Daten und committet sie.
- Mitgliederbereich läuft über Supabase-Projekt `gymhfbnljbosqxqqzdik` mit RLS.

**Kanon-Entscheidung:** Dieser Ordner ist die einzige DayDom-Website. Siehe `HANDOFF.md` und `~/Claude/_ops/entscheidung-website.md`.

---

## Fallstrick beim Arbeiten

Nach jedem `npm run build` den Cache-Busting-Parameter in `index.html` hochzählen — `bundle.js?v=N` **und** `styles.css?v=N`. Ohne das sehen Besucher die alte Fassung.

---

## Nächste Schritte

- [ ] Testimonials-Carousel aus dem Archiv portieren (~2 h) — erst wenn echte Kundenstimmen vorliegen
- [ ] Ken-Burns-Hero + Gold-Beams-Canvas portieren (~2 h, optional)
- [ ] Bilder auf WebP umstellen, Fonts lokal einbinden
- [ ] Steuernummer im Impressum ergänzen

Quellen für die ersten beiden Punkte: `~/Archiv/2026-08_stillgelegt/daydom-website/relaunch-entwurf-19-07/`
