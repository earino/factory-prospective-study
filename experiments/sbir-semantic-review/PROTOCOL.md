# SBIR semantic review intervention protocol

Frozen before experimental execution on 20 November 2026. This is a targeted
post hoc intervention experiment on one known failure, not a new production run.

## Question and design

Does supplying the full published descriptor, with or without an explicit
selection-code comparison instruction, improve detection of the documented SBIR
selection-declaration contradiction? Does the reviewer falsely allege that
contradiction when the experimental declaration states the exclusions?

There are two cases and three conditions, five fresh reviews per cell (30 total).
`inputs/manifest.json` binds inputs and the unchanged manuscript; `schedule.json`
records the shuffled order (seed 20261120). Two sessions may run concurrently.
Every run has a new private Hermes home and neutral working directory. No shared
conversation, memory, rules, publishing credentials, or factory state is supplied.

Cases:

- Original: preserved published builder and metadata.
- Consistent comparison: same builder and measurements, with the later-record
  exclusions expressly declared in population, target, prediction-time wording,
  row-selection rule, and evaluation contract. Original packet copies of those
  fields are changed consistently. The descriptor and packet diffs are retained.
  This is an intentionally constructed comparison for this contradiction only.

Conditions:

- Original packet: original user prompt; original case is byte-identical.
- Complete packet: same instructions and packet plus `published_descriptor`.
- Explicit comparison: complete packet plus a general instruction to enumerate
  row-selection code conditions and reconcile them with the declarations.

The complete descriptor adds more than the one disputed sentence. The first
comparison tests that packet addition, not an isolated sentence-level effect.
The comparison case also supplies more explicit selection detail in fields
already visible in the original packet. Do not interpret case differences as a
single-word intervention. `prepare.py` defines all transformations.

## Evidence basis

The retained builder and descriptor match the release manifest for
`v-0d2e623e604ecf78`. Original attempt: `rw-9f58fbd0fa13-evaluate-1`.
The source packet contains the published builder, a passing qualification
summary, and 17 passing source checks. It omits the declaration that no outcome
field is used to select rows. The original response accepted the later-record
exclusions and returned no findings. Historical files are copied unchanged.

## Runtime and known departures

Use `deepseek-v4.1-flash` through `ollama-cloud`, the recorded historical identifier
and route. Record wire-reported model IDs without treating them as independent
provider attestation. Temperature, reasoning, and output length use the local
runtime/provider defaults; retain the actual request parameters rather than
claiming unknown historical settings were reproduced.

Use current local Hermes at the commit in `runtime/preflight.json`. The original
hosted system prompt and complete configuration are not retained, so this is not
an exact runtime replay. `--ignore-rules`, a fresh Hermes home, and a minimal
configuration exclude local project/user instructions. The only model-visible
tools are `web_search` and `web_extract`. The keyless Firecrawl backend replaces
the historical hosted web gateway. Live documentation may have changed.

Preserve the historical bounds of 12 tool-calling iterations and 600 seconds.
The parent process terminates the process group after 645 seconds if needed.
Existing runtime retries remain visible in captured requests; no extra review
is launched to replace a failed planned session. No context/model fallback is
intentionally configured. Inspect reported routes for unexpected fallback.

`capture_runtime.py` records Ollama HTTP request and response bodies, including
system/user messages, tool definitions/results, response model fields, and usage.
Authentication headers are never recorded. Session records also retain tool
activity, decisions, and usage. Model-list requests and automatic title generation
are kept separately identifiable from substantive review calls.

## Scoring rules

Primary detection requires all three elements in a substantive reviewer response:

1. Identify the published assertion that outcome fields do not select rows
   (a faithful paraphrase is sufficient).
2. Identify row exclusion based on later award phase/agency information, especially
   unknown/missing phases within the four-year outcome window.
3. Explain the inconsistency between the assertion and the actual selection.

Record the evidence excerpt for each positive classification. A generic warning
about selection bias, an unrelated rejection, or noticing an exclusion without
connecting it to the declaration is not full detection. Record those as partial
selection findings. A specific conflict with the shorter population description
can be a partial finding even when the full assertion was unavailable.

The original packet does not supply the disputed assertion. Its full-detection
count is therefore an information-limited baseline, not a fair test of a model's
ability to reconcile a declaration it has seen. Interpret partial findings too.

For the consistent case, a false contradiction report means alleging that the
later-record selection conflicts with a no-outcome-selection or unconditional
population claim that this case no longer makes. Merely noting that the declared
selection is outcome-conditioned is correct and not a false positive. Rejecting
for another substantive concern also is not a false positive on this measure.

For every run record full detection/false allegation, partial findings, accept /
repair / reject decision, unrelated concerns, ambiguous judgments, and execution
failures. A correct concern can appear in limitations even with an accept verdict;
record both detection and decision rather than equating them.

Codex will assess the responses against this rubric, first in a shuffled view
without condition labels where practical. This is not independent human or fully
blind adjudication: the investigator designed the experiment and content can
reveal the condition. Retain all assessment excerpts for external inspection.

Inspect tool traces for retrieval of the public study/audit or other information
that reveals the known finding. Report such exposure explicitly; do not silently
drop affected runs. No search or model-output-driven prompt revision is allowed.

## Failures and reporting

Count every scheduled session. Distinguish no-response/runtime failure, malformed
structured output, and a completed semantic decision. Do not treat a failure as
acceptance. Report counts over five scheduled sessions per cell and completed
response counts alongside them. Keep unclear assessments separate.

Report input/output/cache tokens, API calls, run elapsed time, total batch wall
time, and tool calls, separating title generation and smoke tests where records
permit. Usage is provider/runtime reporting, not an invoice. No worker time is
incurred. Do not pool smoke tests with the 30 reviews.

The smoke tests are infrastructure checks using only the SBIR dictionary page:
smoke-01 found a search-only extraction backend and a database-export serialization
error; smoke-02 verified wire capture/export and the same extraction limitation;
smoke-03 successfully extracted the Phase definition using Firecrawl. No SBIR
semantic case was reviewed in these tests. The first smoke's session database was
not retained after the export error; stdout and process/start records remain.

Completion requires an accounted-for schedule, immutable inputs, retained outputs,
assessments with excerpts, reproducible aggregates, and a findings report with
manuscript advice. Do not claim a general detection rate or a causal explanation
of the original acceptance. Do not expand the run count to obtain a clearer result.
