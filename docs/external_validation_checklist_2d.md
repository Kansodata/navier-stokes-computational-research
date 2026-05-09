# External Validation Checklist (2D Solver)

Use this checklist before claiming external validation progress for the current solver.

## 1) Current solver scope
- [x] 2D only
- [x] Periodic domain
- [x] Pseudo-spectral discretization
- [x] Vorticity-streamfunction formulation
- [x] External scientific validation protocol exists: `docs/external_scientific_validation_protocol_2d.md`

## 2) Applicable external references (max 3)
- [ ] Taylor-Green vortex 2D analytical reference is explicitly cited and matched
- [ ] Pseudo-spectral method reference (Orszag-type) is cited for method-level consistency
- [ ] Energy/enstrophy decay consistency reference is cited for qualitative physical behavior

## 3) Non-applicable references (explicit)
- [x] Lid-driven cavity benchmarks are out of scope (non-periodic boundaries)
- [x] 3D turbulence benchmarks are out of scope (no 3D solver)
- [x] Wall-bounded flow benchmarks are out of scope

## 4) Externally comparable metrics
- [ ] Total kinetic energy evolution
- [ ] Enstrophy evolution
- [ ] Energy spectrum shape/trend

## 5) Current tolerance status
- [x] Taylor-Green tolerance is numerically justified (roundoff-limited floor)
- [x] Physical decay tolerance is heuristic
- [x] Spectral diagnostics are informative and not a formal gate

## 6) Current risks
- [x] Circular internal validation risk
- [x] Missing direct comparison against external datasets/reports
- [x] Spectrum not enforced as a pass/fail criterion

## 7) Decisions enabled by this document
- [x] Stress validation in 2D can run with explicit scope boundaries
- [x] `spectral_evidence` can be promoted to formal warning status
- [x] Claims remain bounded: no turbulence generalization, no 3D claims

## 8) Allowed claim
- [x] "Validation is consistent in a controlled 2D environment."

## 9) Blocked claims
- [x] General turbulence validation
- [x] Universal physical validity
- [x] Navier-Stokes 3D validity
