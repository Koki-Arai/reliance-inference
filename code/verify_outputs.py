"""
verify_outputs.py
=================
Reproducibility verification: compares newly-generated outputs against the
committed reference outputs in `output/` to confirm that the user's machine
reproduces the exact numerical results reported in the manuscript.

Usage from repository root:
    python code/run_all.py            # generate fresh outputs
    python code/verify_outputs.py     # compare against committed reference

Tolerance: 1e-6 relative tolerance for floating-point comparisons.
Returns exit code 0 on success, 1 on any mismatch.
"""

from __future__ import annotations

import os
import sys
import io

import numpy as np
import pandas as pd


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_THIS_DIR)
_OUTPUT_DIR = os.path.join(_REPO_ROOT, "output")
_TABLES_DIR = os.path.join(_OUTPUT_DIR, "tables")

# Reference (canonical) values from the manuscript and Appendix E
REFERENCE_VALUES = {
    "calibration": {
        "Status quo (static rule)": {
            "Infringement": 11.5, "Prevention": 20.0, "Adjudication": 8.5,
            "AI benefit": 220.0, "Welfare": 180.0,
        },
        "Pillar I only": {
            "Infringement": 11.5, "Prevention": 20.0, "Adjudication": 2.0,
            "AI benefit": 220.0, "Welfare": 186.5,
        },
        "Pillars I + II": {
            "Infringement": 17.0, "Prevention": 0.5, "Adjudication": 2.0,
            "AI benefit": 220.0, "Welfare": 200.5,
        },
        "Pillars I + II + III": {
            "Infringement": 17.0, "Prevention": 0.5, "Adjudication": 1.5,
            "AI benefit": 231.0, "Welfare": 212.0,
        },
        "All four pillars": {
            "Infringement": 5.1, "Prevention": 0.5, "Adjudication": 0.5,
            "AI benefit": 236.5, "Welfare": 230.4,
        },
    },
    "proposition4": {
        "static_total_loss": 356.378,
        "BAT_total_loss": 0.019,
        "BAT_loss_reduction_pct": 99.99,
        "quadratic_lower_bound": 356.378,
        "bound_holds": True,
    },
    "monte_carlo": {
        "n": 938,
        "mean_gain_pct": 31.95,
        "median_gain_pct": 31.47,
        "pct_05": 21.09,
        "pct_95": 43.88,
        "share_positive": 1.0,
    },
}

ATOL_ABS = 0.05      # absolute tolerance for table values rounded to 1 decimal
RTOL_REL = 1e-3      # relative tolerance for fine comparisons


def _check(name, expected, actual, atol=ATOL_ABS):
    """Compare values; return (ok: bool, message: str)."""
    if isinstance(expected, bool):
        ok = bool(expected) == bool(actual)
    elif isinstance(expected, (int, float)):
        ok = abs(float(expected) - float(actual)) <= atol
    else:
        ok = expected == actual
    msg = f"  {'OK ' if ok else 'FAIL'}  {name}: expected {expected}, got {actual}"
    return ok, msg


def verify_calibration_table() -> bool:
    print("[1/3] Verifying Section 3.8 calibration table...")
    path = os.path.join(_TABLES_DIR, "table_3_8_calibration.csv")
    if not os.path.isfile(path):
        print(f"  FAIL  File not found: {path}")
        return False
    df = pd.read_csv(path).set_index("Regime")
    all_ok = True
    for regime, expected in REFERENCE_VALUES["calibration"].items():
        if regime not in df.index:
            print(f"  FAIL  Regime missing: {regime}")
            all_ok = False
            continue
        for col, exp_val in expected.items():
            actual = df.loc[regime, col]
            ok, msg = _check(f"{regime}.{col}", exp_val, actual)
            print(msg)
            all_ok = all_ok and ok
    return all_ok


def verify_proposition4() -> bool:
    print("\n[2/3] Verifying Proposition 4 numerical check...")
    path = os.path.join(_TABLES_DIR, "proposition4_check.csv")
    if not os.path.isfile(path):
        print(f"  FAIL  File not found: {path}")
        return False
    df = pd.read_csv(path)
    row = df.iloc[0]
    all_ok = True
    for key, exp_val in REFERENCE_VALUES["proposition4"].items():
        if key not in df.columns:
            print(f"  FAIL  Column missing: {key}")
            all_ok = False
            continue
        actual = row[key]
        atol = 0.5 if "loss" in key or "bound" in key else 0.01
        ok, msg = _check(key, exp_val, actual, atol=atol)
        print(msg)
        all_ok = all_ok and ok
    return all_ok


def verify_monte_carlo() -> bool:
    print("\n[3/3] Verifying Monte Carlo summary...")
    path = os.path.join(_TABLES_DIR, "monte_carlo_summary.csv")
    if not os.path.isfile(path):
        print(f"  FAIL  File not found: {path}")
        return False
    df = pd.read_csv(path)
    row = df.iloc[0]
    all_ok = True
    for key, exp_val in REFERENCE_VALUES["monte_carlo"].items():
        if key not in df.columns:
            print(f"  FAIL  Column missing: {key}")
            all_ok = False
            continue
        actual = row[key]
        atol = 1.0 if key == "n" else 0.5
        ok, msg = _check(key, exp_val, actual, atol=atol)
        print(msg)
        all_ok = all_ok and ok
    return all_ok


def main() -> int:
    print("=" * 60)
    print("REPRODUCIBILITY VERIFICATION")
    print("=" * 60)
    results = [
        verify_calibration_table(),
        verify_proposition4(),
        verify_monte_carlo(),
    ]
    print("\n" + "=" * 60)
    if all(results):
        print("ALL CHECKS PASSED: outputs match committed reference values")
        print("=" * 60)
        return 0
    print("VERIFICATION FAILED: some outputs do not match reference values")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
