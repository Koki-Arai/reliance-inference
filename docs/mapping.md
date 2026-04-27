# Code-to-Manuscript Mapping

This document provides a detailed mapping from each result in the
manuscript to the corresponding code module and function.

---

## Section 2: Model

| Result            | Statement                                           | Code location                       |
|-------------------|-----------------------------------------------------|-------------------------------------|
| Assumption 1      | q₁ > q₂(0) > q₀ > 0; q₂ decreasing                 | `code/model.py::Params` (defaults), enforced in `monte_carlo` rejection |
| Lemma 1           | Λ(e) is strictly decreasing in e                    | `code/model.py::Lambda`             |
| Lemma 2           | Corner-solution property of D's filtering effort    | `code/model.py::social_optimum_effort` |
| Proposition 1     | Bayesian characterization of tripartite framework   | `code/model.py::posterior_case_iia` |
| Proposition 2     | CCA extension to AI black-box environments          | (analytical only; no numeric)       |
| Result 1          | Inference vs. direct-proof efficiency               | (analytical only)                   |
| Proposition 3     | Efficient safe-harbor threshold                     | `code/model.py::social_optimum_effort` |

---

## Section 3: Architecture

| Result            | Statement                                           | Code location                       |
|-------------------|-----------------------------------------------------|-------------------------------------|
| Lemma 3           | Unraveling under tiered disclosure                  | (analytical; proof in Appendix A)   |
| Proposition 4     | Institutional delay; quadratic loss bound           | `code/dynamics.py::proposition4_check` |
| Section 3.8 Table | Four-pillar welfare decomposition (Table 1)         | `code/model.py::four_pillar_table`  |
| Figure 1          | Dynamic welfare paths (Section 3.7)                 | `code/plots.py::fig_dynamics`       |
| Figure 2          | Welfare decomposition by regime (Section 3.8)       | `code/plots.py::fig_decomposition`  |

---

## Mathematical Appendix

### Appendix A: Lemma 3 proof

Analytical only. The unraveling logic is standard (Grossman 1981; Milgrom
1981) and does not require numerical verification beyond the welfare effects
in `four_pillar_table`.

### Appendix B: Correlated types

| Result            | Statement                                           | Code location                       |
|-------------------|-----------------------------------------------------|-------------------------------------|
| Lemma B.1         | Correlation–conditional probability equivalence     | `code/model.py::posterior_case_iia` (rho parameter) |
| Proposition B.1   | Posterior strictly decreasing in ρ_θa               | `code/sensitivity.py::correlation_sensitivity` |
| Figure E.3        | Numerical verification of Proposition B.1           | `code/plots.py::fig_correlation`    |

### Appendix C: Oligopolistic developers

Analytical only. The duopoly extension establishes existence of symmetric
Nash equilibrium and the welfare ranking e_M < e_N < e^SO. No numerical
verification is required for the existence proof; the welfare ranking is
implicit in the comparison between the monopoly result (Lemma 2) and the
calibrated four-pillar gain.

### Appendix D: Behavioral departures

Analytical only. Propositions D.1–D.2 establish bounds on welfare loss
under anchoring and base-rate neglect; the bounds are analytical and apply
post-Pillar-I (i.e., to the residual Tier-3 population only).

### Appendix E: Computational implementation

| Section           | Content                                             | Code location                       |
|-------------------|-----------------------------------------------------|-------------------------------------|
| E.1               | Functional forms; reproducibility                    | `code/model.py` (Params, q2, cost), `code/run_all.py` (seed) |
| E.2 / Table E.1   | Numerical verification of main results              | `tests/test_smoke.py`               |
| E.3 / Figure E.1  | One-at-a-time sensitivity                            | `code/sensitivity.py::standard_sensitivity_grid`, `code/plots.py::fig_sensitivity` |
| E.4 / Table E.2   | Monte Carlo summary statistics                      | `code/sensitivity.py::monte_carlo`, `code/sensitivity.py::summarize_monte_carlo` |
| E.4 / Figure E.2  | Monte Carlo histogram                                | `code/plots.py::fig_monte_carlo`    |
| E.5 / Figure E.3  | Correlation sensitivity (verifies Proposition B.1)  | `code/plots.py::fig_correlation`    |

---

## Output Files

| Output file                              | Manuscript location           |
|-------------------------------------------|-------------------------------|
| `output/tables/table_3_8_calibration.csv` | Table 1 (Section 3.8)         |
| `output/tables/proposition4_check.csv`    | Cited in Section 3.7, Table E.1 |
| `output/tables/monte_carlo_summary.csv`   | Table E.2 (Appendix E.4)      |
| `output/tables/monte_carlo_full_draws.csv`| Source for Figure E.2          |
| `output/figures/fig_dynamics.png`         | Figure 1 (Section 3.7)        |
| `output/figures/fig_decomposition.png`    | Figure 2 (Section 3.8)        |
| `output/figures/fig_sensitivity.png`      | Figure E.1 (Appendix E.3)     |
| `output/figures/fig_monte_carlo.png`      | Figure E.2 (Appendix E.4)     |
| `output/figures/fig_correlation.png`      | Figure E.3 (Appendix E.5)     |
