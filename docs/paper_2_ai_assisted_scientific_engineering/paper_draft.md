# Controlled AI-Assisted Scientific Engineering: A Fail-Closed Human-in-the-Loop Workflow for Reproducible Computational Research

## Draft status

This document is an internal evidence-grounded draft. It is not submission-ready.

Submission readiness requires, at minimum:

- verified external literature review;
- verified external citations;
- venue-specific formatting;
- final figure/table selection;
- final review of anonymization requirements if the target venue requires double-blind review.

This draft uses only repository-internal evidence artifacts currently available under `docs/paper_2_ai_assisted_scientific_engineering/`. It does not introduce external references, unsupported bibliographic claims, or claims of productivity improvement, general causal impact, autonomous scientific validation by AI, mathematical proof, 3D Navier-Stokes validity, or generalization beyond the observed case study.

## Abstract

AI-assisted coding and agentic development workflows are increasingly used in software engineering, but their use in computational science introduces specific risks: unsupported scientific claims, silent numerical regressions, weak reproducibility, and overreliance on generated code or documentation. This paper presents a longitudinal GitHub-based case study of a controlled AI-assisted scientific engineering workflow applied to a 2D incompressible periodic pseudo-spectral Navier-Stokes research repository. The workflow combines human-in-the-loop decision making, specialized review agents, explicit scientific non-claims, rollback discipline, validation artifacts, and fail-closed continuous integration checks.

Using pull requests, repository metadata, validation records, and GitHub Actions outcomes as evidence, the study characterizes how governance controls were encoded into day-to-day scientific software development. The available evidence supports descriptive claims about workflow structure, traceability, validation coverage, and CI outcomes, including both successful and failed CI runs. It does not establish autonomous scientific validation by AI, productivity improvement, statistical significance, 3D Navier-Stokes validity, or mathematical proof. The contribution is a reproducible evidence protocol and case-study framework for evaluating controlled AI-assisted engineering in computational research.

## 1. Introduction

AI-assisted development workflows can accelerate drafting, refactoring, documentation, and review activities, but computational research introduces a stricter evidentiary burden than ordinary application development. In scientific computing, a syntactically correct implementation is not enough. The workflow must preserve numerical assumptions, validation boundaries, reproducibility, and scientific claim discipline.

This paper studies an AI-assisted workflow as an engineering and governance object. The underlying repository implements and validates a controlled 2D incompressible periodic pseudo-spectral Navier-Stokes research code, but the central contribution of this paper is not a new CFD result. The repository is used as a case study for examining how a human-in-the-loop AI-assisted process can be structured around explicit boundaries, validation records, rollback plans, and fail-closed CI gates.

The primary research question is:

> How can an AI-assisted, human-in-the-loop engineering workflow be structured to preserve scientific boundaries, reproducibility, and fail-closed validation in a computational research project?

The thesis is intentionally narrow: AI-assisted scientific software development can be made more auditable when embedded inside a controlled human-in-the-loop workflow with explicit scientific boundaries, agentic review roles, rollback plans, validation artifacts, and fail-closed CI gates. This paper does not argue that AI agents independently validate science, reduce defects causally, or improve productivity.

## 2. Background and Motivation

### 2.1 AI-assisted coding and the risk of unconstrained development

Unconstrained AI-assisted development can produce plausible code, documentation, and explanations without sufficient evidence that the scientific interpretation is valid. In this draft, the informal term `vibe coding` is treated only as shorthand for unconstrained or weakly governed AI-assisted development. It is not treated as a formal method or as an empirical construct with externally validated measurement.

The central risk is not merely incorrect code generation. In computational science, an uncontrolled workflow can produce overclaiming, undocumented assumptions, validation gaps, missing rollback paths, or CI configurations that pass operationally while failing to inspect scientific artifact status.

### 2.2 Research software engineering constraints

Research software engineering requires reproducible artifacts, traceable decisions, versioned evidence, and explicit review boundaries. Scientific claims should be connected to validation evidence, and validation evidence should be separated from mathematical proof or broad physical generalization.

In the studied repository, the workflow records these constraints through pull request bodies, documentation files, validation protocols, CI status evidence, rollback notes, and agent role specifications. These artifacts make the workflow inspectable after the fact.

### 2.3 Scientific computing validation risk

Numerical software requires stronger evidence than conventional application code because small implementation changes can silently alter stability, convergence, or physical interpretation. A passing test suite or successful CI run is operationally useful, but it does not by itself prove numerical correctness, physical validity, or mathematical truth.

The repository therefore distinguishes several evidence categories: solver behavior, validation artifacts, diagnostic outputs, CI outcomes, human review requirements, and prohibited scientific claims.

### 2.4 Human-in-the-loop agentic workflows

In this case study, agents are treated as structured review roles and workflow components, not as autonomous authorities. They document responsibilities such as numerical-methods review, physical validation, adversarial claim review, reproducibility review, and documentation review. The human remains responsible for direction, acceptance, merge decisions, and scientific boundary control.

## 3. Case Study Context

The case study repository is a 2D incompressible periodic pseudo-spectral Navier-Stokes computational research project. The scientific implementation provides context for the workflow, but the paper's object of analysis is the controlled engineering process around it.

The case study explicitly excludes:

- 3D Navier-Stokes claims;
- Millennium Problem claims;
- theorem-level mathematical proof claims;
- physical overinterpretation beyond the documented 2D computational scope;
- claims that AI independently validates scientific truth.

The repository history includes PR-level evidence, PR metadata, CI outcomes, agent documentation, validation protocols, validation artifacts, and paper-specific metrics files. These provide a longitudinal evidence base for studying workflow governance rather than scientific novelty.

## 4. Methodology

### 4.1 Study design

This is a longitudinal GitHub-based case study. The unit of observation is the pull request, supplemented by repository-level documentation and CI outcome files.

The analysis is descriptive. It characterizes observable workflow controls and evidence artifacts. It does not claim statistical significance, causal inference, productivity gain, or general external validity.

### 4.2 Unit of analysis

Each pull request is treated as an engineering event. PRs are used to observe change type, validation evidence, rollback evidence, non-claims, agent involvement, governance controls, and CI outcomes when available.

### 4.3 Evidence sources

The draft uses the following internal evidence artifacts:

- `paper_outline.md`;
- `evidence_protocol.md`;
- `pr_evidence_dataset.csv`;
- `evidence_metrics.md`;
- `pr_metadata_dataset.csv`;
- `metadata_metrics.md`;
- `pr_ci_outcomes.csv`;
- `ci_metrics.md`;
- `ci_outcomes_notes.md`;
- `ci_backfill_31_40.md`;
- `ci_backfill_41_50.md`;
- `ci_backfill_51_68.md`.

### 4.4 Classification schema

The PR evidence dataset classifies PRs using fields such as:

- `change_type`;
- `agent_related`;
- `scientific_scope`;
- `validation_evidence`;
- `rollback_present`;
- `non_claims_present`;
- `defect_or_risk_type`;
- `governance_control`.

These fields are used as descriptive labels. They are not treated as independent causal variables.

### 4.5 CI outcome curation

CI outcomes are curated in `pr_ci_outcomes.csv` and summarized in `ci_metrics.md`. The CI dataset covers PR #31 through PR #68, after introduction of the automated validation workflow.

The CI metrics are interpreted as operational workflow evidence. CI success indicates that the configured workflow completed successfully for the recorded run. CI failure indicates a recorded workflow failure. Neither outcome is treated as proof or disproof of scientific validity.

### 4.6 Conservative interpretation policy

The interpretation policy separates:

- workflow evidence;
- validation evidence;
- CI evidence;
- scientific validity;
- mathematical proof;
- productivity claims.

The draft uses conservative language such as `documents`, `records`, `supports descriptive evidence`, and `does not establish`. Stronger claims require external evidence not present in the current repository snapshot.

## 5. Workflow Architecture

### 5.1 Human-in-the-loop control

The workflow is human-in-the-loop. The human lead approves direction, scope, merge decisions, and scientific boundaries. AI-assisted work is treated as support for implementation, documentation, and structured review, not as a source of independent scientific authority.

### 5.2 Specialized agentic review roles

The repository documents specialized review roles. In paper text, these can be described using neutral role names while mapping them to repository agent names.

| Paper role | Repository agent |
|---|---|
| Numerical methods auditor | `kansodata-numerical-methods-auditor` |
| Physical validator | `kansodata-physical-validator` |
| Adversarial scientific reviewer | `kansodata-advocatus-diaboli` |
| Chief scientific reviewer | `kansodata-chief-scientific-reviewer` |
| Reproducibility and CI auditor | `kansodata-reproducibility-and-ci-auditor` |
| Python documentation auditor | `kansodata-python-documentation-auditor` |

These roles support review structure. They do not replace external scientific validation or human scientific responsibility.

### 5.3 Fail-closed validation controls

The workflow includes fail-closed controls around validation artifacts and CI. A key risk in scientific CI is a false-positive workflow where commands exit successfully but generated validation artifacts record internal failure states. The repository addresses this by adding checks that inspect artifact status, schema, and critical metrics.

These controls support auditability and reduce silent failure risk at the workflow level. They do not prove physical validity or mathematical correctness.

### 5.4 Rollback discipline

Rollback plans are recorded as governance artifacts. The evidence metrics identify 34 PRs with explicit rollback evidence across 63 PR-level observations. This supports the descriptive claim that rollback discipline was repeatedly encoded into PR workflow, although it does not prove that all rollbacks would be operationally trivial in every environment.

## 6. Results

The results are descriptive and repository-grounded.

### 6.1 PR evidence metrics

The PR evidence dataset contains 63 PR-level observations. It records repeated use of governance and validation controls:

| Metric | Count |
|---|---:|
| PR-level observations | 63 |
| Agent-related PRs | 12 |
| PRs with explicit rollback evidence | 34 |
| PRs with explicit non-claims | 42 |
| PRs with non-unknown validation evidence | 46 |

These metrics support the narrow statement that the repository repeatedly recorded scientific boundaries, validation evidence, rollback discipline, and agentic review roles. They do not establish causal effectiveness, productivity improvement, or scientific correctness.

### 6.2 PR lifecycle metrics

The metadata dataset contains 65 PR-level observations.

| Metric | Value |
|---|---:|
| PR-level metadata observations | 65 |
| Merged PRs | 63 |
| Closed without merge | 2 |
| Median cycle time | 91 seconds |
| Mean cycle time | 193.43 seconds |
| One-commit PRs | 42 |

These metrics document a rapid, small-batch PR-centered workflow. They do not imply review depth, productivity gain, or code quality by themselves.

### 6.3 CI outcome metrics

The CI outcome dataset contains 38 rows covering PR #31 through PR #68.

| Metric | Value |
|---|---:|
| CI outcome rows | 38 |
| Covered PR range | PR #31-#68 |
| Success count | 36 |
| Failure count | 2 |
| Unknown/unavailable count | 0 |
| Failure PRs | #45, #56 |

The two recorded CI failures are PR #45 and PR #56. The dataset records them as completed failures. No additional root-cause claim is made in this draft unless supported by a separate evidence artifact.

### 6.4 Evidence datasets

| Dataset | File | Scope | Interpretation |
|---|---|---|---|
| PR evidence dataset | `pr_evidence_dataset.csv` | PR #1-#63 | Governance and validation classification |
| PR metadata dataset | `pr_metadata_dataset.csv` | PR #1-#65 | Lifecycle and merge metadata |
| CI outcome dataset | `pr_ci_outcomes.csv` | PR #31-#68 | Operational CI workflow evidence |
| Evidence metrics | `evidence_metrics.md` | Summary of PR evidence | Descriptive metrics |
| Metadata metrics | `metadata_metrics.md` | Summary of metadata | Descriptive lifecycle metrics |
| CI metrics | `ci_metrics.md` | Summary of CI outcomes | Operational CI evidence only |

### 6.5 Governance metrics

| Governance signal | Recorded evidence |
|---|---:|
| Explicit rollback evidence | 34 PRs |
| Explicit non-claims | 42 PRs |
| Non-unknown validation evidence | 46 PRs |
| Agent-related PRs | 12 PRs |
| CI outcome rows | 38 rows |
| CI failures preserved | 2 rows |

The presence of failure evidence is important because it prevents a success-only narrative. Recorded failures make the dataset more credible as workflow evidence, provided the interpretation remains conservative.

## 7. Discussion

### 7.1 What the workflow appears to support

The repository evidence supports descriptive claims about auditability, traceability, and explicit scientific boundary control. The workflow records PR-level evidence, validation artifacts, CI outcomes, rollback plans, and agentic review roles. It also preserves both successful and failed CI outcomes.

### 7.2 What the workflow does not prove

The workflow does not establish:

- autonomous AI scientific validation;
- mathematical proof;
- 3D Navier-Stokes validity;
- general CFD validity;
- statistical significance;
- productivity improvement;
- causal defect reduction;
- generalization beyond this repository.

Short PR cycle time does not prove review quality. CI success does not prove scientific validity. Agent involvement does not prove that agents independently validated numerical truth.

### 7.3 Why failure evidence strengthens the case study

Failure evidence improves the credibility of the dataset because it shows that the workflow did not merely preserve successful outcomes. PR #45 and PR #56 are recorded as CI failures. Their presence supports analysis of fail-closed workflow behavior, but does not by itself identify root causes or scientific implications.

### 7.4 Relevance beyond the case study

The workflow may be relevant to other computational research repositories that use AI-assisted development, but this remains a cautious implication rather than a proven generalization. Other domains may require different validation standards, different review roles, and different CI artifact contracts.

## 8. Threats to Validity

### 8.1 Internal validity

The case study is based on one repository. Human and AI-assisted work are intertwined, and some PR bodies or historical fields may be unavailable. Some validation evidence is reported in PR text rather than independently re-executed during dataset curation.

### 8.2 External validity

The repository is a 2D scientific Python research code. Results may not generalize to other scientific domains, industrial codebases, larger multi-author teams, private workflows, or regulated software environments.

### 8.3 Construct validity

The metrics describe workflow artifacts, not direct scientific quality. PR cycle time is not a measure of review quality. CI success is not a measure of numerical correctness. Agent-related labels are conservative and based on visible repository evidence.

### 8.4 Temporal validity

AI tooling, repository governance, and CI behavior can change rapidly. The observed workflow matured during the study period, so earlier and later PRs may not represent the same governance maturity level.

## 9. Related Work

This related work is scoped to verified seed references already mapped for this manuscript. The cited literature provides framing for the paper's workflow and evidence boundaries; it does not establish scientific validity for the repository, prove mathematical claims, or imply productivity gains.

### 9.1 AI-assisted software engineering

Recent survey work on large language models in software engineering describes a broad and rapidly developing literature around coding, review, maintenance, and other software-engineering tasks, while also identifying methodological gaps and open questions in the evidence base [@waseem2023_llms_se_slr]. Earlier review work on deep learning in software engineering similarly motivates a conservative reading of AI-for-SE results because task coverage and evidence quality are heterogeneous [@humayoun2020_dl_se_slr].

For this paper, that literature supports positioning rather than validation. The case study is not used to claim autonomous AI competence, causal productivity improvement, or general software-quality gains. Instead, it studies a controlled AI-assisted engineering workflow in which AI outputs remain subject to explicit human review, repository evidence, and fail-closed validation rules.

### 9.2 Empirical software engineering and repository-based evidence

Repository-based empirical work provides a useful context for GitHub-derived evidence, including the value and limitations of studying development artifacts, pull requests, issues, and project histories. A systematic review of GitHub-based open-source development challenges reports recurring challenge categories and methodological constraints in repository-mining studies [@ayala2020_oss_challenges_github_slr].

This paper is consistent with that framing because it treats GitHub artifacts as workflow evidence rather than direct evidence of scientific correctness. Pull-request metadata, labels, commit history, and documented review outcomes support a descriptive longitudinal case study. They do not, by themselves, establish that the scientific model is valid, that numerical results are correct, or that the workflow generalizes beyond the observed repository.

### 9.3 Research software engineering and reproducibility

Research software governance depends on traceable artifacts, reusable metadata, and clear attribution. The software citation principles motivate explicit and standardized metadata for research software so that software contributions can be identified, credited, and traced [@smith2016_software_citation_principles]. The FAIR principles provide a recognized framework for improving the findability, accessibility, interoperability, and reusability of research outputs [@wilkinson2016_fair_principles].

These references support the paper's emphasis on documented artifacts, reproducible workflow records, and versioned evidence. They do not imply that a repository is scientifically valid merely because it is documented, cited, or organized according to reproducibility-oriented principles. In this manuscript, software citation and FAIR-oriented framing are used as governance context, not as substitutes for scientific validation or peer review.

### 9.4 Scientific software validation and verification

The current seed bibliography does not include a dedicated scientific software verification-and-validation reference. For that reason, this subsection remains deliberately bounded. The reproducibility and citation literature motivates traceability and stewardship of research software artifacts [@smith2016_software_citation_principles; @wilkinson2016_fair_principles], but it does not establish solver correctness, numerical convergence, physical validity, or mathematical proof.

Accordingly, this paper separates CI evidence, workflow evidence, repository evidence, and scientific validity. Passing tests or documenting validation artifacts can support operational confidence and auditability within the repository, but it does not imply proof of the Navier-Stokes problem, validation of three-dimensional behavior, or general numerical correctness. Additional venue-specific V&V references may be required before journal submission if the manuscript expands claims about numerical validation.

### 9.5 Human-in-the-loop AI systems and agentic review roles

The AI-assisted software-engineering literature motivates interest in LLM-supported engineering workflows, but the verified seed references do not establish that AI agents can independently validate scientific claims [@waseem2023_llms_se_slr; @humayoun2020_dl_se_slr]. This limitation is central to the workflow studied here: agentic roles are treated as review aids and structured control points, not autonomous scientific authorities.

The paper's human-in-the-loop framing therefore remains fail-closed. AI-generated recommendations, review comments, or implementation suggestions require human acceptance and repository-grounded validation before they can affect the scientific record. This positioning supports the manuscript's governance contribution without claiming AI autonomy, independent scientific judgment, or causal improvements in research productivity.

### 9.6 Positioning of this paper

This paper is positioned at the intersection of AI-assisted software engineering, empirical repository-based software engineering, and research software reproducibility. Existing AI-for-SE reviews provide context for the breadth and uncertainty of AI-assisted engineering evidence [@waseem2023_llms_se_slr; @humayoun2020_dl_se_slr]. Repository-mining literature supports a cautious interpretation of GitHub-derived case-study evidence [@ayala2020_oss_challenges_github_slr]. Software citation and FAIR-oriented work motivate traceability, stewardship, and artifact governance for research software [@smith2016_software_citation_principles; @wilkinson2016_fair_principles].

The contribution of this paper is therefore not a CFD novelty claim, a mathematical result, or a general claim that AI improves software engineering. It is a conservative, repository-grounded case study of a controlled AI-assisted scientific engineering workflow with explicit evidence boundaries, human review, rollback discipline, and fail-closed validation semantics.

This related-work section is intentionally scoped to verified seed references. Additional venue-specific references may be added before journal submission, but no unsupported claims are introduced here.

## 10. Conclusion

This draft presents a conservative, evidence-grounded case study of controlled AI-assisted scientific engineering. The repository records a workflow that combines human-in-the-loop decisions, explicit scientific non-claims, rollback discipline, validation artifacts, CI evidence, and specialized agentic review roles.

Across the current evidence base, the repository documents repeated governance controls and operational validation signals. The paper's contribution is a reproducible evidence protocol and descriptive case-study framework for studying controlled AI-assisted engineering in computational research. It does not claim that AI independently validates science, that the workflow improves productivity, that CI proves scientific validity, or that the repository establishes 3D Navier-Stokes results.

## Appendix A: Evidence artifacts

| Artifact | Purpose |
|---|---|
| `paper_outline.md` | Paper plan and claim boundaries |
| `evidence_protocol.md` | Evidence collection and interpretation protocol |
| `pr_evidence_dataset.csv` | PR-level governance and validation classifications |
| `evidence_metrics.md` | Descriptive PR evidence metrics |
| `pr_metadata_dataset.csv` | Objective PR lifecycle metadata |
| `metadata_metrics.md` | Metadata-derived descriptive metrics |
| `pr_ci_outcomes.csv` | CI outcome rows for PR #31-#68 |
| `ci_metrics.md` | CI metrics summary |
| `ci_outcomes_notes.md` | CI outcome notes |
| `ci_backfill_31_40.md` | CI backfill notes for PR #31-#40 |
| `ci_backfill_41_50.md` | CI backfill notes for PR #41-#50 |
| `ci_backfill_51_68.md` | CI backfill notes for PR #51-#68 |

## Appendix B: Claim boundaries

| Allowed claim | Prohibited claim |
|---|---|
| The repository provides a longitudinal case study of controlled AI-assisted scientific engineering. | AI solved Navier-Stokes. |
| PR evidence records repeated governance controls. | The repository solves 3D Navier-Stokes. |
| CI outcomes include successes and failures. | CI success proves scientific validity. |
| Agent roles were documented as review responsibilities. | Agents independently validated scientific truth. |
| The workflow is auditable through GitHub artifacts. | The workflow caused productivity improvement. |
| The case study supports descriptive evidence. | The findings generalize to all scientific software projects. |

## Appendix C: Tables to finalize before submission

| Table/Figure | Status | Required action |
|---|---|---|
| Evidence datasets table | Drafted | Verify against final repository snapshot |
| Governance metrics table | Drafted | Recompute if datasets change |
| CI outcomes table | Drafted | Verify after final CI backfill decision |
| Agent roles table | Drafted | Confirm final agent names and responsibilities |
| Allowed/prohibited claims table | Drafted | Review before venue submission |
| Workflow architecture figure | Pending | Create diagram |
| Evidence-building timeline figure | Pending | Create timeline for PR #63-#75 or final range |
| CI outcome timeline figure | Pending | Create from `pr_ci_outcomes.csv` |

## Publication note

The most defensible publication path is to first release a preprint after external references and figures are completed, then submit to a venue focused on scientific software engineering, research software reproducibility, or empirical software engineering. This draft should not be submitted until the Related Work section contains verified citations and the figures/tables are finalized.
