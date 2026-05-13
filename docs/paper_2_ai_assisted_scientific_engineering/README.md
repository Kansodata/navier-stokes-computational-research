# Paper 2: AI-Assisted Scientific Engineering Evidence

This directory contains the initial evidence base for a methodological paper about controlled AI-assisted scientific software engineering.

The paper studies a human-in-the-loop engineering workflow applied to a real computational science project: a 2D incompressible periodic pseudo-spectral Navier-Stokes research repository.

## Scope

The paper is not a claim that AI autonomously performs scientific validation. It is a study of how AI-assisted development, agentic review roles, fail-closed validation, rollback discipline, and explicit scientific boundaries can be encoded into a reproducible engineering workflow.

## Explicit non-claims

- No claim of solving 3D Navier-Stokes.
- No claim of solving the Millennium Problem.
- No theorem-level mathematical proof claim.
- No claim that AI replaces human scientific oversight.
- No claim that agentic review is deterministic or sufficient by itself.
- No physical interpretation beyond validated 2D periodic evidence.

## Evidence policy

Every statement intended for the paper must be traceable to at least one of:

- GitHub Pull Requests.
- GitHub Actions or validation logs.
- Repository artifacts.
- Documented prompts or human instructions.
- Review or audit documents.

Unconfirmed data must be marked as `unknown`. Reported but not independently re-executed validation must be marked as `reported_manual`.

## Initial files

- `evidence_protocol.md`: methodology for evidence extraction and classification.
- `pr_evidence_dataset.csv`: initial PR-level observation dataset.

## Current maturity

This is an initial evidence protocol and seed dataset. It supports study design and later quantitative analysis, but it does not yet support final statistical claims.