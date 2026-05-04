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

## Spectral evidence
The harness also writes optional spectral evidence for the final velocity field:

- `outputs/benchmarks/physical_decay_2d/spectral_diagnostics.json`

The main `physical_decay_validation.json` includes a `spectral_evidence` section with:

- `total_spectral_energy`
- `high_wavenumber_energy_fraction`
- `max_resolved_wavenumber`
- `nyquist_wavenumber_estimate`
- `interpretation = diagnostic_only_not_hard_gate`

This spectral evidence is diagnostic only. It is not currently a hard validation gate, and `physical_decay_status` does not depend on the high-wavenumber fraction.

## What it does not validate
- It does not prove general turbulence validity.
- It does not establish formal convergence proofs.
- It does not imply 3D global existence/smoothness.
- It does not solve the Navier-Stokes Millennium problem.
- It does not use spectral evidence as a standalone proof of resolution adequacy.

## Acceptance criteria
- `runtime_execution` reflects execution and baseline validation status.
- `physical_decay_status` is `passed` only if all physical checks pass.
- `scientific_acceptance` remains `human_review_required`.
- `spectral_evidence.status` is `available` when final spectral diagnostics are generated.

## Scientific interpretation
Passing this harness means the controlled 2D unforced viscous case is numerically and physically consistent under the implemented checks. Spectral evidence adds visibility into the final velocity-field energy distribution, but remains diagnostic evidence only.

## Explicit limits
The harness is constrained to one controlled 2D setup and does not justify broad claims of generalization beyond its tested regime.
