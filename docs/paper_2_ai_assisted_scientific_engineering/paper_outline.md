# Paper 2 Outline: Controlled AI-Assisted Scientific Engineering

## 1. Tentative title

**Beyond Vibe Coding: Controlled AI-Assisted Scientific Engineering for Reproducible Computational Research**

Alternative conservative title:

**Fail-Closed Human-in-the-Loop Agentic Workflows for Reproducible Scientific Computing: A Longitudinal GitHub Case Study**

Preferred title for submission planning:

**Controlled AI-Assisted Scientific Engineering: A Fail-Closed Human-in-the-Loop Workflow for Reproducible Computational Research**

## 2. Preliminary abstract

AI-assisted coding and agentic development workflows are increasingly used in software engineering, but their use in computational science introduces specific risks: unsupported scientific claims, silent numerical regressions, weak reproducibility, and overreliance on generated code or documentation. This paper presents a longitudinal GitHub-based case study of a controlled AI-assisted scientific engineering workflow applied to a 2D incompressible periodic pseudo-spectral Navier-Stokes research repository. The workflow combines human-in-the-loop decision making, specialized review agents, explicit scientific non-claims, rollback discipline, validation artifacts, and fail-closed continuous integration checks. Using pull requests, repository metadata, validation records, and GitHub Actions outcomes as evidence, the study characterizes how governance controls were encoded into day-to-day scientific software development. The current evidence supports descriptive claims about workflow structure, traceability, validation coverage, and CI outcomes, including both successful and failed CI runs. It does not claim autonomous scientific validation by AI, productivity improvement, statistical significance, 3D Navier-Stokes validity, or mathematical proof. The contribution is a reproducible evidence protocol and case-study framework for evaluating controlled AI-assisted engineering in computational research.

## 3. Research question

Primary research question:

> How can an AI-assisted, human-in-the-loop engineering workflow be structured to preserve scientific boundaries, reproducibility, and fail-closed validation in a computational research project?

Secondary research questions:

1. What governance controls can be observed and measured through GitHub PR evidence?
2. How often were rollback plans, scientific non-claims, validation evidence, and agent-related review artifacts present?
3. How can CI outcomes be represented as operational evidence without overstating scientific validity?
4. What limitations arise when using repository history as an empirical source for AI-assisted scientific engineering?

## 4. Central thesis

The paper should defend a narrow and falsifiable thesis:

> AI-assisted scientific software development can be made more auditable when embedded inside a controlled human-in-the-loop workflow with explicit scientific boundaries, agentic review roles, rollback plans, validation artifacts, and fail-closed CI gates.

The paper must not defend the stronger thesis that AI agents independently validate science or improve productivity.

## 5. Contributions

The paper's contributions should be stated conservatively:

1. A GitHub-based evidence protocol for studying AI-assisted scientific software engineering.
2. A PR-level longitudinal dataset covering project evolution, governance controls, and validation evidence.
3. A metadata dataset capturing PR lifecycle characteristics.
4. A CI outcomes dataset covering PR #31-#68 after introduction of the automated validation workflow.
5. A failure/risk taxonomy for AI-assisted computational science workflows.
6. A case-study analysis of a controlled 2D scientific computing repository using specialized agentic review roles.
7. A conservative interpretation framework that separates workflow evidence from scientific proof.

## 6. Target venue category

Possible venue categories:

- Scientific software engineering.
- Computational science reproducibility.
- AI-assisted software engineering.
- Software engineering empirical case studies.
- Research software engineering workshops.

Avoid positioning the paper as a pure CFD paper. The Navier-Stokes repository is the case study, not the main scientific CFD contribution.

## 7. Proposed paper structure

### 1. Introduction

Purpose:

- Introduce the rise of AI-assisted coding and agentic development.
- Explain why computational science is high risk for uncontrolled AI-assisted workflows.
- Define the problem of unsupported claims, brittle validation, and hidden regressions.
- State that the paper studies a controlled human-in-the-loop workflow.

Evidence to use:

- `README.md` in the Paper 2 evidence directory.
- `evidence_protocol.md`.
- PR #63 methodological note.

Claims allowed:

- The project uses AI-assisted workflow evidence as a study object.
- The repository contains explicit scientific boundary controls.

Claims prohibited:

- AI autonomously performed scientific validation.
- The workflow is generally superior to human-only workflows.

### 2. Background and Motivation

Subsections:

#### 2.1 AI-assisted coding and the risk of vibe coding

Use the term `vibe coding` carefully. Treat it as informal shorthand for unconstrained AI-assisted development, not as a formal scientific method.

#### 2.2 Research software engineering constraints

Discuss reproducibility, version control, validation, review, and traceability.

#### 2.3 Scientific computing validation risk

Explain why numerical software requires stronger evidence than ordinary application code.

#### 2.4 Human-in-the-loop agentic workflows

Define agents as review roles and workflow components, not autonomous authorities.

Evidence to use:

- Agent documentation PRs: #15, #17, #18, #32, #55, #59.
- `pr_evidence_dataset.csv`.

### 3. Case Study Context

Purpose:

- Describe the repository under study.
- State scientific scope: 2D incompressible periodic pseudo-spectral Navier-Stokes computational research.
- Clarify that this paper is about workflow governance, not CFD novelty.

Required scientific boundaries:

- No 3D Navier-Stokes claim.
- No Millennium Problem claim.
- No theorem-level mathematical proof claim.
- No physical overinterpretation.

Evidence to use:

- `pr_evidence_dataset.csv`.
- `pr_metadata_dataset.csv`.
- `evidence_metrics.md`.
- `metadata_metrics.md`.

### 4. Methodology

Purpose:

Describe how evidence was collected and classified.

Subsections:

#### 4.1 Study design

Longitudinal GitHub-based case study.

#### 4.2 Unit of analysis

Each PR is an engineering event.

#### 4.3 Evidence sources

- PR bodies and metadata.
- GitHub Actions workflow outcomes.
- Validation commands reported in PRs.
- Agent documentation.
- Paper 2 evidence artifacts.

#### 4.4 Classification schema

Use columns from `pr_evidence_dataset.csv`:

- `change_type`
- `agent_related`
- `scientific_scope`
- `validation_evidence`
- `rollback_present`
- `non_claims_present`
- `defect_or_risk_type`
- `governance_control`

#### 4.5 CI outcome curation

Use `pr_ci_outcomes.csv` and the backfill notes.

#### 4.6 Conservative interpretation policy

Explicitly separate:

- workflow evidence;
- validation evidence;
- scientific proof;
- productivity claims.

Evidence to use:

- `evidence_protocol.md`.
- `ci_outcomes_notes.md`.
- `ci_backfill_31_40.md`.
- `ci_backfill_41_50.md`.
- `ci_backfill_51_68.md`.

### 5. Workflow Architecture

Purpose:

Describe the controlled AI-assisted engineering workflow.

Subsections:

#### 5.1 Human-in-the-loop control

Human author approves direction, merge decisions, and scientific boundaries.

#### 5.2 Specialized agentic review roles

Use neutral names in paper text:

- Numerical methods auditor.
- Physical validator.
- Adversarial scientific reviewer.
- Chief scientific reviewer.
- Reproducibility and CI auditor.
- Python documentation auditor.

Map to repository names in a table:

| Paper role | Repository agent |
|---|---|
| Numerical methods auditor | `kansodata-numerical-methods-auditor` |
| Physical validator | `kansodata-physical-validator` |
| Adversarial reviewer | `kansodata-advocatus-diaboli` |
| Chief scientific reviewer | `kansodata-chief-scientific-reviewer` |
| Reproducibility and CI auditor | `kansodata-reproducibility-and-ci-auditor` |
| Python documentation auditor | `kansodata-python-documentation-auditor` |

#### 5.3 Fail-closed validation controls

Discuss fail-closed JSON checks, artifact validation, CI outcomes.

#### 5.4 Rollback discipline

Discuss rollback as repeated governance artifact.

Evidence to use:

- PR #33.
- PR #55.
- PR #61.
- `evidence_metrics.md`.

### 6. Results

This section must be descriptive, not causal.

#### 6.1 PR evidence metrics

Use `evidence_metrics.md`:

- 63 PR-level observations.
- 12 agent-related PRs.
- 34 PRs with explicit rollback evidence.
- 42 PRs with explicit non-claims.
- 46 PRs with non-unknown validation evidence.

#### 6.2 PR lifecycle metrics

Use `metadata_metrics.md`:

- 65 metadata observations.
- 63 merged PRs.
- 2 closed without merge.
- Median cycle time: 91 seconds.
- Mean cycle time: 193.43 seconds.
- 42 one-commit PRs.

Caution:

These are workflow descriptors, not productivity claims.

#### 6.3 CI outcome metrics

Use `pr_ci_outcomes.csv` after PR #71:

Expected current CI dataset coverage:

- PR #31-#68.
- Confirmed success rows.
- Confirmed failure rows: PR #45 and PR #56.

Do not claim full scientific validity from CI success.

#### 6.4 Failure evidence

Discuss real failure evidence:

- PR #45: CI failure followed by PR #46 success.
- PR #56: CI failure followed by later successful PRs.
- PR #25: JSON serialization defect.
- PR #28/#29: de-aliasing correction sequence.

#### 6.5 Governance evidence

Discuss repeated patterns:

- scientific boundaries;
- rollback notes;
- validation commands;
- diagnostic-only labeling;
- human-review-required status;
- fail-closed checks.

### 7. Discussion

Subsections:

#### 7.1 What the workflow appears to support

Allowed:

- improved auditability;
- explicit scope control;
- traceable validation evidence;
- structured scientific review roles;
- recorded CI failures and successes.

#### 7.2 What the workflow does not prove

Must state clearly:

- no causal productivity claim;
- no autonomous AI scientific validation claim;
- no statistical significance claim;
- no generalization beyond the case study;
- no 3D Navier-Stokes claim.

#### 7.3 Why failure evidence strengthens the paper

CI failures and bugfix PRs make the dataset more credible than success-only storytelling.

#### 7.4 Relevance beyond Navier-Stokes

Discuss cautiously: the workflow may be applicable to other computational research repositories, but this is not proven.

### 8. Threats to Validity

Use and expand from `evidence_protocol.md`.

#### 8.1 Internal validity

- Single repository.
- Human and assistant workflow intertwined.
- Some PR bodies unavailable.
- Some validation reported manually.

#### 8.2 External validity

- CFD/scientific Python repository may not generalize.
- Private or industrial workflows may differ.

#### 8.3 Construct validity

- Productivity is not directly measured.
- PR cycle time does not equal review quality.
- CI success does not equal scientific validity.
- Agent involvement is conservatively classified.

#### 8.4 Temporal validity

- AI systems evolve quickly.
- Repository governance matured during the study period.
- Tooling and CI behavior can change.

### 9. Related Work

This section requires external literature review before final drafting.

Target literature areas:

- AI-assisted software engineering.
- Agentic coding workflows.
- Reproducible research software engineering.
- Scientific software validation and verification.
- Human-in-the-loop AI systems.
- Empirical software engineering case-study methodology.

Do not add references here until verified from reliable sources.

### 10. Conclusion

Conservative conclusion:

Controlled AI-assisted scientific engineering can be made auditable when embedded in human-in-the-loop review, explicit scientific non-claims, rollback plans, validation artifacts, and fail-closed CI gates. This case study provides evidence of such a workflow in a real computational research repository, but does not establish general causality, autonomous scientific validity, or productivity improvement.

## 8. Proposed tables and figures

### Table 1: Agent roles and responsibilities

Source:

- PR #15, #17, #18, #32, #55, #59.

### Table 2: Evidence datasets

Rows:

- PR evidence dataset.
- PR metadata dataset.
- CI outcomes dataset.
- Evidence metrics.
- Metadata metrics.

### Table 3: Governance metrics

Source:

- `evidence_metrics.md`.

### Table 4: CI outcomes summary

Source:

- `pr_ci_outcomes.csv`.

Expected categories:

- success;
- failure;
- not available if later added.

### Figure 1: Workflow architecture

Flow:

User / human lead -> AI-assisted implementation -> specialized agents -> validation artifacts -> CI fail-closed checks -> PR review -> merge/reject.

### Figure 2: Timeline of evidence-building PRs

Use PR #63-#71.

### Figure 3: CI outcome timeline

Use PR #31-#68.

## 9. Claims allowed

The paper may claim:

- The repository provides a longitudinal case study of controlled AI-assisted scientific engineering.
- PR evidence shows repeated use of rollback plans, non-claims, validation evidence, and governance controls.
- CI outcomes include both successes and failures.
- Agentic roles were documented as review responsibilities.
- The workflow is auditable through GitHub artifacts.

## 10. Claims prohibited

The paper must not claim:

- AI solved Navier-Stokes.
- The repository solves 3D Navier-Stokes.
- The repository addresses the Millennium Problem beyond explicit non-claims.
- The workflow proves mathematical correctness.
- AI agents independently validated scientific truth.
- The workflow caused productivity improvement.
- Short PR cycle time proves review quality.
- CI success proves physical or numerical validity.
- The findings generalize to all scientific software projects.

## 11. Minimum evidence readiness before writing full draft

Ready:

- Evidence protocol.
- PR evidence dataset.
- Evidence metrics.
- PR metadata dataset.
- Metadata metrics.
- CI outcome dataset PR #31-#68.
- CI backfill notes.

Still needed before full paper submission:

1. External literature review with verified citations.
2. Final CI metrics summary derived from `pr_ci_outcomes.csv`.
3. One or two diagrams.
4. Final decision on target venue style.
5. Optional anonymization decision if needed for peer review.

## 12. Next recommended repository artifact

Create:

```text
docs/paper_2_ai_assisted_scientific_engineering/ci_metrics.md
```

Purpose:

- Summarize final CI coverage after PR #71.
- Count successes and failures.
- Identify failure cases PR #45 and PR #56.
- State interpretation limits.

After `ci_metrics.md`, create:

```text
docs/paper_2_ai_assisted_scientific_engineering/paper_draft.md
```
