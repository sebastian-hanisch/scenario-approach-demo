# Chance-Constraint mit Garantie: der Szenario-Ansatz – Streamlit-Demo

Fünftes Stück der **Optimierung-unter-Unsicherheit-Linie** der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“.
Anders als die Fall-Demos (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt sie **ein** Verfahren, den **Szenario-Ansatz** (Calafiore und Campi), an einem wachsenden Beispiel.
**Kante in der Linie:** Wo die [robuste Demo](https://github.com/sebastian-hanisch/robust-opt-demo) eine **Menge** garantiert, garantiert dieses Stück eine **Wahrscheinlichkeit**: Ein Szenario-LP über N gezogene
Szenarien liefert einen Plan, dessen wahre Verletzungswahrscheinlichkeit mit vorab bekannter Konfidenz unter ε liegt. Das Vehikel ist das Kapazitäts-Vehikel der
[Wurzel](https://github.com/sebastian-hanisch/newsvendor-evpi-demo), hier **ohne Umlagerung**: sechs Entscheidungsvariablen.

## Warum dieses Problem

„Mit 95 % Wahrscheinlichkeit höchstens eine kleine Fehlmenge“ lässt sich nicht direkt rechnen, wenn man die Verteilung nicht kennt. Der Szenario-Ansatz ersetzt die Wahrscheinlichkeitsaussage durch N harte
Nebenbedingungen und liefert eine **Schranke**, wie groß N sein muss. Die Demo misst, **ob die Garantie hält, wie nah die Schranke an der Wirklichkeit liegt und was sie kostet**.

## Modell

Sechs Standorte, Kapazität x_j zu 1 je Einheit; Zukauf bis 50 % der mittleren Nachfrage; **Fehlmenge insgesamt** g(x, D) = Σ_k (D_k − x_k − u_k)⁺. Gesucht: min c·x mit
P(g(x, D) ≤ b) ≥ 1 − ε. Die Nachfrage ist lognormal mit gemeinsamem Faktor; geprüft wird auf 20 000 frischen Szenarien, die die Optimierung nie sieht. Formeln im 📐-Expander der App.

## Methodik

- **Szenario-LP:** N Szenarien, für jedes Σ_k w_sk ≤ b mit w_sk ≥ D_sk − x_k − u_k (ein LP mit N · 6 Hilfsvariablen).
- **Drei Schranken** für N bei d = 6: die **exakte Binomialform** (Campi und Garatti 2008), die **einfache Formel** (2/ε)(ln(1/β) + d) und die **Formel von Calafiore und Campi 2006**.
- **Prüfen:** wahre Verletzung V(x_N) auf der Referenz, Kosten, Stützszenarien (Szenarien mit bindender Nebenbedingung).
- **Rücknahme:** dieselbe Lösung, gleichmäßig je Standort gekürzt, bis V genau ε erreicht (Bisektion): die Differenz ist der Preis des Überschutzes.
- **Experiment:** 100 unabhängige Ziehungen je Szenarienzahl (zwei kleine Zahlen und die drei Schranken).

## Befunde (gemessen, keine Behauptungen)

Voreinstellung (ε = 5 %, β = 1 %, b = 30, Streuung 35 %, Seed 7); jede Aussage in `tests/test_claims.py` als Band belegt.

| Frage | Befund |
|---|---|
| **Wie viele Szenarien verlangt die Garantie?** | Exakte Schranke 259, einfache Formel 425 (1,6-fach), Calafiore und Campi 2006: 1 082 (4,2-fach). Bei ε = 2 %, β = 0,001 %: 1 119 / 1 752 / 3 927; bei ε = 10 %, β = 1 %: 127 / 213 / 464. |
| **Hält die Garantie?** | Bei N = 259 verletzt keine der 100 Ziehungen ε; die wahre Verletzung liegt im Median bei 1,6 %, im 95. Perzentil bei 2,8 % (erlaubt: 5 %). |
| **Was passiert bei zu wenig Szenarien?** | N = 20: 96 % der Ziehungen verletzen ε (Median 12,8 %). N = 60: 64 % (Median 5,6 %). |
| **Wie weit ist die Schranke von der Wirklichkeit?** | Die Garantie ist ein Schlimmster-Fall-Satz: in dem Beispiel liegt die wahre Verletzung weit unter ε. Das heißt Überschutz. |
| **Was kostet die Garantie?** | Mittlere Kosten 1 025 bei N = 259, 1 102 bei 425, 1 242 bei 1 082 (zum Vergleich 658 bei N = 20, das ε aber nicht hält). Dieselbe Lösung bis zur Grenze ε zurückgenommen kostet 841: die Garantie bei N = 259 ist 22 % teurer als nötig. |
| **Wie viele Stützszenarien?** | Im Mittel 4,4 von höchstens 6 bei N = 259, 5,1 bei N = 1 082: Nur wenige Szenarien bestimmen den Plan. |
| **Wie typisch ist eine Ziehung?** | Die Kosten schwanken stark: In 25 Ziehungen von 804 bis 1 316; die wahre Verletzung von 0,3 % bis 4,7 %. |

## Ehrliche Grenzen

- **Nur konvexe Probleme.** Die Garantie gilt nur dort; hier ist die Fehlmenge konvex in der Kapazität. Mit ganzzahligen oder nichtkonvexen Entscheidungen gilt die Schranke nicht.
- **Unabhängige Ziehungen aus der wahren Verteilung.** Verschobene Verteilungen und Trends sind nicht abgedeckt.
- **Überschutz ist der Preis der Garantie.** Wer die Verteilung kennt, kann die Grenze direkt treffen und spart rund ein Fünftel der Kosten.
- **Eine Instanz, ein ε je Lauf.** Die Prozentzahlen hängen an Instanz und Schwelle.
- **Ohne Umlagerung.** Mit Umlagerung hinge die Nebenbedingung nur an der Summe der Kapazitäten (d = 1): Die Schranke wäre sehr klein und das Problem eine einfache Quantilregel.

## Verifikation

- **Kern:** Fehlmenge und Verletzung an Handwerten, Szenario-LP an der Mini-Instanz von Hand (110 und 100), Rücknahme stoppt bei ε und tut nichts bei schon verletztem ε, die drei Schranken an Handwerten (425 aus der Formel), Binomialschranke ist das kleinste N mit Garantie.
- **Orakel (`tests/test_oracle_scenario_approach.py`):** dasselbe LP als eigenes Modell in OR-Tools (GLOP, 1e-7); bei einem Standort ist der Plan das Stichprobenmaximum minus Grenze und Schwelle
  (geschlossene Form), die wahre Verletzung folgt der Beta(1, N)-Verteilung (Mittel 1/(N+1), P(V > ε) = (1 − ε)^N über 300 Ziehungen) und die Binomialschranke ist dort exakt gleich (1 − ε)^N.
- **Claims (`tests/test_claims.py`):** Schranken, Garantie bei der exakten Schranke, Verletzung bei kleinem N, Kosten über N, Überschutz, Stützszenarien, typische Ziehung.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Experiment-Knopf, Footer.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-App |
| `sap_rng.py`, `sap_scenario.py` | Zufall, Instanz und Nachfrage-Szenarien (wie in der Wurzel) |
| `sap_core.py` | Fehlmenge, Verletzung, Szenario-LP, Rücknahme, die drei Schranken |
| `sap_evaluation.py` | Ziehung gegen die Referenz, Experiment |
| `sap_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `sap_presets.py` | Permalink (Begrenzen, Einrasten), Presets, Zufalls-Seed-Buttons |
| `sap_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanz, Orakel, Claims, Presets, AppTest-Smoke-Test, Footer |

## Bewusst nicht umgesetzt

- **Verwerfen von Szenarien** (Chance-Constrained-SAA mit Entfernen der teuersten): würde den Überschutz senken, ist aber ein ganzzahliges Problem.
- **Ganzzahlige Entscheidungen:** außerhalb der konvexen Garantie.
- **Gemeinsamer Faktor als Information:** Szenarien sind hier ohne Zusatzwissen gezogen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Unsicherheit: von EVPI bis rollierend](https://sebastianhanisch.net/konzepte-optimierung-unsicherheit.html).
