# Paper 2 Anti-Hallucination Checklist

## 1. Title

Anti-Hallucination Checklist for Paper 2 Bibliographic and Publication Phase

## 2. Purpose

Provide a fail-closed control checklist to prevent invented citations, unsupported claims, source misuse, and evidence-category confusion during Paper 2 preparation.

This checklist is designed to protect claim integrity for:

- citation verification;
- claim-to-source alignment;
- related-work drafting;
- preprint/submission readiness review.

## 3. Scope

This checklist applies to documentation and manuscript workflow artifacts related to:

- `paper_draft.md`;
- `publication_plan.md`;
- `literature_review_plan.md`;
- `literature_review_map.csv` (when created);
- citation-insertion PRs;
- related-work and discussion claim updates.

It is a documentation governance control, not a solver/CI/test control.

## 4. When this checklist is mandatory

Run this checklist before merge of any PR that:

- adds or edits citations;
- adds or edits related-work paragraphs;
- modifies claim strength tied to external literature;
- updates publication-facing manuscript text;
- changes claim boundaries involving AI, reproducibility, CI, scientific validity, or productivity.

## 5. Bibliographic verification checklist

For each reference candidate, confirm all required metadata:

1. title present and consistent;
2. authors present and consistent;
3. year present and consistent;
4. DOI present and valid, or canonical URL present and valid when DOI is unavailable;
5. source type acceptable for the claim category;
6. reference traceable to a concrete manuscript claim.

If any required field is missing for a required citation, fail closed.

## 6. Claim-to-source alignment checklist

For each cited sentence or paragraph:

1. the source explicitly supports the exact sentence scope;
2. wording does not exceed what the source states;
3. causal language is avoided unless explicitly evidenced;
4. generalization is bounded to what the source supports;
5. claim category matches source category (method, context, limitation, policy);
6. if support is partial, claim text is narrowed.

## 7. Forbidden patterns

Do not allow:

- placeholder citations presented as real;
- “citation laundering” (using one source to imply unsupported claims);
- decorative citations with no claim linkage;
- source-title paraphrase as evidence without reading the source;
- using CI/tooling references as proof of scientific validity;
- converting internal repo observations into external literature claims;
- attributing autonomous scientific authority to AI agents.

## 8. Evidence separation checklist

Verify strict separation between:

- external literature evidence;
- internal repository evidence;
- CI evidence;
- workflow evidence;
- scientific validity;
- mathematical proof;
- productivity claims.

Required rule:

- A sentence must not mix categories in a way that inflates claim strength.

Examples:

- CI pass != scientific validity.
- Internal PR history != external literature evidence.
- Workflow documentation != mathematical proof.

## 9. DOI/URL verification checklist

For each reference:

1. DOI resolves to the expected title/authors/year, or canonical URL resolves to expected source;
2. URL is stable/canonical (publisher, proceedings, arXiv canonical entry, official venue page);
3. no shortened or opaque redirect links as primary reference;
4. no dead/unreachable primary links for required references;
5. DOI/URL captured exactly in citation map artifact.

If DOI/URL cannot be verified, treat as blocked for required claims.

## 10. Related Work checklist

Before marking Related Work as ready:

1. all subsection claims mapped to verified sources;
2. no unsupported bridge from software-engineering literature to scientific-proof claims;
3. no reframing as pure CFD novelty paper;
4. no implicit claim that references validate repository results directly without matching evidence chain;
5. limitations and threats-to-validity wording remains conservative.

## 11. Paper draft citation insertion checklist

Before inserting any citation into `paper_draft.md`:

1. reference has bibliographic verification pass;
2. a corresponding `literature_review_map.csv` row exists;
3. claim text has been reviewed for overclaim risk;
4. evidence category separation has been checked;
5. insertion includes only claims supported by verified source content;
6. unresolved concerns are documented as observations or blockers.

## 12. Agent review checklist

Minimum review path for citation-impacting PRs:

1. `kansodata-scientific-literature-auditor` checks bibliographic validity and claim support;
2. `kansodata-advocatus-diaboli` challenges overclaim and unsupported extrapolation;
3. `kansodata-reproducibility-and-ci-auditor` checks boundary between workflow/CI evidence and scientific claims;
4. `kansodata-chief-scientific-reviewer` consolidates final decision.

Agents are review roles only. They do not replace human scientific review or peer review.

## 13. P0 blockers

Any of the following is a merge/publication blocker:

- invented citation;
- fake DOI;
- unverifiable URL;
- missing title/authors/year;
- source does not support the sentence where it is cited;
- citation inserted without `literature_review_map.csv` row;
- internal repo evidence presented as external literature;
- claim that AI independently validates science;
- claim that CI proves scientific validity;
- productivity improvement claim without direct empirical evidence.

Decision rule:

- any `P0` => `blocked`.

## 14. P1 issues

Must be corrected before formal submission; may be allowed with explicit follow-up before merge when non-critical:

- weak but not false source class used for secondary context;
- imprecise wording that overstates scope without direct contradiction;
- incomplete limitations wording for a citation-backed claim;
- ambiguous section-level mapping in literature review notes;
- missing canonical-source normalization where source is still verifiable.

Decision guidance:

- unresolved `P1` => `approved_with_observations` only if no `P0` exists.

## 15. Required PR evidence before merge

A citation-impacting PR must include:

1. explicit list of edited claims/sentences;
2. citation verification evidence for each new/modified reference;
3. claim-to-citation mapping evidence (including `literature_review_map.csv` row reference);
4. statement confirming evidence-category separation;
5. reviewer decision (`approved`, `approved_with_observations`, or `blocked`);
6. rollback note for documentation-only reversion.

## 16. Rollback plan

If this checklist update must be reverted, revert only:

- `docs/paper_2_ai_assisted_scientific_engineering/anti_hallucination_checklist.md`

Do not change code, tests, CI, datasets, notebooks, or paper data artifacts as part of this rollback.
