# Automatic Quality Interpretation

## Purpose

The automatic quality interpretation layer turns validation and convergence artifacts into a short machine-readable and human-readable diagnosis. It is intended to guide review, not to establish mathematical proof.

## Status values

- `aprobado`: the baseline checks and expected artifacts are within current heuristic thresholds.
- `advertencia`: at least one signal deserves review, but the run is not automatically rejected.
- `requiere_revision`: one or more signals are strong enough that the result should be reviewed before being used as a reference artifact.

## Benchmark heuristics

- Energy trend ratio above `1.10` produces a warning.
- Enstrophy trend ratio above `1.10` produces a warning.
- CFL peak at or above `0.75 * cfl_limit` produces a warning.
- Missing critical benchmark artifacts produces `requiere_revision`.

## Convergence heuristics

- Relative final-energy difference `<= 0.25` is treated as acceptable.
- Relative final-energy difference `> 0.25` and `<= 0.75` produces a warning.
- Relative final-energy difference `> 0.75` produces `requiere_revision`.
- Relative final-enstrophy difference above `0.20` produces a warning.
- Relative final max-velocity difference above `0.10` produces a warning.
- CFL peak at or above `0.75 * cfl_limit` produces a warning.
- Only two resolutions produces a warning because it cannot estimate a reliable trend.

## Limitations

These thresholds are practical review heuristics. They are not formal acceptance criteria for numerical convergence, physical validity, or theorem-level claims.
