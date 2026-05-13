# Evidence Metrics for Paper 2

This document derives conservative descriptive metrics from `pr_evidence_dataset.csv` for the Paper 2 study on controlled AI-assisted scientific engineering.

The metrics are intentionally descriptive. They do not claim statistical significance, productivity improvement, causal AI impact, or scientific correctness by themselves.

## Dataset snapshot

Source file:

- `docs/paper_2_ai_assisted_scientific_engineering/pr_evidence_dataset.csv`

Snapshot represented:

- Pull Requests analyzed: PR #1 through PR #63.
- Total PR-level observations: 63.
- Dataset maturity: seed longitudinal dataset.
- Evidence model: PR metadata plus available PR bodies and curated conservative classifications.

## High-level counts

| Metric | Count | Percentage |
|---|---:|---:|
| Total PR observations | 63 | 100.00% |
| Agent-related PRs | 12 | 19.05% |
| Non-agent-related PRs | 51 | 80.95% |
| PRs with explicit rollback evidence | 34 | 53.97% |
| PRs with rollback explicitly absent | 7 | 11.11% |
| PRs with rollback unknown | 22 | 34.92% |
| PRs with explicit non-claims | 42 | 66.67% |
| PRs with non-claims explicitly absent | 1 | 1.59% |
| PRs with non-claims unknown | 20 | 31.75% |
| PRs with non-unknown validation evidence | 46 | 73.02% |
| PRs with unknown validation evidence | 17 | 26.98% |

## Validation evidence classification

| Validation classification | Count | Percentage |
|---|---:|---:|
| `reported_manual` | 34 | 53.97% |
| `ci` | 6 | 9.52% |
| `not_required` | 3 | 4.76% |
| `unknown` | 20 | 31.75% |

Interpretation:

- `reported_manual` means validation was reported in PR text but not independently re-executed by this dataset curation step.
- `ci` means the row records CI-oriented validation or a CI governance change.
- `not_required` is used for changes where runtime validation was explicitly unnecessary, such as metadata-only changes.
- `unknown` is preserved when the extracted evidence is insufficient.

## Scientific scope distribution

| Scientific scope | Count | Percentage |
|---|---:|---:|
| documentation | 29 | 46.03% |
| validation | 21 | 33.33% |
| solver | 7 | 11.11% |
| ci | 3 | 4.76% |
| configuration | 2 | 3.17% |
| benchmark | 1 | 1.59% |

Interpretation:

The observed workflow is documentation-heavy and validation-heavy. This supports the paper framing as a governance and reproducibility case study, not merely a solver-development narrative.

## Change-type distribution

| Change type | Count |
|---|---:|
| validation_harness | 8 |
| agent_doc | 6 |
| citation_doc | 4 |
| license_metadata | 4 |
| solver_mechanism | 4 |
| ci_governance | 3 |
| visual_diagnostics | 3 |
| audit_doc | 2 |
| bugfix | 2 |
| config_gate | 2 |
| documentation | 2 |
| numerical_fix | 2 |
| reporting | 2 |
| scientific_summary | 2 |
| agent_architecture | 1 |
| agent_pipeline | 1 |
| baseline_checkpoint | 1 |
| benchmark | 1 |
| design_gate | 1 |
| diagnostic_harness | 1 |
| diagnostic_infrastructure | 1 |
| diagnostic_integration | 1 |
| infrastructure_solver | 1 |
| methodology_doc | 1 |
| scientific_checklist | 1 |
| scientific_evidence_doc | 1 |
| scientific_protocol | 1 |
| test_governance | 1 |
| validation_infrastructure | 1 |
| validation_schema | 1 |
| validation_semantics | 1 |

## Defect and risk categories

The dataset records risk or defect labels in `defect_or_risk_type`. These are qualitative labels and should not be treated as mutually exclusive root-cause findings without deeper review.

Notable categories include:

- numerical de-aliasing defects;
- serialization and reproducibility defects;
- false-positive CI risk;
- artifact-ordering defects;
- external validation gaps;
- physical or turbulence overclaim risks;
- documentation and traceability gaps;
- license and citation metadata gaps;
- agent and governance pipeline gaps.

## Governance controls observed

The dataset identifies recurring governance controls, including:

- explicit rollback plans;
- scientific non-claims;
- diagnostic-only labeling;
- human-review-required acceptance;
- fail-closed artifact checking;
- CI validation workflow;
- agentic numerical review;
- agentic physical validation;
- adversarial scientific review;
- chief scientific reviewer coordination;
- reproducibility and CI auditor role;
- design-before-implementation gates.

## Current limitations of the metrics

These metrics are not final paper results yet.

Known limitations:

1. The `outcome` column is underpopulated. Most rows remain `unknown`, even when the PR was later merged. This prevents reliable merge-rate analysis.
2. Several PRs have unavailable or empty bodies in the extracted evidence. They are intentionally retained as `unknown` rather than excluded.
3. `reported_manual` validation was not independently re-executed during this curation step.
4. Duplicate or superseded-looking PRs are included to reduce survivorship bias, but they may require later normalization.
5. Agent involvement is conservative and based on PR title/body evidence, not hidden work sessions.
6. The dataset does not yet include GitHub Actions run outcomes per PR.
7. The dataset does not yet include timestamps sufficient for cycle-time or productivity analysis.
8. These metrics describe governance coverage, not scientific correctness.

## Conservative interpretation for the paper

The current dataset supports the following narrow statement:

> Across 63 PR-level observations, the repository exhibits repeated use of explicit scientific boundaries, rollback discipline, validation evidence, fail-closed checks, and specialized agentic review roles as part of a controlled human-in-the-loop scientific engineering workflow.

The current dataset does not yet support:

- causal claims that agents reduced defects;
- productivity improvement claims;
- statistical significance claims;
- claims that AI autonomously validated scientific results;
- generalization beyond this case study.

## Recommended next evidence step

The next recommended curation step is to enrich the dataset with GitHub-derived PR status metadata:

- actual merged/closed state;
- merge commit SHA;
- GitHub Actions conclusion per PR head SHA;
- changed file count;
- additions/deletions;
- created/merged timestamps.

That enrichment would allow stronger longitudinal analysis without changing scientific claims.
