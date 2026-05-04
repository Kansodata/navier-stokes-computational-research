# Scientific Validation Summary

## Scope

This document summarizes the current scientific and computational validation status of the `navier-stokes-computational-research` repository.

The project is a reproducible computational research baseline for deterministic 2D incompressible Navier-Stokes simulations on periodic domains. It does not claim to solve the 3D Navier-Stokes Millennium Prize problem and does not provide theorem-level mathematical proof.

## Current validated capabilities

### 1. Pseudo-spectral 2D solver

The repository implements a pseudo-spectral vorticity-streamfunction solver for 2D incompressible Navier-Stokes experiments on periodic domains.

The streamfunction convention was corrected so that the velocity reconstruction is consistent with the Taylor-Green analytical validation case.

Current convention:

```text
u =  ∂ψ/∂y
v = -∂ψ/∂x
Δψ = -ω
```

This correction removed the previous sign inversion detected by Taylor-Green validation.

### 2. Runtime benchmark validation

The reproducible benchmark verifies that the simulation pipeline runs end-to-end, generates metrics, applies stability checks, and writes validation artifacts.

The benchmark validates practical runtime properties:

- finite metrics;
- CFL margin;
- diffusion margin;
- kinetic energy trend;
- enstrophy trend;
- report generation.

This is a runtime and stability validation, not a mathematical proof.

### 3. Baseline convergence study

The baseline convergence harness compares final diagnostic metrics across grid refinements.

Default mode:

```text
32x32
64x64
```

Extended mode:

```text
32x32
64x64
128x128
256x256
512x512
```

This study uses a deterministic vortex-pair initial condition. It provides heuristic evidence of consistency across refinements, but it does not use an exact analytical reference solution.

Therefore, its status is intentionally separated into:

```text
runtime_execution
heuristic_consistency
scientific_acceptance
```

The self-convergence orders reported for this study are diagnostic only.

### 4. Taylor-Green analytical validation

The Taylor-Green validation compares the numerical velocity field against the controlled 2D analytical Taylor-Green solution.

The validation computes:

```text
L2 error
L∞ error
relative L2 error
```

The multi-resolution Taylor-Green validation currently runs:

```text
32x32
64x64
128x128
256x256
```

The result reached machine-precision-level error under the configured tolerances, so the report uses:

```text
formal_error_convergence = passed_roundoff_floor
```

This means the controlled 2D analytical case matched the exact solution up to numerical roundoff precision. It also means convergence-order estimation is intentionally suppressed because the remaining error is dominated by floating-point noise rather than discretization error.

## Why Taylor-Green stops at 256x256

The general convergence study reaches `512x512` because it is a heuristic baseline consistency experiment using a vortex-pair initial condition.

Taylor-Green convergence currently stops at `256x256` because the analytical validation already reaches roundoff-level error at lower resolutions. Running `512x512` would be computationally more expensive but would not add meaningful scientific evidence for this specific case, because the measurable error is already dominated by floating-point precision.

In short:

```text
512x512 is useful for the heuristic vortex baseline.
256x256 is sufficient for the current Taylor-Green analytical verification.
```

A future Taylor-Green `512x512` run may still be added as an optional stress check, but it should not be required for the default analytical validation path.

## Scientific interpretation

The current project supports the following claim:

> The repository provides a reproducible and tested computational baseline for controlled 2D incompressible Navier-Stokes simulations, including benchmark validation, heuristic convergence diagnostics, and Taylor-Green analytical verification to roundoff precision.

The current project does not support the following claim:

> The repository solves or proves the 3D Navier-Stokes existence and smoothness problem.

## Benefits

### Computational benefits

- Reproducible command-line experiments.
- Deterministic benchmark and convergence harnesses.
- Machine-readable JSON and CSV artifacts.
- Local static reports for inspection.
- Automated tests for solver behavior, validation, reporting, and Taylor-Green verification.

### Scientific benefits

- Clear distinction between runtime success and scientific acceptance.
- Analytical verification against a known 2D solution.
- Detection and correction of a sign-convention error.
- Explicit prevention of misleading convergence-order estimates at roundoff floor.
- Conservative scientific language that avoids unsupported claims.

### Engineering benefits

- Modular solver, validation, reporting, and CLI structure.
- Fail-fast checks for numerical instability.
- Clear artifact paths for reproducibility.
- Git-tracked scientific milestones through pull requests.

## Current limitations

- 2D periodic domain only.
- No 3D solver.
- No non-periodic boundary conditions.
- No forcing model in the baseline.
- Single explicit time integration scheme.
- Baseline convergence study is heuristic.
- Taylor-Green validation is controlled and analytical, but still limited to 2D.

## Recommended next steps

### Step 1: Add Taylor-Green visual diagnostics

Add plots for:

- L2 error by resolution;
- L∞ error by resolution;
- relative error by resolution;
- optional log-scale error plot.

Because the current error is near roundoff, the plots should explicitly show the roundoff floor.

### Step 2: Add a measurable-error verification case

Taylor-Green currently reaches machine precision, which is excellent for correctness but not ideal for estimating convergence rates.

A future case should intentionally produce measurable discretization error. Candidate approaches:

- longer final physical time;
- modified viscosity;
- coarser grid sequence;
- manufactured solution;
- high-resolution reference solution.

### Step 3: Separate spatial and temporal convergence

The current studies scale `dt` with grid resolution. Future validation should separate:

```text
spatial convergence
temporal convergence
coupled space-time convergence
```

This will clarify whether observed error comes mainly from grid spacing, time integration, or both.

### Step 4: Add CI validation

Add a GitHub Actions workflow that runs:

```bash
pytest
```

Optionally include a lightweight Taylor-Green smoke validation.

### Step 5: Prepare a technical paper draft

Create a first technical manuscript draft describing:

- method;
- solver convention;
- validation protocol;
- Taylor-Green verification;
- convergence-study limitations;
- reproducibility artifacts;
- future research roadmap.

Suggested title:

```text
A reproducible computational baseline for 2D incompressible Navier-Stokes validation using Taylor-Green vortices
```

## Final status

The project has reached a solid first research milestone:

```text
Solver corrected.
Taylor-Green analytical validation implemented.
Roundoff-floor handling implemented.
Runtime, heuristic, and scientific statuses separated.
Documentation aligned with current behavior.
No unsupported 3D mathematical claims.
```
