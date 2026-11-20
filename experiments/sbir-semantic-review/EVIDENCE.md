# Historical evidence for the experiment

The test concerns a documented selection-declaration contradiction in the first
published SBIR release. It does not assume that excluding uncertain outcomes is
always wrong, that the resulting prediction task is useless, or that its scores
are biased by a measured amount.

## Identity and publication

The historical attempt is `rw-9f58fbd0fa13-evaluate-1`, recorded on 14 November
2026. The release version is `v-0d2e623e604ecf78`.

[The retained release manifest](inputs/historical/published-manifest.json) binds
these files:

- Builder SHA-256:
  `83c612c6325b71e358d962750c56737f824cf2ed3d8751148a5f369c8e5ec73e`.
- Construction descriptor SHA-256:
  `3b668f1e98c1c80ebeada1e2b055eb9c60a318c404b1e7e73149a60bc1370c78`.

The builder in the saved review prompt matches those published builder bytes.
[Retrieval provenance](inputs/historical/retrieval.json) identifies the original
factory export commit. The earlier [acceptance audit](../../paper/analysis/final-2026-11-16/SBIR-ACCEPTANCE-AUDIT.md)
and [public evidence receipt](../../paper-agent27-short/analysis/public-evidence-verification.json)
remain available. This experiment does not repeat publication or modify a release.

## Declaration and filters

The [published descriptor](inputs/historical/published-construction.json), at
`quality.timing.row_selection.rule`, says:

> Later Phase II records from the same firm key and agency define the target; no outcome field is used to select rows.

The [builder](inputs/build.py), lines 493–500, does the following:

```python
        ambiguous = False
        for future in range(year + 1, year + 5):
            if future in unknown_phase.get((key, agency), set()):
                ambiguous = True
                break
        if ambiguous:
            excluded['unknown_phase_in_window'] += 1
            continue
```

The first pass populates `unknown_phase` using the phase field (lines 344–359).
Other exclusions use firm-level missing-year and ambiguous-agency sets
(lines 338–359 and 406–417). These records can come from later years. The
qualification descriptor names `phase` as a label-source column. Thus the
selection declaration and code disagree about using outcome-related fields to
select the population. This is a contract mismatch; it is not proof of predictive
label leakage through the shipped features.

## What the original acceptance saw and decided

The [original prompt](inputs/historical/evaluate-1/prompt.txt) includes the complete
builder, the population description, construction notes, evaluation contract,
source/license evidence, baseline measurements, a passing qualification summary,
and 17 passing source checks. The source checks report 98 exclusions for unknown
phase in the outcome window. That count covers this one filter, not all exclusions
or a measured score effect.

The instructions explicitly ask for population/selection checks and comparison
of actual code with stated rules. The full row-selection declaration quoted above
is absent from this packet.

The [saved response](inputs/historical/evaluate-1/response.json) accepts with no
findings. Its reason includes “Population matches the rule” and
“unknown/missing phases in a window are excluded rather than labeled negative.”
The [transcript](inputs/historical/evaluate-1/transcript.json) records one
`web_extract` call for two SBIR publisher pages. It does not record execution of
the builder by this semantic reviewer.

The separate pre-scoring review identified the mismatch from the published code
and descriptor. Its [retained report](../../evidence/reviews/sbir-phase1-to-phase2-conversion/PRE-REVIEW.md)
is separate from the original acceptance record.

## Alternative explanations and limits

- Dropping uncertain labels can be reasonable. The historical contradiction is
  the mismatch with the declaration, not the exclusion policy by itself.
- The original reviewer did notice the exclusions. The record does not support
  claiming that the code was unavailable or that the exclusions were invisible.
- The omitted declaration is one incomplete input. Its omission alone does not
  establish why the historical reviewer accepted the task.
- The full descriptor also discloses exclusions in limitations, while its
  selection rule denies outcome-based selection. The experiment retains that
  disagreement in the original case; it does not resolve it on the model's behalf.
- The experimental consistent case states the exclusions explicitly. It is not
  a historical correction and does not establish the safety or usefulness of
  outcome-conditioned selection for all intended uses.
- No dataset is rebuilt and no effect on downstream scores is estimated.

`inputs/manifest.json`, `freeze.json`, and `verify.py` make the version and packet
comparisons inspectable. The current experiment is assessed separately from the
historical observation.
