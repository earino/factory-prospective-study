# SBIR review intervention: neither tested change detected the contradiction

20 November 2026. Completed post hoc experiment on one preserved release.

**Verified:** All 15 reviews of the original case accepted it. None connected
the published assertion that outcome fields do not select rows to the builder's
later-record exclusions. Supplying the complete descriptor produced 0 detections
in 5 reviews; adding an explicit selection-code comparison instruction also
produced 0 in 5. Neither intervention is a demonstrated remedy in this experiment.

The historical release and submitted manuscripts are unchanged. No production
workers, Scout sessions, budget transfers, or replacement reviews were needed.

## What was tested

The [frozen protocol](PROTOCOL.md) specified two cases, three conditions, and five
fresh sessions per cell before responses were inspected. The original case uses
the preserved builder and descriptor. The constructed comparison declares the
later-record exclusions and keeps the builder and check measurements unchanged.
It establishes agreement for this selection rule, not overall task validity.

The original packet contains the builder, population description, qualification
summary, and source checks. The complete packet adds the full descriptor. The
explicit-comparison condition also instructs the reviewer to enumerate selection
conditions and reconcile them with the declarations. The original packet omits
the disputed assertion, so its detection count is an information-limited baseline.

Every session used the recorded historical model identifier,
`deepseek-v4.1-flash`, through `ollama-cloud`, with only web search and extraction,
12 tool-calling iterations, and a 600-second runtime budget. Current local Hermes
and keyless Firecrawl differ from the historical hosted runtime. The original
complete system configuration was not retained. This tests interventions with
preserved inputs; it is not an exact replay of the historical runtime.

## Results

Each row accounts for five scheduled sessions and five final responses. Detection
requires the declaration, the later-record exclusion, and an explanation of their
conflict. A general selection warning or an unrelated repair is insufficient.

| Case | Packet/instruction | Target contradiction reported | Partial selection finding | Stated decisions |
|---|---|---:|---:|---|
| Original | Original packet | 0/5 | 4/5 | 5 accept |
| Original | Complete packet | 0/5 | 5/5 | 5 accept |
| Original | Explicit comparison | 0/5 | 5/5 | 5 accept |
| Consistent comparison | Original packet | 0/5 | 5/5 | 5 accept |
| Consistent comparison | Complete packet | 0/5 | 5/5 | 3 accept, 2 repair |
| Consistent comparison | Explicit comparison | 0/5 | 5/5 | 5 accept* |

*One response (`r04`, initially assessed as `b16`) states accept but contains
malformed JSON in its limitations array. This cell therefore has four valid
structured accept decisions and one malformed response with a legible accept
statement. It is not counted as a valid machine-readable acceptance. All 30
processes exited successfully, with no timeout or missing final response.

The consistent-case counts are false allegations of this specific contradiction,
not tests of every possible defect. Its two repair decisions concern firm-identity
resolution. Those concerns were not independently adjudicated here. Zero false
allegations is weak evidence of discrimination when the reviewer also detects
none of the original contradictions.

**Verified:** The two fuller-packet conditions supplied the disputed sentence in
the actual captured HTTP requests. All ten original-case responses in those
conditions noticed relevant selection filters, but none identified the required
conflict. The result is more specific than failure to read or mention the code.

For example, `r03` (original case, explicit comparison; blind ID `b26`) describes
the extra filters as “conservative label-validity drops that can only remove rows
and cannot expose outcomes,” and says the descriptor's eighth limitation covers
the phase/agency exclusions. It then accepts. `r21` (`b14`, same condition) says
the exclusions are broader than the population text, but treats them as
conservative guards and an outcome-window-informed drop. Neither reconciles this
with “no outcome field is used to select rows.” These excerpts support the narrow
finding that noticing selection was insufficient for detection in these runs.

The [assessments](assessment/assessments.json) retain exact supporting excerpts
for all responses. Codex, the same investigator who prepared the protocol, first
read all responses under shuffled IDs without opening the assignment mapping.
Content could reveal the condition. The initial observations were hashed before
joining case identities; this is not independent human or fully blind assessment.
No ambiguous primary classifications were recorded.

## Challenge to the interpretation

**Verified:** The original descriptor itself contains both the no-outcome-selection
assertion and a limitation describing phase/agency exclusions. The original
reviewer already had that limitation. A review can reasonably regard exclusion
of uncertain labels as permissible retrospective construction. The contradiction
is between the categorical declaration and those implemented exclusions; it does
not establish that exclusion is always wrong or that the dataset is worthless.

**Inferred:** Some responses appear to give priority to the limitation and to the
idea that conservative exclusion protects labels. Their words support that
interpretation, but do not establish an internal reasoning mechanism. The tested
instruction did not direct the model to one expected answer, and no further
prompt variants were tried after inspecting these results.

**Unverified:** This experiment does not establish why the historical reviewer
accepted the release, whether another model or a narrower assertion-specific
check would detect it, or whether the exclusions changed predictive scores.
It also does not test a deterministic semantic assertion. The proposed full-
contract intervention remains unsupported as a remedy here.

**Contradicted by these runs:** The expectation that simply supplying the full
descriptor, or adding the tested reconciliation instruction, would reliably
expose this contradiction under this runtime. This is not a claim that fuller
review packets are unnecessary or that semantic review cannot work.

## Execution, usage, and exposure

**Verified:** The batch ran from 17:37:46 to 18:23:42 UTC on 20 November, with two
concurrent fresh sessions. Wall time was 45.94 minutes; summed session elapsed
time was 88.17 minutes. Individual runs took 93.55–294.01 seconds (median 168.56).
Worker time was zero. All returned model IDs matched the requested identifier;
this is provider/runtime reporting, not independent model attestation.

The wire and Hermes usage records reconcile exactly:

- Reviews: 83 API calls; 1,719,442 uncached input tokens; 1,935,958 cache-read
  tokens; 1,298,505 reported output tokens.
- Automatic titles: 30 calls; 4,242 uncached input, 8,328 cache-read, and 387
  output tokens.
- Combined wire prompt tokens: 3,667,970, including cached input. Combined output:
  1,298,892. Do not add cached tokens a second time to that wire prompt total.
- Web tools: 83 calls. Counts and timing are in [usage.json](results/usage.json).
  These are reported tokens, not a bill or a count of final-answer words.

Smoke tests are excluded. Retained smoke-02 and smoke-03 records contain 3 calls
each, respectively 1,696/3,202 uncached input, 4,676/4,680 cached input, and
431/740 output tokens. Smoke-01 exposed a database-export error and its session
database was not retained; complete setup usage cannot be recovered from that
record. The successful smoke used only a source-documentation question.

**Verified within the stated inspection:** All 83 tool-result records were
indexed. Requested URLs/queries and returned repository links were inspected;
screening for the study, factory, author, release identifier, selection declaration,
and semantic-review terms found no matches. Returned GitHub material concerned
other SBIR tools and data work. No retrieval of this study or its known-failure
audit was identified. [The inventory](results/tool-exposure.json) and full tool
results are retained. This does not rule out prior model exposure or an indirect
reference that this inspection missed. No run was excluded for tool activity.

## Recommendation for the paper

Retain the current end-to-end experience-paper framing and the historical SBIR
case. Do not present full-contract review as an effective fix. These results
add a useful negative intervention result, but a six-cell experiment needs its
protocol and runtime limits to be interpretable. It does not justify replacing
the paper's operating evidence or expanding its claims before the deadline.

Keep the submitted five-page manuscript unchanged in this execution and publish
this report with the evidence. If the authors choose to update the submission,
the useful addition is a short result next to the SBIR case, linked to this
protocol: five reviews with the complete descriptor and five with the additional
comparison instruction all accepted the original case without identifying the
contradiction. State that these were post hoc tests under a current local runtime.
Do not imply that all 30 reviews tested the defective case or that the comparison
descriptor is a validated dataset. No new visualization is needed for the short
paper; the six-row table belongs with this report and can support the presentation.

## Completion evidence

- Historical identity and exact paths: [EVIDENCE.md](EVIDENCE.md), input manifest,
  original acceptance packet/response, and unchanged builder hash.
- Frozen design: protocol, schedule, case diffs, and `freeze.json`, committed
  before execution at `8c06a5bc07c640dbe2d0a83d891058e42ac06ba6`.
- All 30 trials: `runs/r01` through `runs/r30`, including wire bodies, session
  records, final responses, and process status. No replacement trials.
- Assessment and reproducible totals: `assessment/`, `summarize.py`, and `results/`.
- Integrity: `verify.py --complete` and `check_capture.py` verify 27 frozen input
  files, 30 fresh sessions, actual prompts/model IDs, exact final-response capture,
  and 183 lossless response archives, including smoke captures.
- Submitted manuscript, figures, archives, and PDFs retain their frozen hashes.
  Final clean-checkout and CI verification are recorded in [PROGRESS.md](PROGRESS.md).
