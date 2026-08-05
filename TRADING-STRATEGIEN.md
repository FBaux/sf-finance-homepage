# TRADING-STRATEGIEN — DayDom Performance Group

Festgehaltener Stand der drei Setups, Diktat vom 05.08.2026.

**Instrument: Gold (XAUUSD).** Alle Zeitangaben und Level-Definitionen beziehen
sich darauf.

Die Begriffe sind aus der Sprachaufnahme in die übliche Schreibweise überführt:
FVG = Fair Value Gap, IFVG = Inverse Fair Value Gap, OB = Order Block,
VAH/VAL/POC = Value Area High / Value Area Low / Point of Control.

---

## Bestätigungsmodell (gilt für alle drei Strategien)

**Was als Sweep gilt:** der Docht darf durch das Level laufen, die 15m-Kerze muss
aber wieder **diesseits des Levels schließen**. Klassische Wick-Rejection. Ein
Close jenseits des Levels ist kein Sweep, sondern ein Durchbruch — dann gibt es
kein Setup.

**Gültigkeitsfenster:** die Bestätigung muss innerhalb von **2–3 15m-Kerzen** nach
dem Sweep kommen, also spätestens nach rund 45 Minuten. Danach ist das Setup
verworfen — kommt die Reaktion nicht zügig, war sie nicht stark genug.

**Alle Bestätigungen werden im 15-Minuten-Chart gesucht.** Ohne Ausnahme, in
allen drei Strategien — unabhängig davon, auf welchem Zeitrahmen der Auslöser
liegt. Ein 4H-Order-Block wird also nicht auf einer 4H-Kerze bestätigt, sondern
auf 15m.

Nach dem Auslöser wird nie direkt eingestiegen. Es braucht **eine** der beiden Bestätigungen:

1. **IFVG** — eine bestehende FVG wird gegenläufig durchhandelt und invertiert.
   Gültig erst, wenn die Kerze **außerhalb der IFVG schließt**. Ein Docht reicht nicht.
2. **Engulfing** — Umkehrkerze, die den Körper der Vorkerze vollständig umschließt.

Erst mit einer der beiden Bestätigungen wird der Entry gesetzt.

**Stop Loss** — hängt davon ab, welche der beiden Bestätigungen gegriffen hat:

- **Nach IFVG:** knapp jenseits der FVG, mit Puffer von rund **25 % der FVG-Größe**.
  Bei Long unter, bei Short über die Gap.
- **Nach Engulfing:** knapp jenseits von **Hoch bzw. Tief der Engulfing-Kerze**,
  ohne prozentualen Puffer. Hier gibt es keine FVG als Bezugsgröße.

**Trade-Management:** keins. SL und TP stehen beim Entry und werden nicht mehr
angefasst — keine Teilabnahme, kein Break-even-Stop, kein Nachziehen. Die
Position läuft in den Stop oder ins Ziel. Bewusst so gewählt, damit die Setups
sauber messbar bleiben.

Der Stop hängt damit immer an der **15m-Bestätigungs-Gap**, nie an der Zone, die
den Auslöser geliefert hat. Auch bei einem 4H-Order-Block sitzt der Stop an der
15m-IFVG — er liegt dann deutlich innerhalb der HTF-Zone. Das ist so gewollt:
enger Stop, hohes RR, dafür bewusst mehr Fehlversuche.

---

## Strategie 1 — Volume Profile der Asia Session

**Auslöser: Sweep eines Volume-Profile-Levels.**

1. Volume Profile über die **komplette Asia Session** ziehen.
   Aktuell eingetragenes Fenster: **02:00–10:00**. Das Fenster ist die aktuelle
   Einstellung, nicht Teil der Strategie-Definition — bei Broker- oder
   Zeitzonenwechsel anpassen.
2. Aus dem Profil ergeben sich **VAH**, **VAL** und **POC**.
3. **Erst ab 10:00 gehandelt**, also nach Session-Ende. Bis dahin läuft das Profil
   noch, die Level stehen nicht fest. Ein Sweep innerhalb der Asia-Session zählt
   nicht — gesucht wird der Sweep gegen die **abgeschlossene** Range, im
   London-/NY-Fenster.
4. Warten, bis eines dieser Level gesweept wird — **bevorzugt VAH oder VAL**.
5. Bestätigung abwarten: IFVG mit Close außerhalb, oder Engulfing — im 15m-Chart.
6. **Entry** auf Bestätigung.
7. **Ziel: 2:1 RR, ungedeckelt.** Anders als in Strategie 2 wird hier nicht
   vorzeitig geschlossen — der POC und das gegenüberliegende Value-Area-Level
   gelten als Durchgangsstationen, nicht als Ziel. SL nach dem Bestätigungsmodell
   oben (~25 % Puffer über der FVG).

---

## Strategie 2 — Session Sweep

Der klassische Fall, gleiche Mechanik ohne Volume Profile.

1. **Session High** oder **Session Low** wird gesweept — Liquidität wird rausgenommen.
   In Frage kommen die Ranges von **Asia, London und NY**. Maßgeblich ist immer
   die jeweils **abgeschlossene** Session, deren Hoch/Tief dann im folgenden
   Fenster als Liquiditätsziel dient. Das Vortages-Hoch/-Tief zählt nicht dazu.
2. Bestätigung abwarten: IFVG oder Engulfing — im 15m-Chart.
3. **Entry** auf Bestätigung.
4. SL nach dem Bestätigungsmodell.
5. **Ziel: 2:1 RR, gedeckelt am nächsten relevanten Level.** Liegt eine Zone vor
   dem rechnerischen 2:1-Ziel, wird dort geschlossen statt darauf zu hoffen,
   dass der Preis durchläuft.

---

## Strategie 3 — HTF Order Block / FVG Reaction

Höherer Zeitrahmen, Ziel ergibt sich aus der Struktur statt aus einem festen RR.

1. **1H- oder 4H-Order-Block** identifizieren — per Indikator oder manuell.
   Ebenso die **1H- bzw. 4H-FVG**.
2. Warten auf den **Hit** der jeweiligen Zone (OB oder FVG).
   Mehrfache Tests sind zulässig — eine schon einmal angetestete Zone bleibt
   gültig. Erst wenn der Preis **komplett durch die Zone geschlossen** hat, ist
   sie verbraucht und liefert kein Setup mehr.
3. **Reaktion abwarten** — der Preis muss drehen.
4. Bestätigung: IFVG oder Engulfing — **im 15m-Chart**, nicht im Zeitrahmen der Zone.
5. **Stop Loss:** 25 % jenseits der 15m-IFVG, nicht hinter der HTF-Zone.
6. **Take Profit:** die nächste Zone **im selben Zeitrahmen**.
   - 4H-Setup → nächster 4H-OB; liegt eine 4H-FVG davor, ist die das Ziel.
   - 1H-Setup → nächster 1H-OB; liegt eine 1H-FVG davor, ist die das Ziel.

Der Zeitrahmen bleibt über Setup und Ziel hinweg konsistent — ein 4H-Einstieg
targetiert keine 1H-Zone.

---

## Offene Punkte

Nicht diktiert, bewusst nicht angenommen — vor der Umsetzung zu klären:

- Wenn **beide** Bestätigungen auftreten (Engulfing erzeugt eine IFVG): welcher
  Stop gilt dann — der engere oder der an der IFVG?
- Was gilt als „relevantes Level" für die **Deckelung in Strategie 2** — nur
  Session-Level, oder auch HTF-Zonen und Volume-Profile-Level?
- Gibt es ein **Maximum an Trades pro Tag**, und wird bei Hochtief-News
  (CPI, FOMC, NFP) pausiert? Bei Gold relevant.
