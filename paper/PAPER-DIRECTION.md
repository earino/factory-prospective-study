# Current paper direction — AGENT’27

Agreed with Eduardo on 15 November 2026. **This is the current editorial direction.**
It supersedes earlier outlines and framing where they conflict. The paper-writing
prompt must follow it. It changes the emphasis of the paper, not the study cohort,
experiments, recorded outcomes, or deadlines.

## Accepted review and revision contract — 15 November, evening

The user approved this sequence after reviewing external feedback. Keep the
seven-page experience paper centered on the integrated factory. Cost, independent
use, and source validity are distinct evidence, not interchangeable success tests.
This section supersedes earlier wording that calls consumer optimization a test of
usefulness without specifying what it can establish.

Central statement: an integrated agentic factory discovers sources and publishes
prediction tasks at low observed recurring cost. Independent experiments test
artifact use and modeling headroom; source audits examine task assumptions that
successful execution and model scores cannot verify.

Accept the review's requests for a clearer contribution, bounded cost metric,
separate evaluation questions, less accounting detail, and relevant validity
literature. Do not claim a lowest-cost result, human labor savings, universal task
validity, intervention-free operation, or 29 independent dataset replications.
Do not turn unresolved timing concerns into proven defects, demote all consumer
measurements to anecdotes, or infer a paper-format requirement from the review.
No new auditing framework, experiments, production changes, or source selection.

Implement in this order:
1. Record this agreed direction.
2. Rewrite abstract/introduction around the complete workflow and bounded findings.
3. Separate operation, independent use, and validity in the questions/results.
4. Shorten and bound recurring operating expenditure per publication; keep detailed
   rates, exclusions, and reproducible accounting in the evidence repository.
5. Distinguish demonstrated discrepancies, conditional limitations, and unresolved
   concerns; connect each to its practical consequence.
6. Verify and selectively integrate relevant validity literature and cost boundaries.
7. Organize discussion around integration, recurring expenditure, and complementary
   consumer/source checks; retain small-cohort and procedural-isolation limits.
8. Check claims, numbers, controls, unsuccessful attempts, references, seven-page
   layout, clean source build, and exact-commit CI.

Before sign-off, conduct at least three full-manuscript review passes with a fresh
reading brief each time. Read the complete paper on every pass; compare it against
all supplied feedback, record findings/corrections, and do not substitute a
section-only edit or automated check for a whole-paper review. These are separate
self-reviews, not independent reviewers. The audit trail is in
[REVISION-REVIEW.md](REVISION-REVIEW.md).

## Main claim and purpose

Working title: **From Public Data to Prediction Benchmarks: Cost, Reliability, and
Lessons from an Agent-Driven Factory**.

Main question: **What does it take to operate an agent system that discovers public
sources, turns them into prediction benchmarks, and publishes usable artifacts—and
what does each successful outcome cost?**

Write an empirical experience paper about the complete deployed factory. Connect
three bodies of evidence: the source-to-publication workflow; the production
record, including failures and interventions; and independent use of the published
artifacts. The consumer optimization study tests the usefulness of the outputs.
It is not the central product or a general contest between research agents and
hyperparameter search.

The contribution is observed engineering experience with a complete workflow and
inspectable evidence. Do not claim to be the first dataset-discovery agent, the
first automated benchmark generator, or the first end-to-end system. Explain the
actual starting points, outputs, and evaluation boundaries of related systems.

The two additional cost-literature reviews read on 15 November reinforce this
direction: low marginal generation cost already has precedents. Our focus is the
complete operating factory, its production outcomes and recurring costs, and
independent evidence of output usefulness. Distinguish the factory's checks before
publication from the separate consumer evaluation; the latter is not its only
verification step. Use the corrections in
[the literature notes](materials/VERIFIED-LITERATURE-NOTES.md#additional-cost-literature-reviews--15-november-2026)
before using either review's proposed prose or cost comparisons.

AGENT’27 explicitly welcomes experience papers and emphasizes empirical evidence,
reusable methods, operations, and validation across the agent lifecycle:
https://conf.researchr.org/track/icse-2027/agent-2027-papers

## Opening and abstract: why the factory exists

Eduardo's 15 November prose revision: lead with the work needed to turn public
sources into usable prediction benchmarks, and why connecting those steps makes
exploration practical for a small research group. Then explain the system,
observation and evaluation, main findings, and contribution. Counts are evidence,
not the motivation. The independent consumer study tests the factory's outputs;
it is not the reason the factory was built.

Keep the abstract self-contained. Include the cost boundary and substantive
quality findings, but leave detailed tariff ranges, retry chronology, pending-run
status, and operational timestamps to the methods and results. Do not replace
motivation with a status report or a list of disclaimers. Preserve the distinction
between low measured operating cost and unmeasured human labor savings.

## Put production cost and reliability near the front

Report the production funnel, elapsed time, resource use, failure and retry causes,
and documented interventions. Use consistent observation boundaries. Separate
carry-in work from new work; do not present window spending divided by releases
as a full lifetime construction cost when work began before the window.

Report attributable production cost per published benchmark, including discovery,
unsuccessful candidates, repairs, and publication—not just the final successful
build. Show the underlying totals and denominator. Where attribution is incomplete,
identify the coverage rather than manufacture precision.

Keep these quantities distinct:

- Actual charges and any explicit allocation of subscription costs.
- Measured tokens, calls, worker time, and elapsed time.
- Usage-based price estimates, with their assumptions.
- Independent consumer-evaluation cost.
- One-time development effort and recurring human intervention.

A small incremental subscription bill does not imply zero inference resources.
Unmeasured human effort is unknown, not zero. Do not use cumulative CLI cost sums
as invoices. Explain what a reader would need to reproduce the operating setup.

There is no matched human-construction study. Do not claim a measured historical
cost reduction or an “X times cheaper than humans” result. Low observed operating
cost is useful evidence in its own right. MLE-Smith already reports low task
generation costs: version 1, section 4.2 reports $0.78 per task including generation
and verification. Its supplied-data starting point differs from our discovery
workflow. Pin the cited version and compare coverage, not bare prices:
https://arxiv.org/html/2510.07307v1

## Use independent consumption to assess output value

**Agreed clarification, 15 November:** the factory produces datasets; the consumer
agent is an evaluation instrument. The paper asks whether the released artifacts
support reproducible prediction research, not whether Claude beats tuned XGBoost.
This editorial emphasis was clarified after inspecting interim results. It does
not change the registered protocol, controls, metrics, selection, or experiments.

Assess four things: source-to-publication operation; independent artifact use;
modeling headroom over a fixed untuned model; and production cost and quality
problems that survive factory checks. There is no single score threshold for
usefulness, and improved AUC does not establish scientific or operational value.

- **Primary performance comparison:** the existing untuned XGBoost scaffold
  (100 trees, maximum depth 6, learning rate 0.1, native categorical handling).
  It describes a reproducible starting point and improvement from experimentation.
  It is not a null model or an artificially weakened control.
- **Secondary comparison:** the existing XGBoost random search, matched to recorded
  eligible fitting CPU, with its cap and per-fit overshoot disclosed. It tests
  added benefit of agent-led experimentation over conventional parameter tuning.
  Retain all its scores and intervals with comparable visibility. Do not remove,
  weaken, rerun, or relabel the control to manufacture favorable results.
- **Independent quality evidence:** source meaning, population, feature timing,
  dependence structure, saved-model replay, and code/transcript review. These
  assess validity separately from either model comparison. Known defects remain.

Present both performance comparisons side by side in the main figure. Label the
fixed model "untuned XGBoost" and the search control "tuned random search" rather
than use an ambiguous "baseline." State exact settings and what each answers.
Report all runs and unresolved reviews. Do not count correlated runs as independent
replications or turn point estimates into interval-supported claims.

A conventional search doing well can show that a task supports experimentation.
A consumer agent not beating it does not establish poor dataset quality. Conversely,
beating the untuned model does not repair a defective target or prove usefulness.
Cost per publication remains distinct from unmeasured cost per validated, useful
benchmark, including correction and expert review.

## Discuss human analytical work briefly and precisely

Map observed factory stages to familiar activities: finding sources, interpreting
documentation, choosing questions, transforming data, checking requirements, and
preparing and distributing artifacts. Describe automated acceptance as release
decisions under a human-defined standing policy. Do not equate this with replacing
all expert judgment or accountability.

The discussion can propose that low recurring production costs make it practical
for small research groups to investigate sources they would otherwise leave
unexplored. This is an implication, not a measured labor-market effect.

Useful foundations, checked at the passage/abstract level on 15 November:

- Kandel et al., *Enterprise Data Analysis and Visualization: An Interview Study*
  (2012): discovery, wrangling, profiling, modeling, and reporting in analysts’ work.
  https://vis.csail.mit.edu/classes/6.859/readings/pdfs/Kandel-EnterpriseDataAnalysisAndVisualization.pdf
- Demirer et al., *Chaining Tasks, Redefining Work: A Theory of AI Automation*
  (2026, preprint): connected steps and task allocation affect automation. Use as
  an interpretive connection; this single-system study does not causally test it.
  https://arxiv.org/abs/2606.15960
- Sambasivan et al., *Data Cascades in High-Stakes AI* (CHI 2021): data problems can
  produce downstream failures. Relevant to artifact review, without transferring
  its high-stakes setting or prevalence estimates to our study.
  https://research.google/pubs/everyone-wants-to-do-the-model-work-not-the-data-work-data-cascades-in-high-stakes-ai/

Read materials/VERIFIED-LITERATURE-NOTES.md for corrections to both incoming
reviews. Verify precise claims and publication metadata before adding citations.
Keep this discussion focused; do not turn the paper into a labor-economics survey.

## Paper structure and presentation

Eduardo’s requested length: at most seven IEEE pages including references (confirmed 15 November).

1. Introduction: lead with the problem and why the factory was built, then the
   observed output, cost, and independent-use findings.
2. System and work allocation: explain the complete workflow and the responsibilities
   of models, deterministic software, and humans.
3. Study method: observation window, production record, cost accounting, and consumer
   evaluation. State actual dates without a long scheduling-history narrative.
4. Results: production yield and cost first; independent usefulness second; failures
   and interventions alongside both.
5. Discussion and related work: connecting tasks, automated acceptance, practical
   engineering lessons, and the bounded connection to human analytical work.
6. Conclusion: answer the main question only as far as the evidence permits.

Prefer three main figures: the workflow; production outcomes and costs; consumer
results with uncertainty. Use readable vector graphics with source data and code.
Keep detailed optimization histories in the evidence repository.

Use clear technical English and the inverted pyramid principle. Avoid inflated
novelty, unsupported autonomy claims, and treating automation as proof of quality.
Final numbers must come from the completed evidence review, not this direction note.

## Next work

Reconcile production costs and record coverage; complete artifact and transcript
reviews; build the three figures; write the manuscript around the resulting
evidence. Continue collection under the existing schedule. Do not add new studies
or delay writing to expand the literature search.

Interim cost evidence is now available in [the cost report](../evidence/costs/2026-11-15/REPORT.md), with pinned inputs and an offline calculation script. Update the same method at the final cutoff; do not reuse frozen-only consumer cost totals.

The [first full draft](README.md) is now written in LaTeX and compiled to seven
IEEE pages. Update it from the final evidence; retain the interim snapshot and
use [SIGNOFF.md](SIGNOFF.md) to track the concrete remaining review work.
