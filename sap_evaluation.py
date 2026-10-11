"""Kennzahlen: eine Ziehung des Szenario-Ansatzes gegen die wahre Verteilung, das Experiment über Szenarienzahlen, die drei Schranken.

Die „wahre“ Verteilung zum Prüfen sind 20 000 frische lognormale Szenarien (Seed REF_SEED), die der Szenario-Ansatz nie sieht."""

from dataclasses import dataclass

import numpy as np

import sap_constants as C
import sap_core as K
from sap_scenario import Instance, demand_scenarios, make_instance


@dataclass(frozen=True)
class Settings:
    eps: float = C.DEFAULT_EPS
    beta: float = C.DEFAULT_BETA
    n: int = C.DEFAULT_N
    b: int = C.DEFAULT_B
    sigma: float = C.DEFAULT_SIGMA
    seed: int = C.DEFAULT_SEED
    draw: int = C.DEFAULT_DRAW


@dataclass(frozen=True)
class Draw:
    n: int
    x: tuple[float, ...]
    cost: float              # c . x
    violation: float         # wahre Verletzungswahrscheinlichkeit V(x_N) auf der Referenz
    cost_pulled_back: float  # Kosten derselben Lösung, bis V genau eps erreicht (nur wenn V <= eps)
    support: int             # Zahl der Stützszenarien: Szenarien mit bindender Nebenbedingung


@dataclass(frozen=True)
class Bounds:
    d: int
    simple: int
    calafiore_campi: int
    binomial: int


def build_instance(settings: Settings) -> Instance:
    return make_instance(
        settings.seed, sigma=settings.sigma, rho=C.RHO, budget_ratio=C.BUDGET_FREE,
        spot_mult=C.SPOT_MULT, transfer=False,
    )


def reference_demand(inst: Instance) -> np.ndarray:
    demand, _ = demand_scenarios(inst, C.REF_SEED, count=C.REF_SCENARIOS)
    return demand


def draw_seed(base: int, k: int, n: int) -> int:
    return 1_000_003 * int(base) + 7919 * int(k) + 17 * int(n) + 11


def bounds_for(eps: float, beta: float, d: int = C.J) -> Bounds:
    return Bounds(d, K.n_simple(eps, beta, d), K.n_calafiore_campi(eps, beta, d), K.n_binomial(eps, beta, d))


def one_draw(inst: Instance, ref: np.ndarray, n: int, b: float, eps: float, seed: int, tol: float = 1e-7) -> Draw:
    sample, _ = demand_scenarios(inst, seed, count=n)
    x, cost = K.solve_scenario_lp(inst, sample, b)
    v = K.violation(inst, x, ref, b)
    support = int(np.sum(np.isclose(K.unmet_total(inst, x, sample), b, atol=tol) | (K.unmet_total(inst, x, sample) > b - tol)))
    if v <= eps:
        xb, _ = K.pull_back(inst, x, ref, b, eps)
        cost_back = float(inst.cap_cost * xb.sum())
    else:
        cost_back = float("nan")
    return Draw(n, tuple(float(t) for t in x), float(cost), v, cost_back, support)


def experiment(settings: Settings, progress=None) -> list[dict]:
    """Je Szenarienzahl REPEATS unabhängige Ziehungen: Verteilung der wahren Verletzung und Kosten."""
    inst = build_instance(settings)
    ref = reference_demand(inst)
    bnd = bounds_for(settings.eps, settings.beta)
    sizes = sorted(set(C.SMALL_N) | {bnd.binomial, bnd.simple, bnd.calafiore_campi})
    rows, done, total = [], 0, len(sizes) * C.REPEATS
    for n in sizes:
        v, cost, back, support = [], [], [], []
        for k in range(C.REPEATS):
            d = one_draw(inst, ref, n, settings.b, settings.eps, draw_seed(settings.draw, k, n))
            v.append(d.violation)
            cost.append(d.cost)
            back.append(d.cost_pulled_back)
            support.append(d.support)
            done += 1
            if progress is not None:
                progress(done / total)
        v = np.array(v)
        rows.append({
            "n": n, "label": _label(n, bnd),
            "v_median": float(np.median(v)), "v_p95": float(np.percentile(v, 95)), "v_mean": float(v.mean()),
            "share_over": float(np.mean(v > settings.eps)),
            "cost": float(np.mean(cost)), "cost_back": float(np.nanmean(back)) if np.isfinite(back).any() else float("nan"),
            "support": float(np.mean(support)),
        })
    return rows


def _label(n: int, bnd: Bounds) -> str:
    names = []
    if n == bnd.binomial:
        names.append("exakte Schranke")
    if n == bnd.simple:
        names.append("einfache Formel")
    if n == bnd.calafiore_campi:
        names.append("Calafiore/Campi 2006")
    return ", ".join(names) if names else "kleine Zahl"
