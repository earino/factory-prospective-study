# SBIR semantic review experiment plan

Date: 20 November 2026.
Status: Plan saved; experiment not started.

Test whether a complete selection declaration and an explicit code-to-contract
comparison help a semantic reviewer detect the documented SBIR selection
contradiction. Preserve the submitted paper and historical releases. Decide
whether the results warrant a manuscript addition only after the experiment.

## Question and scope

The historical case concerns agreement between the published population/selection
declaration and the builder's exclusions based on later award records. The test
does not establish overall task validity, score effects, or a defect rate across
releases. The intervention is designed after examining this known failure.

No all-release audit, dataset reconstruction, production change, or repeated
prompt tuning is included. A negative or inconclusive result is a valid outcome.

## 1. Freeze evidence and rules

- Locate the published SBIR builder and descriptor, original review packet and
  instructions, check reports, and acceptance response in the retained evidence.
- Confirm they refer to the same published version. Record paths, commits,
  release identifiers, hashes, and any gaps.
- Confirm the exact selection declaration absent from the original packet.
- Write the scoring rules and execution settings before running reviews.
- Store the experiment separately, for example under
  `experiments/sbir-semantic-review/`, with immutable input copies and a manifest.

Checkpoint: proceed only if the preserved records support the intended comparison.
If not, report the specific evidence gap without constructing a substitute history.

## 2. Prepare cases and conditions

Two cases:

1. **Original contradiction:** the published descriptor and builder.
2. **Consistent comparison:** an experimental descriptor that explicitly declares
   the builder's later-record exclusions. Keep the builder unchanged. Check that
   all relevant population and selection wording agrees with those exclusions.
   Preserve the descriptor diff. This is a constructed comparison, not a corrected
   historical release or a claim of overall semantic validity.

Three conditions, each receiving the same builder and check reports:

1. **Original packet:** original inputs and instructions.
2. **Complete packet:** add the full descriptor; keep instructions unchanged.
3. **Explicit comparison:** complete packet plus an instruction to identify
   row-exclusion conditions, compare them with declared population and selection
   rules, and cite any contradiction.

Apply the same packet-construction procedure to both cases. If descriptor fields
also appear in the original packet, update those fields consistently for the
comparison case and record the changes. Do not insert the expected answer or
this investigation into reviewer inputs.

## 3. Run the isolated harness

Run five fresh sessions per case and condition: 2 cases × 3 conditions × 5
repetitions = **30 planned reviews**. Randomize execution order with a recorded
seed. Do not treat matching seeds as paired model randomness unless supported.

- Use the original production model identifier and settings if available.
  Record requested and reported identifiers. If unavailable, record the replacement
  before execution and describe the experiment as a new intervention test.
- Keep tool access and execution limits consistent across conditions. Inspect
  the original configuration before setting them; record departures from it.
- Save exact requests, responses, tool activity, usage, duration, and errors.
- Retain failed attempts and distinguish them from completed review decisions.
  Do not silently replace failures or select favorable runs.
- Use an isolated harness with no production-state or publication credentials.
  No factory workers or full dataset downloads are needed.

Check the harness with a smoke test before the 30 reviews. Keep smoke-test records
separate and do not use them to optimize the substantive review instructions.

## 4. Assess responses

Define detection before execution: the response must identify the declaration
that outcome fields do not select rows, identify the exclusion based on later
award-phase information, and explain their conflict. A rejection for another
reason is not detection. Record partial findings separately.

For each response, record:

- Specific contradiction detected, with supporting excerpts.
- Evidence cited from the declaration and builder.
- Acceptance, repair, or rejection decision.
- False allegation of that contradiction in the consistent case.
- Unrelated concerns, ambiguous judgments, and execution failures.

Hide condition labels during assessment where practical. State who performed
the assessment and retain the rubric and excerpts for inspection. Report counts
out of five per cell, including failure counts, plus usage and elapsed time.
These repetitions describe responses to these inputs, not general reliability.

## 5. Interpret and decide on paper inclusion

- Original versus complete packet tests the added descriptor information.
- Complete packet versus explicit comparison tests the added instruction.
- The consistent case checks whether improved detection comes with false
  contradiction reports on the comparison input.
- Frequent detection with the original packet would indicate variability in
  this case; it would not erase the retained historical acceptance.
- Failure of either intervention leaves the proposed remedy unsupported here.

Produce a short findings report and a compact results table. Add a manuscript
result only if it provides a clear engineering lesson within five pages without
displacing stronger evidence. Otherwise retain it in the evidence repository and
use it for the CEU Data Jamboree presentation or later work.

Any manuscript addition must distinguish observed responses from generalization,
state that the intervention followed inspection of the case, and avoid claiming
that a fuller packet would necessarily have changed the historical decision.

## Deliverables and completion

1. Frozen inputs, hashes, case diff, protocol, and reproducible harness.
2. All planned-run records, including failures.
3. Assessments with evidence excerpts and aggregate counts.
4. A findings report with limits and a manuscript inclusion recommendation.

Completion means all 30 planned reviews are accounted for and the assessment is
reproducible. Do not expand the experiment to obtain a favorable result.

## Time allocation

Initial estimate: **4–6 hours**, subject to input and model-access checks:

- Evidence inspection and harness: 1–2 hours.
- Execution and assessment: 1–2 hours.
- Analysis and, only if warranted, manuscript integration and PDF verification:
  1–2 hours.

Reassess after evidence inspection and the smoke test. Stop and document a
blocking access or evidence gap rather than expanding scope. The user-provided
submission deadline is 21 November 2026 at 12:59:59 Paris time. The experiment
does not make revision of the already-submitted paper a requirement.
