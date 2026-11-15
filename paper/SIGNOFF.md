# First-draft evidence and verification — 15 November 2026

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
