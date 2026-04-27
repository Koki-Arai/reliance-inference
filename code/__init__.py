"""
Replication code for "Reliance Inference and Institutional Architecture
under Generative AI: A Law-and-Economics Analysis."

Modules:
    model        Core model: posteriors, welfare function, four-pillar
                 decomposition.
    dynamics     Dynamic welfare analysis (Proposition 4).
    sensitivity  One-at-a-time sensitivity and Monte Carlo robustness.
    plots        Figure generation.

Scripts:
    run_all          Reproduces all tables and figures.
    verify_outputs   Verifies outputs against committed reference values.
"""

__version__ = "1.0.0"
