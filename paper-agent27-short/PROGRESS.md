# Progress

The five-page manuscript is revised with the authorized disclosure comparison.
The table now separates source-review findings from release disclosure. Timing
range and median remain in the text; individual times remain in the evidence.

- Inspected the pinned README and descriptor for each of twelve reviewed releases.
- Verified all 24 documents against their original manifests and saved full copies.
- Recorded exact passages, per-finding judgments and rationale in
  `analysis/disclosure-review.json`, summarized in `analysis/DISCLOSURE-REVIEW.md`.
- Five of six listed conditions have corresponding stated restrictions; carrier
  exits are stated but apparent entries are not. SBIR's documents conflict.
- Rebuilt and inspected the five-page PDF; readable separate disclosure column,
  unchanged font size, and no changes to the longer-paper directory.

Artifact hashes and portable-build verification are recorded in `output/QA.json`.
The revision is committed/pushed with exact-commit CI checked before delivery.
The paper is not submitted; the evidence repository remains private.

Final prose revision: merged the two generic lessons, added the construction-cost
lesson, replaced the vague concern count with 1/3/4, changed the table header to
Principal review finding, and defined tool-calling cycles while removing the
unused construction turn detail. PDF and portable archive reverified.

Figure 1 redrawn with observed milestones, model return contracts, neutral review
packet input, and the semantic repair cap. Publication policy is inside the green
box. Dashed/solid borders support grayscale reading. The packet connector now
reaches the Evaluate model box directly. Original graphic dimensions retained;
all pages, grayscale and font sizes checked before delivery.

Workflow revision: replaced the two-row stage grid with one activity sequence.
Builder generation and execution are separate; Model/Code labels identify
responsibility, and one return path shows semantic repair. The controller has
a shared operations band. Counts remain in results prose. The proposed SBIR
evidence diagram was removed after author review because it duplicated the
prose and occupied too much space. The original SBIR prose is retained.
All five pages and the grayscale workflow were inspected; the portable source
archive builds independently with matching PDF text.

Consumer-performance addition: Figure 3 shows the fixed untuned XGBoost baseline
and consumer median/range for all twelve evaluated releases, sorted by median.
The method states model settings, validation selection, held-out scoring, and
the descriptive meaning of the ranges. Results and abstract report that all
three consumer runs exceed the reference on eleven tasks; airline routes are
mixed. Source-review limitations remain in place. Cawley and Talbot and
MLAgentBench were restored and checked against publisher pages. Supporting
identities, scores, qualifications, and interpretation are recorded in
`analysis/consumer-results.json` and `analysis/CONSUMER-RESULTS.md`.

All five pages were inspected; the new plot was also checked in grayscale.
The portable source builds with identical PDF text. Figure generation and the
revised evidence checks passed in a separate checkout. No new experiments ran.

Tuned-control revision: the performance comparison now includes all three paired
random-search controls per release. The abstract reports completion only. Methods
state the fitting-CPU target and its limits, with Bergstra and Bengio restored.
Results distinguish nine all-positive paired task comparisons, two mixed tasks,
and research grants favoring random search; overlapping score ranges are named.
The Table I interpretation sentence remains. Following author feedback, the
figure shows paired AUC differences on one shared axis, with two separated tracks
per task. Direct changes replace separate method panels and overlapping symbols.
The manuscript contains no discussion of these editorial decisions.

Final visualization revision: two aligned difference panels, one against the
untuned reference and one against paired tuned search. Both share the same
limits, zero position, task order, and marker style. The performance figure is
now full width above the cost chart on page 4; figure references update
automatically. The manuscript remains five pages.

Final display polish: the release records now supply one canonical short task name
and publication order to the performance plot. Prose uses the same names. The
absolute-score-range sentence is removed. Cost is Fig. 2, performance Fig. 3,
with matching citation order. The cost figure is 72% of its former height and
labels construction inference ($8.62) and workers ($15.89). The release table
omits the repeated Consumer column, while retaining Not evaluated findings for
the two non-cohort releases. The workflow adds an execution-diagnostics repair
path. Neither the diagram nor the prose attributes all 260 build retries to
execution repairs; the existing waiting/reconciliation distinction remains.

## Final rationale, citation and release preparation — 16 November 2026

Added two sentences explaining the model/controller work allocation. Added the
Hermes Agent runtime with its upstream link after checking the pinned factory call
path. Added the author's *Identical Runs, Different Results* citation to support
the repeated-run discussion; the entry existed but had not been cited. Kept the
abstract, performance framing, cost terminology and remedy caveat unchanged.

Reworked the root README for evidence readers; retained its monitor instructions
in MONITOR-OPERATIONS.md. EVIDENCE.md links the SBIR packet directly and provides
commit-pinned consumer archives. Verified 1,957 integrity-listed files against 17
remote commits. Recorded reference/model checks and remaining public-release
steps in RELEASE-CHECK.md. No visibility change or conference submission.

## Wastewater name and cost-label spacing — 16 November 2026

Use Wastewater exceedance consistently in Table I, Figure 3 and prose. The
canonical release label generates both the table and figure. Figure 2 uses a
single-line Construction label, with checks and baseline fitting stated in its
caption. A 20% height increase was tried but exceeded five pages; the single-line
option keeps labels clear within the original footprint. Record checks and the
portable build pass. Pages 1–2 are unchanged; pages 3–5 were inspected.

## Workflow legend — 16 November 2026

Figure 1 caption now identifies blue dashed boxes as model tasks and green solid
boxes as code operations. It replaces the generic separation sentence and retains
the repair explanation. Five pages; page 2 visually checked, all other pages
pixel-identical, and portable build text matches. Record verification passed.

## Co-author — 16 November 2026

Added Szilard Pafka as second author, with Epoch and szilard@epoch.com, matching
the author block in the previous *Identical Runs, Different Results* manuscript.
Updated PDF author metadata and the AI-assistance responsibility statement to
plural. Five pages; portable source builds identically. All five pages inspected
after minor text reflow. Record verification passed.

## Complete accounting and inspectable acceptance failure — 16 November 2026

Reconciled all 540 stage attempts and all 54 discovery-completed candidates at
the fixed cutoff. Table II reports every stage/outcome cell. There are 119 done,
366 retry, 21 repair, 31 defer, two reject, and one open attempt. The 54 candidates
were 14 published, 37 deferred, two rejected, and one active. These are cutoff
states, not a closed-cohort success rate.

The 366 retries divide into 206 worker outcomes, 98 model-invocation failures,
61 proposal/controller validation failures, and one publication reconciliation.
The 206 worker retry records match 206 distinct deleted workers; 205 carry the
construction/qualification-failure outcome and one expiry before durable upload.
These operation categories do not identify unique bugs or prove root causes.
The pinned state implementation shows that waiting resumes the same attempt;
corrected the earlier wording that could imply wait polls inflated attempt counts.
The final-state export cannot recover the number of intermediate waits.

Replaced the successful-release trace with exact SBIR selection-rule, builder
condition, and acceptance-response excerpts. The missing-declaration
counterfactual remains untested. Publication now explains code-checked anonymous
receipts, and results distinguish fourteen verified publications, twelve
consumer/source-reviewed releases, and the unknown number semantically valid.
Retained both performance controls with less repeated numerical narration.
Clarified that eight concern entries include three separate lead-task findings.
Related work states the contribution as observed operating evidence.

Hosted research is documented from September 2026 and the replacement controller
from November. Added that history without extending the measured 81.53-hour
window or claiming uninterrupted operation of the present configuration.
Pinned sources are in analysis/operational-source-excerpts.json.

The manuscript fits five pages with the existing figures and release table plus
the small accounting table. No new experiment or production operation was run.

Verification: revised generator and record checker pass in a separate checkout;
the extracted portable source builds to matching PDF text. All five pages were
inspected, fonts are embedded, and no overfull boxes or unresolved references
remain. All 310 original long-paper hashes match.

## Deferral reconciliation — 16 November 2026

Checked the reviewers' proposed reconciliation against candidate histories rather
than inferring it from totals. Of the 37 deferred discovery-completed candidates,
31 reached the five-worker-failure limit, three the five-task-failure limit,
two the semantic repair limit, and one had an explicit build deferral. Only the
two semantic-repair cases had completed a build. Thus 35 deferred before any
completed build, not the review's proposed 36. The 18 build-completed candidates
were 14 published, two rejected, and two deferred; the active candidate had no
completed build at cutoff.

Added the 34/2/1 reconciliation, explained that limit-triggering attempts keep
Retry/Repair outcomes, and clarified repeated stage completion in Table II's
caption. The execution-cost lesson now connects 35 pre-completion deferrals with
the observed construction expenditure. No causal link to tool-less generation
is claimed. The generator records every deferred candidate's final attempt and
the verifier checks the five-failure scope counters.

The compact job export contains truncated result JSON for all 205
construction/qualification failures; the expired worker has no result object.
It does not contain full failure diagnostics. No complete cause taxonomy was
added from these aggregate outcome labels, and no new experiment was run.

Final deferral revision: five pages; clean-checkout accounting/history checks
and portable PDF text comparison pass. Pages 1-2 are pixel-identical to the
previous inspected build; pages 3-5 were re-inspected. No template or font changes.

## Public evidence release — 16 November 2026

Eduardo reported marking the HotCRP submission ready for review, then explicitly
authorized public release. Changed the study repository from private to public.
Forty-six unauthenticated requests verified visibility, core paper/SBIR files,
all 17 pinned consumer tree links and integrity manifests, and one model and one
complete archive part with matching hashes. Recorded public-evidence-verification.json
and updated the reader-facing release status. The PDF and research artifacts are
unchanged. Submission completion is the author's report, not a browser readback.

## arXiv package — 16 November 2026

Prepared a separate 10-file source ZIP with root main.tex/main.bbl, the IEEE
class/style, bibliography, three figures, and table inputs. Added the required
IEEE submission notice only to the preprint's first-page footer. The conference
source/PDF and its portable source archive are unchanged. Clean extraction and
three PDFLaTeX passes produce five pages, with no unresolved references or
overfull boxes. Body text matches after excluding the notice; pages 2–5 are
pixel-identical and page 1 was visually inspected. All fonts are embedded.
Copied the upload ZIP to ~/Downloads/dataset-factory-arxiv.zip. No arXiv upload
or final submission is claimed; Eduardo is completing the form.

## SBIR review intervention — 20 November 2026

Completed the separate 30-review experiment under the frozen protocol. Neither
providing the full descriptor nor adding the explicit selection-code comparison
instruction detected the contradiction in five original-case reviews each. All
15 original-case reviews accepted. The report distinguishes partial findings,
unrelated repairs, and one malformed comparison response. See
`../experiments/sbir-semantic-review/FINDINGS.md` for evidence and limits.
The submitted source, figures, conference PDF and arXiv package remain unchanged;
the experiment is retained as evidence rather than silently revising submissions.

## Five-page semantic-review result trial — 20 November 2026

Checkpoint: annotated tag `agent27-before-semantic-review-update-2026-11-20`,
commit `9b184d98317cb697021fcb9d3776739a60b30f01`, pushed before editing. Tagged
conference PDF SHA-256: `5589905184ea739878a6c50df2648a5fdc5765638ee37353271205d4e70a3f8a`.
Tag-push CI run `44806371028` passed. Main remains at this checkpoint; the trial
uses branch `paper/semantic-review-result` in a separate worktree.

Added a bounded post hoc experiment paragraph beside the historical SBIR case.
It reports the two descriptors, three conditions, five reviews per combination,
runtime differences, frozen detection rubric, all original-case acceptances,
comparison repairs, and the malformed comparison response. Replaced the proposed
remedy with the observed lesson. Explicitly excluded post hoc evaluations from
production expenditure. Shortened repeated prose to make room; all empirical
figures, tables, citations, the document preamble, font sizes, and margins remain
unchanged. No writing-process discussion was added to the manuscript.

The first trial was six pages. The concise trial is five, with all five pages
rendered and inspected. The portable source ZIP rebuilds with matching PDF text,
embedded fonts, and no overfull boxes or unresolved references. `output/QA.json`
records artifact hashes and the final clean-build check. The main checkout,
submitted PDFs, and arXiv upload package are untouched. No resubmission occurred.

## Independent-review round 2 — 20 November 2026

Shortened the experiment paragraph from 116 to 91 whitespace-delimited words and
the lesson from 34 to 21. The result now explicitly states that all ten original-
case reviews receiving the full descriptor noted relevant filters but failed to
connect them to the contradictory declaration. The consistent-control result is
reported without claiming discrimination; runtime differences remain explicit.
Detailed grading, unrelated repairs, and malformed-output accounting stay in the
public experiment records.

Restored the tagged baseline's complete-builder detail, repair/publication prose,
Wastewater lesson and conclusion. The baseline tag remains unchanged. All five
pages were rendered and inspected; the portable archive builds to matching text,
with embedded fonts and no overfull boxes or unresolved references. The Desktop
comparison uses the original tagged PDF and this second revision, not the first
trial as its baseline. Nothing was uploaded to HotCRP or arXiv.

## Independent-review round 3 — 20 November 2026

Reduced the experiment paragraph to 65 words, focusing on the ten original-case
reviews supplied with the full descriptor (five also received explicit comparison
instructions). Removed the broad filter-noticing count: one response discusses
phase records excluded from labeling, which does not clearly demonstrate that it
recognized dataset-row exclusion. Replaced it with r03's exact “conservative
label-validity drops” phrase. The full design and all 30 responses remain public.
The lesson now states that acceptance did not establish reconciliation, without
proposing another untested fix.

Verified the protocol, report, and quoted response through anonymous downloads
from the evidence commit. Five-page portable build matches the inspected PDF;
all fonts are embedded and no overfull boxes or unresolved references occur.
Pages 1–3 render identically to round 2; pages 4–5 were re-inspected. Desktop
round 3 contains the exact original tagged baseline and the new revision. The
same independent-review prompt is copied to the clipboard and saved beside them.
No conference or arXiv upload was made.

## Minimal-result revision, round 4 — 20 November 2026

Reduced the post hoc result to two sentences (33 whitespace-delimited words).
They state the ten full-descriptor reviews, the extra filter-to-declaration
instruction in five, and zero detections. Removed control enumeration, the quote,
and the 30-review count from the manuscript; the complete public experiment record
is unchanged. Checked the other 20 responses: five original-packet reviews and
fifteen consistent-descriptor reviews reported no target contradiction. None
provides a hidden successful detection that would change the reported conclusion.

Added one-task/reviewer-model/runtime limits in Section VII. Restored the imperative
lesson heading and a short instruction to check selection claims against code.
Did not propose a new untested release gate. Original conclusion, empirical
figures/tables, references, font sizes and margins remain unchanged.

Portable build is five pages and text-identical to the inspected PDF, with embedded
fonts and no overfull boxes or unresolved references. Pages 1–3 render identically
to round 3; pages 4–5 were inspected. Desktop round 4 again compares the exact tagged
baseline with this version. Neither HotCRP nor arXiv was updated.

## Targeted review edits, round 5 — 20 November 2026

Made only the three required manuscript edits. The result states that the reruns
test whether supplying the omitted declaration exposes the contradiction, without
claiming to test the cause of historical acceptance. The lesson states the observed
acceptance failure and proposes no remedy. Limitations names local Hermes and
Firecrawl versus the original hosted runtime and web gateway, as recorded in
`runtime/preflight.json` and the protocol. The model identifier and provider route
were retained; the original full runtime configuration is unavailable. The abstract
and all other manuscript text remain unchanged from round 4.

The PDF remains five pages. Pages 1–3 render identically to round 4; pages 4–5
were inspected. The portable archive builds to identical PDF text, with all fonts
embedded and no overfull boxes or unresolved references. Desktop round 5 pairs
this revision with the exact tagged baseline. No HotCRP or arXiv upload was made.

## Bounded clarity revision and adversarial comparison — 20 November 2026

Comparison checkpoint: `agent27-semantic-review-round5-2026-11-20` at
`2fb394c9b3a279de6ad3c431ef2f36ae5a388f83`. Applied the agreed clarity edits
without changing experiments, results, figures, or claim scope. Table II now labels
attempt outcomes; prose separates these from candidate states. Checked that the
30 discovery Defer attempts concern none of the 54 discovery-completed candidates,
and all 19 additional successful builds followed semantic repair. Rounded the
operating headline while preserving exact costs in the records. Fitting CPU
remains distinct from total resources. Consumer performance has an explicit role
within released contracts; no claim of task validity was added.

The revised PDF is five pages and 20 TeX whitespace-delimited words shorter. All
five pages were inspected; a clean portable build reproduces the PDF text with
embedded fonts and no overfull boxes or unresolved references. The abstract, SBIR
result, lessons, limitations, and conclusion are unchanged. Desktop's
`Dataset Factory - Clarity Review` contains the exact saved checkpoint, the edited
PDF, and the single adversarial prompt.

Requested one comparison through `claude -p` with Read-only tools and both PDFs.
It failed authentication before inference: the CLI login expired and cannot renew.
Eduardo was asked to run `claude auth login`. No review has yet occurred; after
login, run the saved prompt once, resolve only material errors, and stop. No
HotCRP or arXiv upload occurred.
