# 2D Incompressible Navier-Stokes Research Repository

Production-oriented research scaffold for deterministic 2D incompressible Navier-Stokes simulations in Python. The implementation uses a pseudo-spectral vorticity-streamfunction formulation on a periodic domain, with explicit stability guards, reproducible experiments, metrics capture, plots, tests, and a CLI runner.

## Assumptions

- The solver targets 2D, incompressible, periodic domains.
- Spatial derivatives are evaluated spectrally with FFTs.
- Time integration uses a second-order explicit Heun scheme.
- Stability is enforced conservatively through both advection CFL and diffusion checks.
- The pressure field is eliminated through the streamfunction-vorticity formulation.
- Random initial conditions are deterministic under fixed seeds.

## Repository Layout

- `src/navier_stokes_research/solver/`: pseudo-spectral solver and numerical utilities.
- `src/navier_stokes_research/initial_conditions/`: random and vortex-pair initial states.
- `src/navier_stokes_research/metrics/`: energy, enstrophy, and max-velocity diagnostics.
- `src/navier_stokes_research/visualization/`: heatmaps and metric evolution plots.
- `src/navier_stokes_research/runner.py`: simulation orchestration and artifact writing.
- `src/navier_stokes_research/cli.py`: command-line entrypoint.
- `configs/`: reproducible experiment configurations.
- `experiments/`: example runner scripts.
- `tests/`: core numerical tests.
- `notebooks/`: analysis notebook.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Run a Simulation

```bash
nsim --config configs/baseline_random.json
```

Override selected parameters:

```bash
nsim --config configs/baseline_random.json --steps 100 --dt 0.0015 --output-dir outputs/quick_run
```

Artifacts are written under the configured `output_dir`:

- `metrics.csv`
- `resolved_config.json`
- `plots/metric_evolution.png`
- `plots/vorticity_*.png`
- `snapshots/vorticity_*.npy`

## Example Experiment

```bash
python experiments/run_baseline.py
```

## Validation

```bash
pytest
python -m navier_stokes_research.cli --config configs/baseline_random.json --steps 20 --output-dir outputs/smoke_test
```

## Hardening Features

- Fails fast on CFL condition violations.
- Fails fast when the diffusion stability threshold is exceeded.
- Raises `FloatingPointError` on NaN/Inf detection.
- Reproducible seeded initial conditions.
- Persists the resolved runtime configuration for auditability.

## Notes

This project is intentionally scoped to a clean periodic-domain research baseline. Extensions such as forcing, boundaries other than periodic, adaptive stepping, and higher-order integrators should be added as separate, isolated changes rather than folded into this baseline.
