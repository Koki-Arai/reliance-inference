"""
plots.py
========
Figure generation for the manuscript appendix and Online Companion.

Figures produced:
- fig_dynamics.png: time paths of pi_theta, e^SO, and welfare under static vs BAT
- fig_sensitivity.png: 6-panel sensitivity heatmap
- fig_monte_carlo.png: histogram of welfare gain distribution
- fig_correlation.png: normative fiction as function of rho_theta_a
- fig_decomposition.png: bar chart of welfare decomposition by regime
"""

from __future__ import annotations

import os
from typing import Dict

import matplotlib
matplotlib.use('Agg')   # Non-interactive backend for headless / Colab
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model import Params, four_pillar_table
from dynamics import (DynamicParams, time_varying_e_so, static_rule_path,
                      bat_rule_path, proposition4_check, trajectory_pi_theta)
from sensitivity import (standard_sensitivity_grid, monte_carlo,
                         correlation_sensitivity, summarize_monte_carlo)


# Common style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'legend.fontsize': 9,
    'figure.dpi': 120,
})


def fig_dynamics(p: Params, d: DynamicParams,
                 output_dir: str = 'figures') -> str:
    """Time paths under static rule vs BAT (Pillar II)."""
    os.makedirs(output_dir, exist_ok=True)
    res = proposition4_check(p, d)

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))

    t = np.arange(d.T)

    # Panel 1: pi_theta(t)
    ax = axes[0]
    ax.plot(t, trajectory_pi_theta(d), 'k-', linewidth=1.6)
    ax.set_xlabel('Quarter')
    ax.set_ylabel(r'$\pi_\theta(t)$')
    ax.set_title('(a) Training-data inclusion prevalence')
    ax.grid(alpha=0.3)

    # Panel 2: e^SO_t vs e*
    ax = axes[1]
    ax.plot(t, res['e_so_path'], 'b-', linewidth=1.6, label=r'$e^{SO}_t$')
    ax.axhline(p.e_star, color='r', linestyle='--', linewidth=1.4,
               label=r'$e^*$ (static)')
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Effort')
    ax.set_title(r'(b) Optimal effort $e^{SO}_t$ vs. static rule')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)

    # Panel 3: cumulative welfare loss
    ax = axes[2]
    discount = np.exp(-d.r * t)
    static_loss = discount * (res['W_so_path'] - res['W_static'])
    bat_loss = discount * (res['W_so_path'] - res['W_bat'])
    ax.plot(t, np.cumsum(static_loss), 'r-', linewidth=1.6,
            label=f'Static (total = {res["total_loss_static"]:.1f})')
    ax.plot(t, np.cumsum(bat_loss), 'g-', linewidth=1.6,
            label=f'BAT (total = {res["total_loss_bat"]:.1f})')
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Cumulative discounted loss')
    ax.set_title('(c) Cumulative welfare loss (Proposition 4)')
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, 'fig_dynamics.png')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return path


def fig_sensitivity(p: Params, output_dir: str = 'figures') -> str:
    """Six-panel one-at-a-time sensitivity."""
    os.makedirs(output_dir, exist_ok=True)
    grid = standard_sensitivity_grid(p)

    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    panels = [
        ('pi_theta', r'$\pi_\theta$'),
        ('pi_a', r'$\pi_a$'),
        ('q0', r'$q_0$'),
        ('q2_0', r'$q_2(0)$'),
        ('H', r'$H$'),
        ('c_e_star', r'$c(e^*)$'),
    ]

    for ax, (name, label) in zip(axes.ravel(), panels):
        df = grid[name]
        ax.plot(df[name], df['gain_pct'], 'b-', linewidth=1.6)
        ax.axhline(0, color='gray', linewidth=0.6)
        ax.set_xlabel(label)
        ax.set_ylabel('Welfare gain (%)')
        ax.set_title(f'Sensitivity to {label}')
        ax.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, 'fig_sensitivity.png')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return path


def fig_monte_carlo(p: Params, n_draws: int = 1000,
                    output_dir: str = 'figures') -> str:
    """Histogram of Monte Carlo welfare gain distribution."""
    os.makedirs(output_dir, exist_ok=True)
    df = monte_carlo(n_draws=n_draws, base_params=p)
    summary = summarize_monte_carlo(df)

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.hist(df['gain_pct'].dropna(), bins=40, color='steelblue',
            edgecolor='white', alpha=0.85)
    ax.axvline(summary['mean_gain_pct'], color='red', linestyle='--',
               linewidth=1.5,
               label=f"Mean: {summary['mean_gain_pct']:.2f}%")
    ax.axvline(summary['pct_05'], color='orange', linestyle=':',
               linewidth=1.2,
               label=f"5th pct: {summary['pct_05']:.2f}%")
    ax.axvline(summary['pct_95'], color='orange', linestyle=':',
               linewidth=1.2,
               label=f"95th pct: {summary['pct_95']:.2f}%")
    ax.set_xlabel('Welfare gain from full architecture (% over status quo)')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Monte Carlo distribution of welfare gain '
                 f'(n = {summary["n"]})')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, 'fig_monte_carlo.png')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return path


def fig_correlation(p: Params, output_dir: str = 'figures') -> str:
    """Normative fiction as function of rho_theta_a (Appendix B)."""
    os.makedirs(output_dir, exist_ok=True)
    df = correlation_sensitivity(base_params=p)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0))

    ax = axes[0]
    ax.plot(df['rho_theta_a'], df['posterior'], 'b-', linewidth=1.6)
    ax.axvline(0, color='gray', linewidth=0.6, linestyle=':')
    ax.set_xlabel(r'$\rho_{\theta a}$')
    ax.set_ylabel(r'$\Pr(\theta=1 \mid s\geq s^*, a=0)$')
    ax.set_title('(a) Bayesian posterior in Case (ii-a)')
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(df['rho_theta_a'], df['normative_fiction'], 'r-', linewidth=1.6)
    ax.axvline(0, color='gray', linewidth=0.6, linestyle=':')
    ax.set_xlabel(r'$\rho_{\theta a}$')
    ax.set_ylabel('Normative fiction magnitude')
    ax.set_title('(b) Magnitude of upward fiction')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, 'fig_correlation.png')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return path


def fig_decomposition(p: Params, output_dir: str = 'figures') -> str:
    """Welfare decomposition bar chart by regime."""
    os.makedirs(output_dir, exist_ok=True)
    table = four_pillar_table(p)

    regimes = ['status_quo', 'pillar_I', 'pillar_I_II',
               'pillar_I_II_III', 'all_four_pillars']
    labels = ['Status quo', 'Pillar I', 'Pillars I+II',
              'Pillars I+II+III', 'All four']

    inf_loss = [table[r]['infringement'] for r in regimes]
    prev = [table[r]['prevention'] for r in regimes]
    adj = [table[r]['adjudication'] for r in regimes]
    B = [table[r]['B'] for r in regimes]
    W = [table[r]['welfare'] for r in regimes]

    x = np.arange(len(regimes))
    width = 0.6

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    ax = axes[0]
    ax.bar(x, B, width, label='AI benefit', color='#4e79a7')
    ax.bar(x, [-i for i in inf_loss], width,
           label='Infringement loss', color='#e15759', bottom=0)
    ax.bar(x, [-i for i in prev], width,
           label='Prevention cost', color='#76b7b2',
           bottom=[-i for i in inf_loss])
    ax.bar(x, [-i for i in adj], width,
           label='Adjudication errors', color='#f28e2b',
           bottom=[-i - j for i, j in zip(inf_loss, prev)])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20)
    ax.set_ylabel('Component value')
    ax.set_title('(a) Welfare components by regime')
    ax.legend(loc='lower right', fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[1]
    bars = ax.bar(x, W, width, color='steelblue', edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20)
    ax.set_ylabel(r'Total welfare $\mathcal{W}$')
    ax.set_title('(b) Total welfare')
    for i, bar in enumerate(bars):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f'{W[i]:.1f}', ha='center', va='bottom', fontsize=9)
    ax.grid(alpha=0.3, axis='y')

    plt.tight_layout()
    path = os.path.join(output_dir, 'fig_decomposition.png')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return path


def make_all_figures(p: Params | None = None,
                     d: DynamicParams | None = None,
                     output_dir: str = 'figures',
                     n_mc_draws: int = 1000) -> Dict[str, str]:
    """Generate all figures and return a dict of paths."""
    p = Params() if p is None else p
    d = DynamicParams() if d is None else d
    paths = {
        'dynamics': fig_dynamics(p, d, output_dir),
        'sensitivity': fig_sensitivity(p, output_dir),
        'monte_carlo': fig_monte_carlo(p, n_mc_draws, output_dir),
        'correlation': fig_correlation(p, output_dir),
        'decomposition': fig_decomposition(p, output_dir),
    }
    return paths
