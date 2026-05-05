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
- Provides Taylor-Green 2D analytical validation and multi-resolution error diagnostics.
- Provides a controlled 2D stress validation harness.
- Produces local static HTML reports in Spanish by default.
- Writes automatic quality interpretation JSON files for benchmark and convergence runs.

## What this repository does not do

- It does not claim physical truth for general turbulence regimes.
- It does not establish convergence proofs or theoretical guarantees.
- It does not cover non-periodic boundaries in this baseline.
- It does not solve the 3D Navier-Stokes Millennium problem.

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

Default mode runs the `32x32`, `64x64` baseline study. Extended mode runs the larger refinement sequence `32x32`, `64x64`, `128x128`, `256x256`, and `512x512`:

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

The convergence report separates runtime execution, heuristic consistency, and scientific acceptance. Estimated self-convergence orders are diagnostic evidence only and are not formal proof.

## Run Taylor-Green 2D validation

```bash
python -m navier_stokes_research.cli --taylor-green-validation
```

This command writes:

- `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json`

The report includes resolved configuration, domain, resolution, viscosity, final physical time, finite error metrics (`L2`, `L∞`, and relative error when numerically meaningful), and explicit status separation (`execution_status` vs `accuracy_status`) with `warnings`.

Taylor-Green convergence artifacts also include deterministic diagnostic plots by resolution (`L2`, `L∞`, relative `L2`, and a combined log-scale view) with explicit `ROUND_OFF_ERROR_FLOOR` reference lines.

## Run Taylor-Green 2D convergence validation

```bash
python -m navier_stokes_research.cli --taylor-green-convergence
```

This command runs the controlled analytical Taylor-Green case across the default resolutions `32x32`, `64x64`, `128x128`, and `256x256`. It writes:

- `outputs/benchmarks/taylor_green_convergence_2d/taylor_green_convergence_summary.json`
- `outputs/benchmarks/taylor_green_convergence_2d/taylor_green_convergence_metrics.csv`
- `outputs/benchmarks/taylor_green_convergence_2d/n*/taylor_green_2d/taylor_green_validation.json`

This harness compares numerical velocity fields against the analytical 2D Taylor-Green velocity solution. When errors reach the configured roundoff floor, convergence-order estimates are intentionally omitted to avoid reporting numerical-noise artifacts. A `formal_error_convergence` value of `passed_roundoff_floor` means the controlled 2D analytical case matched to machine precision under the configured tolerances.

## Run physical decay validation

```bash
python -m navier_stokes_research.cli --physical-decay-validation
```

This command runs a controlled 2D unforced viscous decay diagnostic and writes:

- `outputs/benchmarks/physical_decay_2d/physical_decay_validation.json`
- `outputs/benchmarks/physical_decay_2d/spectral_diagnostics.json`

It is a numerical/physical diagnostic for this bounded 2D setup and is not a formal proof or a 3D Navier-Stokes result. Spectral evidence is diagnostic only and is not a hard validation gate.

## Run 2D stress validation

```bash
python -m navier_stokes_research.cli --stress-validation-2d
```

This command runs a controlled scenario matrix that attempts to stress the 2D solver without expanding scope to 3D. It writes:

- `outputs/benchmarks/stress_validation_2d/stress_validation_summary.json`

The harness records `passed`, `warning`, `failed`, and `expected_fail_closed` outcomes. Expected fail-closed CFL cases do not count as global failures when they fail for the configured expected reason. Spectral high-wavenumber evidence is diagnostic only and is not a hard gate.
External-reference 2D harness command: `python -m navier_stokes_research.cli --external-validation-2d`.
Time-refinement 2D harness command: `python -m navier_stokes_research.cli --time-refinement-2d` -> `outputs/benchmarks/time_refinement_2d/time_refinement_summary.json`.

## Spectral diagnostics

The repository includes a pure internal API for 2D velocity spectral-energy diagnostics:

- `navier_stokes_research.spectral_diagnostics.compute_velocity_energy_spectrum_2d`

This iteration does not add a CLI command for spectral diagnostics. The module is intended as numerical evidence support and not as a formal proof mechanism.

## Local static visual reports

Reports are local static HTML files with embedded CSS and no external dependencies. They are generated in Spanish by default and can be opened directly from the filesystem:

- `outputs/benchmarks/baseline_2d_incompressible/report.html`
- `outputs/convergence/baseline_resolution_study/report.html`

They are intended for reproducible visual inspection, not formal scientific proof.

The optional local index is written to:

- `outputs/reports/index.html`

## Scientific evidence and validation

- [docs/literature_review.md](docs/literature_review.md)
- [docs/validation_evidence_matrix.md](docs/validation_evidence_matrix.md)
- [docs/references.bib](docs/references.bib)

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
- Estimated self-convergence orders are diagnostic only and require scientific review.
- This does not prove formal numerical convergence by itself.
- Automatic quality status uses heuristic thresholds documented in `docs/quality_interpretation.md`.

For Taylor-Green convergence outputs:

- `l2_error`, `linf_error`, and `relative_error` compare against the analytical 2D Taylor-Green velocity solution.
- `accuracy_status=passed` means configured error tolerances were satisfied.
- `formal_error_convergence=passed_roundoff_floor` means the analytical case matched to machine precision and convergence-order estimation was suppressed because the remaining error is numerical roundoff noise.
- Taylor-Green validation remains a controlled 2D verification case, not a 3D existence/smoothness proof.

## Reproducibility guarantees

- Seed-controlled random initial condition generation.
- Fixed benchmark parameters in code.
- Fixed convergence-study default parameters in code (`32x32`, `64x64`) and fixed seed.
- Fixed extended convergence-study parameters in code (`32x32`, `64x64`, `128x128`, `256x256`, `512x512`).
- Fixed Taylor-Green convergence-study parameters in code (`32x32`, `64x64`, `128x128`, `256x256`).
- Fixed stress-validation scenario matrix in code.
- Convergence study uses a smooth deterministic vortex-pair initial condition for better comparability across resolutions.
- Taylor-Green convergence study uses a controlled analytical 2D velocity solution.
- Persisted `resolved_config.json` per run.
- Deterministic benchmark artifact path under `outputs/benchmarks/`.

## Repository layout

- `src/navier_stokes_research/solver/`: pseudo-spectral solver and numerical utilities.
- `src/navier_stokes_research/initial_conditions/`: random and vortex initial states.
- `src/navier_stokes_research/metrics/`: core diagnostics.
- `src/navier_stokes_research/validation/`: validation checks and JSON reporting.
- `src/navier_stokes_research/benchmark.py`: reproducible benchmark configuration and run.
- `src/navier_stokes_research/convergence.py`: reproducible convergence-study harness.
- `src/navier_stokes_research/taylor_green.py`: controlled Taylor-Green analytical validation and convergence harness.
- `src/navier_stokes_research/stress_validation.py`: controlled 2D stress validation harness.
- `src/navier_stokes_research/interpretation.py`: heuristic quality interpretation.
- `src/navier_stokes_research/runner.py`: simulation orchestration.
- `src/navier_stokes_research/cli.py`: terminal entrypoint.
- `tests/`: deterministic unit tests for numerics, validation, benchmark, reporting, and Taylor-Green validation.
- `docs/`: research notes and validation protocol.

## Current limitations

- 2D periodic domain only.
- Single explicit time integration scheme.
- No forcing model in baseline.
- Validation layer is practical quality control, not formal verification.
- Convergence harness is a baseline consistency study, not a formal convergence proof.
- Quality thresholds are heuristic review aids, not mathematical criteria.
- Taylor-Green validation is a controlled 2D case and does not prove global existence/smoothness for 3D Navier-Stokes.
- Stress validation is an engineering robustness diagnostic, not a solver proof.
- Near-floor error saturation in Taylor-Green convergence diagnostics indicates roundoff-limited behavior, not a standalone formal convergence proof.

## Future research roadmap

1. Extend convergence study with more refinement levels and independent time refinement.
2. Controlled forcing scenarios with documented parameter sweeps.
3. Extended diagnostics and uncertainty quantification.
4. Optional alternative discretizations behind stable interfaces.

See [docs/research_notes.md](docs/research_notes.md), [docs/validation_protocol.md](docs/validation_protocol.md), [docs/convergence_study.md](docs/convergence_study.md), [docs/reports.md](docs/reports.md), [docs/quality_interpretation.md](docs/quality_interpretation.md), [docs/advocatus_diaboli_taylor_green.md](docs/advocatus_diaboli_taylor_green.md), [docs/physical_decay_validation.md](docs/physical_decay_validation.md), [docs/spectral_diagnostics.md](docs/spectral_diagnostics.md), [docs/stress_validation_2d.md](docs/stress_validation_2d.md), [docs/external_validation_checklist_2d.md](docs/external_validation_checklist_2d.md), [docs/agents/kansodata-numerical-methods-auditor.md](docs/agents/kansodata-numerical-methods-auditor.md), [docs/agents/kansodata-physical-validator.md](docs/agents/kansodata-physical-validator.md), [docs/agents/kansodata-advocatus-diaboli.md](docs/agents/kansodata-advocatus-diaboli.md), and [docs/agents/kansodata-chief-scientific-reviewer.md](docs/agents/kansodata-chief-scientific-reviewer.md). See also [docs/agents/scientific_validation_pipeline.md](docs/agents/scientific_validation_pipeline.md).
