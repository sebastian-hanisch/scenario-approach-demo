"""Szenario-Ansatz (Calafiore/Campi) für eine Chance-Nebenbedingung der Kapazitätsplanung, ohne Umlagerung.

Aufgabe:  min c.x   u. d. N.   P( sum_k (D_k - x_k - u_k)^+ > b ) <= eps,   x >= 0.
          u_k = Zukaufgrenze von Standort k; die Fehlmenge ist die Nachfrage jenseits von Kapazität plus Zukauf.
Die Menge der zulässigen x je Szenario ist konvex (die Fehlmenge ist konvex in x). Der Szenario-Ansatz erzwingt die Nebenbedingung für N gezogene
Szenarien; das Ergebnis x_N hat eine zufällige Verletzungswahrscheinlichkeit V(x_N), und für konvexe Probleme mit d Entscheidungsvariablen gilt
P( V(x_N) > eps ) <= sum_{i<d} C(N, i) eps^i (1 - eps)^(N-i)   (Campi/Garatti 2008, Satz 2.4).

Einheiten (je eine Regel, DEMO-PLAYBOOK §1b):
  unmet_total         Fehlmenge insgesamt je Szenario bei festem Plan
  violation           Verletzungswahrscheinlichkeit V(x) auf einer Szenarienmenge
  solve_scenario_lp   der Szenario-Ansatz: ein LP über N Szenarien
  pull_back           dieselbe Lösung um gleich viel je Standort zurückgenommen, bis V genau epsilon erreicht
  n_binomial / n_simple / n_calafiore_campi   Stichprobenzahlen aus den drei Formeln"""

import math

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, csr_matrix, hstack, vstack
from scipy.stats import binom

from sap_scenario import Instance


def unmet_total(inst: Instance, x, demand: np.ndarray) -> np.ndarray:
    """Fehlmenge insgesamt je Szenario: Summe_k max(0, D_k - x_k - u_k)."""
    gap = demand - np.asarray(x)[None, :] - np.asarray(inst.spot_limit)[None, :]
    return np.maximum(gap, 0.0).sum(axis=1)


def violation(inst: Instance, x, demand: np.ndarray, b: float, tol: float = 1e-9) -> float:
    """Anteil der Szenarien mit Fehlmenge über b."""
    return float(np.mean(unmet_total(inst, x, demand) > b + tol))


def solve_scenario_lp(inst: Instance, demand: np.ndarray, b: float):
    """min c.x  u. d. N.  fuer jedes Szenario s: Summe_k w_sk <= b,  w_sk >= D_sk - x_k - u_k,  w >= 0.  Rückgabe (x, Zielwert)."""
    n, j = demand.shape
    u = np.asarray(inst.spot_limit)
    # Variablen: x (j), w (n*j). Zeilen: -x_k - w_sk <= -(D_sk - u_k)  (n*j Zeilen);  sum_k w_sk <= b  (n Zeilen)
    rows = np.arange(n * j)
    cols_x = np.tile(np.arange(j), n)
    a1 = hstack([
        coo_matrix((-np.ones(n * j), (rows, cols_x)), shape=(n * j, j)),
        coo_matrix((-np.ones(n * j), (rows, rows)), shape=(n * j, n * j)),
    ]).tocsr()
    b1 = -(demand - u[None, :]).reshape(-1)
    a2 = hstack([
        csr_matrix((n, j)),
        coo_matrix((np.ones(n * j), (np.repeat(np.arange(n), j), np.arange(n * j))), shape=(n, n * j)),
    ]).tocsr()
    b2 = np.full(n, float(b))
    c = np.concatenate([np.full(j, inst.cap_cost), np.zeros(n * j)])
    res = linprog(c, A_ub=vstack([a1, a2]).tocsr(), b_ub=np.concatenate([b1, b2]), bounds=[(0, None)] * (j + n * j), method="highs")
    if res.status != 0:
        raise RuntimeError(f"Szenario-LP nicht lösbar: {res.message}")
    return res.x[:j], float(res.fun)


def pull_back(inst: Instance, x, demand: np.ndarray, b: float, eps: float, iterations: int = 40):
    """Größte gleichmäßige Rücknahme t >= 0 je Standort mit V(max(x - t, 0)) <= eps (Bisektion; V ist in t monoton).

    Rückgabe (x_zurück, t). Liegt V(x) schon über eps, ist t = 0."""
    x = np.asarray(x, dtype=float)
    if violation(inst, x, demand, b) > eps:
        return x.copy(), 0.0
    lo, hi = 0.0, float(x.max())
    if violation(inst, np.maximum(x - hi, 0.0), demand, b) <= eps:
        return np.maximum(x - hi, 0.0), hi
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        if violation(inst, np.maximum(x - mid, 0.0), demand, b) <= eps:
            lo = mid
        else:
            hi = mid
    return np.maximum(x - lo, 0.0), lo


def beta_bound(n: int, eps: float, d: int) -> float:
    """Obere Schranke für P(V > eps): Binomial-Verteilungsfunktion P(Bin(n, eps) <= d - 1) (Campi/Garatti 2008)."""
    return float(binom.cdf(d - 1, n, eps))


def n_binomial(eps: float, beta: float, d: int, n_max: int = 200_000) -> int:
    """Kleinstes N mit beta_bound <= beta (exakte Binomialform; die Schranke fällt in N)."""
    lo, hi = d, d
    while beta_bound(hi, eps, d) > beta:
        lo, hi = hi, hi * 2
        if hi > n_max:
            raise ValueError("n_max überschritten")
    while lo < hi:
        mid = (lo + hi) // 2
        if beta_bound(mid, eps, d) <= beta:
            hi = mid
        else:
            lo = mid + 1
    return lo


def n_simple(eps: float, beta: float, d: int) -> int:
    """Einfache Formel N >= (2 / eps) (ln(1 / beta) + d) (Calafiore/Campi, grobe Fassung)."""
    return int(math.ceil((2.0 / eps) * (math.log(1.0 / beta) + d)))


def n_calafiore_campi(eps: float, beta: float, d: int) -> int:
    """Calafiore/Campi 2006: N >= (2 / eps) ln(1 / beta) + 2 d + (2 d / eps) ln(2 / eps)."""
    return int(math.ceil((2.0 / eps) * math.log(1.0 / beta) + 2 * d + (2.0 * d / eps) * math.log(2.0 / eps)))
