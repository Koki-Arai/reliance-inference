"""
sensitivity.py
==============
Sensitivity analysis and Monte Carlo robustness checks for the
welfare improvements derived in Section 3.8.

Implements:
- One-at-a-time sensitivity (each parameter varied over a grid)
- Monte Carlo: random sampling from prior distributions on parameters
- Correlated-types extension (Appendix B) for sensitivity to rho_theta_a
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

import numpy as np
import pandas as pd

from model import (Params, regime_welfare, posterior_case_iia,
                   normative_fiction)


# ------------------------------------------------------------------
# One-at-a-time sensitivity
# ------------------------------------------------------------------

def one_at_a_time(param_name: str,
                  values: np.ndarray,
                  base_params: Params | None = None) -> pd.DataFrame:
    """Vary one parameter, holding others at baseline; record welfare gain.

    Returns a DataFrame with columns:
    [param_value, W_status_quo, W_full_arch, gain_absolute, gain_pct]
    """
    base = Params() if base_params is None else base_params
    rows = []
    for v in values:
        p = replace(base, **{param_name: float(v)})
        try:
            sq = regime_welfare('status_quo', p)['welfare']
            full = regime_welfare('all_four_pillars', p)['welfare']
            rows.append({
                param_name: float(v),
                'W_status_quo': sq,
                'W_full_arch': full,
                'gain_absolute': full - sq,
                'gain_pct': 100.0 * (full - sq) / sq if sq > 0 else np.nan,
            })
        except Exception as e:
            rows.append({
                param_name: float(v),
                'W_status_quo': np.nan,
                'W_full_arch': np.nan,
                'gain_absolute': np.nan,
                'gain_pct': np.nan,
            })
    return pd.DataFrame(rows)


def standard_sensitivity_grid(base_params: Params | None = None) -> Dict[str, pd.DataFrame]:
    """Run one-at-a-time sensitivity over a standard grid of parameters."""
    base = Params() if base_params is None else base_params
    grids = {
        'pi_theta': np.linspace(0.05, 0.85, 17),
        'pi_a': np.linspace(0.01, 0.40, 14),
        'q0': np.linspace(0.01, 0.30, 15),
        'q2_0': np.linspace(0.10, 0.70, 13),
        'H': np.linspace(50.0, 200.0, 16),
        'c_e_star': np.linspace(5.0, 50.0, 10),
    }
    return {name: one_at_a_time(name, vals, base) for name, vals in grids.items()}


# ------------------------------------------------------------------
# Monte Carlo
# ------------------------------------------------------------------

def monte_carlo(n_draws: int = 1000,
                seed: int = 42,
                base_params: Params | None = None) -> pd.DataFrame:
    """Monte Carlo over uncertain parameters.

    Priors:
        pi_theta ~ Beta(2, 3)        # Mean ~ 0.4, anchored to Kim et al.
        pi_a ~ Beta(1, 9)            # Mean ~ 0.1
        q0 ~ Beta(1, 9)              # Mean ~ 0.1
        q2_0 ~ Beta(2, 3)            # Mean ~ 0.4
        H ~ Uniform(50, 150)
        c_e_star ~ Uniform(10, 40)
    """
    base = Params() if base_params is None else base_params
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_draws):
        try:
            p = replace(
                base,
                pi_theta=float(rng.beta(2, 3)),
                pi_a=float(rng.beta(1, 9)),
                q0=float(rng.beta(1, 9)),
                q2_0=float(rng.beta(2, 3)),
                H=float(rng.uniform(50, 150)),
                c_e_star=float(rng.uniform(10, 40)),
            )
            # Skip if assumptions violate ordering (Assumption 1)
            if not (p.q1 > p.q2_0 > p.q0 > 0):
                continue
            sq = regime_welfare('status_quo', p)['welfare']
            full = regime_welfare('all_four_pillars', p)['welfare']
            rows.append({
                'draw': i,
                'pi_theta': p.pi_theta,
                'pi_a': p.pi_a,
                'q0': p.q0,
                'q2_0': p.q2_0,
                'H': p.H,
                'c_e_star': p.c_e_star,
                'W_status_quo': sq,
                'W_full_arch': full,
                'gain_pct': 100.0 * (full - sq) / sq if sq > 0 else np.nan,
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# Correlated types (Appendix B)
# ------------------------------------------------------------------

def correlation_sensitivity(rho_grid: np.ndarray | None = None,
                            base_params: Params | None = None) -> pd.DataFrame:
    """Sensitivity of normative fiction to rho_theta_a (Appendix B)."""
    base = Params() if base_params is None else base_params
    if rho_grid is None:
        rho_grid = np.linspace(-0.3, 0.7, 21)
    rows = []
    for rho in rho_grid:
        try:
            post = posterior_case_iia(0.0, base, rho=float(rho))
            fic = normative_fiction(0.0, base, rho=float(rho))
            rows.append({
                'rho_theta_a': float(rho),
                'posterior': post,
                'normative_fiction': fic,
            })
        except ValueError:
            # rho induces invalid joint distribution; skip
            continue
    return pd.DataFrame(rows)


def summarize_monte_carlo(df: pd.DataFrame) -> Dict[str, float]:
    """Summary statistics of the Monte Carlo gain distribution."""
    g = df['gain_pct'].dropna()
    return {
        'n': int(len(g)),
        'mean_gain_pct': float(g.mean()),
        'median_gain_pct': float(g.median()),
        'std_gain_pct': float(g.std()),
        'pct_05': float(g.quantile(0.05)),
        'pct_95': float(g.quantile(0.95)),
        'share_positive': float((g > 0).mean()),
    }
