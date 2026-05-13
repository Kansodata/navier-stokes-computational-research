# CI Outcomes Notes for Paper 2

This note documents the current maturity of `pr_ci_outcomes.csv`.

## Scope

The initial CI outcomes dataset records confirmed GitHub Actions outcomes for recent Paper 2 evidence PRs where the connector returned workflow runs for the PR head SHA.

Currently confirmed:

| PR | Workflow | Status | Conclusion | Run number |
|---:|---|---|---|---:|
| 65 | CI | completed | success | 74 |
| 66 | CI | completed | success | 76 |
| 67 | CI | completed | success | 78 |

## Interpretation

These rows show that the recent documentation and evidence-dataset PRs passed the repository CI workflow. They do not prove scientific correctness, model validity, productivity improvement, or causal agent effectiveness.

## Known limitations

- This is an initial CI outcome seed, not a full historical CI backfill.
- Earlier PRs require separate workflow-run lookup by head SHA or merge commit SHA.
- CI success only means the configured workflow completed successfully for that commit.
- CI success does not replace human scientific review.
- CI success does not imply that all physical or numerical claims are valid.

## Recommended next step

Backfill CI outcomes for earlier PRs in batches, preferably starting at PR #31 because that PR introduced the automated validation workflow.

Suggested batches:

1. PR #31-#40.
2. PR #41-#50.
3. PR #51-#67.

Each batch should preserve `not_available` or `unknown` when no workflow run is returned by the API.
