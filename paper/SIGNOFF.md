# Draft evidence and verification — 15 November 2026

**Current revision:** the readability revision at the end of this
file supersedes prior editorial wording. The evening consumer update remains the
evidence boundary. Earlier sections retain the provenance of previous drafts.

**Delivered scope:** a complete seven-page IEEE LaTeX draft, including references,
using the available interim evidence. This is not a final scientific or submission
sign-off. No factory state, release, consumer run, frozen model, or original study
record was modified to produce the draft.

## Evidence boundary

Production window: 12 November 21:27:59 UTC through 15 November 14:24:01 UTC.
Compact inputs captured at 16:09:38 UTC from study commit
`662c7a1b8037e17168018a5a24cbebe885515472`.
The production export and intervention are pinned to factory evidence commit
`f4aaf5cd44d427594811b7168111015fc55b510a`.
`analysis/draft-inputs.json` retains the compact input files and their SHA256 hashes.
It includes original outcomes only, not outcomes of quota-recovery runs.

## Claim-to-record mapping

- **11 publications, all new admissions:** cost inputs `cohort.json`, linked
  publication identities and times; `summary.json` supplies 42 carry-in and 65 new
  candidate records. The latter are search slots, not 107 distinct sources.
- **394 stage attempts and 41/14/11/11 completed candidate milestones:**
  `analysis/render_figures.py` filters both attempt exports by start timestamp,
  counts stage/status pairs, and deduplicates successful milestones by candidate.
  `analysis/derived.json` retains the results. Repeated build successes are not
  additional candidates. This is not a completed-cohort yield estimate.
- **40–189 minutes, median 106 minutes:** same script subtracts candidate creation
  from publication timestamps for the 11 successful releases only.
- **$27.84–$27.94, $2.53–$2.54 per publication:**
  `../evidence/costs/2026-11-15/REPORT.md`, its pinned inputs and calculation script.
  Includes failed production work, workers and allocated hosting; excludes
  development, labor, upstream collection and independent consumer evaluation.
  Tariff timing, currency conversion, boundary sessions and invoice limitations
  are disclosed. All-peak alternative is $39.27 / $3.57 per publication.
- **374 usage sessions, 2,412 calls and token totals; 187 worker lifetimes:**
  same cost summary and detailed model/worker records. Five missing usage entries
  have Scout's pre-generation HTTP 402 readback, not an inferred zero.
- **21 frozen / 12 failed original consumer attempts:** original sealed consumer
  summaries for all eleven pinned dataset identities. Their stale pilot wording
  and cumulative cost totals are not used. Eleven ordinary and released baselines
  have holdout scores. Seven datasets have three scored consumers each.
- **Table I and Figure 3:** saved holdout scores and existing paired bootstrap
  records. All three runs shown, no best-run selection. Figure covers six datasets;
  PHMSA grouping remains unresolved. FDA product-code grouping is partial.
  Bootstrap results are not a completed semantic compliance verdict.
- **19 no-change training-feature probes, two unresolved assertion errors:**
  per-run `training-feature-probes.json` files, read independently of wrapper
  execution status. Errors are FDA run 2 and T100 run 3. No rerun or repaired model
  substituted. All 21 artifact probes report agreement/order invariance on 25 rows.
- **SBIR selection discrepancy:** prescoring review section 5 and pinned
  `reproduction/build.py` (first-year phase selection and firm ambiguity sets),
  compared with `construction.json` population declaration. Code paths checked
  directly while drafting. Selection effect size is unknown. The award-option
  hypothesis is explicitly not presented as proven leakage.
- **Wastewater history/interface:** prescoring review section 6, pinned builder's
  `any_exc` label and previous-year construction (lines 605–648 inspected), and
  saved row/batch/order probe reports. The 11,800 exact public-pair matches are
  attributed to the prescoring review; not independently recomputed for this draft.
  No universal cross-row safety claim is made.
- **Civil-trial timing:** prescoring review's codebook-based defendant jury-demand
  finding. The draft explicitly limits model gains to the shipped retrospective
  table; it does not claim valid filing-time prediction.
- **Worker accounting intervention:** `analysis/worker-budget-intervention.md`,
  source identity in `analysis/intervention-source.json`. Generic change restored
  headroom without manual candidate advancement. This is not claimed to be the
  only intervention in the window.
- **Literature:** `materials/VERIFIED-LITERATURE-NOTES.md` and earlier reference
  verification records. Chaining v2 metadata checked directly on arXiv on this
  date (accepted ACM EC 2026). The short incoming review's $28-per-release error
  and supposed MLE-Smith cost correction are not used.

## Draft checks completed

- Compiled with pdfLaTeX and BibTeX; seven letter-size IEEE pages including references.
- All seven pages rendered and visually inspected; figures are vector PDF.
- No overfull boxes or unresolved citations/references in the final LaTeX log.
- All PDF fonts embedded; no Type 3 fonts.
- Tables and plots generated from the captured JSON; no handwritten plot values.
- Source bundle compiled from a clean temporary directory (see `output/QA.json`).
- The draft is linked from the paper README and retains the agreed cost/integration
  framing and a short discussion of human analytical work.

## Remaining for the final paper

- Replace interim production accounting with the final export and reconcile all
  routing, deployment and intervention records.
- Integrate the authorized quota-recovery evaluations when frozen and reviewed;
  retain original failures and do not choose favorable runs across retries.
- Complete selected-code and substantive transcript review across the cohort.
  Automated flag absence and probe-script success are not substitutes.
- Resolve or explicitly retain the two training-feature probe errors; assess
  source-contract findings without modifying evaluated artifacts or hiding scores.
- Confirm exact-artifact qualification evidence during final producer review.
  Draft capture checks manifest qualification claims and hashes but does not rerun
  worker qualification or independently rebuild all datasets.
- Final author review of prose, affiliation, claims and venue submission details.
  Evidence remains private during drafting; nothing has been submitted or made public.

## Literature revision — 15 November 2026

- Increased cited works from 12 to 20 and integrated them into the argument.
- Added the author's actual arXiv paper with Szilárd Pafka, XGBoost, production
  reliability, artifact evaluation, data curation, and human analytical work.
- Used published EMNLP versions for CurationBench and agentic data engineering;
  recorded primary-source checks and limits in the literature notes.
- Kept the captured evidence, numerical results, figures, and unresolved cases.
- Cut repeated explanations to retain seven pages at the original IEEE settings.
- Rebuilt, rendered, and inspected all seven pages. The portable source bundle
  also builds in a clean directory with matching text and no unresolved citations
  or overfull boxes; its hashes are recorded in `output/QA.json`.


## Consumer update — 15 November 2026, captured 17:01 UTC

The seven-page LaTeX draft now contains all 12 cohort publications, 24 frozen
consumer models across eight datasets, and the completed wildlife-strike recovery.
The original `draft-inputs.json` is unchanged. The additive snapshot is
`analysis/update-inputs-2026-11-15.json`; it records input hashes and the explicit
selection of `faa-wildlife-strike-substantial-damage-retry-1` for that dataset.
Original failed outcomes remain preserved and reported, with no favorable-run
selection across original and recovery attempts.

- **Twelfth publication:** the pinned queue and public snapshot identify
  `sdwis-lcr-lead-action-level-next-period`, verified at 14:56:16 UTC. It fills the
  existing 12-release cap, not a revised outcome-dependent cohort. No consumer
  metrics are available for it in this snapshot.
- **Cost and production attempts:** unchanged 14:24:01 UTC export. All cost ratios,
  worker counts, stage counts, and successful-release latencies retain their
  original 11-publication denominator. No estimate is divided by 12.
- **Wildlife-strike qualification:** retrieved the published, manifest-bound
  passing gate 1.6.1 report (SHA256 beginning `4747ab0ebaef1c10`). The release's
  own hash-verified qualifier and dependencies accepted the complete saved train,
  validation, holdout, metadata, and published quality descriptor in a separate
  temporary copy. Artifact digest: `ae75ab5acd1b27ae...`. This rechecks the worker's
  original evidence; no model fit or new qualification was run. Compact report,
  receipt, and provenance are in `analysis/update-2026-11-15/`.
- **Wildlife-strike scores:** saved recovery summary, finished at 16:44:24 UTC.
  All three consumer models are frozen. Table I and Figure 3 derive from these
  saved results and the paired bootstrap output, not handwritten plot values.
- **Interval interpretation:** all three differences against the ordinary control
  have lower bounds above zero. Against paired random search, only run 2 does.
  Incident-day clustering does not account for aircraft, airport, or operator
  dependence across days. The source review also limits claims to retrospective
  current-snapshot use. No general agent-superiority claim is added.
- **Probes:** 24 batch/order passes on the sampled rows; 21 own-label probes show
  no changed tested cells, and three have unresolved assertion errors (FDA run 2,
  T100 run 3, FAA recovery run 1). These are not completed compliance verdicts.
- **Still outstanding at this snapshot:** Seattle and railway-hazmat recovery,
  first evaluation of drinking-water lead, full semantic code/transcript review,
  resolution or explicit retention of all three probe errors, final production
  accounting, and author review. Utility-reliability access failures remain.
- **Presentation checks:** all seven pages rendered and inspected; 20 references
  retained; source bundle rebuilt in a clean directory with matching PDF text,
  embedded fonts, no Type 3 fonts, no overfull boxes or unresolved citations.
  `output/QA.json` hashes both evidence snapshots and delivered artifacts.

## Motivation and abstract revision — 15 November 2026

Rewrote the abstract and the first two introduction paragraphs to lead with the
work of constructing prediction benchmarks and why the factory was built. The
201-word abstract follows motivation, approach, evidence, findings, and contribution.
Detailed tariff ranges and pending-run chronology remain in the body. No evidence,
result, cost denominator, experiment, or production setting changed. Recorded the
opening's purpose in `PAPER-DIRECTION.md` for subsequent revisions. All seven pages
were rendered and inspected; the source bundle passes the clean-build checks.


## Factory usefulness and comparator interpretation — 15 November 2026

Eduardo requested that the paper distinguish dataset usefulness from consumer-agent
superiority. Recorded the direction in `PAPER-DIRECTION.md` and revised the abstract,
RQ3, methods, results, main comparison figure, discussion, and conclusion.

The untuned scaffold is the primary performance reference for modeling headroom;
paired tuned random search remains a visible secondary comparison of added agent
benefit. Both controls and all underlying scores were already present. No protocol,
experiment, selection, release, or model was changed. The manuscript explicitly
notes that this presentation emphasis was clarified after interim results.

`analysis/comparator-summary.json` is generated from the same frozen bootstrap
records as Figure 3. It retains all three intervals against each comparator for
all seven datasets with a declared grouping. The figure uses identical scales,
shows both comparisons side by side, and checks that no interval is clipped.

- All three consumer point estimates exceed the untuned scaffold on seven of the
  eight completed tasks; airline routes are mixed. Pipeline penalties has no CI.
- All three intervals against untuned XGBoost are above zero for civil trials,
  device recalls, wastewater, and wildlife strikes, conditional on their groupings
  and unresolved semantic/probe limitations. This is not four validated benchmarks.
- Against tuned random search, all three intervals are above zero for civil trials
  and device recalls. One wastewater and one wildlife-strike interval are above
  zero; all other available intervals include zero. No unfavorable result is hidden.
- Cost remains per publication, not per validated useful benchmark; correction and
  expert-review effort are unmeasured. Known source/selection/timing defects remain.

All seven pages rendered and inspected. The PDF keeps 20 references and original
IEEE type/margins. Portable source rebuild and numerical cross-checks pass; artifact
and immutable-input hashes are recorded in `output/QA.json`.


## Evening recovery integration — 15 November 2026

**Current manuscript:** 12 publications, 29 scored consumer models across ten
releases. Nine releases have three models; Seattle has two. Utility-reliability
provider access failures remain, and drinking-water evaluation is still running.
The production/cost export remains pinned to 14:24:01 UTC and 11 publications.
No cost denominator, experiment, selection rule, or original outcome was changed.

Evidence is captured in `analysis/evening-inputs-2026-11-15.json`, additive to the
two earlier snapshots. It pins both recovery summaries, reviews, original probe
execution failures, the Seattle blocker, and corrected probe outputs. The renderer
selects all three authorized recovery executions, without choosing favorable runs.

- **Seattle:** recovery finished at 18:29:30 UTC; run 1 is blocked, runs 2 and 3 are
  frozen/scored. Both have positive pointwise paired intervals against each control
  under issuance-day grouping. Missing-field associations prompted an unverified
  post-issuance timing concern. The runner's file-presence rule stopped run 1 even
  though its blocker declared `blocks_scoring: false`. No retrospective freezing,
  scoring, or resumption of that attempt was performed. The figure preserves run
  identities: only run-2 squares and run-3 triangles are drawn for Seattle.
- **Seattle review repair:** original artifact/training probes failed when trying
  to load the nonexistent run-1 frozen artifact. The original scripts were run
  against a temporary view containing only the two already-frozen runs in its
  copied order. Original study directories, model bytes, and records were untouched.
  Both models pass sampled batch/order and own-label checks. This resolves the
  missing-artifact execution error, not the task's timing concern. Scripts, tool
  hashes, inclusion/exclusion lists and logs are in `evening-2026-11-15/seattle-probes/`.
- **Railway hazmat:** recovery finished at 20:08:03 UTC; three frozen/scored models.
  Saved AUC range 0.78409–0.79106; untuned 0.73130; paired random 0.74728–0.75127.
  All three paired intervals are positive against each comparator under accident-day
  resampling. Repeated-carrier/location dependence and current-snapshot timing limit
  interpretation. Source review did not verify the publisher dictionary, so the
  task is not promoted to verified first-notification forecasting.
- **Exact-byte qualification:** the original passing worker reports for Seattle
  and railway were downloaded from their pinned public release, hash-checked against
  each manifest, and accepted with the release's own qualifier/dependencies over
  all saved split files plus the published quality descriptor. Digests begin
  `a220e68c960ee6b6` and `aedd811fdb6a80fd`. Compact evidence and reproduction script
  are in `analysis/evening-2026-11-15/`. No new model scoring or qualification occurred.
- **Comparisons:** every scored consumer point estimate exceeds untuned XGBoost on
  nine of ten tasks; airline routes are mixed. All three untuned comparisons have
  positive intervals for five tasks; Seattle adds two positive comparisons. For
  tuned search, three tasks have all three positive intervals; Seattle adds two,
  with one additional positive comparison each for wastewater and wildlife strikes.
  These are conditional comparisons, not counts of scientifically validated tasks.
- **Probes:** 29 batch/order passes; 26 own-label probes with no changed tested cells;
  the same three assertion errors (FDA r2, T100 r3, FAA recovery r1) remain. All
  original failed attempts and probe failures are retained.

Still required for submission: integrate the final dataset outcome; complete
selected-code and transcript review and assess the three probe assertions; retain
or resolve semantic findings without changing evaluated artifacts; reconcile the
final production accounting/interventions; author review and submission preparation.
These are finite completion tasks, not a new experimental program.

The seven-page PDF and portable LaTeX source were rebuilt. All pages were rendered
and inspected; 20 references remain, with no overfull boxes or undefined references.
Clean-source compilation and numerical consistency checks pass. `output/QA.json`
now hashes all three evidence snapshots.


## Accepted review integrated — 15 November, final editorial pass

Completed the eight ordered changes in PAPER-DIRECTION.md. The complete paper
received three separate self-review passes: reader/argument, skeptical evidence,
and rendered editorial review. Findings, corrections, input manuscript hashes,
and a point-by-point response to the feedback are in REVISION-REVIEW.md.

The integrated factory remains the contribution. Operation, independent use and
validity are separate evaluation questions; recurring expenditure is a bounded
window ratio. Cases distinguish a confirmed selection discrepancy, conditional
scoring access, and unresolved timing. ABC and AgentSuite strengthen the connection
to auditing literature, replacing two peripheral citations while retaining 20
references. No measurements, cohorts, controls, failed outcomes or source artifacts
were changed. No new experimental or production work was introduced.

Verification:
- Seven IEEE pages; all seven final rendered pages read and visually inspected.
- Aggregate audit checks table cells, both controls, interval-supported counts,
  original snapshots/figures, cost denominator and attempt counts. It passes locally
  and in a fresh Git clone without private study workspaces or configuration.
- Portable LaTeX source compiles independently and yields identical extracted text.
- No undefined references or overfull boxes; fonts embedded, no Type 3 fonts.
- Delivered PDF/source and immutable evidence hashes are in output/QA.json.
- Exact-commit CI is checked after push and reported with the revision handoff.

This signs off the requested editorial revision, not the remaining scientific or
submission work. Final collection/accounting, unresolved code/transcript review,
and the author's submission read-through remain as stated above.


## Readability and caption revision — 15 November

Addressed all 13 editorial-commentary items, retained the protected draft notices,
and completed three new full-paper self-reviews recorded in REVISION-REVIEW.md.
Shortened all four captions and sorted Figure 3 by median untuned-model gain,
using the same row order in both panels. Numerical comparisons, snapshots, table
values and the other two figures are unchanged. This is presentation work only;
no production settings, studies, selection rules or model artifacts changed.

Seven pages remain. Numerical checks compare every Figure 3 comparison with the
previous revision and check ascending median order. Source-bundle verification
checks the clean rebuild, text agreement, references, fonts and page count.
Final hashes are in output/QA.json; exact-commit CI is checked after push.


## Abstract rewrite and Figure 1 annotation — 15 November

Replaced the abstract with a 170-word standalone account, checked against the
twelve agreed writing principles and the retained evidence. Removed Figure 1's
no-feedback annotation; the methods still explain the study separation. Body
text and quantitative evidence are unchanged. All seven pages were inspected.
Portable-source and aggregate checks are rerun; output/QA.json records the final
artifacts. This editorial update does not close remaining scientific review.


## Paragraph-value revision — 15 November

Applied the complete paragraph audit. The paper is six IEEE pages, with unchanged
measurements, figures and table, both controls, 20 references and the necessary
limitations. Removed the six standalone low-value paragraphs and compressed
repeated methods and chronology. Draft-status notices remain. All six rendered
pages were read and inspected; reference columns are balanced. The aggregate
audit passes and the portable source is rebuilt and checked. Seattle recovery
remains pending; no new result is implied by this editorial revision.
