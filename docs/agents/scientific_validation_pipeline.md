# Scientific Validation Pipeline

## Purpose

This document defines the multi-agent scientific validation pipeline for the Navier-Stokes computational research repository.

The pipeline coordinates specialized agents to review simulation outputs before accepting scientific conclusions.

It follows evidence-first and fail-closed principles. Missing evidence must block acceptance rather than be replaced by assumptions.

This pipeline does not modify the solver. It defines the review process used to decide whether simulation results and claims are scientifically defensible.

## Agents

The current validation agents are:

- `kansodata-numerical-methods-auditor`
- `kansodata-physical-validator`
- `kansodata-advocatus-diaboli`

### `kansodata-numerical-methods-auditor`

Evaluates whether the numerical method, implementation choices, stability constraints, convergence evidence, and diagnostic interpretations are technically defensible.

It reviews spatial discretization, temporal discretization, spectral operators, vorticity-streamfunction consistency, nonlinear-term formulation, de-aliasing treatment, stability margins, convergence diagnostics, roundoff-floor behavior, and numerical false-positive risk.

### `kansodata-physical-validator`

Evaluates whether simulation observables are physically consistent.

It reviews energy, enstrophy, viscosity, resolution, timestep, initial condition, de-aliasing metadata, and preferably spectral evidence.

### `kansodata-advocatus-diaboli`

Evaluates whether a scientific claim is actually supported by available evidence.

It challenges overstatements, unsupported generalizations, unclear scope, and claims that exceed the validated regime.

## Pipeline Order

### Step 1: Simulation output collection

Collect the minimum evidence package:

- resolved simulation configuration;
- numerical-method description;
- physical diagnostics payload;
- run metadata;
- validation artifacts;
- convergence or benchmark artifacts when relevant;
- git commit;
- relevant plots or spectra when available.

The run must not proceed to scientific acceptance if the minimum evidence package is missing.

### Step 2: Numerical-method audit

Agent:

- `kansodata-numerical-methods-auditor`

Required inputs:

- git commit or branch under review;
- resolved simulation configuration;
- solver method description;
- grid resolution and domain;
- timestep and final physical time;
- viscosity;
- initial condition definition;
- de-aliasing metadata;
- validation JSON artifacts;
- convergence summary JSON when relevant;
- metrics CSV or summarized time-series when relevant.

Possible outputs:

- `NUMERICALLY ACCEPTABLE`
- `NUMERICALLY SUSPICIOUS`
- `NUMERICALLY INVALID`
- `INSUFFICIENT NUMERICAL EVIDENCE`
- `REQUIRES MORE NUMERICAL TESTING`

Numerical-method acceptance is required before physical interpretation. Low numerical error must not be interpreted as physical validity.

### Step 3: Physical validation

Agent:

- `kansodata-physical-validator`

Required inputs:

- kinetic energy;
- enstrophy;
- viscosity;
- resolution;
- timestep;
- physical time;
- initial condition;
- de-aliasing method;
- numerical-method audit verdict.

Possible outputs:

- `VALID`
- `SUSPICIOUS`
- `INVALID`
- `INSUFFICIENT DATA`

A low numerical error does not automatically imply physical validity.

### Step 4: Claim formulation

Claims must be narrowly scoped and tied to available evidence.

A valid claim must state:

- what was tested;
- under which configuration;
- which numerical diagnostics support the statement;
- which physical metrics support the statement;
- what remains outside the validated scope.

A single benchmark must not be used to justify broad turbulence, 3D, singularity, or general robustness claims.

### Step 5: Adversarial claim review

Agent:

- `kansodata-advocatus-diaboli`

Required inputs:

- claim under review;
- available evidence;
- validation scope;
- numerical-method audit verdict;
- numerical diagnostics if relevant;
- physical validation verdict;
- physical diagnostics if relevant;
- paths or links to supporting artifacts when available.

Possible outputs:

- `ACCEPTABLE CLAIM`
- `OVERSTATED CLAIM`
- `UNSUPPORTED CLAIM`
- `REQUIRES NARROWING`
- `REQUIRES MORE EVIDENCE`

### Step 6: Final gate

A result may be accepted only if:

- numerical-method audit is `NUMERICALLY ACCEPTABLE`, or explicitly scoped as requiring more numerical testing;
- physical validation is `VALID`, or explicitly scoped as diagnostic evidence rather than physical proof;
- adversarial review is not `UNSUPPORTED CLAIM`;
- adversarial review is not `OVERSTATED CLAIM`;
- the claim is consistent with the evidence package.

Otherwise the result must be rejected, narrowed, or sent back for more evidence.

## Fail-Closed Rules

- Missing numerical-method artifacts must produce `INSUFFICIENT NUMERICAL EVIDENCE` or rejection.
- Missing physical diagnostics must produce `INSUFFICIENT DATA` or rejection.
- Missing claim scope must produce `UNSUPPORTED CLAIM`.
- Numerical accuracy alone cannot imply physical validity.
- Physical validity alone cannot imply broad scientific generality.
- A single benchmark cannot justify general turbulence or 3D claims.
- The pipeline must not invent missing configuration, diagnostics, spectra, validation artifacts, or method details.

## Final Decision States

The final pipeline decision must be one of:

- `ACCEPT RESULT`
- `ACCEPT WITH NARROWED CLAIM`
- `REQUEST MORE EVIDENCE`
- `REJECT RESULT`
- `OPEN ISSUE`

## Minimal Evidence Package

Each reviewed result should include:

- simulation configuration;
- git commit;
- numerical-method description;
- numerical diagnostics or convergence artifacts when relevant;
- physical diagnostics payload;
- validation JSON;
- optional plots or spectra;
- claim text;
- `kansodata-numerical-methods-auditor` verdict;
- `kansodata-physical-validator` verdict;
- `kansodata-advocatus-diaboli` verdict.

## Example

Unsafe claim:

> The solver is robust for Navier-Stokes turbulence.

Expected outcome:

- `kansodata-numerical-methods-auditor`: `REQUIRES MORE NUMERICAL TESTING` unless nonlinear, de-aliasing, convergence, and spectral diagnostics support the claim.
- `kansodata-physical-validator`: insufficient unless nonlinear and spectral diagnostics exist.
- `kansodata-advocatus-diaboli`: `OVERSTATED CLAIM` or `UNSUPPORTED CLAIM`.

Safe rewording:

> The solver has passed controlled 2D Taylor-Green analytical validation and now exposes fail-closed physical diagnostics required for further nonlinear validation.

## Future ComandoIA Integration

ComandoIA may later orchestrate this pipeline by collecting outputs, invoking validation agents, storing verdicts, and generating review reports.

ComandoIA must not bypass validation gates.

ComandoIA must not invent missing evidence.

ComandoIA should treat this pipeline as an auditable scientific control layer, not as an automatic proof engine.

## Scientific Limits

This pipeline does not:

- prove Navier-Stokes existence or smoothness;
- solve the Millennium Prize problem;
- validate 3D behavior;
- replace human scientific review;
- prove general turbulence validity from limited benchmarks.

It is a practical, auditable validation workflow for controlled computational research.
