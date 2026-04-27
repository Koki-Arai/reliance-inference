# Contributing

Thank you for your interest in this replication package. As a research
artifact accompanying a published paper, the primary purpose of this
repository is to enable verification and reproduction of the numerical
results in *"Reliance Inference and Institutional Architecture under
Generative AI: A Law-and-Economics Analysis."*

## What contributions are welcome?

- **Reproducibility issues**: bug reports for cases where the code does not
  reproduce the documented reference values, or fails to run on a supported
  platform.
- **Documentation improvements**: clarifications to the README, mapping
  document, or reproducibility statement.
- **Test additions**: additional smoke tests for results not currently covered.
- **Compatibility patches**: minor changes to maintain compatibility with new
  versions of NumPy, SciPy, pandas, or Matplotlib.

## What contributions are not appropriate?

- Changes to the model specification, calibration, or numerical procedures
  that would alter the published results. Such changes should appear in a
  separate fork and a follow-up paper, not in this replication archive.
- New features or extensions unrelated to reproducing the published results.

## How to contribute

1. **Open an Issue first**: describe the problem or proposed change. The
   author will respond within a reasonable timeframe.
2. **Fork and submit a Pull Request** if your contribution is appropriate
   and has been discussed in an Issue.
3. **Run tests locally**: ensure `python tests/test_smoke.py` passes before
   submitting a PR.
4. **Verify reproducibility**: if your PR modifies code in `code/`, run
   `python code/run_all.py` followed by `python code/verify_outputs.py` to
   confirm that all reference values still reproduce.

## Coding conventions

- Python 3.9+ syntax.
- PEP 8 formatting (no enforced linter, but please be consistent).
- Docstrings for all public functions, with cross-references to the
  manuscript section or proposition where the result is stated.
- All randomness must use explicit seeds; do not modify global random state.

## Contact

Questions: please open a GitHub Issue.
