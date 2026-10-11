"""Einheiten: Fehlmenge, Verletzung, Szenario-LP, Rücknahme und die drei Schranken an Handwerten."""

import math

import numpy as np
import pytest

import sap_constants as C
import sap_core as K
import sap_evaluation as ev


def test_unmet_total_hand_values(mini):
    d = np.array([[100.0, 60.0], [130.0, 60.0], [130.0, 100.0]])
    x = np.array([80.0, 30.0])
    # Zukaufgrenzen 50 und 30: Standort 1 deckt bis 130, Standort 2 bis 60
    assert list(K.unmet_total(mini, x, d)) == pytest.approx([0.0, 0.0, 40.0])


def test_violation_counts_strictly_above_the_threshold(mini):
    d = np.array([[130.0, 70.0], [130.0, 60.0], [100.0, 60.0], [140.0, 60.0]])
    x = np.array([80.0, 30.0])
    # Fehlmengen 10, 0, 0, 10
    assert K.violation(mini, x, d, b=10.0) == 0.0
    assert K.violation(mini, x, d, b=9.0) == 0.5


def test_scenario_lp_hand_values(mini):
    d = np.array([[100.0, 60.0], [130.0, 60.0]])
    x, cost = K.solve_scenario_lp(mini, d, b=0.0)
    assert x == pytest.approx([80.0, 30.0]) and cost == pytest.approx(110.0)
    # mit b = 10 darf insgesamt 10 Einheiten weniger vorgehalten werden
    _, cost10 = K.solve_scenario_lp(mini, d, b=10.0)
    assert cost10 == pytest.approx(100.0)


def test_scenario_lp_satisfies_every_scenario_constraint():
    inst = ev.build_instance(ev.Settings())
    demand, _ = ev.demand_scenarios(inst, 3, count=80)
    x, _ = K.solve_scenario_lp(inst, demand, b=30.0)
    assert (K.unmet_total(inst, x, demand) <= 30.0 + 1e-6).all()


def test_pull_back_stops_at_epsilon():
    inst = ev.build_instance(ev.Settings())
    ref = ev.reference_demand(inst)
    demand, _ = ev.demand_scenarios(inst, 5, count=400)
    x, _ = K.solve_scenario_lp(inst, demand, b=30.0)
    xb, t = K.pull_back(inst, x, ref, 30.0, 0.05)
    assert t > 0
    assert K.violation(inst, xb, ref, 30.0) <= 0.05
    assert K.violation(inst, np.maximum(xb - 0.5, 0.0), ref, 30.0) > 0.05 - 0.002   # etwas mehr Rücknahme überschreitet die Grenze


def test_pull_back_does_nothing_when_epsilon_is_already_violated():
    inst = ev.build_instance(ev.Settings())
    ref = ev.reference_demand(inst)
    x = np.asarray(inst.mu) * 0.2
    xb, t = K.pull_back(inst, x, ref, 0.0, 0.05)
    assert t == 0.0 and np.allclose(xb, x)


def test_the_three_bounds_at_the_default_setting():
    b = ev.bounds_for(0.05, 0.01)
    assert b.d == 6
    assert b.simple == math.ceil(40 * (math.log(100) + 6)) == 425
    assert b.calafiore_campi == 1082
    assert b.binomial == 259
    assert b.binomial < b.simple < b.calafiore_campi


def test_binomial_bound_is_the_smallest_n_meeting_beta():
    for eps, beta in ((0.05, 1e-2), (0.1, 1e-3), (0.02, 1e-5)):
        n = K.n_binomial(eps, beta, 6)
        assert K.beta_bound(n, eps, 6) <= beta
        assert K.beta_bound(n - 1, eps, 6) > beta


def test_beta_bound_is_the_binomial_cdf_by_direct_summation():
    n, eps, d = 40, 0.1, 4
    direct = sum(math.comb(n, i) * eps ** i * (1 - eps) ** (n - i) for i in range(d))
    assert K.beta_bound(n, eps, d) == pytest.approx(direct, rel=1e-12)


def test_reference_size_and_slider_grid_are_consistent():
    assert C.N_MIN <= C.DEFAULT_N <= C.N_MAX
    assert (C.DEFAULT_N - C.N_MIN) % C.N_STEP == 0
    assert (C.DEFAULT_B - C.B_MIN) % C.B_STEP == 0
    assert C.REF_SCENARIOS >= 20_000
