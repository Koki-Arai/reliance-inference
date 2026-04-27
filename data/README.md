# Calibration Data Sources

This replication package does **not** rely on any external data files.
All analyses are based on calibrated parameter values whose magnitudes are
anchored to the empirical literature, principally Kim, Jin, and Lee (2026).

The `code/model.py::Params` class encodes the default calibration as
documented in Section 3.8 of the manuscript:

| Parameter   | Value | Source / Justification                                   |
|-------------|-------|----------------------------------------------------------|
| `pi_theta`  | 0.4   | Kim, Jin, and Lee (2026): median IP-level invasion intensity in heavily affected segments (Genshin Impact, Original works) |
| `pi_a`      | 0.1   | Inference from low AI-adoption rates among incumbent creators (<0.5%) reported in Kim, Jin, and Lee (2026) |
| `q1`        | 0.9   | Stylized: high reproduction probability under intentional prompting |
| `q2_0`      | 0.4   | Stylized: moderate incidental similarity at zero filtering effort |
| `q0`        | 0.1   | Stylized: low coincidental similarity baseline                |
| `H`         | 100   | Normalized: per-infringement social loss                       |
| `c(e*)`     | 20    | Stylized: prevention cost at the safe-harbor threshold         |
| `alpha_I`   | 10    | Stylized: Type I error weight                                  |
| `alpha_II`  | 10    | Stylized: Type II error weight                                 |
| `B0`        | 200   | Stylized: baseline AI deployment benefit                       |
| `B_slope`   | 50    | Stylized: marginal benefit of pi_theta on aggregate B          |
| `e_star`    | 0.6   | Stylized: statutory safe-harbor threshold                       |

The Monte Carlo analysis in Appendix E.4 places the following priors on the
six identifying parameters:

- `pi_theta` ~ Beta(2, 3), with mean 0.4 (anchored to Kim, Jin, and Lee 2026)
- `pi_a` ~ Beta(1, 9), with mean 0.1
- `q0` ~ Beta(1, 9)
- `q2_0` ~ Beta(2, 3)
- `H` ~ Uniform(50, 150)
- `c(e*)` ~ Uniform(10, 40)

Draws violating Assumption 1 (q₁ > q₂(0) > q₀ > 0) are rejected.

## Reference

Kim, S., Jin, G. Z., & Lee, E. (2026). *Does Generative AI Crowd Out Human
Creators? Evidence from Pixiv*. NBER Working Paper No. 34733. Cambridge, MA:
National Bureau of Economic Research.
