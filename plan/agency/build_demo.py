"""Demo-Builder: Lead-JSON -> statische Demo-Website.

python3 build_demo.py samples/beauty_muster.json [--live]
Ausgabe: out/<slug>/index.html  (Demo-Modus: noindex + Hinweisbanner)
"""
import json, re, sys, datetime, pathlib, unicodedata
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = pathlib.Path(__file__).parent
env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["j2", "html"]))
BRANCHES = json.loads((ROOT / "templates/branches.json").read_text())
DAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def slug(s):
    s = s.lower().translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def schema(b, t):
    return json.dumps({
        "@context": "https://schema.org", "@type": t["schema_type"], "name": b["name"],
        "telephone": b.get("phone"), "email": b.get("email"),
        "address": {"@type": "PostalAddress", "streetAddress": b["street"], "postalCode": b["zip"],
                    "addressLocality": b["city"], "addressCountry": "DE"},
        "openingHours": [f"{d} {h}" for d, h in b["hours"] if re.match(r"\d", h)],
    }, ensure_ascii=False).replace("</", "<\\/")


def build(lead_path, live=False):
    b = json.loads(pathlib.Path(lead_path).read_text())
    t = BRANCHES[b["branch"]]
    b["hours"] = [(DAYS[i], h) for i, h in enumerate(b["hours"])]
    html = env.get_template("site.html.j2").render(
        b=b, t=t, demo=not live, schema=schema(b, t), year=datetime.date.today().year,
        form_action=b.get("form_action", "#termin"))
    out = ROOT / "out" / slug(b["name"]) / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


if __name__ == "__main__":
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        print(build(p, live="--live" in sys.argv))
