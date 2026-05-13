# CI Backfill Batch: PR #31-#40

This document records the first historical CI outcome backfill batch for Paper 2.

## Batch scope

Covered PRs:

- PR #31 through PR #40.

Rationale:

- PR #31 introduced the automated GitHub Actions validation workflow.
- Therefore, PR #31 is the natural starting point for historical CI evidence curation.

## Confirmed outcomes

All queried PR head SHAs in this batch returned a GitHub Actions workflow run with:

```text
workflow_name = CI
workflow_status = completed
workflow_conclusion = success
```

Confirmed run numbers:

| PR | Run number | Run ID |
|---:|---:|---:|
| 31 | 1 | 25399847979 |
| 32 | 3 | 25402070468 |
| 33 | 5 | 25403372552 |
| 34 | 7 | 25408362741 |
| 35 | 9 | 25409308164 |
| 36 | 11 | 25409830002 |
| 37 | 13 | 25411521403 |
| 38 | 15 | 25411533745 |
| 39 | 17 | 25412180991 |
| 40 | 19 | 25412336973 |

## Special note on PR #37 and PR #38

PR #37 and PR #38 share the same head SHA in the available metadata. The workflow query returned two successful CI runs for that SHA. The dataset records one run per PR and notes the shared-head-SHA condition.

## Interpretation limits

CI success means the configured workflow completed successfully for the queried commit. It does not prove:

- scientific correctness;
- physical validity beyond the test scope;
- mathematical proof;
- 3D Navier-Stokes validity;
- causal effectiveness of AI agents;
- productivity improvement.

## Remaining CI backfill

Recommended next batches:

1. PR #41-#50.
2. PR #51-#68.

Earlier PRs #1-#30 predate the automated CI workflow introduced in PR #31 and should be treated separately if analyzed.
