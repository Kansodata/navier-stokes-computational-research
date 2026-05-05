# Literature Review (2D Incompressible Periodic Scope)

## Scope and intent

This note summarizes the minimum scientific basis used by the repository for reproducible 2D incompressible Navier-Stokes validation on periodic domains. It does not claim 3D Navier-Stokes resolution and does not claim any Millennium Prize result.

## Core numerical method references

The project uses a Fourier pseudo-spectral vorticity-streamfunction formulation in a periodic domain. Standard references for this class of methods include Canuto et al. and Peyret, which provide established formulations for spectral differentiation, incompressible flow treatment, and practical implementation considerations.

For aliasing control in nonlinear terms, Orszag's 1971 references motivate explicit high-wavenumber filtering and the practical 2/3 de-aliasing strategy in pseudo-spectral workflows.

## Analytical validation reference

Taylor and Green (1937) provides a canonical analytical flow construction used in controlled verification scenarios. In this repository, Taylor-Green is used as a bounded 2D analytical check to verify implementation consistency and numerical behavior under deterministic settings.

The convergence harness interpretation is conservative: when errors reach machine-precision scale, `passed_roundoff_floor` indicates roundoff-limited behavior rather than a general proof of convergence.

## Physical diagnostics context

The repository tracks kinetic energy, enstrophy, and spectral-energy indicators for reproducible diagnostics in 2D viscous unforced runs. Classical 2D turbulence theory (e.g., Kraichnan) provides context for energy/enstrophy behavior, but current project thresholds remain engineering diagnostics and should not be interpreted as universal physical validation.

## Verification and validation framing

The repository separates runtime execution outcomes from scientific-acceptance interpretation, consistent with conservative V&V practice. ASME V&V 20 is used as a methodological reference point for verification/validation discipline, while no formal standards compliance claim is made.

## Current evidence limits

- Evidence is strongest for deterministic numerical consistency in 2D periodic settings.
- Spectral and physical-decay diagnostics are informative but not standalone proof criteria.
- Claims outside 2D periodic incompressible scope are out of scope by design.
