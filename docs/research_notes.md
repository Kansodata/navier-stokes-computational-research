# Research Notes: 2D Incompressible Navier-Stokes Baseline

## Why start in 2D

This repository starts from a 2D incompressible periodic-domain formulation because it is a well-understood computational setting for:

- controlled numerical experiments,
- reproducible diagnostics,
- and software hardening before scaling complexity.

The goal is engineering quality and reproducible computation, not a broad mathematical claim.

## Why this is not the Millennium problem

The Clay Millennium Navier-Stokes problem concerns existence and smoothness in 3D incompressible flow. This repository simulates a 2D periodic setting with a specific numerical discretization and finite runtime horizon. It does not address the 3D theoretical problem and does not provide evidence toward proving or disproving it.

## How this baseline supports future exploration

This baseline provides:

- deterministic initial condition generation,
- explicit stability checks,
- machine-readable validation artifacts,
- and repeatable benchmark outputs.

These are prerequisites for credible follow-up studies such as forcing models, refined grids, or more demanding regimes.

## What is required before any mathematical claim

Before making any mathematical claim, the project would require at minimum:

- rigorous convergence and consistency studies across resolutions and timesteps,
- independent verification of implementation details,
- formal uncertainty quantification and sensitivity analyses,
- and peer-reviewed mathematical arguments outside simulation-only evidence.
