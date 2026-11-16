# Record inputs checked before drafting

## Production mechanics

Source: public factory repository at `215715771b1c93f474cc7a8a223c732bf4710266`,
the final deployed revision in the window; the earlier route change only changed
model/provider settings. Inspected `factory/engine.py`, `task_prompts.py`,
`model_tasks.py`, `state.py`, and `config/pipeline.json` using git show.

- Discovery receives a broad rotating domain focus and previously selected titles.
  `seed` alternates infrastructure/environment and institutions/commerce/transport/
  public services; at most two pending candidates. A candidate initially is a search
  slot. Web search/extract are the only research tools. The model follows official
  downloads, field definitions and reuse terms, returning ready/defer, source
  evidence and a binary prediction task with population, features and fixed splits.
- Discovery and review use at most 12 turns and 600 seconds. Construction tasks
  use the write-only wrapper, no tools, at most six turns and 600 seconds. Runtime
  admission can impose tighter limits. Models return data, not lifecycle commands.
- Construction receives saved source/task evidence, a descriptor schema, previous
  proposal and bounded failure diagnostics. Worker code fetches data, builds CSVs,
  checks full artifacts and runs the fixed baseline. Models do not directly launch
  workers or operate the coordinator. Repairs reuse unchanged proposal fields.
- Access and terms failures can invoke bounded web research for the same source.
  Formatting failures can repair retained responses without rediscovery. Worker
  execution errors and semantic findings return to construction; new immutable
  job IDs preserve previous artifacts. A fifth accumulated semantic repair/reject
  outcome defers the candidate (normally four returns to build); stage failures
  also have separate five-failure model-task and worker scopes. Waiting can resume
  an existing attempt and does not itself start another model call. Do not label
  all 260 build retries as LLM code-repair rounds.
- Semantic review receives source/task, complete builder, compact qualification,
  source and license checks, baseline results, evaluation contract, construction
  notes and prior unresolved findings. It does not receive the complete quality
  descriptor: the SBIR published selection rule is missing from the actual packet.
- Deterministic code owns persistent state, bounded transitions/retries, resource
  admission, worker lifecycle, artifact identities, dual publication and anonymous
  verification. Source interpretation and accept/repair/reject judgments are model
  decisions under standing policy, not human per-release approval.

## Window and release times

`protocol.json` registers enrollment at 2026-11-12T21:27:59.319944Z. Seven earlier
published pilot datasets are excluded from the new-release cohort. This observation
start follows deployment of the temporary operating allowance; it is not system
inception. `evidence/setup/READY.json` records the baseline/export setup. The fixed
closing export is 2026-11-16T07:00Z; no extension is required for this paper.

`release-records.json` derives every admission/publication interval from the frozen
`paper/analysis/final-inputs-2026-11-16.json`, and retains the timestamps. The final
two task IDs are USGS streamgage record survival (hydrology) and California beach
advisory duration (public/environmental health). Neither is in the consumer cohort.

## Review scope and selected findings

All twelve selected reports follow `prompts/pre-review.md`: pinned contract and
builder, permitted public training/validation data, source meaning, timing,
selection, split and history checks; no holdout rows or factory private state.
They are Fable 5.2 reviews, separate from the DeepSeek production review, under the
same operator. They are not an independent team or a uniform full-source audit.

Coverage differs: FJC and FAA fetched publisher documents and matched their hashes;
CAA fetched a live dictionary; FDA had a search-summary corroboration but a primary
page was inaccessible. EIA, T100 and FRA used pinned evidence without external
source retrieval. All report checks not performed. Raw source snapshots and
holdout rows were outside these reviews. Qualification/source-check assets missing
from those pinned review packets were inspected later for artifact verification,
not retroactively supplied to the original reviews.

The table summarizes selected task-meaning findings, not every diagnostic or an
exhaustive verdict. Each phrase maps to a retained report and section in
`release-records.json`. Several concerns are conditional code paths with unmeasured
incidence (FDA undated recall, CAA resolution dates, SDWIS older-period overlap).
Do not assert observed label corruption from them. SDWIS also reports unit
magnitudes and scoring-population narrowing; these must not silently disappear
behind a 'clean' label. SBIR's later-record selection contradiction is independently
reconstructed from original acceptance inputs; its award-amount timing is a
separate unverified concern. T100's carrier-code interpretation and retrospective
FJC/FAA/FRA timing are conditions of use, not demonstrated misconduct.

The study has no separate source-review report for the last two releases. Their
production acceptance is not a substitute for the separate review column.
No new audit is needed to make the bounded claims in this manuscript.

## Consumer completion, costs and SBIR

Use the final twelve-dataset/36-model selection in the frozen input snapshot,
including the Seattle composite and provider-failure recoveries. Holdout scoring
followed freezing; retained code/transcript checks found no observed prohibited
read, but isolation is procedural. This short paper reports completion, not scores.

`evidence/costs/2026-11-16/REPORT.md` and JSON inputs establish 81.533522 hours,
14 publications, $38.22666599–$38.33494260, $2.730476–$2.738210 per publication,
and all-peak $3.923145. Components: inference $19.10–$19.21; workers $16.86;
hosting $2.26. Boundary-crossing lifetimes and direct-DeepSeek-equivalent pricing
of earlier Nous-routed tokens remain in the method. Stage-cost attribution is now computed directly from these saved model-stage totals and the 259 worker cost rows, using their recorded stage and the original conversion rate; it reconciles to both endpoints of the original total. Hosting remains shared. No retry-count-based allocation is used. See `stage-costs.json`.

`paper/analysis/final-2026-11-16/SBIR-ACCEPTANCE-AUDIT.md`, raw packet, checks and
verifier establish builder identity, population supplied, selection declaration
absent, acceptance of exclusions, and the separate reviewer finding. No causal
counterfactual or measured score effect exists. Maintenance inventory and final
readback support the two service changes and no recorded manual dataset decisions.

## Layout decisions

Use a full-width table with readable findings. Try all four requested columns;
remove per-release latency before reducing font size below normal table size.
No stand-alone successful trace is necessary if the system prose gives concrete
inputs, outputs and repair behavior. Retain wastewater only if the layout allows.

## Published disclosure comparison, 16 November revision

Each selected condition and concern was compared with the original pinned README
and construction descriptor. All 24 documents and their 12 manifests were checked
against the original pins and copied to `disclosure-documents/`. Exact supporting
passages, per-finding judgments and explicit partial-disclosure rationales are in
`disclosure-review.json`; the readable account is `DISCLOSURE-REVIEW.md`. Five of
six selected conditions have stated restrictions; the remaining condition has
its exit side stated but its entry side absent. Explicit isolated-row access is
counted as a stated restriction, not as an explanation or enforcement proof.
SBIR contains conflicting published statements, rather than simply an undisclosed
filter. Findings and disclosure now occupy separate table columns. Per-release
times remain in the evidence; the manuscript retains the range and median.

## Final wording checks

The concern count uses individual findings: one stated, three partly stated, and
four not found (eight total). SDWIS has three concerns, not one table-row verdict.
The revised lessons merge the recordkeeping points and interpret the existing
stage-cost figure, with the 64 percent share restricted to construction and checks.
Research tool-calling cycles are defined in prose. The six-turn runtime ceiling
for the tool-free construction wrapper is omitted as unhelpful implementation
detail; the ten-minute timeout and separate worker execution remain explicit.
The runtime boundary was rechecked in pinned `factory/model_tasks.py` and
`factory/hermes_write_task.py`; `docs/OPERATIONS.md` identifies max-turns as the
tool-calling iteration cap. No new production or consumer experiment was run.

## Workflow figure evidence and layout

Figure 1 keeps the original 7.15 by 2.1 inch graphic. Milestones (54 discovery
completions, 18 build completions, 14 publications) match the frozen attempt
checks and Section IV; they are not rates or a completed-cohort funnel. Return
labels match Section II's structured proposal/deferral, builder/metadata, and
accept/repair/reject with findings. The review-packet annotation identifies the
builder, checks and selected descriptor fields, with a connected path from worker
checks into the review model. It makes no causal claim about SBIR. The four-return
cap matches Section II and pinned state.py's fifth-repair deferral.

Model boxes have dashed borders and code boxes solid borders, preserving the
distinction in grayscale. Publication has no model box; standing policy is inside
the operation box. The legend is in the caption. Font extraction from the composed
PDF reports diagram text at 9 pt (rounded) and the caption at 8 pt. To retain the
original height and legibility, the lower-priority exit arrows and per-box turn
limits are omitted. No per-stage exit counts are inferred.

The final connectors show one execution sequence, not separate control-flow and
data-flow overlays. Discovery output enters code generation; worker output enters
the review model; review output enters deterministic routing. There is no direct
worker-to-routing bypass. Semantic repair returns to code generation.
