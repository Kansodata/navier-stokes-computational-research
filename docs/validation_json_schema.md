# Validation JSON Schema

## Purpose

This document defines a normalized JSON schema for validation artifacts used by the 2D incompressible periodic pseudo-spectral Navier-Stokes research baseline.

The schema exists to improve:

- auditable scientific traceability,
- fail-closed CI checks,
- machine-readable cross-run comparison,
- future read-only reporting integration.

## Why this schema exists

Historically, validation artifacts were useful but heterogeneous. A normalized schema provides a stable contract for:

- automated checkers,
- multi-agent scientific review,
- consolidated validation reports,
- safe historical comparisons.

## Formal separation: verification, validation, diagnostics

- `verification`: numerical/implementation consistency checks against expected numerical behavior.
- `validation`: bounded physical-consistency checks in the declared scope.
- `diagnostic`: informative indicators that do not claim formal acceptance by themselves.

This repository still requires human scientific review. A passing JSON status is not a mathematical proof.

## Required fields

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Schema contract version, currently `1.0`. |
| `validation_id` | string | Stable identifier of the validation artifact. |
| `validation_type` | string | `verification`, `validation`, or `diagnostic`. |
| `status` | string | `passed`, `failed`, `warning`, or `skipped`. |
| `generated_at_utc` | string | UTC ISO-8601 timestamp (`...Z`). |
| `solver_scope` | string | Must remain `2d_incompressible_periodic_pseudo_spectral`. |
| `claim_scope` | string | Conservative, bounded scope statement. |
| `parameters` | object | Input/run configuration summary for this validation. |
| `metrics` | object | Reported numeric outcomes. |
| `thresholds` | object | Explicit decision thresholds/criteria used by the validation. |
| `artifacts` | object | Paths or references to generated files. |
| `limitations` | array | Explicit scope limits and non-claims. |
| `notes` | array | Additional contextual notes. |

## Allowed values

### `validation_type`

- `verification`
- `validation`
- `diagnostic`

### `status`

- `passed`
- `failed`
- `warning`
- `skipped`

### `solver_scope`

- `2d_incompressible_periodic_pseudo_spectral`

## `claim_scope` rules

Allowed examples:

- `analytical_solution_verification_2d`
- `physical_consistency_validation_2d`
- `diagnostic_only`
- `numerical_regression_check`
- `literature_traceability`
- `no_formal_convergence_claim`

Forbidden or unsafe examples:

- `navier_stokes_solution`
- `general_solver_validation`
- `3d_ready`
- `millennium_relevant`
- `proof`
- `formal_resolution`

## Example: Taylor-Green 2D (verification)

```json
{
  "schema_version": "1.0",
  "validation_id": "taylor_green_2d",
  "validation_type": "verification",
  "status": "passed",
  "generated_at_utc": "2026-01-01T00:00:00Z",
  "solver_scope": "2d_incompressible_periodic_pseudo_spectral",
  "claim_scope": "analytical_solution_verification_2d",
  "parameters": {"resolution": 64, "dt": 0.0015, "steps": 160},
  "metrics": {"l2": 1.0e-15, "linf": 2.0e-15, "relative": 1.5e-15},
  "thresholds": {"l2": 1.0e-10, "linf": 1.0e-10, "relative": 1.0e-10},
  "artifacts": {"summary_json": "outputs/benchmarks/taylor_green_2d/taylor_green_validation.json"},
  "limitations": ["controlled_2d_case_only", "not_a_3d_existence_or_smoothness_proof"],
  "notes": ["Roundoff-limited agreement does not imply general convergence proof."]
}
```

## Example: Physical decay 2D (validation)

```json
{
  "schema_version": "1.0",
  "validation_id": "physical_decay_2d",
  "validation_type": "validation",
  "status": "passed",
  "generated_at_utc": "2026-01-01T00:00:00Z",
  "solver_scope": "2d_incompressible_periodic_pseudo_spectral",
  "claim_scope": "physical_consistency_validation_2d",
  "parameters": {"resolution": 64, "viscosity": 0.001},
  "metrics": {"energy_ratio": 0.998, "enstrophy_ratio": 0.995, "cfl_peak": 0.0047},
  "thresholds": {"non_increasing_with_tolerance": true, "cfl_margin_positive": true},
  "artifacts": {"summary_json": "outputs/benchmarks/physical_decay_2d/physical_decay_validation.json"},
  "limitations": ["diagnostic_numerical_validation_only", "not_formal_physical_universality"],
  "notes": ["Scientific acceptance remains human_review_required."]
}
```

## Example: Multi-resolution energy/enstrophy (diagnostic)

```json
{
  "schema_version": "1.0",
  "validation_id": "multi_resolution_energy_enstrophy_2d",
  "validation_type": "diagnostic",
  "status": "passed",
  "generated_at_utc": "2026-01-01T00:00:00Z",
  "solver_scope": "2d_incompressible_periodic_pseudo_spectral",
  "claim_scope": "numerical_regression_check",
  "parameters": {"resolutions": [32, 64, 96], "final_time": 0.24},
  "metrics": {"runtime_execution": "passed", "energy_enstrophy_regression_status": "passed"},
  "thresholds": {"energy_ratio_upper_bound": 1.1, "enstrophy_ratio_upper_bound": 1.1},
  "artifacts": {"summary_json": "outputs/benchmarks/multi_resolution_energy_enstrophy_2d/multi_resolution_energy_enstrophy_summary.json"},
  "limitations": ["2d_periodic_scope_only", "not_formal_convergence_proof"],
  "notes": ["Regression diagnostic, not universal physical validation."]
}
```

## CI fail-closed compatibility

The schema is designed to work with fail-closed artifact checking:

- missing expected artifact => fail,
- invalid JSON => fail,
- missing required fields => fail,
- unknown/failed status => fail,
- non-finite critical metrics => fail.

## Limitations

- This schema is not a mathematical proof framework.
- This schema does not validate 3D Navier-Stokes behavior.
- This schema does not resolve the Millennium Problem.
- This schema does not replace external scientific peer review.

## Gradual migration plan for legacy artifacts

1. Keep existing artifact fields for backward compatibility while adding normalized fields.
2. Update checker rules incrementally per artifact type.
3. Migrate old artifacts to normalized contracts in controlled iterations.
4. Keep fail-closed behavior enabled during migration.
