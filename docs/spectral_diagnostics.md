# Spectral Diagnostics (2D Velocity Energy)

## Purpose
Provide a pure, deterministic numerical-evidence layer to inspect how kinetic energy is distributed across spectral scales for 2D velocity fields.

## What it validates
- Parseval-consistent total spectral energy for `(u, v)`.
- Non-negative modal and radial-shell energy aggregation.
- High-wavenumber energy fraction as a compact indicator of energy concentration near the resolved limit.

## What it does not validate
- It does not prove formal convergence.
- It does not validate general turbulence physics by itself.
- It does not replace controlled benchmark validations.
- It does not imply 3D existence/smoothness claims.
- It does not solve the Millennium problem.

## High-wavenumber energy fraction interpretation
`high_wavenumber_energy_fraction` measures the fraction of radial-shell energy for
`k >= cutoff_fraction * max(k)` (default `cutoff_fraction = 2/3`).

- Low values suggest most energy is in larger scales.
- Elevated values can indicate stronger small-scale content and potential resolution stress.
- Interpretation must be combined with runtime stability, physical diagnostics, and configuration context.

## Relation to de-aliasing and resolution
- De-aliasing controls nonlinear alias contamination but does not guarantee physically correct spectra.
- Resolution defines the maximum resolved wavenumber and constrains interpretability of high-`k` content.
- This module reports evidence; it does not impose runtime hard-gates in this iteration.

## Scientific limits
This is a 2D diagnostic tool for numerical evidence. It is not a formal proof, not a complete turbulence validator, and not a 3D Navier-Stokes claim.
