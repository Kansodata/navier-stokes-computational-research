# Publication Plan for Paper 2

## 1. Publication status
- Current status: documentation and evidence artifacts are in repository; publication has not started.
- This plan defines a conservative, staged route for submission readiness.
- No claim is made here that the manuscript is currently accepted, peer-reviewed, or publication-ready without final checks.

## 2. Recommended publication path
- Stage 1: prepare and release a preprint for public timestamping and community visibility.
- Stage 2: submit to one primary software-engineering-oriented venue.
- Stage 3: keep a conservative fallback list of alternative venues if scope/fit feedback requires redirection.

## 3. Preprint path: arXiv
- Recommended first release: arXiv under `cs.SE` (Software Engineering).
- Positioning: controlled AI-assisted scientific engineering workflow with fail-closed controls and reproducibility evidence.
- Explicitly avoid positioning as a pure CFD-results paper.

## 4. Formal venue candidates
- SoftwareX.
- JOSS.
- Empirical Software Engineering.
- Journal of Systems and Software.
- Research Software Engineering / AI-assisted Software Engineering workshop track.

## 5. Recommended primary route
- Primary route: SoftwareX after arXiv preprint.
- Rationale (conservative): SoftwareX is aligned with research software artifacts, reproducibility practices, and engineering workflow reporting.
- Fallback order if needed: JOSS, then Empirical Software Engineering or Journal of Systems and Software, then workshop route.

## 6. Submission-ready checklist
- Final manuscript text aligned with repository evidence scope.
- Claims audit completed: no unsupported statements on productivity, causality, autonomy, or scientific proof.
- Methods section clearly separates workflow evidence from scientific validity evidence.
- Threats/limitations section explicitly present.
- Artifact and data availability statements verified against repository reality.
- Author metadata, affiliations, acknowledgments, and conflict-of-interest declarations reviewed.

## 7. Required figures
- Study timeline figure (PR sequence and governance checkpoints).
- Evidence pipeline figure (inputs, controls, fail-closed gates, outputs).
- CI outcomes summary figure/table derived from `pr_ci_outcomes.csv`.
- Evidence taxonomy figure separating CI/workflow evidence from scientific-validity evidence.
- Reproducibility process diagram (artifact traceability from PR to paper evidence).

## 8. Required external literature review
- Controlled AI-assisted software engineering workflows.
- Research software engineering reproducibility and governance.
- Empirical evidence standards for repository-based longitudinal studies.
- AI-in-the-loop engineering assurance, risk controls, and fail-closed design patterns.
- Venue-specific related-work expectations (SoftwareX/JOSS/EmpSE/JSS) before final submission.

## 9. DOI/release strategy
- Preprint DOI path: use arXiv identifier at preprint stage.
- Repository archival DOI: prepare a versioned release archive (for example Zenodo-linked GitHub release) aligned with submission snapshot.
- Keep manuscript, tag, and artifact snapshot synchronized to a single immutable release reference.

## 10. Double-blind/anonymization decision
- Default decision: non-double-blind preparation for arXiv and likely software-journal routes.
- If a selected venue requires blind review, prepare an anonymized variant package before submission.
- Do not assume blind/non-blind policy without checking the active venue guidelines at submission time.

## 11. Repository readiness checklist
- Paper 2 documentation set present and internally consistent.
- `ci_metrics.md` consistent with `pr_ci_outcomes.csv` and CI backfill notes.
- Evidence references in manuscript map to existing files and commit history.
- Reproducibility instructions executable and minimally complete.
- License, citation metadata, and authorship files current.

## 12. Final pre-submission validation
- Run final documentation consistency check across Paper 2 artifacts.
- Verify all tables/figures are traceable to repository files.
- Verify no claim exceeds available evidence scope.
- Freeze submission snapshot via git tag/release candidate branch.
- Perform one final independent read for editorial consistency and conservative claim language.

## 13. Rollback plan
- If this publication plan needs to be reverted, remove or revert only `docs/paper_2_ai_assisted_scientific_engineering/publication_plan.md` in a dedicated follow-up commit.
- No code, CI, dataset, or notebook rollback is required for this atomic documentation-only change.
