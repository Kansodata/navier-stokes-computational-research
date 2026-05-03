# Convergence Study Harness

## Objective

Provide a reproducible, low-ambiguity baseline harness to compare final diagnostics across multiple grid resolutions for the same 2D incompressible periodic-domain scenario.

## Assumptions

- 2D periodic incompressible setting only.
- Same viscosity and random seed across resolutions.
- Smooth deterministic vortex-pair initial condition across resolutions.
- Same target physical horizon is approximated by scaling `dt` with resolution and recomputing steps.
- This harness is an engineering comparison tool, not a formal proof framework.

## What is compared

For each resolution run:

- final kinetic energy,
- final enstrophy,
- final max velocity,
- maximum CFL during the run,
- validation status from existing validation layer.
- automatic quality interpretation from heuristic thresholds.

For consecutive resolutions:

- relative difference in final energy,
- relative difference in final enstrophy,
- relative difference in final max velocity.

## What cannot be concluded

- No theorem-level convergence claim.
- No formal order-of-accuracy estimate in this baseline.
- No guarantee of physical correctness outside this controlled setup.

## Minimum acceptance criteria

- `convergence_summary.json` is created.
- `convergence_metrics.csv` is created.
- At least one comparative PNG plot is created.
- `report.html` is created for local static review.
- `convergence_quality.json` is created for machine-readable interpretation.
- Every run includes validation status.
- No NaN/Inf is silently accepted.

## Hardening notes

- Output path is configurable and grouped under a single study directory.
- Failures in individual runs raise clear exceptions and stop the harness.
- Relative differences use `max(abs(reference), 1e-12)` to avoid division-by-zero instability.
- Static HTML report generation must not require network access.
- Normal mode runs `32x32` and `64x64`.
- Extended mode adds `128x128` via `--convergence-extended`.

## Interpretation of relative differences

Relative differences compare final metrics between consecutive resolutions. Smaller values are consistency signals, but they do not prove formal convergence. A large final-energy difference should trigger review of initial-condition comparability, timestep scaling, and whether a separate time-refinement study is needed.

The current interpretation thresholds are documented in `docs/quality_interpretation.md` and should be treated as review heuristics.

## Next steps for more rigorous studies

1. Add three or more resolutions with consistent refinement ratios.
2. Include time-refinement studies independent from spatial refinement.
3. Add integral error norms against a trusted reference trajectory.
4. Define explicit acceptance thresholds grounded in numerical-analysis targets.
