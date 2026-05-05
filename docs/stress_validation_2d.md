# 2D Stress Validation Harness

This document describes the controlled `stress_validation_2d` harness.

## Scope

The harness attempts to stress the existing 2D incompressible Navier-Stokes solver without expanding scope to 3D.

It is intentionally observational:

- it records whether scenarios pass, warn, fail, or fail closed for an expected reason;
- it does not require every stress case to pass;
- it treats expected CFL rejection as a successful fail-closed behavior;
- it treats uncontrolled NaN/Inf behavior as a real failure;
- it does not make theorem-level claims.

## Command

```bash
python -m navier_stokes_research.cli --stress-validation-2d
```

Optional output root:

```bash
python -m navier_stokes_research.cli --stress-validation-2d --benchmark-output-dir outputs/benchmarks
```

The summary artifact is written to:

```text
outputs/benchmarks/stress_validation_2d/stress_validation_summary.json
```

## Scenario matrix

The harness includes the following deterministic scenarios:

1. `baseline_control`
   - nominal deterministic case;
   - expected to pass.

2. `near_cfl_limit`
   - runs close to the configured CFL limit;
   - expected result is `passed` or `warning`, not a crash.

3. `cfl_violation_expected_fail`
   - intentionally starts above the configured CFL safety limit;
   - expected result is `expected_fail_closed`.

4. `low_viscosity`
   - lower dissipation case;
   - observed for stability without broad physical claims.

5. `high_amplitude`
   - stresses velocity reconstruction and CFL handling;
   - may pass, warn, or fail closed.

6. `coarse_grid`
   - low-resolution diagnostic case;
   - produces evidence only, not accuracy claims.

7. `multiple_seeds`
   - runs several deterministic seeds;
   - summarizes sensitivity without statistical generalization.

8. `spectral_high_k_observation`
   - records `high_wavenumber_energy_fraction`;
   - diagnostic only, not a hard gate in this iteration.

## Scenario statuses

Allowed scenario statuses are:

- `passed`
- `warning`
- `failed`
- `expected_fail_closed`

`expected_fail_closed` does not count as a global failure when the scenario fails for the configured expected reason.

## Global statuses

The summary JSON contains:

```text
acceptance_statuses.runtime_execution
acceptance_statuses.stress_validation_status
acceptance_statuses.scientific_acceptance
```

`scientific_acceptance` is always:

```text
human_review_required
```

## Scientific limits

This harness is a 2D engineering and numerical robustness diagnostic.

It does not prove formal convergence.
It does not validate general turbulence behavior.
It does not solve or claim to solve the 3D Navier-Stokes Millennium problem.
