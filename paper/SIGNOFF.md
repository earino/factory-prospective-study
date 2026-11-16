# Current paper evidence and verification — 16 November 2026

The seven-page draft includes all twelve consumer datasets and 36 scored models.
Consumer evaluation and selected-code review are complete. **Production accounting
still ends at 15 November, 14:24 UTC. Final sign-off remains open until the
scheduled 16 November, 07:00 UTC production export is reconciled and integrated.**
The paper has not been submitted, and the evidence repository remains private.

Earlier draft records are preserved in
[the sign-off history](analysis/final-2026-11-16/SIGNOFF-HISTORY.md).

## Claim-to-evidence mapping

- **Continuing factory and automatic dataset decisions.** Production records
  and the maintenance inventory distinguish two generic service changes—inference
  routing and worker-reservation accounting—from dataset decisions. No manual
  source, label, candidate-state or acceptance change was recorded in the inspected
  window. See [the SBIR and maintenance audit](analysis/final-2026-11-16/SBIR-ACCEPTANCE-AUDIT.md).
  Reconcile any later service events with the final export.
- **11 publications, 394 stage attempts, and recurring cost of $27.84–$27.94.**
  These remain the measured 64.93-hour window, not the final observation window.
  [Cost evidence](../evidence/costs/2026-11-15/REPORT.md) includes failed production
  attempts, temporary workers and allocated hosting. It excludes development,
  labor and independent consumer evaluation. The $2.53–$2.54 publication ratio is
  not cost per validated useful benchmark or a measured saving over human work.
- **Twelve datasets, 36 scored models, 49 physical research attempts.**
  [The completed consumer snapshot](analysis/consumer-complete-inputs-2026-11-16.json)
  retains original and recovery summaries, pins, and report hashes. The record
  contains 36 scored outcomes, twelve provider failures and one premature stop.
  Seattle combines the fresh r1 with unchanged r2/r3; its original stop remains
  recorded. [The composite provenance](analysis/final-2026-11-16/seattle-composite/provenance.json)
  and [baseline agreement check](analysis/final-2026-11-16/seattle-composite/prediction-agreement.json)
  document that combination. No successful model was selected by holdout score.
- **Modeling headroom.** All three models exceed untuned XGBoost on eleven of
  twelve datasets. All three intervals are positive for seven datasets against
  the untuned control and five against tuned random search. Drinking-water has
  two positive intervals against the untuned control. The other comparisons and
  every run remain visible in Table I and Figure 3.
  [Numerical verification](analysis/revision-checks.json) checks these claims
  against saved scores and paired bootstrap reports. Intervals are conditional
  on the fitted models, cohort and declared dependence groups.
- **Exact evaluated artifacts.** All twelve releases have passing original
  worker qualification reports accepted against the full saved study artifacts.
  [Qualification coverage](analysis/final-2026-11-16/qualification-coverage.json)
  links version-bound receipts. No dataset or model was changed for this review.
- **Selected-code and conduct checks.**
  [The review](analysis/final-2026-11-16/CODE-CONDUCT-REVIEW.md) covers all 36 selected
  solutions, their relevant fitting/preparation code, flagged requests and targeted
  follow-up. It found no observed prohibited holdout read. Sampled batch/order
  and own-label probes pass for all 36; three earlier checker errors were resolved
  by accounting for actual training-row mappings, without modifying models.
  Two recorded external events are pandas dependency imports, not data reads.
  This is bounded review, not proof of complete compliance or technical isolation.
- **SBIR acceptance failure.**
  [Original acceptance evidence](analysis/final-2026-11-16/sbir-acceptance/checks.json)
  verifies the published builder and population text in the original prompt.
  The full selection declaration was absent. The reviewer saw and accepted
  later-record exclusions as label handling but did not reconcile them with all
  population claims. A separate pre-scoring review found the contradiction in
  the published code and declaration. We do not claim that adding the declaration
  would necessarily have changed acceptance or quantify the effect on scores.
- **Transferable lessons and related work.** Section V distinguishes observed
  controls from proposed design responses; no controlled effectiveness claim is
  made. The 22 references and bounded cost comparisons are documented in
  [the literature notes](materials/VERIFIED-LITERATURE-NOTES.md).

## Verification of this draft

[QA.json](output/QA.json) records the PDF/source hashes, seven-page count, embedded
fonts, absence of overfull boxes or unresolved references, and matching text from
a clean portable-source build. All seven rendered pages were inspected after the
consumer update. [The clean-checkout receipt](analysis/final-2026-11-16/consumer-complete-clean-check.json)
records an independent checkout build and numerical verification. Earlier evidence
snapshots retain their original hashes.

The current PDF is [paper.pdf](output/paper.pdf); the portable source is
[paper-source.zip](output/paper-source.zip). Exact-commit CI is checked after push.

## Remaining closure and genuine limits

Integrate the scheduled final production export, recalculate costs, reconcile
later service events and update all production counts and dates. Repeat numerical,
clean-build and page checks on that final artifact; then record its commit and CI.

The consumer cohort is closed and complete. No additional consumer experiment is
needed. PHMSA penalties lack an operator grouping, so their differences have no
intervals. Other grouping and historical-timing limits, the SBIR population
mismatch, and wastewater's scoring-access dependence remain explicit. We do not
claim general factory reliability, universal benchmark validity, total economic
cost, or technically enforced consumer isolation.
