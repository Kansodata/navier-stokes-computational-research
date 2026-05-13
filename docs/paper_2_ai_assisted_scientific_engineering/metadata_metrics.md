# Metadata Metrics for Paper 2

This document derives objective descriptive metrics from `pr_metadata_dataset.csv` for the Paper 2 study on controlled AI-assisted scientific engineering.

The metrics are descriptive only. They do not establish productivity gains, causal AI impact, statistical significance, or scientific correctness.

## Dataset snapshot

Source file:

- `docs/paper_2_ai_assisted_scientific_engineering/pr_metadata_dataset.csv`

Snapshot represented:

- Pull Requests analyzed: PR #1 through PR #65.
- Total PR-level metadata observations: 65.
- Closed PRs: 65.
- Open PRs: 0.
- Draft PRs: 0.
- Observation window: 2026-05-03T22:04:04Z through 2026-05-13T04:36:02Z.
- Approximate observation duration: 9 days, 6 hours, 31 minutes, 58 seconds.

## Merge outcome metrics

| Metric | Count | Percentage |
|---|---:|---:|
| Total PR observations | 65 | 100.00% |
| Merged PRs | 63 | 96.92% |
| Closed without merge | 2 | 3.08% |
| Draft PRs | 0 | 0.00% |

Closed-unmerged PRs:

- PR #11: `docs: add scientific validation summary`.
- PR #28: `fix: apply dealiasing to nonlinear RHS term`, later superseded by PR #29.

Interpretation:

The dataset shows a highly merge-oriented workflow. This should not be interpreted as a quality metric by itself because several PRs appear to be short-lived operational or duplicate/superseded PRs.

## PR cycle-time metrics

Cycle time is computed from `created_at` to `merged_at` for merged PRs only.

| Metric | Value |
|---|---:|
| Merged PRs with cycle time | 63 |
| Minimum cycle time | 6 seconds |
| Median cycle time | 91 seconds / 1.52 minutes |
| Mean cycle time | 193.43 seconds / 3.22 minutes |
| Maximum cycle time | 1,889 seconds / 31.48 minutes |

Interpretation:

The short median cycle time suggests rapid, small-scope PR operation. It does not prove productivity improvement, review quality, or agent effectiveness. The metric primarily supports a descriptive claim: the observed workflow used frequent small PRs rather than long-lived branches.

## Commit-count metrics

| Metric | Value |
|---|---:|
| Total commits across PR observations | 103 |
| Mean commits per PR | 1.58 |
| Median commits per PR | 1 |
| Maximum commits in a PR | 6 |

Commit-count distribution:

| Commits per PR | PR count | Percentage |
|---:|---:|---:|
| 0 | 1 | 1.54% |
| 1 | 42 | 64.62% |
| 2 | 11 | 16.92% |
| 3 | 7 | 10.77% |
| 4 | 3 | 4.62% |
| 6 | 1 | 1.54% |

Interpretation:

Most PRs were one-commit changes. This is consistent with a controlled, incremental engineering style. It does not by itself prove code quality or scientific reliability.

## PR creation distribution by date

| Date UTC | PRs created |
|---|---:|
| 2026-05-03 | 7 |
| 2026-05-04 | 16 |
| 2026-05-05 | 11 |
| 2026-05-06 | 24 |
| 2026-05-09 | 4 |
| 2026-05-13 | 3 |

Interpretation:

The observed development period contains concentrated bursts of activity, especially on 2026-05-06. The dataset does not yet explain whether these bursts correspond to human scheduling, Codex batch execution, agent-guided iteration, or repository maintenance phases.

## File-stat availability

The metadata dataset includes `changed_files`, `additions`, and `deletions` when available from individual PR fetches. Most historical PRs obtained through bulk metadata did not expose these fields.

Known limitation:

- File-stat coverage is incomplete.
- Size-of-change analysis should not be treated as complete until PR file stats are backfilled for all PRs.

Rows with directly available file-stat evidence include at least:

- PR #1.
- PR #62.
- PR #63.
- PR #64.
- PR #65.

## Conservative interpretation for the paper

The current metadata supports the following narrow statement:

> Across 65 PR-level metadata observations, the project exhibits a rapid, small-batch, PR-centered workflow with a high merge ratio, mostly one-commit PRs, and explicitly preserved closed-unmerged records for superseded or non-merged work.

The current metadata does not support:

- causal claims that AI improved productivity;
- causal claims that agents reduced defects;
- claims that short PR cycle time implies review depth;
- claims that merged PRs were scientifically valid solely because they were merged;
- complete change-size analysis, because file-stat coverage is incomplete.

## Recommended next evidence step

The next recommended step is to backfill objective GitHub Actions outcomes per PR head SHA or merge commit SHA.

Target file:

- `docs/paper_2_ai_assisted_scientific_engineering/pr_ci_outcomes.csv`

Suggested columns:

- `pr_number`
- `head_sha`
- `merge_commit_sha`
- `workflow_name`
- `workflow_status`
- `workflow_conclusion`
- `run_number`
- `run_url`
- `evidence_notes`

This would allow the paper to distinguish PR metadata from CI validation evidence more rigorously.
