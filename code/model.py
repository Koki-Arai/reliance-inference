"""
model.py
========
Core model for "Reliance Inference and Institutional Architecture under
Generative AI: A Law-and-Economics Analysis".

Implements:
- Bayesian posterior in Case (ii-a) of Proposition 1
- Likelihood ratio Lambda(e)
- Static welfare function W(e; params)
- Socially optimal effort e^SO via numerical optimization
- Four-pillar welfare decomposition

All notation follows the main text; cross-references in docstrings.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Dict, Tuple

import numpy as np
from scipy.optimize import brentq, minimize_scalar


# ------------------------------------------------------------------
# Parameter container
# ------------------------------------------------------------------

@dataclass
class Params:
    """Primitive parameters of the model.

    Defaults match the calibration in Section 3.8 of the manuscript.
    """

    # Probability primitives
    pi_theta: float = 0.4    # Pr(theta = 1): training-data inclusion prior
    pi_a: float = 0.1        # Pr(a = 1): user recognition prior
    q1: float = 0.9          # Pr(s>=s* | a=1, theta=1): intentional reproduction
    q2_0: float = 0.4        # Pr(s>=s* | a=0, theta=1, e=0): incidental at zero effort
    q0: float = 0.1          # Pr(s>=s* | theta=0): coincidental similarity

    # Cost and damages
    c_e_star: float = 20.0   # c(e*) at the safe-harbor threshold
    e_bar: float = 1.0       # Maximum effort (upper bound of effort space)
    e_star: float = 0.6      # Statutory safe-harbor threshold (static)

    # Liability and welfare
    rho_D: float = 0.8       # D's liability share (rho_U = 1 - rho_D)
    L: float = 125.0         # Damages L (so that rho_D * L = 100 = H below)
    H: float = 100.0         # Per-infringement social loss
    alpha_I: float = 10.0    # Type I error weight
    alpha_II: float = 10.0   # Type II error weight
    B0: float = 200.0        # Baseline AI deployment benefit (level term)
    B_slope: float = 50.0    # Marginal benefit of pi_theta on aggregate B

    # Adjudicative-error baseline probabilities (tuned for status quo)
    PrI_static: float = 0.50    # Type I error probability under static rule
    PrII_static: float = 0.35   # Type II error probability under static rule

    @property
    def rho_U(self) -> float:
        return 1.0 - self.rho_D

    def benefit(self, pi_theta: float | None = None) -> float:
        """B(pi_theta): aggregate AI deployment benefit, increasing in pi_theta."""
        x = self.pi_theta if pi_theta is None else pi_theta
        return self.B0 + self.B_slope * x


# ------------------------------------------------------------------
# Probability and posterior expressions
# ------------------------------------------------------------------

def q2(e: float | np.ndarray, p: Params) -> np.ndarray:
    """q_2(e): incidental-similarity probability under training-included case.

    Linear interpolation: q_2(0) = q2_0, q_2(e_bar) = q_0.
    Strictly decreasing, satisfying Assumption 1 of the main text.
    """
    e_arr = np.asarray(e, dtype=float)
    slope = (p.q0 - p.q2_0) / p.e_bar
    return p.q2_0 + slope * e_arr


def Lambda(e: float | np.ndarray, p: Params) -> np.ndarray:
    """Lambda(e): likelihood ratio from Section 2.2.

    Lambda(e) = [pi_a * q1 + (1 - pi_a) * q2(e)] / q0
    """
    num = p.pi_a * p.q1 + (1.0 - p.pi_a) * q2(e, p)
    return num / p.q0


def posterior_case_iia(e: float, p: Params, rho: float = 0.0) -> float:
    """Bayesian posterior Pr(theta = 1 | s >= s*, a = 0) in Case (ii-a).

    Generalized to allow correlation rho between theta and a (Appendix B).
    rho = 0 recovers the independence baseline.
    """
    # Conditional probabilities under correlation rho (Appendix B.1)
    sd = np.sqrt(p.pi_theta * (1 - p.pi_theta) * p.pi_a * (1 - p.pi_a))
    pi_11 = p.pi_theta * p.pi_a + rho * sd
    pi_10 = p.pi_theta - pi_11
    pi_01 = p.pi_a - pi_11
    pi_00 = 1 - pi_11 - pi_10 - pi_01

    # Numerical safety
    if min(pi_11, pi_10, pi_01, pi_00) < 0:
        raise ValueError(f"Joint distribution not valid for rho={rho}")

    num = pi_10 * q2(e, p)
    den = num + pi_00 * p.q0
    return float(num / den) if den > 0 else 0.0


def normative_fiction(e: float, p: Params, rho: float = 0.0) -> float:
    """Magnitude of upward normative fiction in Case (ii-a) of Proposition 1."""
    return 1.0 - posterior_case_iia(e, p, rho)


# ------------------------------------------------------------------
# Cost function
# ------------------------------------------------------------------

def cost(e: float | np.ndarray, p: Params) -> np.ndarray:
    """c(e): convex prevention cost. Quadratic form c(e) = a * e^2.

    Calibrated so that c(e_star) = c_e_star.
    """
    a = p.c_e_star / (p.e_star ** 2)
    e_arr = np.asarray(e, dtype=float)
    return a * (e_arr ** 2)


def cost_prime(e: float | np.ndarray, p: Params) -> np.ndarray:
    """c'(e)."""
    a = p.c_e_star / (p.e_star ** 2)
    e_arr = np.asarray(e, dtype=float)
    return 2.0 * a * e_arr


# ------------------------------------------------------------------
# Static welfare function (Section 2.6)
# ------------------------------------------------------------------

def expected_infringement(e: float | np.ndarray, p: Params) -> np.ndarray:
    """E[infringement loss] = pi_theta * [pi_a * q1 + (1-pi_a) * q2(e)] * H."""
    e_arr = np.asarray(e, dtype=float)
    sim_prob = p.pi_a * p.q1 + (1.0 - p.pi_a) * q2(e_arr, p)
    return p.pi_theta * sim_prob * p.H


def welfare(e: float | np.ndarray,
            p: Params,
            PrI: float | None = None,
            PrII: float | None = None,
            B_value: float | None = None,
            infringement_factor: float = 1.0) -> np.ndarray:
    """W(e) = -E[infringement] - c(e) - [alpha_I PrI + alpha_II PrII] + B.

    Optional overrides allow different regimes (pillars).

    infringement_factor: scaling of the expected infringement term to capture
        the effect of Pillar IV (ECL converts external infringement loss
        into a market-clearing royalty).
    """
    PrI = p.PrI_static if PrI is None else PrI
    PrII = p.PrII_static if PrII is None else PrII
    B_value = p.benefit() if B_value is None else B_value

    inf_loss = infringement_factor * expected_infringement(e, p)
    prev_cost = cost(e, p)
    err_loss = p.alpha_I * PrI + p.alpha_II * PrII

    return -inf_loss - prev_cost - err_loss + B_value


def social_optimum_effort(p: Params,
                          B_value: float | None = None,
                          PrI: float | None = None,
                          PrII: float | None = None,
                          infringement_factor: float = 1.0) -> Tuple[float, float]:
    """Solve for e^SO maximizing W(e) on [0, e_bar].

    Returns (e_SO, W(e_SO)).
    """
    def neg_W(e):
        return -float(welfare(e, p, PrI=PrI, PrII=PrII,
                              B_value=B_value,
                              infringement_factor=infringement_factor))

    res = minimize_scalar(neg_W, bounds=(0.0, p.e_bar), method='bounded',
                          options={'xatol': 1e-7})
    return float(res.x), -float(res.fun)


# ------------------------------------------------------------------
# Four-pillar welfare decomposition (Section 3.8)
# ------------------------------------------------------------------

def regime_welfare(regime: str, p: Params) -> Dict[str, float]:
    """Compute welfare decomposition for a given regime.

    Regimes: 'status_quo', 'pillar_I', 'pillar_I_II', 'pillar_I_II_III',
             'all_four_pillars'.

    Returns a dict with keys: e_used, infringement, prevention,
    adjudication, B, welfare.
    """
    # Effort employed under each regime
    if regime == 'status_quo':
        # Static rule: D bunches at e_star, but PrI and PrII are large
        e_used = p.e_star
        PrI = p.PrI_static
        PrII = p.PrII_static
        B_used = p.benefit()
        inf_factor = 1.0

    elif regime == 'pillar_I':
        # Disclosure unraveling reduces adjudicative errors substantially
        e_used = p.e_star
        PrI = 0.10          # 80% reduction via tier sorting
        PrII = 0.10          # 70% reduction
        B_used = p.benefit()
        inf_factor = 1.0

    elif regime == 'pillar_I_II':
        # BAT safe harbor: e tracks e^SO; effort costs rise but infringement falls
        e_used, _ = social_optimum_effort(p)
        PrI = 0.10
        PrII = 0.10
        B_used = p.benefit()
        inf_factor = 1.0

    elif regime == 'pillar_I_II_III':
        # Plus recognition-based liability: removes user-side deadweight,
        # avoids chilling effect on incumbent creators (B rises)
        e_used, _ = social_optimum_effort(p)
        PrI = 0.075
        PrII = 0.075
        B_used = p.benefit() * 1.05    # 5% chilling-effect avoidance
        inf_factor = 1.0

    elif regime == 'all_four_pillars':
        # Plus ECL: per-infringement loss internalized into market-clearing royalty
        e_used, _ = social_optimum_effort(p)
        PrI = 0.025
        PrII = 0.025
        B_used = p.benefit() * 1.075   # 7.5% benefit increase
        inf_factor = 0.30              # ECL absorbs 70% of external loss

    else:
        raise ValueError(f"Unknown regime: {regime}")

    inf = float(inf_factor * expected_infringement(e_used, p))
    prev = float(cost(e_used, p))
    adj = float(p.alpha_I * PrI + p.alpha_II * PrII)
    W = -inf - prev - adj + B_used

    return {
        "e_used": float(e_used),
        "infringement": inf,
        "prevention": prev,
        "adjudication": adj,
        "B": float(B_used),
        "welfare": float(W),
    }


def four_pillar_table(p: Params | None = None) -> Dict[str, Dict[str, float]]:
    """Reproduce the Section 3.8 calibration table."""
    p = Params() if p is None else p
    regimes = [
        'status_quo',
        'pillar_I',
        'pillar_I_II',
        'pillar_I_II_III',
        'all_four_pillars',
    ]
    return {r: regime_welfare(r, p) for r in regimes}
