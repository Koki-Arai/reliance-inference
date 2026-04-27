"""
test_smoke.py
=============
Smoke tests for the simulation package.

These tests verify that all main propositions and lemmas of the manuscript
hold numerically at the default calibrated parameters.

Run from repository root:
    python tests/test_smoke.py

Or from anywhere with pytest:
    pytest tests/test_smoke.py -v
"""

from __future__ import annotations

import os
import sys

# Add code directory to path so modules can be imported regardless of cwd
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CODE_DIR = os.path.join(_REPO_ROOT, "code")
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

import numpy as np

from model import (Params, q2, Lambda, posterior_case_iia, normative_fiction,
                   cost, welfare, social_optimum_effort, four_pillar_table)
from dynamics import (DynamicParams, trajectory_pi_theta,
                      time_varying_e_so, proposition4_check)
from sensitivity import (one_at_a_time, monte_carlo, correlation_sensitivity,
                         summarize_monte_carlo)


def test_assumption_1():
    p = Params()
    assert p.q1 > p.q2_0 > p.q0 > 0, "Assumption 1 violated"
    print("PASS: Assumption 1 holds at default parameters")


def test_q2_monotone():
    p = Params()
    e_grid = np.linspace(0, p.e_bar, 11)
    q2_vals = q2(e_grid, p)
    assert np.all(np.diff(q2_vals) <= 0), "q2 should be decreasing"
    assert abs(q2_vals[0] - p.q2_0) < 1e-9
    assert abs(q2_vals[-1] - p.q0) < 1e-9
    print(f"PASS: q2(e) monotone decreasing; q2(0)={q2_vals[0]:.3f}, "
          f"q2(e_bar)={q2_vals[-1]:.3f}")


def test_lambda_monotone():
    p = Params()
    e_grid = np.linspace(0, p.e_bar, 11)
    L = Lambda(e_grid, p)
    assert np.all(np.diff(L) <= 0), "Lambda(e) should be decreasing (Lemma 1)"
    print(f"PASS: Lambda(e) monotone decreasing; Lambda(0)={L[0]:.3f}, "
          f"Lambda(e_bar)={L[-1]:.3f}")


def test_posterior_strictly_less_than_one():
    p = Params()
    post = posterior_case_iia(0.0, p)
    assert 0 < post < 1, "Posterior should be strictly interior"
    fic = normative_fiction(0.0, p)
    assert fic > 0, "Normative fiction should be strictly positive"
    print(f"PASS: Proposition 1 - posterior={post:.4f}, fiction={fic:.4f}")


def test_correlation_monotonicity():
    p = Params()
    df = correlation_sensitivity(rho_grid=np.linspace(-0.2, 0.5, 8),
                                 base_params=p)
    posts = df['posterior'].values
    assert np.all(np.diff(posts) <= 1e-9), \
        "Posterior should be (weakly) decreasing in rho (Proposition B.1)"
    print(f"PASS: Proposition B.1 - posterior decreasing in rho_theta_a")


def test_social_optimum_interior():
    p = Params()
    e_so, W_so = social_optimum_effort(p)
    assert 0 < e_so < p.e_bar, f"e^SO should be interior; got {e_so}"
    print(f"PASS: e^SO = {e_so:.4f} (interior); W(e^SO) = {W_so:.4f}")


def test_four_pillar_ranking():
    p = Params()
    table = four_pillar_table(p)
    welfares = [
        table['status_quo']['welfare'],
        table['pillar_I']['welfare'],
        table['pillar_I_II']['welfare'],
        table['pillar_I_II_III']['welfare'],
        table['all_four_pillars']['welfare'],
    ]
    assert all(welfares[i] <= welfares[i+1] + 1e-6
               for i in range(len(welfares)-1)), \
        f"Welfare should be (weakly) monotonically non-decreasing across pillars; got {welfares}"
    gain_pct = 100 * (welfares[-1] - welfares[0]) / welfares[0]
    print(f"PASS: Welfare monotone across pillars; total gain = {gain_pct:.2f}%")
    for name, W in zip(
        ['status_quo', 'I', 'I+II', 'I+II+III', 'all'],
        welfares
    ):
        print(f"      {name:<14s}: W = {W:.2f}")


def test_proposition4():
    p = Params()
    d = DynamicParams()
    res = proposition4_check(p, d)
    assert res['total_loss_static'] >= 0, \
        "Static loss should be non-negative"
    assert res['total_loss_bat'] >= 0, \
        "BAT loss should be non-negative"
    assert res['total_loss_bat'] <= res['total_loss_static'] + 1e-6, \
        "BAT should weakly dominate static"
    assert res['bound_holds'], "Quadratic lower bound should hold"
    print(f"PASS: Proposition 4 numerically verified")
    print(f"      Static loss   = {res['total_loss_static']:.3f}")
    print(f"      BAT loss      = {res['total_loss_bat']:.3f}")
    print(f"      Quad bound    = {res['quadratic_bound']:.3f}")


def test_monte_carlo_robustness():
    p = Params()
    df = monte_carlo(n_draws=200, seed=1, base_params=p)
    summary = summarize_monte_carlo(df)
    assert summary['n'] >= 100, "Most draws should be valid"
    assert summary['share_positive'] >= 0.95, \
        "At least 95% of draws should yield positive gain"
    print(f"PASS: Monte Carlo robust (n={summary['n']})")
    print(f"      mean gain     = {summary['mean_gain_pct']:.2f}%")
    print(f"      median gain   = {summary['median_gain_pct']:.2f}%")
    print(f"      [5%, 95%]     = [{summary['pct_05']:.2f}%, "
          f"{summary['pct_95']:.2f}%]")
    print(f"      share positive= {summary['share_positive']:.4f}")


def test_dynamics_paths():
    p = Params()
    d = DynamicParams()
    pi = trajectory_pi_theta(d)
    assert pi[0] > 0 and pi[-1] < 1
    assert np.all(np.diff(pi) >= -1e-9), "pi_theta should be non-decreasing"
    e_so, W_so = time_varying_e_so(p, d)
    assert e_so.shape == (d.T,)
    print(f"PASS: dynamic paths well-formed")
    print(f"      pi_theta(0)   = {pi[0]:.3f}")
    print(f"      pi_theta(T-1) = {pi[-1]:.3f}")
    print(f"      e^SO(0)       = {e_so[0]:.3f}")
    print(f"      e^SO(T-1)     = {e_so[-1]:.3f}")


if __name__ == '__main__':
    print("=" * 60)
    print("SMOKE TESTS")
    print("=" * 60)
    test_assumption_1()
    test_q2_monotone()
    test_lambda_monotone()
    test_posterior_strictly_less_than_one()
    test_correlation_monotonicity()
    test_social_optimum_interior()
    test_four_pillar_ranking()
    test_dynamics_paths()
    test_proposition4()
    test_monte_carlo_robustness()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
