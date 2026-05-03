# Validation Protocol for Baseline Repository

## What is validated

The current validation layer checks:

- kinetic energy trend ratio,
- enstrophy trend ratio,
- max velocity growth signal,
- NaN/Inf detection in emitted metrics,
- CFL margin against configured limit,
- diffusion stability margin against configured limit.

It also supports an incompressibility residual field in the report when available.

## What is not validated

This protocol does not establish:

- physical correctness for real-world turbulence,
- convergence-order guarantees,
- boundary-condition generality beyond periodic domains,
- or any theorem-level result.

## Numerical stability checks

The solver enforces:

- fail-fast CFL threshold checks,
- fail-fast diffusion threshold checks,
- fail-fast NaN/Inf checks in numerical state updates.

Validation additionally summarizes these checks in JSON for downstream audit pipelines.

## Reproducibility rules

- Use explicit seed in initial conditions.
- Use fixed grid, viscosity, timestep, and step count for benchmark runs.
- Persist resolved run configuration with output artifacts.
- Keep output directory explicit and versioned by experiment intent.

## Acceptance criteria for this baseline

For baseline acceptance:

- unit tests pass,
- benchmark run completes,
- validation status is generated with machine-readable report,
- and artifacts are reproducible for fixed benchmark parameters within numeric tolerances.
