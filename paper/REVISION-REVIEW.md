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
