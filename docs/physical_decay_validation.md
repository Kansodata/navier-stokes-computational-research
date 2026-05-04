# Physical Decay Validation (2D Unforced Viscous Case)

## Purpose
Provide a controlled physical diagnostic for viscous dissipation behavior in a deterministic 2D periodic, unforced simulation.

## What it validates
- Finite metrics across the run (`energy`, `enstrophy`, `max_velocity`, `cfl`).
- Positive viscosity.
- Positive initial energy and enstrophy.
- Non-increasing final energy and enstrophy (with explicit small numerical tolerance).
- Positive CFL margin.
- Positive diffusion margin.

## What it does not validate
- It does not prove general turbulence validity.
- It does not establish formal convergence proofs.
- It does not imply 3D global existence/smoothness.
- It does not solve the Navier-Stokes Millennium problem.

## Acceptance criteria
- `runtime_execution` reflects execution and baseline validation status.
- `physical_decay_status` is `passed` only if all physical checks pass.
- `scientific_acceptance` remains `human_review_required`.

## Scientific interpretation
Passing this harness means the controlled 2D unforced viscous case is numerically and physically consistent under the implemented checks. It is diagnostic evidence only.

## Explicit limits
The harness is constrained to one controlled 2D setup and does not justify broad claims of generalization beyond its tested regime.
