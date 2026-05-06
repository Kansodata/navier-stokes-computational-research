# Validation Protocol for Baseline Repository

## What is validated

The current validation layer checks:

- kinetic energy trend ratio,
- enstrophy trend ratio,
- max velocity growth signal,
- NaN/Inf detection in emitted metrics,
- CFL margin against configured limit,
- diffusion stability margin against configured limit.
- finite error comparison against the analytical 2D Taylor-Green vortex for the controlled canonical setup.
- finite RHS consistency comparison against a manufactured smooth periodic 2D vorticity-streamfunction solution (MMS).

It also supports an incompressibility residual field in the report when available.

## What is not validated

This protocol does not establish:

- physical correctness for real-world turbulence,
- convergence-order guarantees,
- boundary-condition generality beyond periodic domains,
- or any theorem-level result.
- The Taylor-Green check is only a controlled 2D validation target and does not establish global 3D existence/smoothness.
- The MMS check is only a controlled 2D consistency validation target and does not establish global 3D existence/smoothness.

## MMS 2D periodic consistency validation

The command:

- `python -m navier_stokes_research.cli --mms-validation-2d`

evaluates a manufactured periodic smooth 2D vorticity field and analytic source term for:

- `omega_t + u·grad(omega) = nu Delta(omega) + f_mms`

and writes:

- `outputs/benchmarks/mms_validation_2d/mms_validation_summary.json`

The JSON includes:

- `schema_version`,
- `validation_name`,
- `scientific_scope`,
- `scientific_acceptance`,
- `status`,
- `max_absolute_error`,
- `l2_relative_error`,
- `resolution`,
- `viscosity`,
- `limitations`.

This harness is numerical evidence for operator-level consistency in 2D periodic conditions only. It is not a 3D claim, not a Millennium claim, and not a formal proof.

## Taylor-Green 2D controlled validation

The command:

- `python -m navier_stokes_research.cli --taylor-green-validation`

runs a periodic-domain test on `[0, 2π] x [0, 2π]` and writes:

- `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json`

Report content includes:

- resolved configuration,
- domain and resolution,
- viscosity and final physical time,
- `L2` and `L∞` errors,
- relative error when the reference norm is safely non-zero,
- backward-compatible `status` (`passed`/`failed`),
- `execution_status` (`passed`/`failed`) for runtime integrity,
- `accuracy_status` (`passed`/`failed`/`warning`/`not_evaluated`) for precision interpretation,
- `warnings` list for explicit audit signals,
- and technical notes.

Taylor-Green convergence mode also writes reproducible diagnostic PNGs by resolution:

- `L2` error,
- `L∞` error,
- relative `L2` error,
- optional combined log-scale plot.

These figures include an explicit `ROUND_OFF_ERROR_FLOOR` reference. If curves saturate near this floor, interpretation should be "roundoff-limited regime" rather than standalone formal convergence proof.

For critical review of interpretation limits and false-positive risks, see:

- `docs/advocatus_diaboli_taylor_green.md`

## Numerical stability checks

The solver enforces:

- fail-fast CFL threshold checks,
- fail-fast diffusion threshold checks,
- fail-fast NaN/Inf checks in numerical state updates.

Validation additionally summarizes these checks in JSON for downstream audit pipelines.

## Reproducibility rules

- Use explicit seed in initial conditions.
- Use fixed grid, viscosity, timestep, and step count for benchmark runs.
- Persist resolved run configuration with output artifacts.
- Keep output directory explicit and versioned by experiment intent.

## Acceptance criteria for this baseline

For baseline acceptance:

- unit tests pass,
- benchmark run completes,
- validation status is generated with machine-readable report,
- and artifacts are reproducible for fixed benchmark parameters within numeric tolerances.

## Scientific citation traceability

Scientific evidence mapping for each validation component is maintained in:

- `docs/validation_evidence_matrix.md`

Primary references are curated in:

- `docs/references.bib`

Validation JSON schema contract and migration notes are documented in:

- `docs/validation_json_schema.md`

Consolidated scientific validation report generation:

- `python -m navier_stokes_research.cli --scientific-validation-report`
- `python -m navier_stokes_research.cli --scientific-validation-report --pdf`
- `python -m navier_stokes_research.cli --validation-figures`
- `python -m navier_stokes_research.cli --forced-turbulence-validation-2d`
- `python -m navier_stokes_research.cli --resolution-sensitivity-study-2d`
- `python -m navier_stokes_research.cli --hpc-fftw-benchmark`
- `python -m navier_stokes_research.cli --mms-validation-2d`
- `python scripts/hpc_fftw_benchmark.py` for manual benchmark execution.
- `python scripts/resolution_sensitivity_study.py` for the extended `64,128,256,512` forced-resolution matrix.
- Outputs:
  - `outputs/reports/scientific_validation_report.json`
  - `outputs/reports/scientific_validation_report.md`
  - `outputs/reports/scientific_validation_report.pdf`
  - `outputs/figures/figures_manifest.json`
  - `outputs/figures/*.png`
  - `outputs/benchmarks/forced_turbulence_validation_2d/forced_turbulence_validation_summary.json`
  - `outputs/benchmarks/resolution_sensitivity_2d/resolution_sensitivity_summary.json`
  - `outputs/benchmarks/hpc_fftw_benchmark/hpc_fftw_benchmark_summary.json`
  - `outputs/benchmarks/mms_validation_2d/mms_validation_summary.json`
- `scientific_acceptance` remains `human_review_required` by design.
- Visual artifacts are evidence support only; they are not 3D validation, not a Millennium solution, and not formal proof.
- PDF report generation is fail-closed when consolidated critical evidence yields overall `failed` status.
- PDF output is designed as a human-readable scientific review artifact, not as a raw console/JSON dump.
- PDF output includes a paginated validation matrix, conservative interpretation, warning/gap cards, optional generated figures (when available), and a final artifact index.
- Forced turbulence budget and spectral outputs are diagnostic-only until scientific review.
- Resolution sensitivity output explains spectral slope warnings and 2/3 de-alias cutoff limits; it is not a formal cascade or convergence proof.
- HPC FFTW benchmark output is infrastructure/performance evidence only; it does not imply improved physical validity.

## Convergence study protocol

The convergence harness runs a fixed seeded scenario over multiple resolutions and writes:

- `convergence_summary.json`
- `convergence_metrics.csv`
- `convergence_comparison.png`

Protocol constraints:

- same viscosity and seed across runs,
- smooth deterministic vortex-pair initial condition across resolutions,
- target physical horizon approximated with resolution-scaled `dt`,
- post-run validation required for each resolution,
- relative differences computed between consecutive resolutions.

Interpretation limits:

- these comparisons provide reproducibility and consistency signals,
- they do not constitute formal convergence proof or mathematical guarantees.
