# Replication Package

## *Reliance Inference and Institutional Architecture under Generative AI: A Law-and-Economics Analysis*

This repository contains the replication code and outputs for the manuscript
*"Reliance Inference and Institutional Architecture under Generative AI: A
Law-and-Economics Analysis"* by Rina Suzuki, Kenji Suzuki, and Koki Arai.

The code reproduces all numerical results in **Sections 3.7–3.8** and the
**Mathematical Appendix E** of the manuscript, including:

- The four-pillar welfare decomposition (Table 1, Section 3.8)
- The dynamic welfare loss under static vs. BAT rules (Figure 1, Proposition 4)
- The supermodular complementarity visualization (Figure 2)
- One-at-a-time sensitivity analysis (Figure E.1)
- Monte Carlo robustness over 1,000 prior draws (Figure E.2, Table E.2)
- Numerical verification of correlated-types extension (Figure E.3, Appendix B)

---

## Quick Start

### Option 1: Local Python (recommended for full reproduction)

```bash
# Clone repository
git clone https://github.com/<USERNAME>/reliance-inference-replication.git
cd reliance-inference-replication

# Set up environment (Python 3.9+)
python -m venv venv
source venv/bin/activate     # macOS/Linux
# venv\Scripts\activate      # Windows
pip install -r requirements.txt

# Verify all propositions hold numerically
python tests/test_smoke.py

# Reproduce all tables and figures
python code/run_all.py
```

Outputs are written to `output/tables/` (CSV) and `output/figures/` (PNG).

### Option 2: Google Colab (interactive, no setup)

Open `notebooks/notebook.ipynb` in Google Colab. The notebook reproduces all
results step-by-step with inline figures and explanations.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<USERNAME>/reliance-inference-replication/blob/main/notebooks/notebook.ipynb)

---

## Repository Structure

```
reliance-inference-replication/
├── README.md                      # This file
├── LICENSE                        # MIT License
├── CITATION.cff                   # Citation metadata (GitHub-recognized)
├── requirements.txt               # Python dependencies
├── .gitignore
├── .github/
│   └── workflows/
│       └── tests.yml              # CI: run smoke tests on push
├── code/                          # Source modules
│   ├── model.py                   # Posteriors, welfare function, four-pillar
│   ├── dynamics.py                # Proposition 4 dynamic analysis
│   ├── sensitivity.py             # One-at-a-time and Monte Carlo
│   ├── plots.py                   # Figure generation
│   └── run_all.py                 # Master script
├── tests/
│   └── test_smoke.py              # Smoke tests for main propositions
├── notebooks/
│   └── notebook.ipynb             # Interactive Colab notebook
├── data/                          # (No external data; calibration in code)
│   └── README.md                  # Calibration source documentation
├── docs/
│   ├── mapping.md                 # Code-to-manuscript result mapping
│   └── reproducibility.md         # Reproducibility statement
└── output/                        # Generated outputs (committed for transparency)
    ├── tables/
    │   ├── table_3_8_calibration.csv
    │   ├── proposition4_check.csv
    │   ├── monte_carlo_summary.csv
    │   └── monte_carlo_full_draws.csv
    └── figures/
        ├── fig_dynamics.png       # Manuscript Figure 1
        ├── fig_decomposition.png  # Manuscript Figure 2
        ├── fig_sensitivity.png    # Appendix Figure E.1
        ├── fig_monte_carlo.png    # Appendix Figure E.2
        └── fig_correlation.png    # Appendix Figure E.3
```

---

## Mapping to the Manuscript

| Result in paper                            | Code module              | Function / Test                       |
|--------------------------------------------|--------------------------|---------------------------------------|
| Lemma 1 (Λ decreasing)                     | `code/model.py`          | `Lambda` / `test_lambda_monotone`     |
| Lemma 2 (corner solution)                  | `code/model.py`          | `social_optimum_effort`               |
| Proposition 1 (Bayesian posterior)         | `code/model.py`          | `posterior_case_iia`                  |
| Proposition 3 (e^SO efficiency)            | `code/model.py`          | `social_optimum_effort`               |
| Proposition 4 (dynamic delay)              | `code/dynamics.py`       | `proposition4_check`                  |
| Proposition B.1 (correlation monotonicity) | `code/sensitivity.py`    | `correlation_sensitivity`             |
| Section 3.8 calibration table              | `code/model.py`          | `four_pillar_table`                   |
| Manuscript Figure 1 (dynamics)             | `code/plots.py`          | `fig_dynamics`                        |
| Manuscript Figure 2 (decomposition)        | `code/plots.py`          | `fig_decomposition`                   |
| Appendix Figure E.1 (sensitivity)          | `code/plots.py`          | `fig_sensitivity`                     |
| Appendix Figure E.2 (Monte Carlo)          | `code/plots.py`          | `fig_monte_carlo`                     |
| Appendix Figure E.3 (correlation)          | `code/plots.py`          | `fig_correlation`                     |

A more detailed mapping is provided in `docs/mapping.md`.

---

## Reproducibility

All randomness uses fixed seeds (default `seed=42`). On any platform meeting
the dependency versions in `requirements.txt`, running `python code/run_all.py`
yields the following key results to floating-point precision:

| Quantity                                    | Value          |
|---------------------------------------------|----------------|
| Posterior in Case (ii-a)                    | 0.7273         |
| Normative fiction magnitude                 | 0.2727         |
| Welfare under all four pillars              | 230.4          |
| Welfare gain over status quo                | 28.0%          |
| Static rule cumulative loss                 | 356.378        |
| BAT rule cumulative loss                    | 0.019          |
| BAT loss reduction                          | 99.99%         |
| Monte Carlo mean welfare gain               | 31.95%         |
| Monte Carlo [5%, 95%] interval              | [21.09%, 43.88%]|
| Share of strictly positive MC gains         | 100.0%         |

Detailed reproducibility procedures are documented in `docs/reproducibility.md`.

---

## Software Requirements

- **Python** 3.9 or later
- **NumPy** ≥ 1.23
- **SciPy** ≥ 1.10
- **pandas** ≥ 1.5
- **Matplotlib** ≥ 3.6

Total runtime: under 60 seconds on a standard laptop (no GPU required).

---

## Citation

If you use this code, please cite both the paper and this repository:

```bibtex
@unpublished{SuzukiSuzukiArai2026,
  author = {Suzuki, Rina and Suzuki, Kenji and Arai, Koki},
  title  = {Reliance Inference and Institutional Architecture under
            Generative AI: A Law-and-Economics Analysis},
  year   = {2026},
  note   = {Working paper},
}

@software{ArAiReplication2026,
  author  = {Arai, Koki},
  title   = {Replication package for "Reliance Inference and Institutional
             Architecture under Generative AI"},
  year    = {2026},
  url     = {https://github.com/<USERNAME>/reliance-inference-replication},
  version = {1.0.0},
}
```

GitHub will automatically generate citation strings from `CITATION.cff`.

---

## License

Code: **MIT License** — see [LICENSE](LICENSE) for details. Replication and
modification are permitted with citation. The manuscript itself is subject to
its publisher's copyright; please consult the published version for citation.

---

## Acknowledgments

This research was supported by JSPS KAKENHI Grant Number 23K01404. The authors
thank Kim, Jin, and Lee (2026) for the empirical magnitudes that anchor the
calibrated welfare results in this paper.

---

## Contact

Questions about the code or replication should be directed to the corresponding
author. Please open a GitHub Issue for bug reports or reproducibility concerns.
