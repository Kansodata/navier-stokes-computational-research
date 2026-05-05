# Validation Evidence Matrix

This matrix links repository validation artifacts to external scientific basis with conservative scope control.

| Validation component | Repository artifact | Scientific basis | Evidence level | Scope limits | Risk of overclaiming |
|---|---|---|---|---|---|
| Taylor-Green 2D analytical validation | `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json` | Taylor & Green (1937), exact analytical benchmark for incompressible flow configuration used by the project. | confirmed | 2D periodic controlled case only. Not a general turbulence validation. | Treating analytical agreement as proof of broader physical validity. |
| Taylor-Green convergence to roundoff floor | `outputs/benchmarks/taylor_green_convergence_2d/taylor_green_convergence_summary.json` | Spectral-method error behavior references (Canuto et al., Peyret). Current project status `passed_roundoff_floor` indicates machine-precision regime. | confirmed | Limited to configured 2D periodic setup and selected resolutions. | Presenting `passed_roundoff_floor` as a universal convergence proof. |
| 2D unforced viscous physical decay | `outputs/benchmarks/physical_decay_2d/physical_decay_validation.json` | 2D turbulence/decay theory context (Kraichnan 1967) plus numerical diagnostics practice. | partial | Diagnostic evidence in 2D periodic unforced viscous regime only. | Interpreting decay checks as universal physical validation. |
| Spectral energy diagnostics | `outputs/benchmarks/physical_decay_2d/spectral_diagnostics.json` and stress spectral fields | Fourier spectral-energy diagnostics from pseudo-spectral literature (Canuto et al., Peyret). | partial | Diagnostic-only in this repository; explicitly not a hard acceptance gate. | Treating spectral shape as standalone physical proof. |
| Fourier pseudo-spectral method | `src/navier_stokes_research/solver/spectral.py` and generated `resolved_config.json` | Canonical references for Fourier pseudo-spectral incompressible flow methods (Canuto et al., Peyret). | confirmed | 2D incompressible periodic domain implementation. | Extrapolating to non-periodic domains or 3D claims. |
| 2/3 de-aliasing rule | `src/navier_stokes_research/solver/numerics.py` (`dealias_mask`) and solver RHS usage | Orszag (1971) de-aliasing references for pseudo-spectral nonlinear term handling. | confirmed | Numerical anti-aliasing control for this discretization; not a physical-model claim. | Claiming de-aliasing alone guarantees global correctness. |
| Verification & validation methodology | Validation JSON separation (`runtime_execution`, `scientific_acceptance`, warnings) across harnesses | ASME V&V 20-2009 framework intent (verification/validation separation and credibility discipline). | partial | Adapted engineering workflow, not formal compliance certification. | Stating full compliance with standards without formal audit. |

## Explicit gap tracking

- G1 (`gap`): A single primary source directly prescribing repository-specific thresholds for spectral warning gates is not established.
- G2 (`gap`): A formal uncertainty quantification framework aligned end-to-end with ASME V&V process artifacts is not yet implemented.
- G3 (`partial`): Physical decay interpretation uses accepted 2D theory context, but current acceptance thresholds remain engineering heuristics in this codebase.

## Interpretation rules (fail-closed)

- `passed_roundoff_floor` must be interpreted as controlled numerical agreement at machine precision, not as a general convergence proof.
- Spectral diagnostics must remain diagnostic-only unless converted to documented, literature-backed acceptance criteria.
- Any claim beyond 2D incompressible periodic scope is out of scope and must be rejected.
