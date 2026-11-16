---
license: other
license_name: upstream-terms-preserved
license_link: LICENSE.md
task_categories:
- tabular-classification
configs:
- config_name: default
  data_files:
  - split: train
    path: extract/public/train.csv
  - split: validation
    path: extract/public/eval.csv
  - split: test
    path: extract/private/holdout.csv
---

# Twelve-month escalation to High Priority Violator status after a Clean Air Act full compliance evaluation

After a Clean Air Act source completes a full compliance evaluation with no active High Priority Violator episode, will that source enter High Priority Violator (HPV) status within the next 12 months?

Derived from U.S. Environmental Protection Agency, Enforcement and Compliance History Online (ECHO) — ICIS-Air. This is not its official product.

Prediction time: ACTUAL_END_DATE, normalized to a date, at the end of the full compliance evaluation; the decision is made after the evaluation report is entered. All historical features use records dated strictly before t. Static facility attributes and program or pollutant membership are current-snapshot approximations, not historical as-of values.

Evaluation scope: `retrospective_research`. Public validation is development data. The downloadable labeled holdout is public; it is not cryptographically sealed. No final holdout benchmark score is claimed.

## Measured baseline

The existing runner was used unchanged on public validation. See `evaluation.json` for rows, controls, per-year results and limitations.

```json
{
  "full_model": {
    "auc": 0.8564337510951802,
    "brier": 0.010757983415853435
  },
  "majority_prior": {
    "auc": 0.5,
    "brier": 0.011294752233612928
  },
  "calendar_identity": {
    "auc": 0.6846038619593475,
    "brier": 0.011472441763088393
  },
  "persistence": {
    "auc": 0.7220891468517395,
    "brier": 0.011180010140842198
  }
}
```

## Limitations

- Single current-vintage snapshot (extract 2026-11-07): earlier records reflect later corrections and back-entry, so this design does not demonstrate what was operationally visible to an agency at the time; it is explicitly retrospective.
- ICIS-Air replaced the Air Facility System around October 2014 and AFS is distributed as a separate frozen file; the design does not join the two, so usable evaluation history is roughly a decade and the build must report the first year with national coverage before accepting the frozen splits.
- HPV designation is discretionary and applied differently across state, local and EPA-led programs and across years, so part of the label reflects agency practice rather than source behaviour; state and agency identifiers are therefore mandatory controls, not optional features.
- Coverage is state-reported and uneven: some agencies enter evaluations late or not at all, and HPV practice changed over the period, so base rates vary by agency and year.
- AIR_POLLUTANT_CLASS_CODE, program lists and pollutant lists are snapshot values rather than as-of-decision values; they are used only as coarse counts and flagged as approximate, and the build should report a variant without them.
- Repeated evaluations at one facility create dependence between rows; the 365-day thinning and the facility-disjoint robustness variant reduce but do not eliminate it, and no facility-random cross-validation is used.
- The 2020-2022 evaluation window overlaps the COVID-19 period, when inspection schedules and enforcement practice were disrupted; this is disclosed rather than corrected.
- Records originate with state, local and tribal agencies and are compiled by EPA; EPA's public-domain statement covers data it produces and factual data elements are not copyrightable, but no state-specific terms were reviewed for individual submissions, and ECHO presents the data 'for informational purposes only'.
- No causal claim: the task ranks escalation risk, it does not estimate the effect of evaluations or enforcement on subsequent compliance.
- Single current-vintage snapshot extracted 2026-11-07: earlier records reflect later corrections and back-entry, so historical operational visibility is unverified; the design is retrospective.
- HPV designation is discretionary and applied differently across state, local and EPA-led programs and years, so part of the label reflects agency practice.
- No full-row availability ledger exists, so training_label_timing is unverified and all feature availability claims are assumptions or current-snapshot facts.
- The supplied research did not name the exact date columns in the stack-test and Title V certification tables; the builder probes documented candidates and fails with observed headers if none is found.
- The hazardous-air-pollutant indicator was not verified, so no HAP count feature is shipped.
- Program and pollutant breadth are current snapshot membership counts, not as-of-decision values.
- The same facility can appear in multiple years; this no-shuffle design does not remove within-facility dependence.
- The 2020-2022 evaluation window overlaps the COVID-19 disruption, which is disclosed rather than corrected.
- No causal claim is made; the task ranks escalation risk and does not estimate effects of evaluations or enforcement.
- No label-derived group rates or target encoding are used; prior history features use only records dated before each evaluation.
- Same-facility same-day full evaluations are collapsed deterministically after the preceding-365-day filter.
- No uncertainty interval; observed differences do not establish universal headroom

## Loading and reproduction

Verify all downloaded files with `verify_dataset.py`. CSV splits live under `extract/`; `meta.json` declares the target and identifiers. `MANIFEST.json` binds data, source snapshot, code and measured evidence.

To reconstruct without network source drift, extract `source-snapshot.tar.gz` into a new cache directory, install `reproduction/requirements.txt` in an isolated Python environment, then run `python reproduction/dataset_run.py --output NEW_EMPTY_DIRECTORY --source-cache CACHE_DIRECTORY`. Compare the qualification artifact digest with this manifest. This performs full validation and baseline evaluation and may need worker resources.

See `LICENSE.md` for source terms and preserved attribution.
