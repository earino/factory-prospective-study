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
