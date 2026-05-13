# Evidence Protocol for AI-Assisted Scientific Engineering Paper

## 1. Study design

This study analyzes a longitudinal GitHub-based case study of AI-assisted scientific software engineering. The case is the `navier-stokes-computational-research` repository, a controlled 2D incompressible periodic pseudo-spectral Navier-Stokes research project.

The objective is to evaluate how an AI-assisted, human-in-the-loop workflow can encode reproducibility, scientific boundary control, fail-closed validation, rollback discipline, and agentic review into day-to-day computational research engineering.

This protocol intentionally treats AI assistance as part of an engineering workflow, not as an autonomous scientific authority.

## 2. Unit of analysis

Each GitHub Pull Request is treated as one engineering event.

A PR may be classified as one or more of:

- solver change;
- validation harness change;
- test or CI governance change;
- documentation or scientific evidence change;
- agent specification change;
- benchmark or diagnostic infrastructure change;
- hotfix or regression repair.

## 3. Evidence sources

Allowed evidence sources are:

1. Pull request metadata:
   - PR number;
   - title;
   - body;
   - changed files;
   - merge state;
   - timestamps when available.
2. Validation evidence:
   - GitHub Actions result;
   - reported local validation commands;
   - validation artifact status;
   - `scripts/check_validation_status.py` results when available.
3. Repository artifacts:
   - docs;
   - validation JSON schemas;
   - test files;
   - scientific reports;
   - benchmark artifacts.
4. Human-AI workflow evidence:
   - prompts used for Codex or assistant-guided changes;
   - explicit user instructions;
   - agent responsibility documents;
   - review/audit documents.
5. Failure evidence:
   - failed tests;
   - bugfix PRs;
   - rejected or narrowed claims;
   - fail-closed outcomes;
   - rollback notes.

## 4. Classification schema

Each PR-level observation should include:

- `pr_number`: GitHub PR number.
- `title`: PR title.
- `change_type`: coarse category of change.
- `agent_related`: whether the PR introduces, updates, or operationalizes an agentic review role.
- `scientific_scope`: scope of the change, such as `documentation`, `validation`, `solver`, `benchmark`, or `governance`.
- `validation_evidence`: commands, checks, or artifacts reported.
- `ci_or_manual_validation`: one of `ci`, `manual`, `reported_manual`, `not_required`, `unknown`.
- `rollback_present`: `true`, `false`, or `unknown`.
- `non_claims_present`: whether explicit scientific limitations or non-claims are documented.
- `defect_or_risk_type`: defect class or risk class addressed.
- `governance_control`: control introduced or exercised.
- `outcome`: accepted, merged, rejected, superseded, diagnostic_only, human_review_required, or unknown.
- `evidence_notes`: concise traceability note.

## 5. Metrics

The paper may compute the following metrics only after dataset coverage is sufficient:

### 5.1 Governance coverage

- Percentage of PRs with rollback plans.
- Percentage of PRs with explicit scientific non-claims.
- Percentage of PRs with validation evidence.
- Percentage of PRs marked documentation-only, solver, validation, benchmark, or governance.

### 5.2 Defect and risk handling

- Count of numerical defects identified and corrected.
- Count of serialization/reproducibility defects corrected.
- Count of physical overinterpretation risks explicitly narrowed.
- Count of fail-closed checks introduced.
- Count of validation artifacts upgraded from diagnostic-only to blocking checks.

### 5.3 Agentic governance

- Count of agent roles introduced.
- Count of PRs referencing agentic review or multi-agent audit.
- Count of PRs where claim boundaries were narrowed by review.
- Count of human-review-required artifacts.

### 5.4 Productivity and documentation

Productivity claims must be conservative. Acceptable measures include:

- number of documentation artifacts created;
- number of validation harnesses introduced;
- number of tests added;
- PR turnaround time only when timestamps are available and interpreted cautiously.

The paper must not claim broad productivity improvements unless supported by explicit measured evidence.

## 6. Failure taxonomy

Failures and risks should be classified as:

### 6.1 Numerical defects

Examples:

- de-aliasing errors;
- convergence interpretation errors;
- unstable timestep handling;
- spectral leakage or high-wavenumber contamination;
- invalid tolerance relaxation.

### 6.2 Physical interpretation defects

Examples:

- unsupported turbulence claims;
- overinterpretation of 2D evidence;
- treating diagnostic artifacts as formal validation;
- claiming physical truth beyond the tested regime.

### 6.3 Reproducibility defects

Examples:

- non-deterministic outputs;
- missing artifact status;
- invalid JSON serialization;
- undocumented commands;
- missing validation reports.

### 6.4 Governance defects

Examples:

- missing rollback plan;
- absent scope boundary;
- absent validation command;
- unclear human review requirement;
- missing CI gate.

### 6.5 AI-induced or AI-amplified risks

Examples:

- hallucinated references;
- unsupported scientific claims;
- unsafe refactors;
- hidden scope expansion;
- unverified generated documentation.

An AI-induced risk may be recorded only when there is direct evidence from prompts, diffs, review comments, or documented human correction. Otherwise classify as `unknown` rather than infer causality.

## 7. Governance taxonomy

Governance controls include:

- explicit scope control;
- rollback plan;
- fail-closed CI or artifact check;
- required validation command list;
- human review requirement;
- diagnostic-only labeling;
- non-claims section;
- agentic review role;
- adversarial review;
- numerical audit;
- physical validation;
- documentation audit;
- reproducibility and CI audit.

## 8. Treatment of prompts and chat-derived evidence

Prompts used to guide Codex or assistant-led work may be used as evidence only if they are preserved in repository documentation, issue/PR text, or a curated prompt log.

This interaction is itself part of the methodological chain: the user explicitly authorized direct GitHub execution instead of Codex and requested that the prompt and step be considered for the paper. This event should be represented as human-in-the-loop workflow evidence, not as autonomous AI action.

Prompt-derived evidence must distinguish:

- user intent;
- assistant recommendation;
- actual repository change;
- validation result;
- human approval or review.

## 9. Explicit non-claims for the paper

The paper must not claim:

- that AI solved Navier-Stokes;
- that the repository solves 3D Navier-Stokes;
- that the workflow proves mathematical correctness;
- that agents are deterministic validators;
- that AI replaces numerical analysts, physicists, or reviewers;
- that improvements generalize beyond the observed case without qualification;
- that productivity or defect reduction was achieved unless measured.

## 10. Threats to validity

### 10.1 Internal validity

- Single-project case study.
- Human author and assistant are part of the same workflow.
- PR text may omit failed intermediate attempts.
- Some validation is reported manually and may not be independently re-executed in the PR body.

### 10.2 External validity

- Findings may not generalize beyond scientific Python repositories.
- CFD-specific validation may not generalize to other scientific domains.
- Small or private repositories may have different collaboration dynamics.

### 10.3 Construct validity

- `productivity` is difficult to measure rigorously.
- `defect prevented` may be ambiguous without a counterfactual baseline.
- Agent involvement may be hard to separate from human oversight.

### 10.4 Temporal validity

- AI model behavior changes over time.
- GitHub Actions and tooling versions evolve.
- Repository governance maturity improves during the observation period.

## 11. Rules for adding evidence

1. Do not invent missing data.
2. Use `unknown` when evidence is unavailable.
3. Use `reported_manual` when validation was reported in PR text but not independently reproduced in this dataset.
4. Do not infer AI causality without direct prompt or review evidence.
5. Preserve explicit scientific boundaries.
6. Prefer narrow, traceable claims.
7. Record both successful and failed events.
8. Keep raw evidence separate from interpretation.
9. Do not use the dataset to claim statistical significance until coverage is complete.
10. Keep the study human-in-the-loop by design.
