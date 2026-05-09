# External Scientific Validation Protocol (2D)

## Purpose

Define a conservative, evidence-first protocol for external scientific validation of the current 2D solver without modifying solver code, numerical tolerances, or numerical results.

## Exact scope

- Solver class: incompressible 2D periodic pseudo-spectral vorticity-streamfunction solver.
- Scope boundary: external-reference alignment for controlled 2D periodic cases only.
- Validation posture: fail-closed, conservative interpretation, human review required for scientific claims.

## Explicit exclusions

- No 3D validation or 3D claim.
- No Millennium Problem claim.
- No theorem-level mathematical proof claim.
- No non-periodic benchmark claim.
- No lid-driven cavity benchmark claim.
- No wall-bounded flow benchmark claim.

## Benchmark set (max 3)

### 1) Taylor-Green 2D analytical validation

- Objective:
  - Verify controlled numerical agreement against the analytical 2D Taylor-Green solution in periodic geometry.
- Base scientific reference:
  - G. I. Taylor and A. E. Green (1937), analytical vortex-decay configuration.
- Related repository artifact:
  - `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json`
- Comparable metrics:
  - `l2_error`, `linf_error`, `relative_error` (when numerically meaningful), execution/accuracy status split.
- Acceptance criterion:
  - `accuracy_status=passed` under existing repository tolerances (unchanged).
- Limitations:
  - Controlled 2D periodic analytical case only; does not generalize to 3D or non-periodic flows.
- Evidence level:
  - `confirmed`
- Overclaiming risk:
  - Treating controlled analytical agreement as universal physical validity.

### 2) Periodic MMS 2D manufactured solution

- Objective:
  - Verify pseudo-spectral RHS consistency against a smooth periodic manufactured solution for 2D incompressible dynamics.
- Base scientific reference:
  - MMS methodology for PDE solver verification (methodological reference class).
- Related repository artifact:
  - `outputs/benchmarks/mms_validation_2d/mms_validation_summary.json`
- Comparable metrics:
  - RMS/relative consistency indicators and solver-reported validation status fields.
- Acceptance criterion:
  - Repository acceptance status for MMS remains satisfied with current thresholds and `scientific_acceptance=human_review_required`.
- Limitations:
  - Manufactured forcing consistency is verification support, not external physical truth demonstration.
- Evidence level:
  - `partial`
- Overclaiming risk:
  - Presenting MMS consistency as proof of broad physical realism.

### 3) 2D viscous decay energy/enstrophy diagnostic

- Objective:
  - Track controlled viscous decay behavior in energy/enstrophy diagnostics within periodic 2D conditions.
- Base scientific reference:
  - 2D turbulence decay context (for example Kraichnan-type theoretical framing) and pseudo-spectral diagnostic practice.
- Related repository artifact:
  - `outputs/benchmarks/physical_decay_2d/physical_decay_validation.json`
- Comparable metrics:
  - Energy trend, enstrophy trend, related diagnostic status/warnings.
- Acceptance criterion:
  - Diagnostic consistency with configured checks; interpreted only as bounded 2D diagnostic evidence.
- Limitations:
  - Not a formal validation gate; thresholds are engineering diagnostics and remain non-theoremic.
- Evidence level:
  - `diagnostic`
- Overclaiming risk:
  - Interpreting decay trends as formal proof or universal turbulence validation.

## Evidence separation

### formal_validation_gate

- Taylor-Green 2D analytical acceptance (`accuracy_status=passed`) in current configured workflow.
- No other benchmark in this protocol is elevated to theorem-level or universal gate.

### diagnostic_evidence

- MMS periodic 2D consistency evidence.
- 2D viscous decay energy/enstrophy evidence.
- All spectral/decay interpretation remains diagnostic unless future literature-backed hard criteria are approved.

### human_review_required

- Any scientific acceptance escalation beyond controlled 2D periodic statements.
- Any claim connecting diagnostics to general turbulence validity.
- Any claim implying 3D relevance, Millennium resolution, or mathematical proof.

## Traceability table

| External reference | Repository command | Artifact | Metric | Acceptance status | Claim allowed |
|---|---|---|---|---|---|
| Taylor-Green 2D analytical case (Taylor & Green, 1937) | `python -m navier_stokes_research.cli --taylor-green-validation` | `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json` | `l2_error`, `linf_error`, `relative_error`, `accuracy_status` | `passed` when configured criteria are met | Controlled 2D analytical agreement claim only |
| Periodic MMS verification methodology | `python -m navier_stokes_research.cli --mms-validation-2d` | `outputs/benchmarks/mms_validation_2d/mms_validation_summary.json` | MMS consistency metrics and reported status fields | `human_review_required` for scientific interpretation | Controlled 2D periodic RHS consistency claim only |
| 2D viscous decay diagnostic literature context | `python -m navier_stokes_research.cli --physical-decay-validation` | `outputs/benchmarks/physical_decay_2d/physical_decay_validation.json` | Energy/enstrophy trends and diagnostics | Diagnostic status (non-formal gate) | Bounded 2D diagnostic consistency claim only |

## Allowed claims

- External validation workflow is defined for controlled 2D incompressible periodic pseudo-spectral scope.
- Taylor-Green analytical agreement supports controlled 2D verification claims.
- MMS and viscous-decay outputs provide bounded diagnostic evidence with mandatory scientific review.

## Blocked claims

- Any 3D Navier-Stokes validity claim.
- Any Millennium Problem resolution claim.
- Any mathematical proof claim.
- Any universal turbulence/physics-validity claim from current diagnostics.
- Any claim that non-periodic, lid-driven cavity, or wall-bounded benchmarks are validated by this protocol.

## Future experimental steps (not implemented in this iteration)

1. Define literature-backed, externally justified acceptance bands for selected 2D periodic diagnostics.
2. Add independent external numeric comparison datasets/reports for the same periodic configurations.
3. Tighten traceability by linking each acceptance decision to archived run metadata and versioned reference citations.
4. Propose a staged escalation path from diagnostic evidence to stronger validation gates, subject to human scientific review and explicit scope approval.
