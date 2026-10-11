"""Chance-Constraint mit Garantie: der Szenario-Ansatz - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sap_constants as C
import sap_core as K
from sap_evaluation import Settings, bounds_for, build_instance, draw_seed, experiment, one_draw, reference_demand
from sap_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    new_draw,
    randomize_seed,
    sync_query_params,
)
from sap_visualization import build_bounds, build_cost, build_plan, build_violation

st.set_page_config(page_title="Szenario-Ansatz – Sebastian Hanisch", layout="wide")


def _de(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def _g(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def _pct(value: float, digits: int = 1) -> str:
    return f"{_de(100.0 * value, digits)} %"


@st.cache_data(show_spinner=False)
def _reference(settings_key):
    sigma, seed = settings_key
    return reference_demand(build_instance(Settings(sigma=sigma, seed=seed)))


@st.cache_data(show_spinner=False)
def _draw(settings):
    inst = build_instance(settings)
    ref = _reference((settings.sigma, settings.seed))
    return one_draw(inst, ref, settings.n, float(settings.b), settings.eps, draw_seed(settings.draw, 0, settings.n))


@st.cache_data(show_spinner=False)
def _experiment(settings):
    return experiment(settings)


st.title("🎯 Chance-Constraint mit Garantie: der Szenario-Ansatz")
st.markdown(
    """
„Mit 95 % Wahrscheinlichkeit darf höchstens eine kleine Fehlmenge entstehen“ ist eine **Chance-Nebenbedingung**: Man kann sie nicht direkt rechnen, weil man die Verteilung nicht kennt.
Der **Szenario-Ansatz** zieht N Szenarien, erzwingt die Bedingung für alle N und beweist: Ist N groß genug, dann gilt die Bedingung mit der gewünschten Wahrscheinlichkeit auch **für die wahre
Verteilung**, und zwar mit einer vorab bekannten Konfidenz. Diese Demo fragt: **Wie viele Szenarien verlangt die Garantie, und was kostet sie?**

Anders als die Fall-Demos zeigt sie **ein** Verfahren an einem wachsenden Beispiel, mit dem Kapazitäts-Vehikel der Linie, hier **ohne Umlagerung** (sechs Entscheidungsvariablen).
Weiter unten: das Experiment, **🚧 Wo die Annahmen enden** und **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Szenario-Ansatz", expanded=True):
    st.markdown(
        """
1. **Aufgabe:** minimale Kapazitätskosten, so dass die Fehlmenge insgesamt (Nachfrage jenseits von Kapazität plus Zukaufgrenze) mit Wahrscheinlichkeit höchstens ε über der Schwelle b liegt.
2. **Ziehen:** N Szenarien der Nachfrage; **für jedes** muss die Fehlmenge unter b bleiben. Das ist ein gewöhnliches LP (konvex, weil die Fehlmenge in der Kapazität konvex ist).
3. **Garantie:** Mit Wahrscheinlichkeit mindestens 1 − β über die Ziehung ist die **wahre** Verletzungswahrscheinlichkeit des Ergebnisses höchstens ε, wenn N die Schranke erreicht (d = 6 Entscheidungsvariablen).
4. **Prüfen:** Das Ergebnis auf 20 000 frischen lognormalen Szenarien, die der Ansatz nie sah: wie oft verletzt, was kostet es?
        """
    )

if C.PRESETS:
    st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
    cols = st.columns(len(C.PRESETS))
    for col, name in zip(cols, C.PRESETS):
        with col:
            st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.markdown("**Garantie**")
    eps = st.radio("ε: erlaubte Verletzungswahrscheinlichkeit", C.EPS_CHOICES, key="eps_radio", horizontal=True,
                   format_func=lambda v: f"{round(v * 100)} %", help="Mit welcher Wahrscheinlichkeit die Fehlmenge-Bedingung höchstens verletzt sein darf.")
    beta = st.radio("β: Irrtumswahrscheinlichkeit der Garantie", C.BETA_CHOICES, key="beta_radio", horizontal=True,
                    format_func=lambda v: f"{v * 100:g} %".replace(".", ","),
                    help="Mit Wahrscheinlichkeit höchstens β über die Ziehung darf die wahre Verletzung doch über ε liegen.")
    b = st.slider("b: erlaubte Fehlmenge insgesamt", *bounds("b_slider"), step=C.B_STEP, key="b_slider",
                  help="Schwelle der Fehlmenge (Einheiten, summiert über die Standorte); darüber zählt ein Szenario als Verletzung.")
    st.markdown("**Stichprobe**")
    n = st.slider("N: Szenarien des Ansatzes", *bounds("n_slider"), step=C.N_STEP, key="n_slider",
                  help="Wie viele Szenarien für das LP gezogen werden. Das Experiment unten läuft über feste Werte.")
    draw = st.number_input("Ziehung (Zufalls-Seed)", *bounds("draw_input"), key="draw_input", step=1)
    st.button("🎲 Neue Ziehung", width="stretch", on_click=new_draw)
    st.markdown("**Nachfrage**")
    sigma = st.slider("Streuung (Log-Streuung σ)", *bounds("sigma_slider"), step=C.SIGMA_STEP, key="sigma_slider",
                      help="Wie stark die Nachfrage um ihren Mittelwert schwankt.")
    st.markdown("**Instanz**")
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)

sync_query_params({
    "eps_radio": eps, "beta_radio": beta, "n_slider": int(n), "b_slider": int(b), "sigma_slider": sigma,
    "seed_input": int(seed), "draw_input": int(draw),
})

settings = Settings(eps=float(eps), beta=float(beta), n=int(n), b=int(b), sigma=float(sigma), seed=int(seed), draw=int(draw))
exp_key = Settings(eps=settings.eps, beta=settings.beta, n=C.DEFAULT_N, b=settings.b, sigma=settings.sigma, seed=settings.seed, draw=settings.draw)
inst = build_instance(settings)
bnd = bounds_for(settings.eps, settings.beta)

# --- Wie viele Szenarien? -----------------------------------------------------------------------------------------------------------------

st.markdown("## 🔢 Wie viele Szenarien verlangt die Garantie?")
c1, c2, c3 = st.columns(3)
c1.metric("Exakte Schranke (Binomialform)", f"{bnd.binomial}", delta="kleinstes N mit Garantie", delta_color="off")
c2.metric("Einfache Formel", f"{bnd.simple}", delta=f"{_de(bnd.simple / bnd.binomial, 1)}-fach der exakten", delta_color="off")
c3.metric("Calafiore/Campi 2006", f"{bnd.calafiore_campi}", delta=f"{_de(bnd.calafiore_campi / bnd.binomial, 1)}-fach der exakten", delta_color="off")
st.plotly_chart(build_bounds(bnd, settings.n), width="stretch", key="bounds_chart")
st.caption(
    f"Für ε = {_pct(settings.eps, 0)}, β = {_g(settings.beta * 100)} % und d = {bnd.d} Entscheidungsvariablen. Alle drei Zahlen **garantieren**; die Binomialform ist die schärfste "
    "bekannte, die anderen sind einfache, aber weitaus großzügigere Abschätzungen."
)

# --- Eine Ziehung -------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Eine Ziehung")
with st.spinner("Löse das Szenario-LP und prüfe es auf 20 000 frischen Szenarien …"):
    d = _draw(settings)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Kosten der Kapazität", f"{d.cost:,.0f}".replace(",", "."), delta=f"{_pct(d.cost / d.cost_pulled_back - 1.0)} über der zurückgenommenen Lösung" if d.cost_pulled_back == d.cost_pulled_back else "Grenze überschritten", delta_color="inverse")
m2.metric("Wahre Verletzung V", _pct(d.violation, 2), delta=f"Grenze ε = {_pct(settings.eps, 0)}", delta_color="off")
m3.metric("Stützszenarien", f"{d.support} von höchstens {bnd.d}", delta="Szenarien, die den Plan bestimmen", delta_color="off")
m4.metric("Kosten, bis ε zurückgenommen", f"{d.cost_pulled_back:,.0f}".replace(",", ".") if d.cost_pulled_back == d.cost_pulled_back else "–",
          delta="dieselbe Lösung, gleichmäßig gekürzt, bis V = ε", delta_color="off")
st.plotly_chart(build_plan(inst.mu, inst.spot_limit, d.x), width="stretch", key="plan_chart")
st.caption("Grau: so viel Kapazität bräuchte ein Standort im Mittel, wenn der Zukauf seine Grenze ausschöpft. Der Plan liegt darüber: das ist der Puffer für die Garantie.")

st.markdown("## ❓ Kernfrage: Hält die Garantie, und was kostet sie?")
if d.violation > settings.eps:
    st.warning(
        f"**Diese Ziehung verletzt ε:** die wahre Verletzung liegt bei {_pct(d.violation, 2)} statt höchstens {_pct(settings.eps, 0)}. "
        + ("Mit N unter der Schranke ist das zu erwarten." if settings.n < bnd.binomial else
           f"Bei N ≥ {bnd.binomial} ist das höchstens mit Wahrscheinlichkeit β = {_g(settings.beta * 100)} % möglich; die Garantie ist nur mit dieser Konfidenz.")
    )
elif settings.n < bnd.binomial:
    st.info(
        f"**Diese Ziehung hält ε** ({_pct(d.violation, 2)}), aber N = {settings.n} liegt unter der Schranke von {bnd.binomial}: Das ist Glück, keine Garantie. "
        "Das Experiment zeigt, wie oft solche Ziehungen verletzen."
    )
else:
    over = d.cost / d.cost_pulled_back - 1.0 if d.cost_pulled_back == d.cost_pulled_back else 0.0
    st.success(
        f"**Die Garantie hält:** wahre Verletzung {_pct(d.violation, 2)} bei erlaubtem {_pct(settings.eps, 0)}. Der Preis des Überschutzes: die Lösung ist "
        f"{_pct(over, 0)} teurer, als sie bei genau ε sein müsste."
    )
st.caption("Das ist **eine** Ziehung. Wie sich die wahre Verletzung über viele Ziehungen verteilt, zeigt das Experiment.")

st.markdown("---")

# --- Experiment ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie oft hält die Garantie, und was kostet sie?")
st.caption(
    f"{C.REPEATS} unabhängige Ziehungen je Szenarienzahl: zwei kleine Zahlen und die drei Schranken. Die Szenarienzahl-Regler wirkt hier nicht; "
    "ε, β, b, Streuung, Instanz und Ziehung gelten."
)
if st.button("Experiment starten (ca. 30 Sekunden)", key="run_experiment"):
    st.session_state["experiment_done"] = exp_key
if st.session_state.get("experiment_done") == exp_key:
    with st.spinner("Rechne die Ziehungen …"):
        rows = _experiment(exp_key)
    st.plotly_chart(build_violation(rows, settings.eps), width="stretch", key="violation_chart")
    st.caption("Je Szenarienzahl: Median und 95. Perzentil der wahren Verletzungswahrscheinlichkeit über die Ziehungen, gegen ε.")
    st.plotly_chart(build_cost(rows), width="stretch", key="cost_chart")
    st.caption("Mittlere Kosten je Szenarienzahl; gestrichelt: dieselben Lösungen, bis V genau ε erreicht (nur dort gezeigt, wo die meisten Ziehungen ε halten).")
    table = [
        {"N": r["n"], "Quelle": r["label"], "Anteil Ziehungen mit V > ε": f"{100 * r['share_over']:.0f} %",
         "V Median": f"{100 * r['v_median']:.1f} %".replace(".", ","), "V 95. Perz.": f"{100 * r['v_p95']:.1f} %".replace(".", ","),
         "Kosten (Mittel)": round(r["cost"]), "Stützszenarien (Mittel)": round(r["support"], 1)}
        for r in rows
    ]
    st.dataframe(table, hide_index=True, width="stretch")
    exact = next(r for r in rows if r["n"] == bnd.binomial)
    smallest = rows[0]
    st.info(
        f"Bei der exakten Schranke (N = {exact['n']}) verletzen {_de(100 * exact['share_over'], 0)} % der Ziehungen ε; im Median liegt die wahre Verletzung bei "
        f"{_de(100 * exact['v_median'], 1)} % statt {_pct(settings.eps, 0)}. Bei N = {smallest['n']} verletzen {_de(100 * smallest['share_over'], 0)} % der Ziehungen. "
        f"Die Schranke ist mit {_de(exact['cost'] / smallest['cost'], 1)}-fachen Kosten gegenüber N = {smallest['n']} nicht umsonst."
    )
else:
    st.info("Das Experiment läuft auf Knopfdruck, weil es mehrere hundert Optimierungen rechnet.")

st.markdown("---")

# --- Grenzen ------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Das Problem ist konvex** | Die Garantie gilt nur für konvexe Probleme (hier: die Fehlmenge ist konvex in der Kapazität). Mit ganzzahligen Entscheidungen oder nichtkonvexen Nebenbedingungen gilt die Schranke nicht. | – |
| **Die Ziehungen sind unabhängig aus der wahren Verteilung** | Bei verschobener Verteilung oder abhängigen Szenarien (Nachfrage-Trend) gilt die Garantie nicht. | [Stichproben-Demo (SAA)](https://github.com/sebastian-hanisch/saa-demo): was eine Stichprobe über die Verteilung sagt |
| **Die Lösung ist eindeutig** | Bei mehreren Optima kann die Lösung zufällig gewählt sein; die Schranke gilt mit Zusatzannahmen weiter, die hier nicht geprüft werden. | – |
| **ε und β sind gesetzt** | Sie sind Vorgaben des Planers. Strengere Werte kosten viele Szenarien und Kapazität. | – |
| **Die Garantie ist eine Obergrenze** | Die Schranke ist für den schlimmsten konvexen Fall scharf; in diesem Beispiel liegt die wahre Verletzung weit unter ε (Überschutz), das Verfahren verschenkt Kosten. | [robuste Demo](https://github.com/sebastian-hanisch/robust-opt-demo): Garantie in einer Menge statt über Wahrscheinlichkeiten |
| **Ohne Umlagerung** | Mit Umlagerung hinge die Nebenbedingung nur an der Summe der Kapazitäten (d = 1): die Schranke wäre viel kleiner, das Problem aber eine Quantilregel wie in der Prognose-Linie. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Chance-Problem.** Gesucht ist die billigste Kapazität $x\in\mathbb R^d_{\ge 0}$ mit

$$\min_x\; c^\top x\qquad\text{u. d. N.}\qquad \mathbb P\big(g(x,D)\le b\big)\ge 1-\varepsilon,\qquad g(x,D)=\sum_k \big(D_k-x_k-u_k\big)^+$$

Die Verteilung von $D$ ist unbekannt.

**Szenario-Ansatz.** Man zieht $N$ unabhängige Szenarien $D^{(1)},\dots,D^{(N)}$ und löst das LP

$$\min_x\; c^\top x\qquad\text{u. d. N.}\qquad g(x,D^{(s)})\le b\quad s=1,\dots,N$$

(mit Hilfsvariablen $w_{sk}\ge D^{(s)}_k-x_k-u_k$, $w\ge 0$, $\sum_k w_{sk}\le b$).

**Garantie.** Die wahre Verletzungswahrscheinlichkeit $V(x_N)=\mathbb P(g(x_N,D)>b)$ ist zufällig, und für konvexe Probleme mit $d$ Entscheidungsvariablen gilt (Campi und Garatti 2008, Satz 2.4)

$$\mathbb P\big(V(x_N)>\varepsilon\big)\;\le\;\sum_{i=0}^{d-1}\binom{N}{i}\varepsilon^i(1-\varepsilon)^{N-i}\;=:\;\beta(N).$$

Gesucht ist das kleinste $N$ mit $\beta(N)\le\beta$. Gröbere hinreichende Schranken sind $N\ge\tfrac{2}{\varepsilon}\big(\ln\tfrac1\beta+d\big)$ und
(Calafiore und Campi 2006) $N\ge\tfrac2\varepsilon\ln\tfrac1\beta+2d+\tfrac{2d}{\varepsilon}\ln\tfrac2\varepsilon$.

**Rücknahme.** „Bis ε zurückgenommen“ heißt: Mit $t\ge 0$ ist $x(t)=\max(x_N-t,0)$; $V(x(t))$ steigt mit $t$, und $t^\ast$ ist das größte $t$ mit $V(x(t))\le\varepsilon$ (Bisektion auf 20 000
Referenzszenarien). Die Kostendifferenz $c^\top(x_N-x(t^\ast))$ ist der Preis des Überschutzes.

**Literatur.** Calafiore & Campi, *The Scenario Approach to Robust Control Design*, IEEE TAC 51(5), 2006, S. 742–753; Campi & Garatti, *The Exact Feasibility of Randomized Solutions of Uncertain
Convex Programs*, SIAM J. Optim. 19(3), 2008, S. 1211–1230. Beide Formeln wurden aus dem Volltext nachgerechnet; die Beispielzahl einer Tabelle des Drucks weicht um 50 von der Binomialform ab
(11 749 statt 11 799 für ε = 0,0025, d = 10, β = 10⁻⁵), vermutlich ein Druckfehler.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
