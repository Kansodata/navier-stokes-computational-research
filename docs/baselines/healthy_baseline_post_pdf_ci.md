# Healthy Baseline Checkpoint (Post PDF + CI)

- Checkpoint date (UTC): 2026-05-06
- Baseline branch reference: `main` (post merge of PR #57)

## Verified state

- CI status: green on Python `3.10`, `3.11`, `3.12`.
- Relevant PRs in this baseline window:
  - `#55`
  - `#56`
  - `#57`
- Scientific PDF status:
  - `python -m navier_stokes_research.cli --scientific-validation-report --pdf`
  - PDF artifact path: `outputs/reports/scientific_validation_report.pdf`
- Consolidated report status (current expected interpretation):
  - `failed = 0`
  - `hpc_fftw_benchmark = info` (non-critical infrastructure benchmark, specialized schema)
  - `overall_status = warning` (conservative scientific warnings still present)

## Explicit limits

- 2D incompressible periodic baseline only.
- No claim of 3D Navier-Stokes solution.
- No Millennium Problem claim.
- No mathematical proof claim.
- Human scientific review remains required.

## Recommended next steps

1. Keep fail-closed gates for critical artifacts and invalid schemas.
2. Continue reducing warning-class scientific gaps with targeted evidence.
3. Keep `hpc_fftw_benchmark` interpretation as infrastructure/performance evidence only.
4. Periodically regenerate PDF/report artifacts and re-check CI matrix on `3.10/3.11/3.12`.
