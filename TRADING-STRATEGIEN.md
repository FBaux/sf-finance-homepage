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
   Eine FVG, die aus dem Sweep-Move selbst stammt, ist das stärkere Signal; eine
   ältere Gap, die zufällig am Level liegt, zählt aber ebenso.
2. **Engulfing** — Umkehrkerze, deren **Körper** den Körper der Vorkerze
   vollständig umschließt. Die Dochte spielen keine Rolle; die Kerze muss die
   Vorkerze nicht komplett von High bis Low überdecken.

Erst mit einer der beiden Bestätigungen wird der Entry gesetzt.

**Stop Loss** — hängt davon ab, welche der beiden Bestätigungen gegriffen hat:

- **Nach IFVG:** knapp jenseits der FVG, mit Puffer von rund **25 % der FVG-Größe**.
  Bei Long unter, bei Short über die Gap.
- **Nach Engulfing:** knapp jenseits von **Hoch bzw. Tief der Engulfing-Kerze**,
  ohne prozentualen Puffer. Hier gibt es keine FVG als Bezugsgröße.

**Bei Konfluenz:** fallen zwei Setups zusammen — etwa VAH und Session-High auf
fast demselben Kurs — wird trotzdem nur **ein Trade in normaler Größe** genommen.
Die Konfluenz erhöht die Qualität, nicht die Positionsgröße. Kein doppeltes
Risiko auf derselben Idee.

**Anzahl und News:** kein Tageslimit — jedes gültige Setup wird genommen. Rund um
die großen Termine (**CPI, FOMC, NFP**) wird dagegen nicht gehandelt; bei Gold
sind die Ausschläge dort zu groß für die engen Stops. Das Fenster ist eng
gefasst: **15 Minuten vor bis 15 Minuten nach** der Veröffentlichung. Davor und
danach läuft der normale Betrieb weiter.

**Entry-Ausführung:** Market, direkt beim **Close der 15m-Bestätigungskerze**.
Es wird nicht auf einen Retest in die IFVG oder den Engulfing-Körper gewartet —
lieber ein schlechterer Kurs als ein verpasstes Setup.

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
   Aktuell eingetragenes Fenster: **02:00–10:00 deutscher Zeit (MEZ/MESZ)**.
   Da die Angabe an der lokalen Sommerzeit hängt, verschiebt sich die Session
   zweimal jährlich gegenüber dem Markt — bei der Umstellung prüfen, ob das
   Fenster noch die tatsächliche Asia-Session abdeckt. Das Fenster ist die
   aktuelle Einstellung, nicht Teil der Strategie-Definition.
2. Aus dem Profil ergeben sich **VAH**, **VAL** und **POC**.
3. **Erst ab 10:00 gehandelt**, also nach Session-Ende. Bis dahin läuft das Profil
   noch, die Level stehen nicht fest. Ein Sweep innerhalb der Asia-Session zählt
   nicht — gesucht wird der Sweep gegen die **abgeschlossene** Range, im
   London-/NY-Fenster.
4. Warten, bis **VAH oder VAL** gesweept wird. Nur diese beiden sind Auslöser.
   Der **POC wird eingezeichnet, aber nie gehandelt** — er dient ausschließlich
   der Orientierung im Profil.
5. Bestätigung abwarten: IFVG mit Close außerhalb, oder Engulfing — im 15m-Chart.
6. **Entry** auf Bestätigung.
7. **Ziel: 2:1 RR, ungedeckelt.** Anders als in Strategie 2 wird hier nicht
   vorzeitig geschlossen — POC und gegenüberliegendes Value-Area-Level sind
   Durchgangsstationen, nicht Ziel. SL nach dem Bestätigungsmodell
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
   Als Deckel zählen die **Session-Level** sowie die **1H-/4H-Zonen aus
   Strategie 3** (Order Blocks und FVGs). Die Volume-Profile-Level aus
   Strategie 1 deckeln hier **nicht**.

---

## Strategie 3 — HTF Order Block / FVG Reaction

Höherer Zeitrahmen. Das Ziel ergibt sich aus der Struktur statt aus einem festen
RR — mit 1,5:1 als Untergrenze.

1. **1H- oder 4H-Order-Block** identifizieren — per Indikator oder manuell.
   Ebenso die **1H- bzw. 4H-FVG**.
2. Warten auf den **Hit** der jeweiligen Zone (OB oder FVG).
   Die Zone eines Order Blocks ist die **komplette Kerze von High bis Low**,
   inklusive Dochte — nicht nur der Körper und nicht erst der 50-%-Punkt. Der
   Hit zählt, sobald der Preis das äußere Ende der Zone berührt.
   Mehrfache Tests sind zulässig — eine schon einmal angetestete Zone bleibt
   gültig. Erst wenn der Preis **komplett durch die Zone geschlossen** hat, ist
   sie verbraucht und liefert kein Setup mehr.
3. **Reaktion abwarten** — der Preis muss drehen.
4. Bestätigung: IFVG oder Engulfing — **im 15m-Chart**, nicht im Zeitrahmen der Zone.
5. **Stop Loss:** an der 15m-Bestätigung, nicht hinter der HTF-Zone — 25 %
   jenseits der IFVG bzw. knapp hinter der Engulfing-Kerze.
6. **Mindest-RR: 1,5:1.** Liegt die nächste Zone so nah, dass sich vom 15m-Stop
   aus kein 1,5:1 ergibt, wird der Trade nicht genommen.
7. **Take Profit:** die nächste Zone **im selben Zeitrahmen**.
   - 4H-Setup → nächster 4H-OB; liegt eine 4H-FVG davor, ist die das Ziel.
   - 1H-Setup → nächster 1H-OB; liegt eine 1H-FVG davor, ist die das Ziel.

Der Zeitrahmen bleibt über Setup und Ziel hinweg konsistent — ein 4H-Einstieg
targetiert keine 1H-Zone.

---

## Offene Punkte

Nicht diktiert, bewusst nicht angenommen — vor der Umsetzung zu klären:

- Wenn **beide** Bestätigungen auftreten (Engulfing erzeugt eine IFVG): welcher
  Stop gilt dann — der engere oder der an der IFVG?
- Wie wird die **Positionsgröße** bestimmt — fester Prozentsatz des Kontos pro
  Trade, oder fester Betrag? Bei Prop-Firm-Konten zusätzlich relevant wegen der
  Daily-Loss-Limits.
