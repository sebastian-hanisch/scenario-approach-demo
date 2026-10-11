"""Jede Aussage aus README und App-Text wird hier nachgerechnet (Bänder statt exakter Werte: CI installiert die neuesten numpy/scipy)."""

import numpy as np
import pytest

import sap_constants as C
import sap_evaluation as ev


@pytest.fixture(scope="module")
def rows():
    return {r["n"]: r for r in ev.experiment(ev.Settings())}


def test_the_three_bounds_for_the_default_guarantee():
    b = ev.bounds_for(0.05, 0.01)
    assert (b.binomial, b.simple, b.calafiore_campi) == (259, 425, 1082)
    assert 1.5 <= b.simple / b.binomial <= 1.8
    assert 4.0 <= b.calafiore_campi / b.binomial <= 4.4


def test_the_guarantee_holds_at_the_exact_bound(rows):
    r = rows[259]
    assert r["share_over"] <= 0.04                  # beta = 1 %, 100 Ziehungen: mehr als vier wären sehr unwahrscheinlich
    assert 0.010 <= r["v_median"] <= 0.025          # meist deutlich unter eps = 5 %
    assert r["v_p95"] < 0.05


def test_far_too_few_scenarios_violate_the_guarantee_often(rows):
    assert rows[20]["share_over"] >= 0.85
    assert rows[60]["share_over"] >= 0.4
    assert rows[20]["v_median"] > rows[60]["v_median"] > rows[259]["v_median"] > rows[1082]["v_median"]


def test_the_cost_of_the_guarantee_grows_with_n(rows):
    costs = [rows[n]["cost"] for n in sorted(rows)]
    assert costs == sorted(costs)
    assert rows[1082]["cost"] >= 1.15 * rows[259]["cost"]


def test_most_of_the_cost_is_overprotection(rows):
    r = rows[259]
    over = r["cost"] / r["cost_back"] - 1.0
    assert 0.10 <= over <= 0.35                     # die Lösung ist 10 bis 35 % teurer, als sie bei genau eps sein müsste


def test_support_scenarios_do_not_exceed_the_number_of_decision_variables(rows):
    for r in rows.values():
        assert r["support"] <= C.J + 0.5
    assert rows[259]["support"] >= 3.5


def test_the_default_draw_is_a_typical_one():
    s = ev.Settings()
    inst = ev.build_instance(s)
    d = ev.one_draw(inst, ev.reference_demand(inst), s.n, float(s.b), s.eps, ev.draw_seed(s.draw, 0, s.n))
    assert d.violation <= s.eps
    assert 0.010 <= d.violation <= 0.025
    assert d.cost / d.cost_pulled_back > 1.1
