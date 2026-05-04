# Validation Protocol for Baseline Repository

## What is validated

The current validation layer checks:

- kinetic energy trend ratio,
- enstrophy trend ratio,
- max velocity growth signal,
- NaN/Inf detection in emitted metrics,
- CFL margin against configured limit,
- diffusion stability margin against configured limit.
- finite error comparison against the analytical 2D Taylor-Green vortex for the controlled canonical setup.

It also supports an incompressibility residual field in the report when available.

## What is not validated

This protocol does not establish:

- physical correctness for real-world turbulence,
- convergence-order guarantees,
- boundary-condition generality beyond periodic domains,
- or any theorem-level result.
- The Taylor-Green check is only a controlled 2D validation target and does not establish global 3D existence/smoothness.

## Taylor-Green 2D controlled validation

The command:

- `python -m navier_stokes_research.cli --taylor-green-validation`

runs a periodic-domain test on `[0, 2π] x [0, 2π]` and writes:

- `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json`

Report content includes:

- resolved configuration,
- domain and resolution,
- viscosity and final physical time,
- `L2` and `L∞` errors,
- relative error when the reference norm is safely non-zero,
- backward-compatible `status` (`passed`/`failed`),
- `execution_status` (`passed`/`failed`) for runtime integrity,
- `accuracy_status` (`passed`/`failed`/`warning`/`not_evaluated`) for precision interpretation,
- `warnings` list for explicit audit signals,
- and technical notes.

Taylor-Green convergence mode also writes reproducible diagnostic PNGs by resolution:

- `L2` error,
- `L∞` error,
- relative `L2` error,
- optional combined log-scale plot.

These figures include an explicit `ROUND_OFF_ERROR_FLOOR` reference. If curves saturate near this floor, interpretation should be "roundoff-limited regime" rather than standalone formal convergence proof.

For critical review of interpretation limits and false-positive risks, see:

- `docs/advocatus_diaboli_taylor_green.md`

## Numerical stability checks

The solver enforces:

- fail-fast CFL threshold checks,
- fail-fast diffusion threshold checks,
- fail-fast NaN/Inf checks in numerical state updates.

Validation additionally summarizes these checks in JSON for downstream audit pipelines.

## Spectral de-aliasing / Orszag 2/3 rule

The pseudo-spectral solver applies an explicit Orszag 2/3 mask to the nonlinear convective term in Fourier space.

- Default behavior: de-aliasing enabled (`physics.dealiasing_enabled=true`).
- Controlled comparison mode: de-aliasing can be disabled (`physics.dealiasing_enabled=false`).
- Scope in this baseline: masking is applied to the nonlinear term only; no 3/2 padding is used in this iteration.

Why this is used:

- reduce aliasing contamination from nonlinear mode interactions,
- improve numerical robustness of spectral transfer diagnostics,
- preserve a reversible control path for A/B comparison.

Limits:

- this is a numerical-stability control, not a proof of full nonlinear generalization,
- it does not establish 3D global regularity or solve the Millennium problem.

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

## Convergence study protocol

The convergence harness runs a fixed seeded scenario over multiple resolutions and writes:

- `convergence_summary.json`
- `convergence_metrics.csv`
- `convergence_comparison.png`

Protocol constraints:

- same viscosity and seed across runs,
- smooth deterministic vortex-pair initial condition across resolutions,
- target physical horizon approximated with resolution-scaled `dt`,
- post-run validation required for each resolution,
- relative differences computed between consecutive resolutions.

Interpretation limits:

- these comparisons provide reproducibility and consistency signals,
- they do not constitute formal convergence proof or mathematical guarantees.
