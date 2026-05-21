# Literature Review Plan for Paper 2

## 1. Purpose

This document defines the evidence-first literature review protocol for Paper 2:

**Controlled AI-Assisted Scientific Engineering: A Fail-Closed Human-in-the-Loop Workflow for Reproducible Computational Research**

The goal is to move from an internal repository-grounded draft to a submission-ready manuscript without introducing unsupported references, weak sources, inflated claims, or invented citations.

This plan is intentionally procedural. It does not perform the literature review itself and does not add external claims.

## 2. Current manuscript status

- `paper_draft.md` exists as an internal evidence-grounded draft.
- `publication_plan.md` identifies arXiv `cs.SE` followed by SoftwareX as the preferred route.
- The Related Work section remains pending verified external citations.
- Submission is blocked until references are verified, mapped, and audited.

## 3. Scope of the literature review

The review must cover five areas:

1. AI-assisted software engineering and code generation.
2. Human-in-the-loop and agentic AI workflows.
3. Research software engineering, reproducibility, and software citation.
4. Empirical software engineering methods for repository-based case studies.
5. Scientific software verification, validation, and numerical reproducibility.

The review must support the paper's workflow/governance framing. It must not reposition the paper as a pure CFD or numerical-analysis contribution.

## 4. Accepted source types

Preferred source classes:

- peer-reviewed journal articles;
- peer-reviewed conference papers;
- reputable workshop papers where scope matches research software or AI-assisted software engineering;
- official venue documentation for SoftwareX/JOSS/arXiv submission requirements;
- well-known standards or authoritative guidance for research software citation, reproducibility, or artifact evaluation;
- arXiv preprints only when clearly relevant and when peer-reviewed alternatives are unavailable or less current.

## 5. Prohibited or weak source types

Do not use as primary scholarly support:

- blogs as main evidence;
- marketing pages;
- vendor documentation for broad scientific claims;
- uncited social-media discussions;
- hallucinated references;
- papers whose title/DOI/authors cannot be verified;
- references copied from another model output without independent verification;
- generic AI articles that do not connect to software engineering, research software, reproducibility, or human-in-the-loop governance.

Weak sources may be used only as background notes, not as manuscript citations, unless explicitly justified.

## 6. Search strategy

Search should be performed in a controlled way across these targets:

- ACM Digital Library;
- IEEE Xplore;
- SpringerLink;
- Elsevier/ScienceDirect;
- arXiv;
- Google Scholar for discovery only, followed by verification at publisher/arXiv/DOI source;
- SoftwareX and JOSS archives;
- Empirical Software Engineering and Journal of Systems and Software archives.

Suggested query groups:

### 6.1 AI-assisted software engineering

- `AI-assisted software engineering empirical study`
- `large language models code generation software engineering study`
- `LLM coding assistants software engineering productivity limitations`
- `AI coding assistant reliability software engineering`

### 6.2 Human-in-the-loop and agentic workflows

- `human-in-the-loop AI software engineering workflow`
- `agentic software engineering workflow human oversight`
- `LLM agents software engineering review workflow`
- `human oversight AI-assisted coding`

### 6.3 Research software engineering and reproducibility

- `research software engineering reproducibility governance`
- `scientific software reproducibility software citation`
- `research software citation principles`
- `software artifact reproducibility computational science`

### 6.4 Empirical repository-based studies

- `GitHub mining software repositories empirical study methodology`
- `repository mining threats to validity software engineering`
- `pull request data empirical software engineering limitations`
- `longitudinal GitHub case study software engineering`

### 6.5 Scientific software V&V

- `scientific software verification validation computational science`
- `numerical software verification validation reproducibility`
- `scientific computing validation verification software engineering`
- `continuous integration scientific software validation`

## 7. Evidence extraction template

Each candidate reference must be recorded using this template before it can enter `references.bib`:

```text
title:
authors:
year:
venue/source:
doi_or_url:
source_type:
verified_at:
verified_by:
relevance_area:
claim_supported:
exact_paper_section:
use_as:
  - background
  - method support
  - related work
  - venue/scope support
limitations:
notes:
```

A reference must not be used if `title`, `authors`, `year`, and either DOI or canonical URL cannot be verified.

## 8. Agent-assisted review roles

The literature review should use the repository's agentic review model as a quality-control process. These are review responsibilities, not autonomous authorities.

| Review role | Repository-aligned agent | Responsibility |
|---|---|---|
| Literature relevance auditor | `kansodata-scientific-literature-auditor` if present, otherwise chief reviewer responsibility | Check that cited work is relevant to the exact claim. |
| Adversarial claim reviewer | `kansodata-advocatus-diaboli` | Block overclaiming and weak source usage. |
| Chief scientific reviewer | `kansodata-chief-scientific-reviewer` | Consolidate review decisions and resolve conflicts. |
| Reproducibility and CI auditor | `kansodata-reproducibility-and-ci-auditor` | Ensure cited claims do not exceed repository evidence or reproducibility artifacts. |
| Numerical methods auditor | `kansodata-numerical-methods-auditor` | Ensure V&V or numerical claims are not overstated. |

Agent outputs should be recorded as review notes, not as citations.

## 9. Inclusion criteria

A source can be included if it satisfies all of the following:

- directly supports one or more claims in `paper_draft.md`;
- has verified bibliographic metadata;
- comes from an acceptable source class;
- can be mapped to a specific manuscript section;
- does not force unsupported claims beyond the repository evidence;
- improves the paper's positioning, methodology, or limitations.

## 10. Exclusion criteria

Exclude sources that:

- are not verifiable;
- are only loosely related to AI in general;
- support claims the paper should not make;
- mainly discuss CFD or Navier-Stokes science without contributing to workflow/governance framing;
- duplicate stronger or more authoritative sources;
- introduce venue or domain drift away from software engineering/research software.

## 11. Required citation map before editing paper_draft.md

Before updating `paper_draft.md`, create a citation map with at least these columns:

```text
reference_key,section,claim_supported,source_strength,notes
```

Expected future file:

```text
docs/paper_2_ai_assisted_scientific_engineering/literature_review_map.csv
```

Only after this map exists should citations be inserted into the draft.

## 12. Expected future artifacts

The literature review phase should produce, in order:

1. `literature_review_plan.md` (this file).
2. `literature_review_map.csv`.
3. `references.bib`.
4. Updated `paper_draft.md` Related Work section.
5. Optional `related_work_notes.md` for rejected/weak sources and rationale.

## 13. Minimum target coverage

Before preprint submission, the paper should include verified references for at least:

- 3-5 sources on AI-assisted software engineering or code generation;
- 2-4 sources on human-in-the-loop or agentic AI workflows;
- 3-5 sources on research software engineering, reproducibility, or software citation;
- 2-4 sources on empirical software engineering / repository mining methodology;
- 2-4 sources on scientific software V&V or numerical reproducibility.

Quality is more important than count. Do not include padding references.

## 14. Citation and claim discipline

Every citation must support a specific sentence or paragraph. Citations must not be used decoratively.

Do not cite a source to support a claim it does not make.

Do not use citations to imply:

- this repository is scientifically validated beyond its documented scope;
- the workflow improves productivity;
- the workflow reduces defects causally;
- AI agents independently validate scientific truth;
- CI success proves scientific validity;
- the case study generalizes beyond its observed setting.

## 15. Review checklist before merge of any citation PR

A citation PR should pass this checklist:

- All references have verified title, authors, year, and DOI or canonical URL.
- Each reference appears in `literature_review_map.csv`.
- Each citation is tied to a concrete manuscript claim.
- No citation supports a prohibited claim.
- Related Work distinguishes external literature from internal repository evidence.
- Threats to Validity remain conservative.
- No generated or unverified bibliography entries are present.

## 16. Rollback plan

If this literature review plan is not accepted, revert only:

```text
docs/paper_2_ai_assisted_scientific_engineering/literature_review_plan.md
```

No code, CI, dataset, notebook, solver, or publication artifact rollback is required for this documentation-only change.
