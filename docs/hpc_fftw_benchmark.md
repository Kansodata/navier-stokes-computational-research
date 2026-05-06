# HPC FFTW Benchmark (Baseline vs Opt-In FFTW Solver)

## Purpose

This benchmark measures infrastructure/runtime behavior for the 2D periodic solver stack. It compares:

- baseline NumPy/FFT pseudo-spectral solver (`NavierStokesSpectralSolver`)
- opt-in FFTW implementation (`SpectralSolver512`)

The output is diagnostic and audit-ready. It is not a new physics validation.

## Scope

- 2D incompressible periodic Navier-Stokes only.
- No 3D claims.
- No Millennium Problem claims.
- No mathematical proof claims.
- `scientific_acceptance` remains `human_review_required`.

## Commands

Safe mode:

```bash
python -m navier_stokes_research.cli --hpc-fftw-benchmark
```

Extended mode:

```bash
python -m navier_stokes_research.cli --hpc-fftw-benchmark --hpc-fftw-benchmark-extended
```

Optional script:

```bash
python scripts/hpc_fftw_benchmark.py
python scripts/hpc_fftw_benchmark.py --extended
```

## Artifact

`outputs/benchmarks/hpc_fftw_benchmark/hpc_fftw_benchmark_summary.json`

## Parameters and interpretation

- `speedup_ratio`: runtime ratio baseline/fftw for the selected benchmark setup.
- `energy_relative_difference`, `enstrophy_relative_difference`, `cfl_relative_difference`: operational consistency diagnostics under the benchmark horizon.
- `consistency_status` and `performance_status`: diagnostic statuses, not scientific acceptance.

## What this does NOT mean

- No claim that FFTW is more physically correct.
- No claim that 512 resolution validates turbulence theory.
- No claim that infrastructure speedup implies better scientific validity.
- No replacement of the baseline validated solver for official validation gates.

## Limitations

- Benchmark horizon is intentionally short for controlled runtime cost.
- Results are environment-dependent (CPU, threads, FFT planning effort).
- The benchmark is infrastructure evidence; external scientific review remains required.
