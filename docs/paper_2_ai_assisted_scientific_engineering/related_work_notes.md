# Related Work Notes (Seed)

## Purpose

This file records the initial controlled notes for Paper 2 related-work preparation before any citation insertion into `paper_draft.md` and before creating `references.bib`.

The goal is to keep an evidence-first and fail-closed process for literature usage.

## Accepted candidate sources for this seed phase

The following candidates are currently accepted for metadata-verified mapping only:

1. Software Citation Principles (PeerJ Computer Science, 2016), DOI: `10.7717/peerj-cs.86`.
2. FAIR Guiding Principles for scientific data management and stewardship (Scientific Data, 2016), DOI: `10.1038/sdata.2016.18`.
3. Large Language Models for Software Engineering: A Systematic Literature Review, arXiv: `2308.10620`.
4. Open Source Software Development Challenges: A Systematic Literature Review on GitHub, arXiv: `2003.10750`.
5. A Systematic Literature Review on the Use of Deep Learning in Software Engineering Research, arXiv: `2009.06520`.

These entries are tracked in `literature_review_map.csv` with `verification_status=verified_metadata_pending_full_review`.

## Discarded or not-yet-used sources

At this stage, the following are explicitly not used as primary academic support:

- news articles;
- blog posts;
- social media threads;
- marketing pages;
- sources without verifiable title/authors/year/DOI or canonical URL;
- references that cannot be mapped to a narrow manuscript claim.

No additional external sources are introduced in this seed note.

## Anti-overclaim warnings

- Do not claim that external literature proves scientific validity of this repository.
- Do not claim that CI outcomes prove scientific validity.
- Do not claim that AI independently validates science.
- Do not claim mathematical proof from workflow/process references.
- Do not claim productivity improvement without direct empirical evidence from this study.
- Do not generalize beyond the bounded case-study scope without explicit qualified evidence.

## Next steps before `references.bib`

1. Complete full-text claim-level review for each mapped source.
2. Confirm exact claim-to-source alignment sentence by sentence.
3. Mark weak/partial support and narrow manuscript wording where needed.
4. Run anti-hallucination checklist on all mapped rows.
5. Obtain review decisions from `kansodata-scientific-literature-auditor` and `kansodata-advocatus-diaboli`.
6. Only then prepare `references.bib` and citation insertion PR(s).

## Notes for `kansodata-scientific-literature-auditor`

- Verify that every mapped row has title, authors, year, and DOI/canonical URL.
- Confirm each candidate supports only the narrow claim declared in `claim_supported`.
- Block any attempt to use internal repository evidence as external literature support.
- Block any invented citation, fake DOI, unverifiable URL, or claim-source mismatch.
- Keep separation strict between:
  - external literature evidence;
  - internal repository evidence;
  - CI evidence;
  - workflow evidence;
  - scientific validity;
  - mathematical proof;
  - productivity claims.

## Rollback plan

If this seed note is rejected, revert only:

- `docs/paper_2_ai_assisted_scientific_engineering/literature_review_map.csv`
- `docs/paper_2_ai_assisted_scientific_engineering/related_work_notes.md`

No rollback of code, tests, CI, datasets, notebooks, solver, or manuscript body is required.
