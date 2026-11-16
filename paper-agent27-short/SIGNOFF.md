# Short-paper verification

This receipt covers the five-page draft dated 16 November 2026. It records the
writing task, not conference submission or an assurance of acceptance.

## Scope and evidence

- Separate short version: `draft/main.tex`; the longer paper remains in `../paper/`.
- Five-page IEEE manuscript including references and disclosure: `output/paper.pdf`
  and the page/layout checks in `output/QA.json`.
- Production system and autonomy boundary: pinned factory-code inspection recorded
  in `analysis/RECORD-INPUTS.md`, reflected in Sections II and III.
- Operating record: 81.53 hours, 14 publications, 540 attempts, stage milestones,
  retries and publication latencies checked against frozen records by
  `scripts/verify_records.py`; results in `analysis/record-checks.json`.
- Recurring expenditure and stage allocation: `analysis/stage-costs.json` reconciles
  both original total-cost endpoints. The figure uses recorded model and worker
  stages; hosting remains shared. Boundaries are stated in the cost method.
- Consumer use: all twelve cohort releases have frozen, scored models in retained
  records. The short paper reports completion, with procedural isolation stated,
  and omits AUC, headroom and random-search comparisons.
- Fourteen-release table: record timestamps and selected source-review findings are
  mapped in `analysis/release-records.json`. The last two releases are marked not
  evaluated. Review scope and differing publisher-document access are stated.
- SBIR: original builder identity, review prompt and response checked against the
  retained acceptance packet. The manuscript distinguishes the observed mismatch
  from the untested missing-declaration counterfactual and proposed remedy.
- Wastewater: conditional scoring access is distinguished from observed leakage.
- Engineering lessons separate demonstrated recovery from proposed controls.
- Related work: thirteen citations drawn from the verified literature record;
  no efficiency ranking across different accounting boundaries.
- Prose inspected for writing-process commentary, scope inflation and repeated
  qualifications; the manuscript states the final study and findings directly.
- All 310 original longer-paper files preserve their recorded SHA-256 values.

## Artifact verification

`output/QA.json` records the PDF, manuscript, source-archive and record-check hashes.
The portable archive was extracted into a temporary directory and built there;
its PDF text matches the working version. All five pages were visually reviewed,
all fonts are embedded, and LaTeX reports no overfull boxes or unresolved references.
The normal IEEE class and bibliography style are included in the source archive.

The automated record checks verify recorded quantities and identities. Manual
claim review and page inspection cover interpretation and presentation; passing
the script alone is not a claim that every sentence is correct.

## Delivery

The manuscript is ready for Eduardo's next editorial review. This checkpoint will
be committed and pushed with the repository's exact-commit CI checked before
completion is reported. CI results remain available in GitHub Actions for the
commit carrying this receipt. The repository remains private; nothing is submitted.
