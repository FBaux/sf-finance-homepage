# Agency-Toolkit (Projekt Diamant)

```bash
pip install jinja2
python3 build_demo.py samples/beauty_muster.json        # -> out/<slug>/index.html (Demo: noindex + Banner)
python3 build_demo.py samples/kfz_muster.json --live    # ohne Demo-Banner
python3 lead_research.py --branch beauty --top 40       # braucht Netz: overpass-api.de + Betriebs-Websites
```

- `templates/site.html.j2` – eine Vorlage, Branchen-Themes in `templates/branches.json` (`beauty`, `kfz`).
- Keine externen Fonts/Karten/Tracker → DSGVO-arm. Impressum/Datenschutz sind Platzhalter bis QM-Gate 2.
- `leads/*.csv` und `out/` sind gitignored – **Lead-Daten nie in dieses öffentliche Repo committen.**
