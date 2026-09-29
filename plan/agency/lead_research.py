"""Lead-Research + Scoring (Sales-Agents 1+2).

Quelle: OpenStreetMap (Overpass, ODbL) – nur öffentliche Geschäftsdaten.
python3 lead_research.py --branch beauty --top 40      -> leads/beauty_<datum>.csv + leads/json/*.json
Braucht Netzzugang zu overpass-api.de und zu den Betriebs-Websites.
DSGVO: nur Firmendaten, Zweck B2B-Ansprache per Brief, Löschung nach 30 Tagen ohne Rückmeldung.
"""
import argparse, csv, datetime, json, pathlib, re, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).parent
CITIES = ["Düsseldorf", "Neuss", "Meerbusch", "Ratingen", "Hilden", "Erkrath", "Langenfeld (Rheinland)"]
TAGS = {
    "beauty": ['shop=beauty', 'shop=hairdresser', 'shop=massage', 'shop=tattoo'],
    "kfz": ['shop=car_repair', 'shop=tyres', 'craft=car_repair'],
}
BOOKING = ["treatwell", "planity", "shore.com", "studiobookr", "salonized", "fresha", "booksy", "timify",
           "etermin", "calendly", "terminland", "easyweek", "bookrhub", "terminz", "werkstatt-termin",
           "repairpal", "autobutler", "simplybook"]
UA = {"User-Agent": "Mozilla/5.0 (lead-research; contact via website)"}


def overpass(branch):
    area = "|".join(re.escape(c) for c in CITIES)
    parts = "".join(f'nwr[{k}="{v}"](area.a);' for k, v in (t.split("=") for t in TAGS[branch]))
    q = f'[out:json][timeout:90];area[boundary=administrative][name~"^({area})$"]->.a;({parts});out tags center;'
    req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                                 data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=120))["elements"]


def check_site(url):
    r = {"https": False, "viewport": False, "booking": "", "load_s": None, "old_year": False, "ext_fonts": False, "ok": False}
    if not url:
        return r
    url = url if url.startswith("http") else "http://" + url
    try:
        t = time.time()
        resp = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12)
        html = resp.read(600_000).decode("utf-8", "ignore").lower()
        r.update(ok=True, load_s=round(time.time() - t, 1), https=resp.geturl().startswith("https"),
                 viewport='name="viewport"' in html or "name=viewport" in html,
                 booking=next((b for b in BOOKING if b in html), ""),
                 ext_fonts="fonts.googleapis.com" in html)
        years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(20\d\d)", html)]
        r["old_year"] = bool(years) and max(years) <= datetime.date.today().year - 3
    except Exception:
        pass
    return r


def score(site, has_url):
    if not has_url:
        return 90, ["keine Website"]
    if not site["ok"]:
        return 80, ["Website nicht erreichbar"]
    s, why = 0, []
    for cond, pts, txt in [(not site["https"], 20, "kein HTTPS"), (not site["viewport"], 25, "nicht mobil"),
                           (not site["booking"], 25, "keine Online-Buchung"),
                           ((site["load_s"] or 0) > 3, 10, "langsam"), (site["old_year"], 10, "veraltet"),
                           (site["ext_fonts"], 5, "externe Google Fonts")]:
        if cond:
            s += pts
            why.append(txt)
    return s, why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", choices=TAGS, required=True)
    ap.add_argument("--top", type=int, default=40)
    a = ap.parse_args()

    rows = []
    for e in overpass(a.branch):
        t = e.get("tags", {})
        if not t.get("name"):
            continue
        rows.append({"name": t["name"], "street": f'{t.get("addr:street", "")} {t.get("addr:housenumber", "")}'.strip(),
                     "zip": t.get("addr:postcode", ""), "city": t.get("addr:city", ""),
                     "phone": t.get("phone") or t.get("contact:phone", ""),
                     "website": t.get("website") or t.get("contact:website", ""),
                     "kind": next((t[k] for k in ("shop", "craft") if k in t), ""), "osm": f'{e["type"]}/{e["id"]}'})
    with ThreadPoolExecutor(12) as ex:
        sites = list(ex.map(lambda r: check_site(r["website"]), rows))
    for r, s in zip(rows, sites):
        r["score"], why = score(s, bool(r["website"]))
        r["gruende"] = ", ".join(why)
        r["buchungstool"] = s["booking"]
    rows = [r for r in rows if r["street"] and r["score"] >= 40]
    rows.sort(key=lambda r: -r["score"])
    top = rows[: a.top]

    out = ROOT / "leads"
    (out / "json").mkdir(parents=True, exist_ok=True)
    f = out / f"{a.branch}_{datetime.date.today()}.csv"
    with f.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(top[0]) if top else ["name"])
        w.writeheader()
        w.writerows(top)
    for r in top:  # Skelette für build_demo.py (Öffnungszeiten/Leistungen manuell prüfen!)
        (out / "json" / f'{r["osm"].replace("/", "_")}.json').write_text(json.dumps({
            "branch": a.branch, "name": r["name"], "street": r["street"], "zip": r["zip"],
            "city": r["city"] or "Düsseldorf", "phone": r["phone"],
            "hours": ["nach Vereinbarung"] * 5 + ["geschlossen"] * 2, "quotes": []}, ensure_ascii=False, indent=1))
    print(f"{len(rows)} passende Betriebe, Top-{len(top)} -> {f}")


if __name__ == "__main__":
    main()
