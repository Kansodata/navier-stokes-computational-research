# Figures Plan for Paper 2

## 1. Purpose

This document defines the minimum figure set required to move Paper 2 toward preprint-ready status.

Paper 2:

**Controlled AI-Assisted Scientific Engineering: A Fail-Closed Human-in-the-Loop Workflow for Reproducible Computational Research**

The figures must support workflow, evidence, reproducibility, and claim-boundary explanations. They must not imply numerical proof, 3D Navier-Stokes validity, productivity gains, AI autonomy, or generalization beyond the observed repository.

## 2. Scope

This plan is for Paper 2 only. It does not create figures, modify code, modify datasets, or update `paper_draft.md`.

Figures are intended for:

- arXiv preprint readiness;
- later SoftwareX/JOSS adaptation if needed;
- reviewer-facing explanation of the case-study evidence protocol.

## 3. Figure governance rules

Every figure must have:

- a figure ID;
- a purpose;
- source artifact(s);
- generation mode (`manual_diagram`, `scripted`, or `table_render`);
- claim supported;
- claims explicitly not supported;
- reproducibility status;
- review owner or agent role.

No figure may be used to support a claim stronger than the underlying evidence.

## 4. Minimum figure set

| ID | Working title | Type | Priority | Expected file |
|---|---|---|---|---|
| F1 | Controlled AI-assisted workflow architecture | Architecture diagram | P0 | `figures/paper_2/workflow_architecture.svg` |
| F2 | Evidence pipeline and fail-closed gates | Evidence-flow diagram | P0 | `figures/paper_2/evidence_pipeline.svg` |
| F3 | PR evidence timeline | Timeline | P0 | `figures/paper_2/pr_evidence_timeline.png` |
| F4 | CI outcomes summary | Bar/timeline chart | P0 | `figures/paper_2/ci_outcomes_summary.png` |
| F5 | Claim-boundary taxonomy | Taxonomy diagram/table | P1 | `figures/paper_2/claim_boundary_taxonomy.svg` |

## 5. Figure F1: Controlled AI-assisted workflow architecture

Purpose:

- Show the human-in-the-loop workflow.
- Show agentic review roles as bounded review aids.
- Show merge/review governance and rollback discipline.

Source artifacts:

- `docs/paper_2_ai_assisted_scientific_engineering/paper_draft.md`
- `docs/agents/`
- `docs/paper_2_ai_assisted_scientific_engineering/literature_review_plan.md`

Generation mode:

- `manual_diagram` initially.
- Later may be converted to reproducible Mermaid/SVG if the project standardizes diagram generation.

Claim supported:

- The workflow is structured around human review, specialized agent roles, and explicit governance gates.

Claims not supported:

- AI agents autonomously validate science.
- Agentic review proves correctness.
- The workflow generalizes beyond this repository.

Review owner:

- `kansodata-chief-scientific-reviewer`
- `kansodata-advocatus-diaboli`

## 6. Figure F2: Evidence pipeline and fail-closed gates

Purpose:

- Show how PR bodies, metadata, validation evidence, CI outcomes, and documentation artifacts feed into Paper 2 evidence.
- Show fail-closed interpretation boundaries.

Source artifacts:

- `docs/paper_2_ai_assisted_scientific_engineering/evidence_protocol.md`
- `docs/paper_2_ai_assisted_scientific_engineering/pr_evidence_dataset.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/pr_metadata_dataset.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/pr_ci_outcomes.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_metrics.md`

Generation mode:

- `manual_diagram` or Mermaid-generated SVG.

Claim supported:

- The study uses multiple repository evidence channels and preserves interpretation boundaries.

Claims not supported:

- Repository evidence alone proves scientific validity.
- CI success proves numerical correctness.
- Metadata proves productivity gains.

Review owner:

- `kansodata-reproducibility-and-ci-auditor`
- `kansodata-scientific-literature-auditor`

## 7. Figure F3: PR evidence timeline

Purpose:

- Show longitudinal development of governance controls and evidence artifacts.
- Highlight key PR ranges without implying causal effect.

Source artifacts:

- `docs/paper_2_ai_assisted_scientific_engineering/pr_metadata_dataset.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/pr_evidence_dataset.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/metadata_metrics.md`
- `docs/paper_2_ai_assisted_scientific_engineering/evidence_metrics.md`

Generation mode:

- Prefer `scripted` if generated from CSV.
- Accept `table_render` for first preprint version if scripts are not yet available.

Claim supported:

- The repository provides a longitudinal PR-level evidence base.

Claims not supported:

- More PRs imply higher quality.
- Short PR cycle time proves productivity or review quality.
- Agent involvement caused improvements.

Review owner:

- `kansodata-chief-scientific-reviewer`
- `kansodata-advocatus-diaboli`

## 8. Figure F4: CI outcomes summary

Purpose:

- Summarize CI outcomes for PR #31-#68.
- Preserve both success and failure evidence.

Source artifacts:

- `docs/paper_2_ai_assisted_scientific_engineering/pr_ci_outcomes.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_metrics.md`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_backfill_31_40.md`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_backfill_41_50.md`
- `docs/paper_2_ai_assisted_scientific_engineering/ci_backfill_51_68.md`

Generation mode:

- Prefer `scripted` from `pr_ci_outcomes.csv`.

Required content:

- Total rows: 38.
- Success count: 36.
- Failure count: 2.
- Failure PRs: #45 and #56.
- Unknown/unavailable count: 0.

Claim supported:

- CI outcome evidence is available and includes both success and failure outcomes.

Claims not supported:

- CI success proves scientific validity.
- CI failure implies scientific invalidity.
- CI outcomes prove productivity.

Review owner:

- `kansodata-reproducibility-and-ci-auditor`

## 9. Figure F5: Claim-boundary taxonomy

Purpose:

- Visually separate allowed descriptive claims from prohibited scientific or productivity claims.
- Help reviewers understand conservative interpretation boundaries.

Source artifacts:

- `docs/paper_2_ai_assisted_scientific_engineering/paper_draft.md`
- `docs/paper_2_ai_assisted_scientific_engineering/anti_hallucination_checklist.md`
- `docs/paper_2_ai_assisted_scientific_engineering/literature_review_plan.md`
- `SCIENCE_INTEGRITY.md`

Generation mode:

- `manual_diagram` or `table_render`.

Claim supported:

- The manuscript defines explicit claim boundaries.

Claims not supported:

- Boundary documentation proves scientific correctness.
- Boundary documentation replaces external review.

Review owner:

- `kansodata-advocatus-diaboli`
- `kansodata-chief-scientific-reviewer`

## 10. Preprint minimum

For arXiv preprint readiness, minimum acceptable figure set:

- F1 workflow architecture.
- F2 evidence pipeline.
- F4 CI outcomes summary.

Recommended but not strictly required for first preprint:

- F3 PR evidence timeline.
- F5 claim-boundary taxonomy.

## 11. Reproducibility requirements

Before formal journal submission, any data-driven figure should be reproducible from repository artifacts.

Minimum requirements:

- Source CSV or Markdown evidence file is identified.
- Generation command or manual-generation rationale is recorded.
- Figure file path is stable.
- Figure caption does not exceed source evidence.
- Figure review status is recorded.

## 12. Anti-overclaim checklist for figures

Before any figure is inserted into `paper_draft.md`, verify:

- The figure supports a specific manuscript paragraph.
- The figure is not used as proof of scientific validity.
- The figure does not imply causality or productivity gains.
- The figure does not imply 3D Navier-Stokes scope.
- The figure does not imply autonomous AI scientific validation.
- The caption states the evidence boundary when needed.

## 13. Recommended next PRs

1. Create F1 and F2 as Mermaid or SVG diagrams.
2. Create F4 from `pr_ci_outcomes.csv`.
3. Add captions and figure references to `paper_draft.md`.
4. Add F3/F5 if needed for journal submission.

## 14. Rollback plan

If this plan is rejected, revert only:

- `docs/paper_2_ai_assisted_scientific_engineering/figures_plan.md`

No code, CI, solver, dataset, notebook, bibliography, or manuscript rollback is required for this documentation-only planning artifact.
