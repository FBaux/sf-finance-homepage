"""Erzeugt plan/Projekt-Diamant_Masterplan.pdf  (python3 plan/build_plan_pdf.py)"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table,
                                TableStyle, KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Projekt-Diamant_Masterplan.pdf")

FONT, BOLD = "Helvetica", "Helvetica-Bold"
for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu"):
    if os.path.exists(f"{d}/DejaVuSans.ttf"):
        pdfmetrics.registerFont(TTFont("DV", f"{d}/DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("DVB", f"{d}/DejaVuSans-Bold.ttf"))
        pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")
        FONT, BOLD = "DV", "DVB"
        break

INK = colors.HexColor("#14213d")
ACC = colors.HexColor("#0f766e")
GOLD = colors.HexColor("#b7791f")
RED = colors.HexColor("#b42318")
MUTED = colors.HexColor("#5b6472")
LIGHT = colors.HexColor("#eef2f6")
LINE = colors.HexColor("#cbd2dc")

ss = getSampleStyleSheet()
def st(name, **kw):
    base = dict(fontName=FONT, fontSize=9.5, leading=13.2, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)

H1 = st("H1", fontName=BOLD, fontSize=18, leading=22, spaceBefore=4, spaceAfter=8, textColor=INK)
H2 = st("H2", fontName=BOLD, fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=4, textColor=ACC)
H3 = st("H3", fontName=BOLD, fontSize=10.5, leading=14, spaceBefore=6, spaceAfter=2)
P = st("P", spaceAfter=5)
SM = st("SM", fontSize=8.2, leading=10.6)
SMB = st("SMB", fontName=BOLD, fontSize=8.2, leading=10.6, textColor=colors.white)
NOTE = st("NOTE", fontSize=8.5, leading=11.5, textColor=MUTED)
BUL = st("BUL", leftIndent=12, bulletIndent=2, spaceAfter=2)

def p(t, s=P): return Paragraph(t, s)
def bl(items): return [Paragraph(i, BUL, bulletText="•") for i in items]

def box(text, color=ACC):
    t = Table([[Paragraph(text, st("bx", textColor=INK))]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t

def table(rows, widths, head=ACC, zebra=True):
    data = [[Paragraph(str(c), SMB) for c in rows[0]]] + \
           [[Paragraph(str(c), SM) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), head),
             ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("GRID", (0, 0), (-1, -1), 0.4, LINE),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if zebra:
        for i in range(2, len(data), 2):
            style.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(style))
    return t

# ---------------------------------------------------------------- Org-Chart
def org_chart():
    W, H = 174 * mm, 90 * mm
    d = Drawing(W, H)
    def node(x, y, w, h, title, sub, fill):
        d.add(Rect(x, y, w, h, rx=4, ry=4, fillColor=fill, strokeColor=fill))
        d.add(String(x + w / 2, y + h - 12, title, fontName=BOLD, fontSize=8.2,
                     fillColor=colors.white, textAnchor="middle"))
        for i, s in enumerate(sub):
            d.add(String(x + w / 2, y + h - 23 - i * 9, s, fontName=FONT, fontSize=6.6,
                         fillColor=colors.white, textAnchor="middle"))
    def edge(x1, y1, x2, y2):
        d.add(Line(x1, y1, x2, y2, strokeColor=LINE, strokeWidth=1))

    cx = W / 2
    node(cx - 70, H - 40, 140, 38, "FOUNDER (Mensch)", ["Rechtsträger · Verträge · Calls", "finale Freigabe (Gate 4)"], INK)
    node(cx - 70, H - 92, 140, 38, "CEO-AGENT  „Orchestrator“", ["Strategie · Kapital · Weekly OKR", "verteilt Tasks, eskaliert"], GOLD)
    edge(cx, H - 40, cx, H - 54)

    divs = [("VERTRIEB", ["Head of Sales", "6 Agents"], colors.HexColor("#1d4ed8")),
            ("DELIVERY", ["Head of Delivery", "6 Agents"], colors.HexColor("#0f766e")),
            ("DESIGN", ["Creative Director", "4 Agents"], colors.HexColor("#7c3aed")),
            ("CONTENT", ["Head of Content", "5 Agents"], colors.HexColor("#c2410c")),
            ("QUALITÄT", ["Head of QM (Veto!)", "9 Agents"], RED),
            ("FINANZEN", ["CFO-Agent", "4 Agents"], colors.HexColor("#15803d")),
            ("OPERATIONS", ["COO-Agent", "4 Agents"], colors.HexColor("#475569")),
            ("R&D / ASSETS", ["Head of R&D", "4 Agents"], colors.HexColor("#a16207"))]
    bw, bh, gap = 38 * mm, 38, 5.3 * mm
    rows_y = [H - 150, H - 210]
    bus_y = H - 104
    edge(cx, H - 92, cx, bus_y)
    for r in range(2):
        y = rows_y[r]
        xs = [i * (bw + gap) + 1 for i in range(4)]
        line_y = bus_y if r == 0 else y + bh + 6
        edge(xs[0] + bw / 2, line_y, xs[-1] + bw / 2, line_y)
        if r == 1:
            edge(3, bus_y, 3, line_y)
            edge(3, bus_y, xs[0] + bw / 2, bus_y)
            edge(3, line_y, xs[0] + bw / 2, line_y)
        for i, x in enumerate(xs):
            t, s, c = divs[r * 4 + i]
            edge(x + bw / 2, line_y, x + bw / 2, y + bh)
            node(x, y, bw, bh, t, s, c)
    d.add(String(cx, 18, "QM hat Veto-Recht über jede Kundenauslieferung · CFO hat Veto über jede Ausgabe > 20 €",
                 fontName=BOLD, fontSize=7.4, fillColor=RED, textAnchor="middle"))
    d.add(String(cx, 7, "Summe: 1 Mensch + 1 Orchestrator + 8 Heads + 42 Spezial-Agents",
                 fontName=FONT, fontSize=7.2, fillColor=MUTED, textAnchor="middle"))
    return d

def gate_chart():
    W, H = 174 * mm, 26 * mm
    d = Drawing(W, H)
    gates = [("G0 Brief", "CEO"), ("G1 Draft", "Fach-Agent"), ("G2 Recht", "QM Legal/DSGVO/AI-Act"),
             ("G3 Technik", "QM Tech + Content"), ("G4 Freigabe", "Founder"), ("LIVE", "Monitoring")]
    w = W / len(gates) - 4
    for i, (a, b) in enumerate(gates):
        x = i * (w + 4)
        c = RED if a.startswith(("G2", "G3")) else (INK if a.startswith("G4") else ACC)
        d.add(Rect(x, 22, w, 38, rx=4, ry=4, fillColor=c, strokeColor=c))
        d.add(String(x + w / 2, 45, a, fontName=BOLD, fontSize=8.5, fillColor=colors.white, textAnchor="middle"))
        d.add(String(x + w / 2, 32, b, fontName=FONT, fontSize=6.3, fillColor=colors.white, textAnchor="middle"))
    d.add(String(0, 8, "Kein Gate darf übersprungen werden. Fail in G2/G3 → zurück an G1 mit Fehlerprotokoll.",
                 fontName=FONT, fontSize=7.5, fillColor=MUTED))
    return d

def bar_chart():
    W, H = 174 * mm, 62 * mm
    d = Drawing(W, H)
    data = [("M1", 190, 980, 0), ("M2", 230, 3160, 256), ("M3", 260, 5990, 690)]
    maxv = 6500
    base, top = 16, H - 14
    scale = (top - base) / maxv
    gw = W / 3
    for i, (m, cost, rev, mrr) in enumerate(data):
        x0 = i * gw + gw / 2 - 45
        for j, (v, c, lab) in enumerate([(cost, RED, "Kosten"), (rev, ACC, "Umsatz"), (mrr, GOLD, "MRR")]):
            x = x0 + j * 31
            h = max(v * scale, 1)
            d.add(Rect(x, base, 26, h, fillColor=c, strokeColor=None))
            d.add(String(x + 13, base + h + 3, f"{v:,}".replace(",", ".") + " €", fontName=FONT,
                         fontSize=6.5, fillColor=INK, textAnchor="middle"))
        d.add(String(i * gw + gw / 2, 4, m, fontName=BOLD, fontSize=8.5, fillColor=INK, textAnchor="middle"))
    d.add(Line(0, base, W, base, strokeColor=LINE))
    for j, (c, lab) in enumerate([(RED, "Kosten"), (ACC, "Umsatz (Basis-Szenario)"), (GOLD, "wiederkehrend (MRR, Monatsende)")]):
        d.add(Rect(j * 55 * mm, H - 8, 7, 7, fillColor=c, strokeColor=None))
        d.add(String(j * 55 * mm + 10, H - 7, lab, fontName=FONT, fontSize=7, fillColor=INK))
    return d

# ---------------------------------------------------------------- Seiten
def on_page(c, doc):
    c.saveState()
    c.setFont(FONT, 7.5)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, "Projekt DIAMANT · Masterplan V1.1 · Stand 29.09.2026")
    c.drawRightString(192 * mm, 10 * mm, f"Seite {doc.page}")
    c.setStrokeColor(ACC)
    c.setLineWidth(1.2)
    c.line(18 * mm, 285 * mm, 192 * mm, 285 * mm)
    c.restoreState()

def on_first(c, doc):
    c.saveState()
    c.setFillColor(INK)
    c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, 190 * mm, A4[0], 2.2 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(BOLD, 34)
    c.drawString(20 * mm, 215 * mm, "PROJEKT DIAMANT")
    c.setFont(FONT, 14)
    c.drawString(20 * mm, 203 * mm, "Von 500 € zu wiederkehrendem Einkommen in 90 Tagen")
    c.setFont(FONT, 10.5)
    y = 170 * mm
    for line in ["Masterplan V1 · Strategie · Team-Hierarchie · Qualitätsmanagement",
                 "Budget · 90-Tage-Roadmap · KPIs · Risiken · Kill-Kriterien",
                 "", "Szenario: Alternative Welt. Startkapital 500 € über 3 Monate.",
                 "Regel: legal, sauber, am Limit. Druck formt Diamanten.",
                 "", "Erstellt von: CEO-Agent (Claude) für den Founder",
                 "Stand: 29. September 2026 · Version V1.1 (Nische, Region, Preis festgelegt)"]:
        c.drawString(20 * mm, y, line)
        y -= 7 * mm
    c.setFillColor(GOLD)
    c.setFont(BOLD, 11)
    c.drawString(20 * mm, 40 * mm, "Kernwette: „Erst bauen, dann fragen.“")
    c.setFillColor(colors.white)
    c.setFont(FONT, 9.5)
    c.drawString(20 * mm, 33 * mm, "Wir bauen lokalen Betrieben ihre neue Website, BEVOR wir sie ansprechen –")
    c.drawString(20 * mm, 27 * mm, "und verkaufen dann Setup + monatlichen KI-Anfrage-Autopiloten.")
    c.restoreState()

story = [PageBreak()]

# 1 Executive Summary
story += [p("1 · Executive Summary", H1),
          box("<b>Empfehlung:</b> Wir starten eine <b>produktisierte KI-Digitalagentur für lokale Handwerks- und "
              "Dienstleistungsbetriebe</b> (Engine A, Cashflow ab Woche 3) und bauen daraus ab Monat 3 ein "
              "<b>eigenes SaaS-Produkt „Anfrage-Autopilot“</b> (Engine B, skalierbares Asset). "
              "Content „KI im Handwerk“ (Engine C) liefert ab Monat 2 Inbound-Leads zum Nulltarif."),
          Spacer(1, 6),
          box("<b>V1.1 · Entscheidungen des Founders (29.09.2026):</b> Zielgruppe = <b>Betriebe mit vielen Terminen</b>. "
              "Welle 1: Kosmetik-, Nagel- und Wimpernstudios (No-Show-Quote ~8–15 %, ohne Erinnerungen bis ~25 %; ~40 % der "
              "Online-Buchungen außerhalb der Öffnungszeiten). Welle 2 (A/B-Test): freie Kfz-Werkstätten. Bewusst <b>nicht</b>: "
              "Physio/Ärzte (Gesundheitsdaten Art. 9 DSGVO, Heilmittelwerbegesetz). Region: <b>Düsseldorf + Neuss, Meerbusch, "
              "Ratingen, Hilden, Erkrath, Langenfeld</b>. Preis: <b>490 € Starter</b>. Angebot geschärft: Website + Online-Termin "
              "(vorhandenes Buchungstool einbinden statt ersetzen) + Google-Button \u201eTermin buchen\u201c + Erinnerungen gegen No-Shows.", GOLD),
          Spacer(1, 6),
          p("<b>Warum genau das?</b>"),
          *bl(["<b>Geringster Kapitalbedarf pro € Umsatz:</b> Die Produktion (Website, Texte, Automationen) "
               "erledigen Agents – die einzigen harten Kosten sind Tools (~20–90 €/Monat) und Briefporto.",
               "<b>Riesige Lücke im Markt:</b> Laut Bitkom nutzen ~4 % der Handwerksbetriebe KI, weitere ~9 % planen es. "
               "Handwerker verbringen ~2 h/Tag mit Verwaltung (ZDH). Agenturen verlangen 3.000–8.000 € für eine Website "
               "+ 50–200 €/Monat Wartung – wir liefern für einen Bruchteil in 72 h.",
               "<b>Wiederkehrender Umsatz eingebaut:</b> Jeder Kunde zahlt Setup + Monatsabo → Einkommen stapelt sich (Staffelung ab M3).",
               "<b>Unfairer Vorteil:</b> Wir zeigen jedem Prospect seine <i>fertige</i> neue Website (Demo per QR-Code), "
               "bevor er einen Cent zahlt. Kein Pitch, sondern ein Vorher/Nachher.",
               "<b>Asset statt Hamsterrad:</b> Jede Auslieferung verbessert Templates & den Autopiloten → Engine B."]),
          Spacer(1, 4),
          p("<b>Ziele je Phase (Basis-Szenario, Schätzung):</b>"),
          table([["Phase", "Zeitraum", "Ziel", "Messlatte", "Status-Trigger"],
                 ["1 · Kosten decken", "Tag 1–30", "Alle Kosten wieder drin", "≥ 2 zahlende Pilotkunden (je 490 €)", "Tag 21: 0 Kunden → Pivot-Regel"],
                 ["2 · Leichtes Plus", "Tag 31–60", "Monatsgewinn > 0 + Founder-Einkommen", "≥ 4 neue Kunden, ≥ 4 Abos", "Tag 45: < 3 Kunden gesamt → Plan B"],
                 ["3 · Staffeln", "Tag 61–90", "MRR-Basis + Skalierungshebel", "≥ 600 € MRR, Warteliste SaaS", "Tag 90: MRR < 300 € → Neubewertung"]],
                [30, 22, 42, 44, 36]),
          Spacer(1, 6),
          box("<b>Unbequeme Wahrheit vorweg:</b> Ein KI-Agent kann rechtlich weder ein Gewerbe anmelden, noch Verträge "
              "unterschreiben, noch ein Bankkonto führen. <b>Der Founder ist Pflicht-Mensch im Loop</b>: ~1–2 h/Tag für "
              "Gewerbe, Unterschriften, Kundentermine, Freigaben. Alles andere übernehmen die Agents.", RED),
          PageBreak()]

# 2 Optionen
story += [p("2 · Strategie-Auswahl: Was wir NICHT machen – und warum", H1),
          p("Bewertet wurden 9 Geschäftsmodelle nach Time-to-Cash, Kapitalbedarf, Risiko, Skalierung und Rechtssicherheit "
            "(1 = schlecht, 5 = sehr gut). Gewichtung: Time-to-Cash ×2, weil Phase 1 überlebenswichtig ist."),
          table([["Option", "Speed", "Kap.", "Risiko", "Skal.", "Recht", "Score", "Urteil"],
                 ["A · KI-Digitalagentur lokal (Pre-Build)", "5", "5", "4", "3", "4", "26", "<b>PRIMÄR</b>"],
                 ["B · Nischen-SaaS (Anfrage-Autopilot)", "1", "4", "3", "5", "4", "18", "<b>ab M3 aus A</b>"],
                 ["C · Content/Personal Brand", "1", "5", "4", "5", "4", "20", "<b>Lead-Motor</b>"],
                 ["Freelance-Plattformen (n8n/Automationen)", "4", "5", "4", "2", "5", "24", "Plan B"],
                 ["Trading-Bot mit 500 €", "3", "1", "1", "2", "4", "14", "Nein"],
                 ["Dropshipping / E-Com", "2", "1", "2", "3", "3", "11", "Nein"],
                 ["KI-Content-Farmen / Etsy-Prints", "2", "4", "2", "3", "2", "15", "Nein"],
                 ["SEO-Affiliate-Nischenseiten", "1", "4", "2", "4", "4", "16", "Nein"],
                 ["Info-Produkt / Kurs ohne Reichweite", "1", "5", "3", "4", "4", "18", "Später"]],
                [52, 16, 14, 14, 17, 13, 13, 35]),
          Spacer(1, 6),
          p("Die wichtigsten Absagen im Klartext", H2),
          *bl(["<b>Trading-Bot:</b> Selbst 10 % Rendite/Monat auf 500 € = 50 € – deckt nicht mal Tools. Ein belegter Edge "
               "braucht Monate Backtest/Forward-Test; Totalverlustrisiko. Sinnvoll erst ab 10.000 €+ freiem Kapital (Phase 5+).",
               "<b>Dropshipping:</b> Frisst Kapital für Ads (Tests à 200–500 € pro Produkt), Retourenpflichten, Händlerhaftung.",
               "<b>KI-Content-Farmen:</b> Gesättigt, Plattform-Bans, seit 02.08.2026 zusätzlich Kennzeichnungspflichten nach Art. 50 AI Act.",
               "<b>SEO-Affiliate:</b> 3–9 Monate bis Traffic, AI Overviews senken Klickraten – verfehlt Phase-1-Ziel sicher."]),
          p("Warum Handwerk & lokale Dienstleister als Zielgruppe?", H2),
          *bl(["Hoher Auftragswert pro Kunde (ein gewonnener Auftrag = oft 2.000–20.000 €) → Website amortisiert sich mit 1 Anfrage.",
               "Viele Betriebe haben veraltete oder keine Website, ungepflegte Google-Profile, keine Online-Anfrage.",
               "Wenig Zeit, wenig Tech-Affinität → kaufen „Fertig für mich“, nicht „Mach es selbst“.",
               "Gut findbar: Google Maps, Handwerkskammer-Verzeichnisse, Branchenbücher → Lead-Research automatisierbar."]),
          PageBreak()]

# 3 Offer
story += [p("3 · Das Angebot (Offer-Architektur)", H1),
          p("Drei Stufen, klarer Upgrade-Pfad. Als Kleinunternehmer (§ 19 UStG, Grenze 25.000 € Vorjahr / 100.000 € lfd. Jahr) "
            "sind alle Preise Endpreise ohne USt – ein Preisvorteil gegenüber Agenturen."),
          table([["Paket", "Inhalt", "Preis Pilot (M1)", "Preis regulär (ab M2)", "Lieferzeit"],
                 ["<b>Starter</b>", "Onepager (mobil, schnell, lokales SEO), Google-Unternehmensprofil optimiert, Impressum/Datenschutz, Kontaktformular",
                  "490 € einmalig", "790 €", "72 h nach Material"],
                 ["<b>Pro</b>", "Starter + Leistungsseiten, Bewertungs-Funnel (QR-Karte + Mail-Vorlage), Anfrage-Formular mit Foto-Upload",
                  "–", "1.290 €", "5 Werktage"],
                 ["<b>Autopilot-Abo</b>", "Hosting, Updates, Rechtstexte-Monitoring, KI-Anfrage-Assistent (sortiert Anfragen, Antwortentwurf), Monatsreport",
                  "49 €/Monat", "79–129 €/Monat", "laufend, 3 Mon. Mindestlaufzeit"]],
                [24, 70, 26, 28, 26]),
          Spacer(1, 6),
          p("Garantie & Risikoumkehr", H2),
          *bl(["<b>„Erst sehen, dann zahlen“:</b> Kunde sieht die fertige Demo vor Auftrag. Zahlung 50 % bei Auftrag, 50 % bei Livegang.",
               "<b>Anfrage-Garantie (ab M2):</b> Keine einzige Online-Anfrage in 60 Tagen → 3 Monate Abo gratis.",
               "<b>Keine Knebelung:</b> Domain gehört dem Kunden. Kündigung nach 3 Monaten monatlich möglich."]),
          p("Unit Economics pro Kunde (Schätzung)", H2),
          table([["Posten", "Starter", "Anmerkung"],
                 ["Umsatz Setup", "790 €", "Pilot: 490 €"],
                 ["Direkte Kosten", "~15 €", "Domain ~1–12 €/J, Hosting 0 € (Static/EU), Porto/Druck"],
                 ["Akquise-Kosten", "~60 €", "~50 Briefe × ~1,20 € pro Abschluss (Annahme 2 % Brief→Kunde)"],
                 ["Founder-Zeit", "~2,5 h", "Termin, Fotos/Material, Freigabe"],
                 ["Agent-Zeit", "~4–6 h", "Build, Texte, QA – parallelisierbar"],
                 ["Abo-Umsatz (LTV 12 Mon.)", "~950 €", "79 € × 12, Annahme 70 % bleiben"],
                 ["<b>Deckungsbeitrag Jahr 1</b>", "<b>~1.500 €+</b>", "pro Kunde, vor Tool-Fixkosten"]],
                [52, 30, 92]),
          PageBreak()]

# 4 Team
story += [p("4 · Team & Hierarchie", H1),
          p("Ein Mensch, ein Orchestrator, acht Abteilungen. Jede Rolle ist so definiert, dass sie als eigener Sub-Agent "
            "mit klarem Input/Output laufen kann („Automatisierbar“-Spalte). Die Hierarchie bestimmt, wer wem "
            "Aufgaben gibt, wer prüft und wer Veto hat."),
          org_chart(),
          Spacer(1, 4),
          p("Entscheidungs- und Eskalationsregeln", H2),
          table([["Entscheidung", "Wer entscheidet", "Wer hat Veto", "Eskalation an"],
                 ["Ausgabe ≤ 20 €", "Head der Abteilung", "CFO-Agent", "–"],
                 ["Ausgabe > 20 € / neues Abo", "CEO-Agent", "CFO-Agent", "Founder (Freigabe)"],
                 ["Kundenauslieferung", "Head of Delivery", "Head of QM", "Founder (Gate 4)"],
                 ["Neue Outreach-Kampagne", "Head of Sales", "QM-Recht (UWG)", "CEO-Agent"],
                 ["Preisänderung / neues Angebot", "CEO-Agent", "CFO-Agent", "Founder"],
                 ["Pivot / Kill eines Projekts", "Founder", "–", "–"]],
                [48, 42, 40, 44]),
          PageBreak()]

def dept(title, lead, mission, rows):
    return [KeepTogether([p(title, H2), p(f"<b>Leitung:</b> {lead} &nbsp;·&nbsp; <b>Mission:</b> {mission}", NOTE)]),
            table([["Agent", "Aufgabe", "Input → Output", "Autom."]] + rows, [36, 66, 56, 16]),
            Spacer(1, 4)]

story += [p("5 · Abteilungen im Detail", H1)]
story += dept("5.1 Vertrieb (Growth & Sales)", "Head of Sales", "Planbar 10 qualifizierte Gespräche pro Woche.", [
    ["Lead-Research-Agent", "Findet Betriebe in Radius 30 km: schlechte/keine Website, < 4,3 Sterne oder < 20 Bewertungen", "Branche + PLZ → Lead-Liste (CSV)", "Ja"],
    ["Scoring-Agent", "Bewertet Bedarf (PageSpeed, Mobil, SSL, Impressum, GBP-Lücken) → Score 0–100", "Lead-Liste → priorisierte Top-30", "Ja"],
    ["Demo-Builder-Agent", "Baut personalisierte Demo-Website aus öffentlichen Infos (Pre-Build)", "Lead-Profil → Demo-URL + QR", "Ja"],
    ["Outreach-Copy-Agent", "Schreibt persönlichen Brief mit Vorher/Nachher-Screenshot & QR-Code", "Demo + Score → Brief-PDF", "Ja"],
    ["Closing-Coach-Agent", "Gesprächsleitfaden, Einwandbehandlung, Angebot in 10 Min.", "Gesprächsnotizen → Angebot + Follow-up", "Teilw."],
    ["CRM-Agent", "Pipeline pflegen, Follow-ups terminieren, Conversion messen", "Events → Pipeline-Status + Reminder", "Ja"],
])
story += dept("5.2 Delivery (Produktion)", "Head of Delivery", "Jede Auslieferung in ≤ 72 h, fehlerfrei durch alle Gates.", [
    ["Onboarding-Agent", "Checkliste, Materialabfrage (Logo, Fotos, Leistungen), Kickoff-Mail", "Auftrag → vollständiges Briefing", "Ja"],
    ["Web-Builder-Agent", "Setzt Website aus Template-Bibliothek um (statisch, schnell, EU-Hosting)", "Briefing → Staging-URL", "Ja"],
    ["Local-SEO-Copy-Agent", "Leistungs- & Ortstexte, Meta-Daten, strukturierte Daten (LocalBusiness)", "Briefing → Texte + Schema", "Ja"],
    ["GBP-Agent", "Google-Unternehmensprofil: Kategorien, Leistungen, Fotos, Posts-Plan", "Zugang → optimiertes Profil (Founder klickt)", "Teilw."],
    ["Automation-Agent", "Anfrage-Assistent: Formular → Klassifizierung → Antwortentwurf → Mail/WhatsApp-Hinweis", "Kundenprozess → Workflow", "Ja"],
    ["Handover-Agent", "Übergabe-Video-Skript, Kurzanleitung, Abo-Aktivierung", "Live-Site → Übergabepaket", "Ja"],
])
story += dept("5.3 Design & Brand", "Creative Director", "Premium-Look zum Starter-Preis – Designsystem statt Einzelstücke.", [
    ["UI-Designer-Agent", "Pflegt 6 Branchen-Templates (Elektro, SHK, Maler, Dach, Garten, Kfz)", "Branche → Template-Variante", "Ja"],
    ["Brand-Agent", "Farbpalette/Schrift aus Logo & Fahrzeugbeschriftung ableiten", "Logo/Fotos → Mini-Styleguide", "Ja"],
    ["Visual-Asset-Agent", "Bildauswahl, Freistellung, Icons – nur lizenzfreie/eigene Bilder", "Kundenfotos → optimierte Assets", "Ja"],
    ["Print-Agent", "QR-Bewertungskarte, Brief-Layout, Flyer", "Vorlagen → druckfertige PDFs", "Ja"],
])
story += dept("5.4 Content & Social", "Head of Content", "Ab M2 ≥ 30 % der Leads inbound. Build-in-Public als Vertrauensmotor.", [
    ["Social-Strategist", "Serienformate: „Website-Rettung der Woche“, „1 KI-Hack für Handwerker“", "Ziele → Redaktionsplan (4 Wo.)", "Ja"],
    ["Hook/Script-Agent", "20 Hooks/Woche, Kurzvideo-Skripte (30–45 s), LinkedIn-Posts", "Thema → Skripte", "Ja"],
    ["Case-Study-Agent", "Vorher/Nachher-Fallstudien mit Kennzahlen (nur mit Kundenfreigabe)", "Projektdaten → Case Study", "Ja"],
    ["Repurposing-Agent", "1 Video → 5 Formate (Reel, Post, Karussell, Newsletter, Blog)", "Rohmaterial → Varianten", "Ja"],
    ["Community-Agent", "Kommentare vorbereiten, Handwerker-Gruppen beobachten (keine Spam-Posts)", "Mentions → Antwortentwürfe", "Teilw."],
])
story += [PageBreak()]
story += dept("5.5 Qualitätsmanagement (QM) – mit Veto-Recht", "Head of QM", "Nichts geht live, was rechtlich, technisch oder inhaltlich angreifbar ist.", [
    ["DSGVO-Agent", "Datenschutzerklärung je Site, EU-Hosting, keine Google Fonts extern, Consent nur wenn Tracking, AVV mit jedem Abo-Kunden, Verarbeitungsverzeichnis", "Site + Tools → DSGVO-Checkliste grün/rot", "Teilw."],
    ["Recht & Rahmen-Agent", "Impressum (§ 5 DDG), UWG-Check jeder Outreach-Aktion (§ 7: keine Cold-E-Mails ohne Einwilligung!), AGB & Vertragsvorlagen, Urheber-/Markenrecht", "Kampagne/Vertrag → Freigabe + Risiken", "Teilw."],
    ["AI-Act-Agent", "Art. 50 AI Act (seit 02.08.2026): Chatbot/Assistent muss sich als KI zu erkennen geben; Kennzeichnung KI-generierter Inhalte wo täuschungsgeeignet", "KI-Feature → Kennzeichnungs-Check", "Ja"],
    ["Barrierefreiheits-Agent", "WCAG-2.2-AA-Check (Kontrast, Alt-Texte, Tastatur). BFSG: Kleinstunternehmen oft ausgenommen (~, im Einzelfall prüfen) – trotzdem Standard", "Staging-URL → A11y-Report", "Ja"],
    ["Tech-QA-Agent", "Lighthouse ≥ 90, Mobil-Test, SSL, Security-Header, defekte Links, Formular-Test, Backup", "Staging-URL → Testprotokoll", "Ja"],
    ["Content- & Faktencheck-Agent", "Keine erfundenen Zertifikate/Bewertungen/Referenzen, keine Heilversprechen, Rechtschreibung, Tonalität", "Texte → Korrekturliste", "Ja"],
    ["Finanz-Compliance-Agent", "Rechnungspflichtangaben, § 19-Hinweis, E-Rechnungs-Empfang, Belegablage (GoBD)", "Rechnung → Prüfvermerk", "Ja"],
    ["Kundenzufriedenheits-Agent", "NPS nach Livegang, 30-Tage-Check, Churn-Frühwarnung", "Kundensignale → Maßnahmen", "Ja"],
    ["Red-Team-Agent", "Devil's Advocate: greift jede Strategie, jedes Angebot, jede Annahme an", "Plan → Schwachstellenliste", "Ja"],
])
story += [gate_chart(), Spacer(1, 4),
          box("<b>Rechtlicher Hinweis:</b> Die QM-Agents ersetzen keine Rechtsberatung. Für Vertragsvorlagen & AGB einmalig "
              "anwaltlich geprüfte Muster nutzen (z. B. über IHK/Handwerkskammer-Beratung oder Rechtstext-Anbieter, ~10–25 €/Monat, "
              "sobald Umsatz fließt).", RED),
          PageBreak()]
story += dept("5.6 Finanzen & Controlling", "CFO-Agent", "Budget von 500 € niemals reißen, Cash vor Wachstum.", [
    ["Budget-Guard-Agent", "Hartes Ausgabenlimit je Monat, blockt Abos ohne ROI-Nachweis", "Ausgabeanfrage → OK/Stop", "Ja"],
    ["Buchhaltungs-Agent", "Einnahmen-Überschuss-Rechnung, Belege, Rechnungsstellung", "Belege → EÜR-Tabelle", "Ja"],
    ["Cashflow-Agent", "13-Wochen-Liquiditätsvorschau, offene Posten, Mahnlauf", "Rechnungen → Forecast", "Ja"],
    ["KPI-Agent", "Wöchentliches Dashboard (Leads, Calls, Abschlüsse, MRR, Churn, CAC)", "Rohdaten → Report", "Ja"],
])
story += dept("5.7 Operations & Automatisierung", "COO-Agent", "Jeder Prozess zweimal manuell, beim dritten Mal automatisiert.", [
    ["SOP-Agent", "Schreibt/aktualisiert Checklisten nach jedem Projekt", "Projektlog → SOP V+1", "Ja"],
    ["Workflow-Agent", "Verbindet Formular, CRM, Mail, Kalender (n8n/Make Free-Tier)", "SOP → Automation", "Ja"],
    ["Tool-Stack-Agent", "Prüft Free-Tiers, Kosten, DSGVO-Konformität neuer Tools (mit DSGVO-Agent)", "Tool-Idee → Kurzbewertung", "Ja"],
    ["Knowledge-Agent", "Zentrale Wissensbasis: Templates, Texte, Einwände, Learnings", "Alle Outputs → Wiki", "Ja"],
])
story += dept("5.8 R&amp;D / Asset-Building", "Head of R&amp;D", "Aus Dienstleistung ein skalierbares Produkt formen.", [
    ["Market-Intel-Agent", "Wettbewerber, Preise, neue Förderungen (z. B. Digitalisierungs-Förderprogramme der Länder)", "Web → Monatsbriefing", "Ja"],
    ["Productization-Agent", "Extrahiert wiederkehrende Kundenprobleme → Feature-Liste Anfrage-Autopilot", "Support-Tickets → Roadmap", "Ja"],
    ["Prototyp-Agent", "Baut MVP des SaaS (Multi-Tenant, Stripe/Abo) ab Tag 60", "Roadmap → MVP", "Ja"],
    ["Experiment-Agent", "Kleine Wetten ≤ 30 € (neue Nische, neuer Kanal), 14-Tage-Test, go/kill", "Hypothese → Ergebnis", "Ja"],
])
story += [PageBreak()]

# 6 Budget
story += [p("6 · Budget & Finanzplan", H1),
          p("Grundsatz: <b>Free-Tier first.</b> Jede kostenpflichtige Ausgabe braucht eine Umsatz-Begründung. "
            "Upgrade von Claude Pro auf Max erst, wenn der Engpass nachweislich Rechenzeit ist – nicht vorher."),
          table([["Posten", "M1", "M2", "M3", "Hinweis"],
                 ["Claude (Pro → Max 5x)", "22 €", "90 €", "90 €", "Max ab M2 nur, wenn ≥ 3 Kunden (~85–90 €/Mon.)"],
                 ["Gewerbeanmeldung", "~30 €", "–", "–", "je nach Gemeinde ~20–65 €"],
                 ["Domain eigene Marke + Mail", "~15 €", "~6 €", "~6 €", "Hosting statisch, EU-Region, Free-Tier"],
                 ["Briefe (Druck + Porto)", "~110 €", "~120 €", "~120 €", "~100 Briefe/Monat; wichtigster Akquise-Kanal"],
                 ["Rechtstexte-Dienst", "0 €", "~12 €", "~12 €", "ab erstem Abo-Kunden"],
                 ["Puffer / Experimente", "~13 €", "~2 €", "~32 €", "Experiment-Agent, max. 30 €/Test"],
                 ["<b>Summe Kosten</b>", "<b>~190 €</b>", "<b>~230 €</b>", "<b>~260 €</b>", "<b>Aus Budget: max. 500 € gesamt</b>"],
                 ["Davon aus Startkapital", "190 €", "~230 €", "~80 €", "Rest ab M2 aus Umsatz finanziert"]],
                [44, 18, 18, 18, 76]),
          Spacer(1, 8),
          p("Umsatzprognose (Basis-Szenario)", H2),
          bar_chart(),
          Spacer(1, 4),
          table([["Szenario", "M1 Umsatz", "M2 Umsatz", "M3 Umsatz", "MRR Tag 90", "Annahme"],
                 ["Pessimistisch", "490 €", "1.580 €", "~2.520 €", "~240 €", "1 / 2 / 3 Kunden, Brief-Conversion 1 %"],
                 ["<b>Basis</b>", "<b>980 €</b>", "<b>3.160 €</b>", "<b>~5.990 €</b>", "<b>~690 €</b>", "2 / 4 / 6 Kunden (M3: 4 Starter + 2 Pro); Briefe ~2 % + Besuche, ab M2 Empfehlungen/Inbound; ~70 % Abo"],
                 ["Optimistisch", "1.960 €", "5.500 €", "9.000 €+", "~1.500 €", "4 / 7 / 10 Kunden, Inbound greift"]],
                [26, 22, 22, 22, 22, 60]),
          Spacer(1, 4),
          p("Pessimistisch deckt Phase 1 knapp (490 € Umsatz vs. ~190 € Kosten) → Plan tragfähig, aber Founder-Einkommen "
            "erst in M3. Konfidenz Basis-Szenario: ~55–65 %. Größte Unsicherheit: Brief-Conversion.", NOTE),
          PageBreak()]

# 7 Roadmap
story += [p("7 · 90-Tage-Roadmap", H1),
          p("Phase 1 · Tag 1–30 · „Kosten rein“", H2),
          table([["Tag", "Was", "Wer", "Output"],
                 ["1", "Gewerbe anmelden, Geschäftskonto (kostenlos), Claude Pro; Nische: Termin-Betriebe (Kosmetik/Nails + Kfz), Düsseldorf + Umland", "Founder + CEO", "Rechtsträger steht"],
                 ["2–3", "Eigene Website + 2 Branchen-Templates, Rechtstexte, Vertragsvorlage, Angebots-PDF", "Delivery, Design, QM", "Verkaufsfähiges Setup"],
                 ["3–4", "Lead-Research: 150 Betriebe, Scoring → Top-40", "Sales", "Priorisierte Liste"],
                 ["5–7", "20 Pre-Build-Demos + 20 Briefe mit QR; parallel 10 Vor-Ort-Besuche (Founder, 1 Nachmittag)", "Sales + Founder", "Erste Welle raus"],
                 ["8–14", "Nachfassen (Anruf nur bei bestehender Geschäftsbeziehung/Einwilligung), Gespräche, 2. Welle 40 Briefe", "Sales + Founder", "≥ 5 Gespräche"],
                 ["15–21", "Erste Aufträge liefern (72 h), Case Study #1, Bewertung einholen", "Delivery + QM", "1–2 Kunden live"],
                 ["21", "<b>Checkpoint:</b> 0 zahlende Kunden → Pivot-Regel (Kap. 9)", "CEO + Founder", "go / adjust"],
                 ["22–30", "3. Welle 40 Briefe, Empfehlungsprogramm starten (100 € Gutschrift), Content-Start", "Alle", "≥ 2 Kunden, Kosten gedeckt"]],
                [14, 92, 32, 36]),
          p("Phase 2 · Tag 31–60 · „Leichtes Plus“", H2),
          *bl(["Preise auf regulär (790 € / 79 €) – Pilot-Referenzen als Beweis.",
               "Pro-Paket + Anfrage-Assistent live bei 2 Pilotkunden (Messung: Antwortzeit, Anfragen/Monat).",
               "Content-Engine: 3 Kurzvideos + 2 LinkedIn-Posts/Woche; Serie „Website-Rettung der Woche“.",
               "Zweite Nische testen (Maler/Dach) via Experiment-Agent.",
               "Ziel: ≥ 4 neue Kunden, ≥ 4 Abos aktiv, Founder-Entnahme ≥ 1.000 €."]),
          p("Phase 3 · Tag 61–90 · „Staffeln“", H2),
          *bl(["<b>Stufe 1 – MRR stapeln:</b> Abo-Quote auf 80 %, Upsell Pro/Autopilot bei Bestandskunden.",
               "<b>Stufe 2 – Partner:</b> White-Label für 2–3 Agenturen/Webdesigner (die liefern Kunden, wir produzieren).",
               "<b>Stufe 3 – Asset:</b> MVP „Anfrage-Autopilot“ als SaaS (39–79 €/Monat, Self-Service), Warteliste aus Content.",
               "<b>Stufe 4 – Geografie:</b> Remote-Vertrieb bundesweit über Content + Partner statt Vor-Ort.",
               "Ziel: ≥ 600 € MRR, 50 SaaS-Wartelisten-Kontakte, Plan Monat 4–6 (V2)."]),
          PageBreak()]

# 8 Outreach + SOP
story += [p("8 · Kern-Prozess im Detail: „Pre-Build-Outreach“", H1),
          p("Wichtigster Teilprozess, weil er Phase 1 entscheidet. Rechtlich bewusst über <b>Post & Vor-Ort</b> statt Cold-E-Mail: "
            "E-Mail-Werbung ohne vorherige ausdrückliche Einwilligung ist nach § 7 UWG auch B2B unzulässig (Abmahnrisiko). "
            "Briefe sind zulässig und heben sich ab, weil fast niemand sie mehr schickt."),
          table([["#", "Schritt", "Agent", "Zeit", "Qualitätskriterium"],
                 ["1", "Betrieb finden & Score ≥ 60", "Lead-Research + Scoring", "2 min", "Öffentliche Quellen, keine privaten Daten"],
                 ["2", "Demo-Website bauen (Name, Ort, Leistungen, echte Fakten)", "Demo-Builder", "20 min", "Nichts erfunden; Platzhalterfotos klar markiert"],
                 ["3", "Demo auf noindex-Subdomain, Passwort-/Token-Link", "Web-Builder", "2 min", "Nicht öffentlich auffindbar (Marken-/Namensschutz)"],
                 ["4", "Brief: Vorher/Nachher, 3 konkrete Verbesserungen, QR-Code, Festpreis", "Outreach-Copy + Print", "5 min", "UWG/Recht grün, Absender vollständig"],
                 ["5", "Druck & Versand", "Founder", "1 min", "Batch 20 Stück"],
                 ["6", "Tracking: QR-Aufruf → CRM-Signal → Follow-up-Brief/Besuch", "CRM", "auto", "Nur aggregiertes, cookieloses Tracking"],
                 ["7", "15-Min-Call/Besuch → Angebot sofort", "Founder + Closing-Coach", "20 min", "Angebot < 24 h"],
                 ["8", "Nicht-Kauf: Demo nach 30 Tagen löschen", "Web-Builder", "auto", "Datensparsamkeit (DSGVO)"]],
                [7, 62, 34, 13, 58]),
          Spacer(1, 6),
          p("Brief-Entwurf (V1, Auszug)", H3),
          box("<i>Betreff: Ihre neue Website ist schon fertig – schauen Sie mal (QR-Code unten)</i><br/><br/>"
              "Hallo Herr Müller,<br/>ich habe mir die Website von Müller Haustechnik angesehen. Drei Dinge kosten Sie gerade "
              "wahrscheinlich Anfragen: (1) auf dem Handy nicht lesbar, (2) kein Anfrageformular, (3) Ihr Google-Profil zeigt "
              "veraltete Öffnungszeiten.<br/>Statt Ihnen das nur zu erzählen, habe ich Ihnen eine neue Version gebaut: "
              "[QR-Code]. Gefällt sie Ihnen, geht sie für 790 € in 72 h live – inklusive Rechtstexten und Google-Profil. "
              "Gefällt sie nicht, löschen wir sie nach 30 Tagen. Kein Anruf, kein Druck.<br/>"
              "Viele Grüße, [Founder] · [Telefon] · [Adresse]"),
          p("Conversion-Annahmen (zu validieren in Woche 2)", H3),
          table([["Stufe", "Rate", "aus 100 Briefen"],
                 ["QR-Aufruf", "~15–25 %", "15–25"], ["Rückmeldung", "~5–8 %", "5–8"],
                 ["Gespräch", "~4–6 %", "4–6"], ["Abschluss", "~1–3 %", "1–3"]],
                [60, 50, 64]),
          PageBreak()]

# 9 KPIs + Risiken
story += [p("9 · Steuerung: KPIs, Kill-Kriterien, Risiken", H1),
          p("Wöchentliches Dashboard (KPI-Agent, jeden Montag)", H2),
          table([["KPI", "Ziel M1", "Ziel M2", "Ziel M3", "Rot wenn"],
                 ["Briefe versendet", "100", "100", "100", "< 60 / Monat"],
                 ["QR-Aufrufe", "≥ 15", "≥ 20", "≥ 20", "< 10 %"],
                 ["Gespräche", "≥ 5", "≥ 8", "≥ 10", "< 3"],
                 ["Neue Kunden", "≥ 2", "≥ 4", "≥ 6", "< 50 % Ziel"],
                 ["Aktive Abos", "≥ 1", "≥ 4", "≥ 8", "Churn > 10 %"],
                 ["Lieferzeit Ø", "≤ 72 h", "≤ 72 h", "≤ 48 h", "> 5 Tage"],
                 ["QM-Fehler nach Live", "0", "0", "0", "≥ 1 Rechtsfehler"],
                 ["Kosten kumuliert", "≤ 200 €", "≤ 430 €", "≤ 500 €", "Budget-Guard stoppt"]],
                [44, 30, 30, 30, 40]),
          p("Kill- & Pivot-Kriterien (vorab festgelegt, kein Bauchgefühl)", H2),
          *bl(["<b>Tag 21, 0 Kunden:</b> Angebot anpassen (Preis 290 €, oder nur GBP-Optimierung 190 €) + Nische wechseln.",
               "<b>Tag 45, < 3 Kunden gesamt:</b> Plan B aktivieren – Automations-Gigs (n8n/Make, KI-Workflows) auf Freelance-Plattformen, Delivery-Team bleibt identisch.",
               "<b>Tag 90, MRR < 300 €:</b> Engine B stoppen, voller Fokus auf Projektgeschäft/Partner.",
               "<b>Jederzeit:</b> Rechtsbeanstandung oder Abmahnung → Kampagne stoppen, QM-Post-Mortem."]),
          p("Risikomatrix", H2),
          table([["Risiko", "Wahrsch.", "Wirkung", "Gegenmaßnahme"],
                 ["Brief-Conversion zu niedrig", "mittel", "hoch", "A/B-Tests je 20 Briefe, Vor-Ort-Besuche, Handwerkskammer-Events, Empfehlungsprogramm"],
                 ["Abmahnung (UWG/DSGVO/Marken)", "niedrig", "hoch", "QM-Gates, keine Cold-Mails, Demos noindex + Löschfrist, Musterverträge"],
                 ["KI-Fehler/Halluzination in Kundentexten", "mittel", "mittel", "Faktencheck-Agent + Founder-Freigabe, nur belegte Fakten"],
                 ["Founder-Zeit Engpass", "mittel", "hoch", "Termine bündeln (2 Nachmittage/Woche), alles andere delegiert"],
                 ["Tool-/Preisänderungen", "mittel", "niedrig", "Statische Sites, kein Lock-in, exportierbare Daten"],
                 ["Zahlungsausfall", "niedrig", "mittel", "50 % Anzahlung, Livegang erst nach Restzahlung"],
                 ["Überschreitung Kleinunternehmergrenze", "niedrig (Jahr 1)", "niedrig", "Ab ~20.000 € Umsatz Steuerberater, Regelbesteuerung vorbereiten"]],
                [44, 20, 18, 92]),
          PageBreak()]

# 10 Future + next steps
story += [p("10 · Ausblick & nächste Schritte", H1),
          p("Vision / Future-Idee: „Anfrage-Autopilot“ (Engine B)", H2),
          *bl(["<b>Zweck:</b> Handwerker verlieren Aufträge, weil Anfragen liegen bleiben. Der Autopilot sortiert jede Anfrage "
               "(Web, Mail, WhatsApp Business), fragt fehlende Infos/Fotos nach und legt einen Angebotsentwurf vor.",
               "<b>Inputs:</b> Formular-/Mail-Anfragen, Leistungskatalog & Preise des Betriebs.",
               "<b>Outputs:</b> Priorisierte Anfragen, Rückfragen (als KI gekennzeichnet, Art. 50), Angebotsentwurf zur Freigabe.",
               "<b>Minimal-Implementierung:</b> Formular → Claude API → Supabase (EU) → Mail-Digest; Stripe-Abo; ab Tag 60.",
               "<b>Hebel:</b> Einmal gebaut, 100 Kunden × 49 € = 4.900 € MRR ohne lineare Mehrarbeit."]),
          p("Monat 4–12 (grob)", H2),
          table([["Zeitraum", "Fokus", "Ziel"],
                 ["M4–M6", "SaaS-Beta mit 10 Bestandskunden, Partnerprogramm, 2. Region", "MRR 2.000–3.000 €"],
                 ["M7–M9", "Self-Service-Onboarding, Content skaliert, erste Freelancer (Mensch) für Vor-Ort", "MRR 4.000–6.000 €"],
                 ["M10–M12", "Rücklage aufbauen; erst dann Trading-Bot-R&amp;D mit Risikokapital ≤ 10 % der Rücklage", "Finanzielle Grundsicherung"]],
                [24, 110, 40]),
          p("Die ersten 72 Stunden – To-dos für den Founder", H2),
          *bl(["<b>Heute:</b> Plan freigeben oder challengen (Nische, Preis, Radius).",
               "<b>Morgen:</b> Gewerbe anmelden, Geschäftskonto eröffnen, Adresse & Telefonnummer für Impressum festlegen.",
               "<b>Tag 3:</b> 1 Nachmittag: 10 Betriebe vor Ort besuchen (Gesprächsleitfaden kommt vom Closing-Coach).",
               "Parallel liefert das Agent-Team: Eigene Website, 2 Templates, Lead-Liste Top-40, erste 20 Demos + Briefe."]),
          Spacer(1, 8),
          box("<b>Annahmen-Register (explizit):</b> Founder hat ~1–2 h/Tag, deutsche Adresse, darf Gewerbe anmelden; "
              "Zielregion hat ≥ 150 passende Betriebe im Radius 30 km; Brief-Conversion ~2 % (unvalidiert); "
              "Claude-Preise laut Recherche 09/2026 (Pro ~20 $, Max ab ~85–90 €/Mon.); alle Umsatzzahlen sind Schätzungen. "
              "Recht: Stand Recherche 09/2026, keine Rechtsberatung.", GOLD),
          Spacer(1, 8),
          p("Quellen (Recherche 29.09.2026)", H3),
          p("Bitkom/ZDH-Zahlen via streit-software.de/wissen/ki-handwerk · Website-Preise: meinbetriebonline.de, eoglou.de, "
            "blackforest-webcraft.de · Kleinunternehmergrenzen: taxfix.de, gruenderplattform.de · AI Act Art. 50: "
            "forum-institut.de, passion4it.de · Claude-Preise: kirstenbiema.com, screenapp.io", NOTE)]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=16 * mm,
                        title="Projekt Diamant – Masterplan V1", author="CEO-Agent (Claude)")
doc.build(story, onFirstPage=on_first, onLaterPages=on_page)
print(OUT)
