# Revision and whole-paper review record

## Scope and acceptance

User-authorized revision of the seven-page AGENT’27 experience paper following
external feedback. Follow the eight steps in PAPER-DIRECTION.md, then perform
three full-paper review passes. Experiments, cohort, controls, source artifacts,
and immutable evidence snapshots remain fixed. Final collection/review tasks
listed in SIGNOFF.md are not silently claimed complete by this editorial revision.

Feedback checklist used on every pass:
- F1: Short window/small cohort: bound inference, distinguish models from datasets;
  do not assume that this mandates five pages or infer broad factory viability.
- F2: Cost: state denominator, window, measured/estimated distinction, exclusions,
  and contribution beyond bare per-task prices; no human-cost or efficiency ranking.
- F3: Validity: engage verified relevant literature; distinguish evidence strengths.
- F4: Consumer protocol: state procedural isolation, incomplete review, and scope
  of the measured evidence; no security guarantee or blanket product-quality score.
- F5: Narrative: three legible lessons, less accounting detail, seven readable pages.
- S1–S6: Preserve integrated-system contribution; cost as bounded evidence; audit
  literature; qualified consumer evidence; explicit relation to prior systems;
  motivation and substantive findings in the abstract/introduction.

## Ordered implementation

1. Recorded accepted direction and boundaries in PAPER-DIRECTION.md.
2. Rewrote abstract/introduction: connected work motivates the factory; contribution
   is integrated operation with bounded observations, not a new component or price record.
3. RQ1 operation (including costs), RQ2 independent use, RQ3 validity now match
   results headings. Retained the fixed untuned and tuned controls, all runs, and limits.
4. Reduced cost prose; retained equation meaning in prose, categories, 11-publication
   denominator, carry-in boundary, exclusions, all-peak sensitivity and resource-state
   lesson. Exact counts/rates remain in the unchanged cost evidence. No cost claim
   was extended to the twelfth release or to validated useful tasks.
5. Cases now state confirmed discrepancy, conditional scoring limitation, and
   unverified timing concern separately, with consequences. No issue was promoted
   to proven leakage or dismissed because a consumer scored well.
6. Verified ABC, AgentSuite, MLE-Smith v1 cost passage, AutoSDT archival API-cost
   appendix, and venue format. Added two auditing citations, removed a peripheral
   two-paper sentence, and preserved prior records. See VERIFIED-LITERATURE-NOTES.md.
7. Rewrote three discussion lessons and aligned conclusion. Explicitly separated
   29 models from ten datasets and long-run claims from this observation window.
8. Manuscript and aggregate reviews complete; delivery checks recorded below.

## Whole-paper passes

Three complete readings are recorded below, each using a distinct brief and a
rebuilt manuscript. These are self-reviews, not independent reviewers or claims
of a reset model context.


### Pass 1 — reader and argument review

Fresh brief: read as a workshop reader encountering the system for the first time.
Read all eight compiled pages, including all figures, table, threats and references
(from complete page-text extraction; missing output chunks reread separately).
Input manuscript SHA-256: `917e11877675a035aa9c2e9977c5394c4a195b6b2533c5af4200d88c67d1313b`.

Findings against the feedback:
- F1/F4: cohort and procedural isolation are explicit; no general success-rate claim.
- F2: denominator and exclusions now attach to the cost argument. Cost mechanics
  are reduced, but the same boundary is explained too often across sections.
- F3: new audit citations connect to cases without claiming checklist compliance.
- F5/S6: eight pages fails the user's seven-page limit. Opening, discussion and
  related work repeat the integration/conditionality argument. Cut those repetitions,
  shorten long headings and protocol prose; preserve controls and adverse evidence.
- S1–S5: integration remains central; consumer evidence remains measured but bounded.
  Abstract should say one history feature (the documented case), not plural, and
  should not imply point differences alone establish robust headroom.

Corrections: shorten opening, discussion and protocol narrative; make abstract's
comparison conditional; retain full numerical results/cases. Rebuild before pass 2.


### Pass 2 — skeptical evidence review

Fresh brief: read the complete seven-page paper as an empirical reviewer seeking
claims stronger than their evidence. Read every section, caption, table and
reference from the rebuilt PDF, then inspect the retained snapshots, source-review
records, Seattle probe provenance, and pinned SBIR code/declaration.
Input manuscript SHA-256: `79decf4e5b16b3c0fb95ea68f63577c864741bc1522f98b0afcff43603e12f2d`.

Findings and corrections:
- F1: models/datasets, short window and unresolved outcomes are distinguished;
  no general validity rate or long-run reliability estimate. All original failures
  and both controls remain. No cohort or study change needed.
- F2: numerical recheck reproduces 11-publication denominator, cost range, attempt
  counts and all table cells. Estimates remain distinct from invoices. Qualify
  "every recorded attempt contributes" as every attempt's *recorded resource use*,
  because some attempts have no generation counters; do not imply perfect metering.
- F3: SBIR claim supported by pinned construction.json:281 and build.py:339–354,
  406–417; wastewater's review records the 11,800 pairs and interface condition;
  Seattle remains suspected timing, not confirmed leakage. Method wording implied
  source documents were equally accessible for every review; narrow to available
  documents and identify Fable as the prescoring reviewer. Missing evidence is not
  a passed check. New reference titles/claims match the checked primary sources.
- F4: define independence as separate sessions from the producer under the same
  operator, not institutional independence or secure isolation. Retain the explicit
  shared-host limitation. Spell out ROC AUC on first methods use.
- F5/S1–S6: opening, three results questions and three lessons now agree; seven pages.
  Avoid a final unsupported claim about universal usefulness. Existing distinctions
  and limitation statements already do so; no further reframing needed.

The executable aggregate audit is analysis/verify_revision.py; results are in
analysis/revision-checks.json. It verifies both controls, per-run interval counts,
table values, attempt counts, cost denominator and unchanged snapshots/graphics.
This supports numerical fidelity, not scientific certification of the datasets.


### Pass 3 — complete editorial and delivery review

Fresh brief: read the rendered paper as an editor assessing whether a new reader
can follow the contribution and distinguish its claims. Read all seven pages in
order at 1500-pixel page height, including every figure, table, caption and reference.
Input/final manuscript SHA-256: `88fd0c03aeed83df25ef418084bc38c5939b5ca696d038a597dc3d21eae2ed18`.

Whole-paper verdict against the supplied feedback:
- F1: contribution is a bounded deployment experience. Abstract, introduction and
  conclusion agree on 12 releases, ten scored datasets and 29 models. The short
  window and repeated-attempt unit are explicit in methods/threats; no viability rate.
- F2: first cost mention is bounded by 11 releases, time, development/labor exclusions;
  methods retain carry-in and valuation boundaries. Results give a transparent ratio,
  not a lifetime cost, price record or labor-saving result. Detailed counts have moved
  out of the main narrative but remain in the unchanged evidence.
- F3: validity is one of three evaluation questions. SBIR discrepancy, wastewater
  conditional access, Seattle unresolved timing and missing dependence keys retain
  different evidence strengths. ABC/AgentSuite clarify the relation to prior work.
- F4: separate sessions under the same operator are distinguished from external
  evaluation and secure isolation. Frozen-model scores remain measurements; no
  general compliance or product-validity certification is asserted.
- F5: three named engineering lessons connect to observed evidence. Seven pages,
  standard IEEE font/margins, readable figures and table, no cropped labels/overlap.
  Both comparison panels use the same axis; all scored runs with intervals remain.
- S1–S6: preserves full-workflow contribution; cost bounded; audit literature integrated;
  consumer evidence qualified, not discarded; prior systems' scopes explicit; abstract
  states motivation and findings. The requested five-page defect-centered reframing
  is deliberately not adopted.

No further manuscript changes were needed on this pass. Submission-level missing
work (final observations, remaining semantic review and author prose approval) stays
explicit; it is not covered by an editorial sign-off. Do not equate these three
whole-paper self-reviews with three independent reviewers.

## Completion mapping

1. Direction: PAPER-DIRECTION.md, accepted-review contract.
2. Opening: abstract and Section I, motivation/contribution/bounded findings.
3. Evaluation questions: Section I RQ1–RQ3, Section IV A/B–C–D.
4. Cost: Sections III-B and IV-B, Fig. 2, VI-A; detailed existing cost evidence retained.
5. Case strength/consequences: Section IV-D plus dependence discussion in IV-C.
6. Literature: Section VI, two verified auditing references, primary-source notes.
7. Three lessons: Section V; consistent conclusion in VIII and limits in VII.
8. Aggregate/source audit: analysis/revision-checks.json; final clean PDF/source checks
   in output/QA.json; seven page images inspected. Exact pushed-commit CI is checked
   after the commit, with the result reported in the final handoff.

All three requested full-paper passes are recorded above. Final packaging checks
are separate from those readings and do not count as an additional review pass.


## Readability revision — 15 November, following the phrase inventory

Scope: address all 13 editorial-commentary/repetition items in the chat inventory.
Keep draft-status items 14–18 and the two substantive incomplete-review disclosures
for a later completion pass, as explicitly requested. No evidence updates or new
experiments. The protected notices and phrase inventory are saved in
analysis/readability-scope.json. Both controls are described by function rather
than post-hoc presentation rank; the prior framing history remains in the notes.

Implementation: remove editorial-history sentences, defensive non-claims and
repeated contribution announcements; retain one clear introduction statement.
Also remove two repeated generalization disclaimers whose substance remains in
Threats, and express the tuned-control interpretation directly. Source/code checks,
method boundaries, adverse outcomes and AI assistance disclosure remain.

Three new full-paper reviews follow. These are separate self-reviews, each starting
with a distinct reading brief; they are not independent external reviews.


### Readability pass 1 — first-time reader

Read the complete rebuilt seven-page PDF as continuous text, including all
captions, table cells, references and draft notices. Input manuscript SHA-256:
`b08e1d1f89a66793622af9a29121bc6e8a2211a74a7d31bc872d5b1f074f4455`.

The problem, factory, operation/use/validity questions and conclusion remain connected.
All inventory items 1–13 are removed or expressed as direct descriptions; draft
notices remain. Found two local defects introduced/exposed by tightening:
- The untuned model paragraph repeats "reproducible starting point" in adjacent
  sentences. Keep the definition once.
- "Their integration" after named prior systems could imply reuse of those systems.
  Place the single contribution statement after the prior-work examples and describe
  the workflow explicitly.
Also replace "not universal proofs" with the actual scope of probe coverage.
The method/results distinction, both controls, selected case evidence strengths,
20 references and unresolved review disclosures remain intact. Apply these small
corrections, then reread the full paper from a new brief.


### Readability pass 2 — methods and interpretation

Read all seven rendered pages in order, including full text, figures, table,
references and notices. Fresh brief: assess whether an empirical reader can follow
what was done and what the comparisons establish without our conversation.
Input manuscript SHA-256: `ad405616c5dd74760bc442af77894ed7d79cabe0c910c5773c908b21bfe3616f`.

The integrated factory remains the subject. Cost/use/validity results answer their
questions; no sentence now explains why we kept a control or abandoned a claim.
Both fixed and tuned comparators are fully described and visible; all interval
statements and raw table values match the retained aggregate audit. Draft-status
notices and actual incomplete-review limits remain explicit. Related work connects
to the results without repeated contribution announcements. Conclusions remain
bounded by the short window, task assumptions and incomplete conduct review.

Two terminology fixes remain: "Scout" is undefined for an outside reader, so use
"a single coordinator"; "baseline and untuned-scaffold scores" is ambiguous, so
name the factory baseline and independent untuned XGBoost model. The saved result
kinds include both `released` and `ordinary`, confirming the distinction.
No results, citations, control settings, selection rules or draft notices change.


### Readability pass 3 — complete draft and rendered presentation

Read all seven final rendered pages, including every caption, table, figure and
reference. Fresh brief: can a reader follow this as a coherent interim draft,
with remaining completion work stated but no narration of editorial decisions?
Final manuscript SHA-256: `5b393ae7104e65a43736a6ef056abd3e362875bdc9a02f23ec748a6ba36de958`.

The opening, three questions, methods, results and conclusion remain connected.
No result or interpretation depends on removed editorial history. Both controls
retain their roles and all observations. The draft notices and incomplete-review
disclosures are preserved verbatim. The paper remains seven pages with 20 cited
references. Final scientific reconciliation and author review remain outstanding.

During this pass Eduardo requested two presentation changes: sort Figure 3 by
median gain and shorten all captions. Both panels now share ascending median
untuned-gain order; all run-level values and intervals are unchanged. Reviewed
all four captions: retained reading keys, removed repeated methods and discussion,
and kept the requested pending-result notice. No sorting explanation was added
to the caption. The plot legend initially crossed an airline interval after the
reorder; moved it into the empty lower-left area and inspected the rebuilt page.
Other pages keep the reviewed layout and text.

Verdict: the requested readability revision is complete as a draft. Three new
full-paper self-review passes are recorded above; none is an external review.
Packaging and numerical checks follow separately.


## Abstract rewrite — 15 November

Replaced the abstract as a whole; 170 words. The problem and continuing factory
come first, followed by the evaluation approach, bounded production expenditure,
consumer results, one concrete source finding and its engineering implication.
The cost uses the 11-publication accounting window; ten evaluated releases and
nine with consistently higher point scores are verified by the retained audit.
Scores are not described as significant gains or proof of benchmark validity.
The named population discrepancy is supported in Section IV-D.

Review against the twelve writing principles: concrete problem; early integrated
contribution; connected narrative; brief method; actual findings; selective
numbers; adjacent cost exclusions and named comparators; bounded conclusions;
direct language; no unsupported novelty; specific closing lesson; one standalone
paragraph without citations, unexplained initialisms or editorial history.
On Eduardo's feedback, cut the detailed history-feature explanation and repeated
abstract conclusion. Also removed the no-feedback line from Figure 1; its
methodological explanation remains in Section III-A.

Read the abstract in isolation and against the results. All body text, draft
notices, measured figures, table and evidence remain unchanged. Rendered and
inspected all seven final pages after the rewrite and figure annotation removal.
Final manuscript SHA-256: `659f487c7c7f33d88e6e8a661376deae0499a25bd2976fa631320e22d09d2403`.
