# Changelog

All notable changes to this replication package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-27

### Added

- Initial public release of the replication package.
- Five Python modules (`model.py`, `dynamics.py`, `sensitivity.py`,
  `plots.py`, `run_all.py`) reproducing all numerical results in the paper.
- Smoke tests (`tests/test_smoke.py`) verifying all main propositions.
- Reproducibility verification script (`code/verify_outputs.py`).
- Interactive Google Colab notebook (`notebooks/notebook.ipynb`).
- Comprehensive README with quick-start instructions for both local Python
  and Colab.
- Code-to-manuscript mapping (`docs/mapping.md`) documenting every paper
  result and its corresponding code location.
- Reproducibility statement (`docs/reproducibility.md`) including the
  reference values for all key numerical claims.
- Continuous integration via GitHub Actions, testing on Python 3.9, 3.10,
  3.11, and 3.12 on every push.
- Citation metadata in CITATION.cff for automatic GitHub citation generation.

### Numerical results reproduced

- Section 3.8 four-pillar welfare decomposition (welfare gain: 28.0%).
- Proposition 4 dynamic welfare loss: static = 356.378, BAT = 0.019,
  reduction = 99.99%.
- Monte Carlo robustness (n=938 valid draws of 1000): mean gain 31.95%,
  [5%, 95%] interval [21.09%, 43.88%], 100% positive.
- Appendix B Proposition B.1: posterior strictly decreasing in correlation
  parameter ρ_θa.
