"""Plotly-Figuren: Schranken, Verletzungswahrscheinlichkeit über N, Kosten über N, Plan je Standort. Alle Achsen fest (fixedrange)."""

import plotly.graph_objects as go

import sap_constants as C


def _fixed(fig, height=340):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.24))
    return fig


def build_bounds(bnd, n_selected=None) -> go.Figure:
    items = [
        ("Exakte Schranke (Binomialform)", bnd.binomial, C.COLOR_BINOMIAL),
        ("Einfache Formel (2/ε)(ln 1/β + d)", bnd.simple, C.COLOR_SIMPLE),
        ("Calafiore/Campi 2006", bnd.calafiore_campi, C.COLOR_CC),
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[i[0] for i in items], x=[i[1] for i in items], orientation="h", marker_color=[i[2] for i in items],
        text=[str(i[1]) for i in items], textposition="outside", showlegend=False))
    if n_selected is not None:
        fig.add_vline(x=n_selected, line_dash="dot", line_color="rgba(60,60,60,0.9)", annotation_text=f"gewählt: {n_selected}", annotation_position="top")
    fig.update_xaxes(title="Szenarienzahl N für die Garantie", range=[0, max(i[1] for i in items) * 1.15])
    fig.update_yaxes(autorange="reversed")
    return _fixed(fig, 260)


def build_violation(rows, eps) -> go.Figure:
    """Wahre Verletzungswahrscheinlichkeit je Szenarienzahl: Median und 95. Perzentil über die Ziehungen, gegen ε."""
    n = [r["n"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=n, y=[r["v_median"] for r in rows], mode="lines+markers", name="Median der wahren Verletzung",
                             line=dict(color=C.COLOR_BINOMIAL)))
    fig.add_trace(go.Scatter(x=n, y=[r["v_p95"] for r in rows], mode="lines+markers", name="95. Perzentil",
                             line=dict(color=C.COLOR_SIMPLE, dash="dash")))
    fig.add_hline(y=eps, line_dash="dot", line_color="rgba(60,60,60,0.9)", annotation_text=f"ε = {eps:.0%}".replace(".", ","), annotation_position="top left")
    fig.update_xaxes(title="Szenarienzahl N", type="log", tickvals=n, ticktext=[str(v) for v in n])
    fig.update_yaxes(title="wahre Verletzungswahrscheinlichkeit", tickformat=".0%")
    return _fixed(fig, 340)


def build_cost(rows) -> go.Figure:
    """Mittlere Kosten des Szenario-Ansatzes je N und die Kosten derselben Lösung, bis zur Grenze ε zurückgenommen."""
    n = [r["n"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=n, y=[r["cost"] for r in rows], mode="lines+markers", name="Szenario-Ansatz", line=dict(color=C.COLOR_BINOMIAL)))
    back = [(r["n"], r["cost_back"]) for r in rows if r["cost_back"] == r["cost_back"] and r["share_over"] < 0.5]
    fig.add_trace(go.Scatter(x=[p[0] for p in back], y=[p[1] for p in back], mode="lines+markers",
                             name="bis zur Grenze ε zurückgenommen", line=dict(color=C.COLOR_GRID, dash="dash")))
    fig.update_xaxes(title="Szenarienzahl N", type="log", tickvals=n, ticktext=[str(v) for v in n])
    fig.update_yaxes(title="Kosten der Kapazität")
    return _fixed(fig, 340)


def build_plan(mu, spot_limit, x) -> go.Figure:
    names = [f"Standort {i + 1}" for i in range(len(mu))]
    need = [m - u for m, u in zip(mu, spot_limit)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=need, name="mittlere Nachfrage minus Zukaufgrenze", marker_color=C.COLOR_GRID))
    fig.add_trace(go.Bar(x=names, y=list(x), name="Plan des Szenario-Ansatzes", marker_color=C.COLOR_BINOMIAL))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Kapazität")
    return _fixed(fig, 320)
