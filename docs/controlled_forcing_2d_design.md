# Controlled 2D Forcing V&V Design

## Purpose

This document defines the design and validation requirements for a future controlled forcing module for the 2D incompressible periodic pseudo-spectral solver.

The goal is to support auditable stationary-turbulence-style experiments in a bounded 2D setting without expanding the scientific scope beyond the current repository baseline.

This document is a design gate. It does not implement forcing, does not modify the solver, and does not claim validated turbulent physics.

## Scientific Scope

Allowed scope:

- 2D incompressible Navier-Stokes on periodic domains.
- Vorticity-streamfunction formulation.
- Pseudo-spectral Fourier discretization.
- Controlled, reproducible forcing experiments.
- Diagnostic spectral and energetic evidence.

Out of scope:

- 3D Navier-Stokes.
- Millennium Problem claims.
- Theorem-level mathematical proof.
- General turbulence validity.
- Physical claims without explicit validation artifacts.

## Proposed Forcing Model

### Fourier narrow-band energy injection

Forcing should be defined in Fourier space over a configurable annular band:

- `k_min`
- `k_max`

The active forcing mask should include modes satisfying:

```text
k_min <= sqrt(kx^2 + ky^2) <= k_max
```

Required constraints:

- exclude the zero mode;
- preserve real-valued physical vorticity through Hermitian-compatible forcing;
- apply de-aliasing consistently with the solver nonlinear treatment;
- persist the resolved forcing mask metadata in validation artifacts;
- fail closed if the forcing band is empty.

### Stochastic process

The forcing amplitude should evolve through a seeded stochastic process. Preferred initial process:

- Ornstein-Uhlenbeck process in Fourier space.

Required metadata:

- seed;
- correlation time;
- noise amplitude;
- forcing band;
- normalization convention;
- update cadence;
- generated energy-injection diagnostics.

Required fail-closed checks:

- non-finite forcing coefficients;
- non-finite physical forcing field;
- empty active mode set;
- invalid OU parameters;
- unsupported non-deterministic seed behavior.

## Large-Scale Energy Control

Forced 2D turbulence can accumulate energy at large scales through inverse cascade behavior. The implementation must therefore include a controlled large-scale energy sink.

Preferred first mechanism:

```text
- alpha * omega
```

where `alpha` is an Ekman drag coefficient applied to vorticity.

Design constraints:

- `alpha >= 0`;
- default `alpha = 0` to preserve current unforced behavior;
- forced validation presets must require `alpha > 0` unless a test explicitly validates fail-closed behavior;
- drag contribution must be separately reported in the energy/enstrophy budget;
- no silent activation of drag in existing validation commands.

Optional future mechanism:

- hypoviscosity at low wavenumbers.

Hypoviscosity should not be implemented before Ekman drag has a complete V&V path.

## Proposed Solver Integration

The RHS should remain auditable as separated terms:

```text
rhs = nonlinear + viscous_diffusion + forcing - ekman_drag
```

The implementation should expose term-level diagnostics rather than only the combined RHS.

Required internal boundaries:

- forcing configuration belongs in a dedicated config dataclass, not as loose parameters;
- stochastic state belongs in a dedicated forcing component, not directly inside the solver core unless unavoidable;
- solver defaults must reproduce current unforced behavior exactly;
- forcing must be opt-in only.

## Energy Budget Validation

A forced statistically stationary run must generate a machine-readable energy-budget artifact.

Required quantities:

- energy injection rate estimate: `epsilon_in`;
- viscous dissipation estimate: `epsilon_viscous`;
- Ekman/drag dissipation estimate: `epsilon_drag`;
- total dissipation estimate: `epsilon_diss = epsilon_viscous + epsilon_drag`;
- balance residual: `abs(epsilon_in - epsilon_diss)`;
- normalized balance residual;
- averaging window;
- transient window excluded from statistics;
- runtime execution status;
- budget accuracy/diagnostic status.

Acceptance semantics:

- `execution_status`: whether the run completed without runtime/numerical failure;
- `budget_status`: whether budget diagnostics are internally consistent;
- `scientific_acceptance`: must remain `human_review_required`;
- broad physical interpretation is not automatic, even when the budget residual is small.

## Spectral Validation

The validation harness should generate energy spectra and slope diagnostics.

Target diagnostic ranges:

- inverse-energy-cascade range: expected reference slope near `k^-5/3` when a valid inertial range exists;
- direct-enstrophy-cascade range: expected reference slope near `k^-3` when a valid inertial range exists.

Important caution:

The harness must not claim these slopes are achieved unless:

- an inertial range is explicitly identified;
- enough resolved modes exist in the fitted range;
- fit uncertainty is reported;
- forcing and dissipation ranges are excluded from the slope fit;
- the result passes adversarial review.

Required spectral artifact fields:

- binned wavenumber centers;
- energy spectrum values;
- fit ranges;
- fitted slopes;
- fit residuals or confidence proxy;
- warnings for insufficient inertial range;
- de-aliasing and resolution metadata.

## Fail-Closed Rules

The future implementation must abort or mark validation as failed when any of the following occurs:

- CFL violation;
- diffusion stability violation;
- non-finite vorticity, velocity, RHS, forcing, or diagnostics;
- empty forcing band;
- invalid stochastic process parameters;
- missing validation artifact;
- malformed validation JSON;
- missing required budget fields;
- slope fit attempted with insufficient resolved modes;
- unresolved contradiction between energy budget and spectral diagnostics.

## Minimum Implementation Phases

### Phase 1: Configuration and deterministic no-op compatibility

- Add forcing config with disabled defaults.
- Validate that all existing tests and validation commands remain unchanged.
- Confirm unforced output parity within current tolerances.

### Phase 2: Ekman drag only

- Add opt-in Ekman drag.
- Add unit tests for sign, finite behavior, and disabled default behavior.
- Add energy/enstrophy diagnostic hooks.

### Phase 3: Narrow-band deterministic forcing

- Add deterministic seeded Fourier-band forcing without OU time evolution.
- Validate active mask construction and Hermitian/real-field behavior.

### Phase 4: Ornstein-Uhlenbeck forcing

- Add OU stochastic state with fixed seed reproducibility.
- Validate repeatability and fail-closed parameter checks.

### Phase 5: Forced validation harness

- Add CLI command for controlled forced 2D validation.
- Generate budget and spectral JSON artifacts.
- Keep `scientific_acceptance = human_review_required`.

## Required Review Agents

Before accepting implementation PRs, run the multi-agent scientific review pipeline:

- `kansodata-numerical-methods-auditor`;
- `kansodata-physical-validator`;
- `kansodata-scientific-literature-auditor`;
- `kansodata-advocatus-diaboli`;
- `kansodata-chief-scientific-reviewer`.

Any claim about stationary turbulence, cascade slopes, or energy balance must be traceable to generated artifacts and specialist review output.

## Rollback Strategy

For any future implementation phase:

```bash
git revert <phase_commit_sha>
```

Each phase should be isolated in a small PR so rollback does not affect validated unforced solver behavior.

## Decision

Implementation is not approved by this design document alone.

This document approves only a staged, evidence-first implementation path with fail-closed validation gates and conservative scientific claims.
