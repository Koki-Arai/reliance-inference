# Reproducibility Statement

## Overview

This replication package is designed for full reproducibility of all numerical
results in *"Reliance Inference and Institutional Architecture under
Generative AI: A Law-and-Economics Analysis."* All analyses are
deterministic given the fixed default random seed (`seed=42`).

---

## Reproducibility Checklist

- [x] All data are simulated; no external data files are required.
- [x] All random seeds are fixed (default: `seed=42`).
- [x] All dependency versions are pinned in `requirements.txt`.
- [x] All output artifacts are committed to the repository for diff comparison.
- [x] A verification script (`code/verify_outputs.py`) compares newly-generated
      outputs against the committed reference values.
- [x] Continuous integration (GitHub Actions) tests all main propositions on
      Python 3.9, 3.10, 3.11, and 3.12 on every push.
- [x] A code-to-manuscript mapping is provided in `docs/mapping.md`.

---

## Step-by-Step Reproduction

### 1. Clone the repository

```bash
git clone https://github.com/<USERNAME>/reliance-inference-replication.git
cd reliance-inference-replication
```

### 2. Set up the environment

```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux; or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Verify all main propositions hold numerically

```bash
python tests/test_smoke.py
```

Expected output (last line):

```
ALL TESTS PASSED
```

### 4. Reproduce all tables and figures

```bash
python code/run_all.py
```

This populates `output/tables/` (CSV files) and `output/figures/` (PNG files)
in approximately 30–60 seconds.

### 5. Verify outputs match committed reference values

```bash
python code/verify_outputs.py
```

Expected output (last line):

```
ALL CHECKS PASSED: outputs match committed reference values
```

---

## Reference Values

The following key numbers reported in the manuscript should reproduce exactly
under the default seed:

| Quantity                                           | Reference |
|----------------------------------------------------|-----------|
| Posterior in Case (ii-a)                           | 0.7273    |
| Normative fiction magnitude                        | 0.2727    |
| Welfare under all four pillars                     | 230.4     |
| Welfare gain over status quo                       | 28.0%     |
| Static rule cumulative loss (Proposition 4)        | 356.378   |
| BAT rule cumulative loss                           | 0.019     |
| BAT loss reduction                                 | 99.99%    |
| Quadratic lower bound (Proposition 4)              | 356.378   |
| Monte Carlo: number of valid draws (n=1000 seed=42)| 938       |
| Monte Carlo: mean welfare gain                     | 31.95%    |
| Monte Carlo: median welfare gain                   | 31.47%    |
| Monte Carlo: 5th percentile                        | 21.09%    |
| Monte Carlo: 95th percentile                       | 43.88%    |
| Monte Carlo: share of strictly positive gains      | 100.0%    |

---

## Software Stack

- **Python**: 3.9, 3.10, 3.11, or 3.12 (tested in CI)
- **NumPy**: ≥ 1.23
- **SciPy**: ≥ 1.10 (for `optimize.minimize_scalar`)
- **pandas**: ≥ 1.5
- **Matplotlib**: ≥ 3.6 (with `Agg` backend for headless environments)

No GPU is required. Total runtime: under 60 seconds on a 2020-era laptop.

---

## Computational Determinism

All numerical procedures are deterministic given the fixed seed:

- **NumPy random state**: explicitly seeded via `np.random.default_rng(seed)`
  in `monte_carlo()`. No global random state is modified.
- **SciPy optimization**: `minimize_scalar` with `method='bounded'` is fully
  deterministic given fixed bounds and tolerance (`xatol=1e-7`).
- **Matplotlib**: the `Agg` backend ensures pixel-identical figure output
  across platforms. Minor anti-aliasing differences may appear at the level
  of individual pixels but do not affect the underlying numerical content.

---

## Known Platform Differences

The numerical results in `output/tables/` are reproduced to floating-point
precision on Linux, macOS, and Windows. Figures are visually identical but
may differ at the pixel level due to platform-specific font rendering. To
verify numerical reproducibility independently of figure pixel comparison,
use `code/verify_outputs.py`, which tests only the underlying CSV outputs.

---

## Issues and Contact

Reproducibility concerns or bug reports should be filed as GitHub Issues.
The corresponding author commits to addressing all reproducibility issues
within a reasonable timeframe.
