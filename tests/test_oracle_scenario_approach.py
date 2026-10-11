"""Orakel-Tests (DEMO-PLAYBOOK §12): anderer Rechenweg als der Kern.

1. Dasselbe Szenario-LP als eigenes Modell in OR-Tools (GLOP, Schleifen statt Blockmatrizen).
2. d = 1 (ein Standort): V(x_N) ist Beta(1, N)-verteilt, P(V > eps) = (1 - eps)^N; die Binomialschranke ist dort EXAKT gleich dieser Zahl.
3. d = 1: der Szenario-Plan ist das Maximum der Stichprobe minus Zukaufgrenze minus Schwelle (geschlossene Form statt LP)."""

import dataclasses

import numpy as np
import pytest

import sap_core as K
import sap_evaluation as ev
import sap_scenario as S
from sap_scenario import Instance

pywraplp = pytest.importorskip("ortools.linear_solver.pywraplp")


def _one_location(mean=100.0, sigma=0.35, limit=50.0) -> Instance:
    return Instance(
        mu=(mean,), cap_cost=1.0, spot=(1.9,), unmet=3.0, spot_limit=(limit,), transfer_cost=((0.0,),),
        transfer=False, budget=1e9, sigma=sigma, rho=0.0,
    )


def _glop_value(inst, demand, b) -> float:
    n, j_count = demand.shape
    solver = pywraplp.Solver.CreateSolver("GLOP")
    inf = solver.infinity()
    x = [solver.NumVar(0, inf, f"x{j}") for j in range(j_count)]
    for s in range(n):
        w = [solver.NumVar(0, inf, f"w{s}_{k}") for k in range(j_count)]
        for k in range(j_count):
            solver.Add(w[k] >= float(demand[s, k]) - x[k] - inst.spot_limit[k])
        solver.Add(sum(w) <= b)
    obj = solver.Objective()
    for j in range(j_count):
        obj.SetCoefficient(x[j], inst.cap_cost)
    obj.SetMinimization()
    assert solver.Solve() == pywraplp.Solver.OPTIMAL
    return obj.Value()


@pytest.mark.parametrize("b", [0.0, 30.0])
def test_scenario_lp_matches_independent_glop_model(b):
    inst = dataclasses.replace(
        S.make_instance(61, sigma=0.4, rho=0.4, budget_ratio=10.0, spot_mult=1.6, transfer=False),
        mu=(80.0, 120.0, 100.0), spot_limit=(40.0, 60.0, 50.0), transfer_cost=((0.0,) * 3,) * 3,
    )
    demand, _ = S.demand_scenarios(inst, 7, count=40)
    assert K.solve_scenario_lp(inst, demand, b)[1] == pytest.approx(_glop_value(inst, demand, b), rel=1e-7)


def test_one_location_plan_is_the_sample_maximum_minus_limit_and_threshold():
    inst = _one_location()
    for seed in range(5):
        demand, _ = S.demand_scenarios(inst, seed, count=50)
        for b in (0.0, 20.0):
            x, _ = K.solve_scenario_lp(inst, demand, b)
            assert x[0] == pytest.approx(max(demand[:, 0].max() - inst.spot_limit[0] - b, 0.0), rel=1e-9)


def test_one_location_violation_follows_the_beta_distribution_exactly():
    inst = _one_location()
    ref, _ = S.demand_scenarios(inst, 900_001, count=40_000)
    n, eps, b = 30, 0.10, 0.0
    v = []
    for k in range(300):
        demand, _ = S.demand_scenarios(inst, 1000 + k, count=n)
        x, _ = K.solve_scenario_lp(inst, demand, b)
        v.append(K.violation(inst, x, ref, b))
    v = np.array(v)
    # V ~ Beta(1, N): E[V] = 1 / (N + 1), P(V > eps) = (1 - eps)^N
    se_mean = v.std(ddof=1) / np.sqrt(len(v))
    assert abs(v.mean() - 1.0 / (n + 1)) <= 3.5 * se_mean
    p = (1.0 - eps) ** n
    assert abs(np.mean(v > eps) - p) <= 3.5 * np.sqrt(p * (1 - p) / len(v))
    # und die Binomialschranke ist für d = 1 genau diese Zahl
    assert K.beta_bound(n, eps, 1) == pytest.approx(p, rel=1e-12)
