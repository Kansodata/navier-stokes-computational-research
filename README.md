# 2D Incompressible Navier-Stokes Research Repository

## Scientific disclaimer

This repository is a computational research baseline for deterministic 2D incompressible Navier-Stokes simulations on periodic domains. It does not solve the 3D Navier-Stokes Millennium problem and does not provide theorem-level mathematical claims.

## Problem context

The implementation uses a pseudo-spectral vorticity-streamfunction method with explicit time stepping to support controlled numerical experiments, software validation, and reproducible benchmarking.

## What this repository does

- Runs deterministic 2D incompressible periodic-domain simulations.
- Computes diagnostic metrics: kinetic energy, enstrophy, max velocity, CFL.
- Applies hardening checks (CFL, diffusion, NaN/Inf fail-fast).
- Produces machine-readable validation JSON.
- Provides a reproducible benchmark command and artifact set.
- Provides a reproducible convergence study harness.
- Produces local static HTML reports in Spanish by default.
- Writes automatic quality interpretation JSON files for benchmark and convergence runs.

## What this repository does not do

- It does not claim physical truth for general turbulence regimes.
- It does not establish convergence proofs or theoretical guarantees.
- It does not cover non-periodic boundaries in this baseline.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Run tests

```bash
pytest
```

## Run baseline simulation

```bash
python -m navier_stokes_research.cli --config configs/baseline_random.json
```

With explicit validation report:

```bash
python -m navier_stokes_research.cli --config configs/baseline_random.json --validate
```

Output location can be overridden:

```bash
python -m navier_stokes_research.cli --config configs/baseline_random.json --steps 100 --dt 0.0015 --output-dir outputs/quick_run
```

## Run reproducible benchmark

```bash
python -m navier_stokes_research.cli --benchmark
```

Optional benchmark output root:

```bash
python -m navier_stokes_research.cli --benchmark --benchmark-output-dir outputs/benchmarks
```

The benchmark run also generates a local static report:

- `outputs/benchmarks/baseline_2d_incompressible/report.html`
- `outputs/benchmarks/baseline_2d_incompressible/benchmark_quality.json`

## Run convergence study

```bash
python -m navier_stokes_research.cli --convergence-study
```

Optional extended mode adds `128x128` to the default `32x32`, `64x64` study:

```bash
python -m navier_stokes_research.cli --convergence-study --convergence-extended
```

Optional output root:

```bash
python -m navier_stokes_research.cli --convergence-study --convergence-output-dir outputs/convergence
```

Default study artifacts are written under:

- `outputs/convergence/baseline_resolution_study/convergence_summary.json`
- `outputs/convergence/baseline_resolution_study/convergence_metrics.csv`
- `outputs/convergence/baseline_resolution_study/convergence_comparison.png`
- `outputs/convergence/baseline_resolution_study/report.html`
- `outputs/convergence/baseline_resolution_study/convergence_quality.json`

## Run Taylor-Green 2D validation

```bash
python -m navier_stokes_research.cli --taylor-green-validation
```

This command writes:

- `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json`

The report includes resolved configuration, domain, resolution, viscosity, final physical time, and finite error metrics (`L2`, `L∞`, and relative error when numerically meaningful).

## Local static visual reports

Reports are local static HTML files with embedded CSS and no external dependencies. They are generated in Spanish by default and can be opened directly from the filesystem:

- `outputs/benchmarks/baseline_2d_incompressible/report.html`
- `outputs/convergence/baseline_resolution_study/report.html`

They are intended for reproducible visual inspection, not formal scientific proof.

The optional local index is written to:

- `outputs/reports/index.html`

## How to interpret metrics

- `energy`: discrete kinetic energy proxy over grid cells.
- `enstrophy`: discrete vorticity-square proxy over grid cells.
- `max_velocity`: maximum speed magnitude over the grid.
- `cfl`: CFL number computed from max speed, timestep, and grid spacing.

Validation report (`validation_report.json`) includes trend ratios and stability margins:

- `kinetic_energy_trend.ratio`
- `enstrophy_trend.ratio`
- `cfl_margin.margin_min`
- `diffusion_margin.margin`

`status=pass` indicates all configured checks passed for the recorded run.

For convergence outputs:

- `relative_differences_consecutive` reports relative deltas of final metrics between adjacent resolutions.
- Lower relative differences are a consistency signal across refinements.
- This does not prove formal numerical convergence by itself.
- Automatic quality status uses heuristic thresholds documented in `docs/quality_interpretation.md`.

## Reproducibility guarantees

- Seed-controlled random initial condition generation.
- Fixed benchmark parameters in code.
- Fixed convergence-study default parameters in code (`32x32`, `64x64`) and fixed seed.
- Convergence study uses a smooth deterministic vortex-pair initial condition for better comparability across resolutions.
- Persisted `resolved_config.json` per run.
- Deterministic benchmark artifact path under `outputs/benchmarks/`.

## Repository layout

- `src/navier_stokes_research/solver/`: pseudo-spectral solver and numerical utilities.
- `src/navier_stokes_research/initial_conditions/`: random and vortex initial states.
- `src/navier_stokes_research/metrics/`: core diagnostics.
- `src/navier_stokes_research/validation/`: validation checks and JSON reporting.
- `src/navier_stokes_research/benchmark.py`: reproducible benchmark configuration and run.
- `src/navier_stokes_research/convergence.py`: reproducible convergence-study harness.
- `src/navier_stokes_research/interpretation.py`: heuristic quality interpretation.
- `src/navier_stokes_research/runner.py`: simulation orchestration.
- `src/navier_stokes_research/cli.py`: terminal entrypoint.
- `tests/`: deterministic unit tests for numerics, validation, and benchmark.
- `docs/`: research notes and validation protocol.

## Current limitations

- 2D periodic domain only.
- Single explicit time integration scheme.
- No forcing model in baseline.
- Validation layer is practical quality control, not formal verification.
- Convergence harness is a baseline consistency study, not a formal convergence proof.
- Quality thresholds are heuristic review aids, not mathematical criteria.
- Taylor-Green validation is a controlled 2D case and does not prove global existence/smoothness for 3D Navier-Stokes.

## Future research roadmap

1. Extend convergence study with more refinement levels and independent time refinement.
2. Controlled forcing scenarios with documented parameter sweeps.
3. Extended diagnostics and uncertainty quantification.
4. Optional alternative discretizations behind stable interfaces.

See [docs/research_notes.md](docs/research_notes.md), [docs/validation_protocol.md](docs/validation_protocol.md), [docs/convergence_study.md](docs/convergence_study.md), [docs/reports.md](docs/reports.md), and [docs/quality_interpretation.md](docs/quality_interpretation.md).
