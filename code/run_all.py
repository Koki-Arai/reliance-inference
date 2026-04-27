"""
run_all.py
==========
Master script to reproduce all simulation outputs in the manuscript.

Outputs (written to <repo_root>/output/ by default):
- tables/table_3_8_calibration.csv: Section 3.8 Table 1
- tables/proposition4_check.csv: numerical verification of Proposition 4
- tables/monte_carlo_summary.csv: Monte Carlo summary statistics
- tables/monte_carlo_full_draws.csv: full Monte Carlo draws
- figures/fig_dynamics.png: Manuscript Figure 1
- figures/fig_decomposition.png: Manuscript Figure 2
- figures/fig_sensitivity.png: Appendix Figure E.1
- figures/fig_monte_carlo.png: Appendix Figure E.2
- figures/fig_correlation.png: Appendix Figure E.3

Usage from repository root:
    python code/run_all.py
"""

from __future__ import annotations

import os
import json

import numpy as np
import pandas as pd

from model import Params, four_pillar_table
from dynamics import DynamicParams, proposition4_check
from sensitivity import (monte_carlo, summarize_monte_carlo,
                         standard_sensitivity_grid, correlation_sensitivity)
from plots import make_all_figures


# Default output directory: <repo_root>/output, regardless of where script is run.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_THIS_DIR)
DEFAULT_OUTPUT_ROOT = os.path.join(_REPO_ROOT, "output")


def reproduce_section_3_8_table(p: Params, output_dir: str) -> str:
    """Reproduce the Section 3.8 calibration table."""
    table = four_pillar_table(p)
    rows = []
    labels = {
        'status_quo': 'Status quo (static rule)',
        'pillar_I': 'Pillar I only',
        'pillar_I_II': 'Pillars I + II',
        'pillar_I_II_III': 'Pillars I + II + III',
        'all_four_pillars': 'All four pillars',
    }
    for key, lbl in labels.items():
        d = table[key]
        rows.append({
            'Regime': lbl,
            'Infringement': round(d['infringement'], 1),
            'Prevention': round(d['prevention'], 1),
            'Adjudication': round(d['adjudication'], 1),
            'AI benefit': round(d['B'], 1),
            'Welfare': round(d['welfare'], 1),
        })
    df = pd.DataFrame(rows)
    path = os.path.join(output_dir, 'table_3_8_calibration.csv')
    df.to_csv(path, index=False)
    return path


def proposition4_table(p: Params, d: DynamicParams, output_dir: str) -> str:
    """Numerical verification of Proposition 4."""
    res = proposition4_check(p, d)
    summary = pd.DataFrame([{
        'horizon_T': d.T,
        'discount_rate_r': d.r,
        'pi_theta_initial': d.pi_theta_0,
        'pi_theta_long_run': d.pi_theta_inf,
        'static_e_star': p.e_star,
        'static_total_loss': round(res['total_loss_static'], 3),
        'BAT_total_loss': round(res['total_loss_bat'], 3),
        'BAT_loss_reduction_pct': round(
            100 * (res['total_loss_static'] - res['total_loss_bat'])
            / res['total_loss_static'], 2),
        'W_double_prime_at_e_so': round(res['W_double_prime_at_e_so'], 3),
        'quadratic_lower_bound': round(res['quadratic_bound'], 3),
        'bound_holds': bool(res['bound_holds']),
    }])
    path = os.path.join(output_dir, 'proposition4_check.csv')
    summary.to_csv(path, index=False)
    return path


def monte_carlo_summary_table(p: Params, n_draws: int, output_dir: str,
                              seed: int = 42) -> str:
    """Run Monte Carlo and save summary."""
    df = monte_carlo(n_draws=n_draws, seed=seed, base_params=p)
    summary = summarize_monte_carlo(df)
    path = os.path.join(output_dir, 'monte_carlo_summary.csv')
    pd.DataFrame([summary]).to_csv(path, index=False)
    full_path = os.path.join(output_dir, 'monte_carlo_full_draws.csv')
    df.to_csv(full_path, index=False)
    return path


def run_all(output_root: str | None = None,
            n_mc_draws: int = 1000) -> dict:
    """Run the complete pipeline and produce outputs."""
    if output_root is None:
        output_root = DEFAULT_OUTPUT_ROOT
    os.makedirs(output_root, exist_ok=True)
    tables_dir = os.path.join(output_root, 'tables')
    figures_dir = os.path.join(output_root, 'figures')
    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    p = Params()
    d = DynamicParams()

    print("=" * 60)
    print("SIMULATION PIPELINE")
    print("=" * 60)

    print("\n[1/4] Reproducing Section 3.8 calibration table...")
    t1 = reproduce_section_3_8_table(p, tables_dir)
    print(f"      -> {t1}")

    print("\n[2/4] Running Proposition 4 numerical verification...")
    t2 = proposition4_table(p, d, tables_dir)
    print(f"      -> {t2}")

    print(f"\n[3/4] Running Monte Carlo (n = {n_mc_draws})...")
    t3 = monte_carlo_summary_table(p, n_mc_draws, tables_dir)
    print(f"      -> {t3}")

    print("\n[4/4] Generating figures...")
    figs = make_all_figures(p, d, figures_dir, n_mc_draws=n_mc_draws)
    for name, path in figs.items():
        print(f"      -> {name}: {path}")

    summary = {
        'tables': [t1, t2, t3],
        'figures': figs,
        'output_root': output_root,
    }

    summary_path = os.path.join(output_root, 'run_summary.json')
    with open(summary_path, 'w') as f:
        json.dump({k: (v if not isinstance(v, dict) else v)
                   for k, v in summary.items()}, f, indent=2)

    print("\nDone.")
    return summary


if __name__ == '__main__':
    run_all()
