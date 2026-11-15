# SBIR acceptance: observed failure mechanism

The original reviewer saw the complete construction code and explicitly noticed
later-record exclusions. It accepted those exclusions as label handling while
claiming that the population matched the plan. Its packet omitted the published
selection declaration that says outcome fields do not select rows. This supports
a failure to reconcile the complete population contract with the implemented
filters. It does not establish the model's internal reasoning or prove that a
larger packet would have changed acceptance.

## Evidence and identity

Scout exported the original records without rerunning judgment or changing
production. Codex inspected the code, packet, response, transcript, and release
declarations. The source is `earino/dataset-factory` at
`4e664b3d5fc9dc845bf25190d4bae7969b60a73f`, directory
`audits/prospective-2026-11/sbir-acceptance/`; CI passed for that exact commit.
`sbir-acceptance/retrieval.json` records the 15 retrieved file hashes.

The accepted attempt was `rw-9f58fbd0fa13-evaluate-1`, 14 November
04:25:01--04:27:07 UTC. The deployed factory commit was
`202b83b26fdb6becfcf0ac6e304e7d291693130e`. The recorded model was
`deepseek-v4.1-flash` through `ollama-cloud`.

The release is `v-0d2e623e604ecf78`, with manifest SHA-256
`7d593685f07eb2d2bd452c53541d786eddda01757298f735a4cb823a9efe20c5`.
The manifest binds both the original builder and the published construction
descriptor. `verify_sbir_acceptance.py` verifies those identities and the input/
output facts below using retained files only. Its output is
`sbir-acceptance/checks.json`.

## What the builder does

The task concerns firms with a first Phase I award in 2005--2018, with a positive
label for a Phase II award from the same agency within the next four fiscal years.
The published descriptor at `quality.timing.row_selection.rule` states that
outcome fields do not select rows.

The builder first gathers information from all award years. It excludes firms
with a missing award year, a Phase II record with an ambiguous agency, or an
unknown-phase record with an ambiguous agency (`build.py`, lines 338--359 and
406--417). These exclusions can depend on later records. It also excludes a firm
when an unknown-phase record appears in the four-year outcome window (lines
493--500). The supplied source check reports 98 exclusions from that last rule.
That is not a count of all exclusions or an estimate of score bias. The code uses
the phase field both to define the target and to determine inclusion.

Excluding uncertain labels can be a reasonable construction choice. The defect is
the discrepancy between these filters and the population/selection declarations,
not proof that every affected observation should have been retained. The effect
on predictive scores and substantive conclusions is unmeasured.

## What acceptance could and did inspect

The original prompt explicitly instructs the reviewer to check population and
selection and compare actual code with stated rules. It includes:

- The complete builder, byte-identical to the published builder.
- The proposed task's population, target, and prediction-time description.
- Construction notes, evaluation contract and baseline measurements, source and
  license evidence, a passing qualification summary, and 17 passing source checks.

It does not include the full `quality` descriptor or the quoted selection
assertion. The four-message transcript records one tool call, which retrieves two
SBIR documentation pages. It records no raw-source download or code execution.

The original response accepts with no findings. It says the population matches
the rule, describes the earliest-year selection, and explicitly accepts the
unknown/missing-phase exclusions rather than assigning negative labels. Thus it
is inaccurate to say the reviewer had no code, no population instruction, or no
awareness of the exclusions. Its response evaluates internal consistency without
resolving the complete published contract's contradiction.

The separate Fable pre-scoring review identified the discrepancy on 14 November
from the published builder and construction descriptor. It inspected training
data but neither the raw source CSV nor the holdout. Its original report remains
at `evidence/reviews/sbir-phase1-to-phase2-conversion/PRE-REVIEW.md`. This audit
adds the original acceptance record; it does not retrofit a new production review.

## Lesson and limits

Supply the complete population and selection contract to acceptance, and require
each inclusion/exclusion rule to agree with it. This is a concrete response to
the observed mismatch, not a tested guarantee. No counterfactual reviewer was run,
and the packet omission alone does not explain the model's decision causally.

## Service administration is separate from dataset production

Scout's bounded maintenance inventory identifies two production changes after
the observation window began: the inference-provider route and worker accounting.
The retained commit patches confirm that the former changes two model-routing
fields and the latter changes reservations, worker admission, and dashboard
estimates. Neither patch changes source selection, labels, semantic acceptance,
or published artifacts. Scout reports no manual candidate or acceptance changes.

These records support describing automated dataset production with service
maintenance. They do not justify counting paper review or study administration
as human assistance to the factory. The final export must still be checked for
events after this inventory's 15 November 22:23 UTC collection time.
