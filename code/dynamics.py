"""
dynamics.py
===========
Dynamic welfare analysis implementing Proposition 4 (Institutional Delay)
of the manuscript.

Tracks the time path of:
- pi_theta(t): training-data inclusion prevalence (logistic growth)
- q_0(t): coincidental similarity rate (linear drift)
- e^SO(t): time-varying social optimum
- e^*_t: institutional safe-harbor threshold under static or dynamic (BAT) rules

Computes discounted cumulative welfare loss from institutional delay.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

from model import (Params, social_optimum_effort, welfare,
                   expected_infringement)


@dataclass
class DynamicParams:
    """Time-evolution parameters for Proposition 4."""

    T: int = 40                  # Horizon length (quarters)
    r: float = 0.02              # Quarterly social discount rate
    pi_theta_0: float = 0.20     # Initial training-data inclusion prevalence
    pi_theta_inf: float = 0.85   # Long-run prevalence (logistic asymptote)
    g_pi: float = 0.10           # Logistic growth rate per quarter
    q0_0: float = 0.05           # Initial coincidence rate
    q0_drift: float = 0.0025     # Drift per quarter (stylistic convergence)


def trajectory_pi_theta(d: DynamicParams) -> np.ndarray:
    """Logistic growth path for pi_theta(t)."""
    t = np.arange(d.T)
    A = (d.pi_theta_inf - d.pi_theta_0) / d.pi_theta_0
    return d.pi_theta_inf / (1.0 + A * np.exp(-d.g_pi * t))


def trajectory_q0(d: DynamicParams) -> np.ndarray:
    """Linear drift path for q_0(t), capped at 0.5."""
    t = np.arange(d.T)
    return np.minimum(0.5, d.q0_0 + d.q0_drift * t)


def time_varying_e_so(p: Params, d: DynamicParams) -> Tuple[np.ndarray, np.ndarray]:
    """Compute e^SO_t and W(e^SO_t) at each t."""
    pi_path = trajectory_pi_theta(d)
    q0_path = trajectory_q0(d)
    e_so_path = np.zeros(d.T)
    W_so_path = np.zeros(d.T)
    for t in range(d.T):
        p_t = Params(**{**p.__dict__, 'pi_theta': float(pi_path[t]),
                        'q0': float(q0_path[t])})
        e_so, W_so = social_optimum_effort(p_t)
        e_so_path[t] = e_so
        W_so_path[t] = W_so
    return e_so_path, W_so_path


def static_rule_path(p: Params, d: DynamicParams) -> np.ndarray:
    """Welfare under static safe-harbor threshold e* across time."""
    pi_path = trajectory_pi_theta(d)
    q0_path = trajectory_q0(d)
    W_path = np.zeros(d.T)
    for t in range(d.T):
        p_t = Params(**{**p.__dict__, 'pi_theta': float(pi_path[t]),
                        'q0': float(q0_path[t])})
        W_path[t] = float(welfare(p.e_star, p_t))
    return W_path


def bat_rule_path(p: Params, d: DynamicParams,
                  benchmarking_lag: int = 1) -> np.ndarray:
    """Welfare under BAT (Pillar II) with quarterly benchmarking lag.

    benchmarking_lag = 1 means e^*_t = e^SO_{t-1} (1-period lag).
    """
    pi_path = trajectory_pi_theta(d)
    q0_path = trajectory_q0(d)
    e_so_path, _ = time_varying_e_so(p, d)
    W_path = np.zeros(d.T)
    for t in range(d.T):
        e_used = e_so_path[max(0, t - benchmarking_lag)]
        p_t = Params(**{**p.__dict__, 'pi_theta': float(pi_path[t]),
                        'q0': float(q0_path[t])})
        W_path[t] = float(welfare(e_used, p_t))
    return W_path


def cumulative_loss(W_so: np.ndarray, W_actual: np.ndarray,
                    d: DynamicParams) -> Tuple[np.ndarray, float]:
    """Discounted cumulative welfare loss.

    Returns (per-period discounted loss, total).
    """
    t = np.arange(d.T)
    discount = np.exp(-d.r * t)
    per_period = discount * (W_so - W_actual)
    return per_period, float(per_period.sum())


def proposition4_check(p: Params, d: DynamicParams,
                       benchmarking_lag: int = 1) -> dict:
    """Verify Proposition 4: quadratic welfare loss bound.

    The bound is: Delta W >= (1/2) |W''(e^SO)| * Integral exp(-rt) (e^SO_t - e*)^2 dt
    """
    e_so_path, W_so_path = time_varying_e_so(p, d)

    # Static rule
    W_static = static_rule_path(p, d)
    _, total_loss_static = cumulative_loss(W_so_path, W_static, d)

    # BAT rule
    W_bat = bat_rule_path(p, d, benchmarking_lag)
    _, total_loss_bat = cumulative_loss(W_so_path, W_bat, d)

    # Quadratic bound: numerical estimate of W''(e^SO) at t=0
    eps = 1e-3
    pi_0 = trajectory_pi_theta(d)[0]
    q0_0 = trajectory_q0(d)[0]
    p_0 = Params(**{**p.__dict__, 'pi_theta': float(pi_0), 'q0': float(q0_0)})
    e_so_0 = e_so_path[0]
    W_plus = float(welfare(e_so_0 + eps, p_0))
    W_zero = float(welfare(e_so_0, p_0))
    W_minus = float(welfare(e_so_0 - eps, p_0))
    W_pp = (W_plus - 2 * W_zero + W_minus) / (eps ** 2)

    # Quadratic bound
    t = np.arange(d.T)
    discount = np.exp(-d.r * t)
    gap_sq = (e_so_path - p.e_star) ** 2
    quadratic_bound = 0.5 * abs(W_pp) * float((discount * gap_sq).sum())

    return {
        'e_so_path': e_so_path,
        'W_so_path': W_so_path,
        'W_static': W_static,
        'W_bat': W_bat,
        'total_loss_static': total_loss_static,
        'total_loss_bat': total_loss_bat,
        'W_double_prime_at_e_so': W_pp,
        'quadratic_bound': quadratic_bound,
        'bound_holds': total_loss_static >= quadratic_bound - 1e-6,
    }
