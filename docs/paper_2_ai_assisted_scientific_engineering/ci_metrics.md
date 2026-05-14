# CI Metrics for Paper 2

## Purpose
Provide a conservative, repository-grounded summary of CI outcomes for Paper 2 as operational evidence of workflow execution.

## Source files
The following files are present in the current repository snapshot and were used for this summary:

- `docs/paper_2_ai_assisted_scientific_engineering/pr_ci_outcomes.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_outcomes_notes.md`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_backfill_31_40.md`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_backfill_41_50.md`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_backfill_51_68.md`

## Dataset snapshot
- Snapshot date: 2026-05-14.
- Primary CI dataset: `pr_ci_outcomes.csv`.
- Covered PR interval in dataset: PR #31 to PR #68.

## CI outcome counts
Computed directly from `pr_ci_outcomes.csv`:

- Total rows: 38.
- Covered PR range: 31-68.
- Success count: 36.
- Failure count: 2.
- Unavailable/unknown count: 0 (no row with conclusion outside `success` or `failure`).
- Failure PR list: PR #45, PR #56.
- Specific checks:
  - PR #45 is present with `workflow_status=completed` and `workflow_conclusion=failure`.
  - PR #56 is present with `workflow_status=completed` and `workflow_conclusion=failure`.

## Known failure evidence
Based on dataset rows in `pr_ci_outcomes.csv`:

- PR #45 is recorded as `completed/failure`.
- PR #56 is recorded as `completed/failure`.

No additional root-cause claim is made here beyond recorded CI outcome labels in the dataset.

## Interpretation boundaries
CI success is operational evidence of workflow execution, not proof of numerical correctness, physical validity, mathematical proof, or autonomous AI scientific validation.

## Limitations
- This summary depends on the current `pr_ci_outcomes.csv` snapshot and inherits any omissions or labeling errors in that file.
- CI outcomes are repository-process signals, not direct scientific validation results.
- Duplicate or superseded PR histories may affect historical interpretation and should be resolved in dedicated provenance analysis.

## Conservative paper-ready statement
The CI outcome dataset supports operational evidence about automated workflow behavior. It does not establish numerical correctness, physical validity, mathematical proof, productivity improvement, or autonomous AI scientific validation.

## Recommended next step
Cross-link this CI summary with the broader Paper 2 evidence tables so CI workflow evidence remains explicitly separated from scientific validity claims.

## Rollback plan
If this update must be reverted, restore the prior state by reverting only `docs/paper_2_ai_assisted_scientific_engineering/ci_metrics.md` in a dedicated follow-up commit.
