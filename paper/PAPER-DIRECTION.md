# Current paper direction — AGENT’27

Agreed with Eduardo on 15 November 2026. **This is the current editorial direction.**
It supersedes earlier outlines and framing where they conflict. The paper-writing
prompt must follow it. It changes the emphasis of the paper, not the study cohort,
experiments, recorded outcomes, or deadlines.

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

Ask whether another agent can obtain the public files and carry out meaningful
prediction experiments. Report artifact usability, prediction-task defects,
consumer compliance, and score uncertainty separately. Retain all selected
outcomes, including access failures and unresolved uncertainty.

**Dataset usefulness and consumer-agent superiority are different questions.**
A competitive conventional search method can still demonstrate that a dataset
supports meaningful experimentation. Do not equate a failure to beat random search
with an unusable dataset, or an improved score with proof of a valid benchmark.

Preserve existing controls, frozen results, and code/transcript review. No extra
experiment is required merely to broaden the literature comparison.

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

1. Introduction: lead with final observed output, cost, and independent-use findings.
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
