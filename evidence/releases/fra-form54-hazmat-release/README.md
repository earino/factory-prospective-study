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

# Will a hazmat-bearing U.S. train accident release hazardous material? Forward release prediction at first notification from Form FRA 6180.54 scene circumstances

At the moment a U.S. train accident involving hazardous-material cars is first reported, will at least one of those cars release hazardous material?

Derived from U.S. Department of Transportation, Federal Railroad Administration (FRA), Office of Railroad Safety; published on data.transportation.gov. This is not its official product.

Prediction time: At first notification of the accident, when the crew and dispatcher report it and before Form FRA 6180.54 is prepared. Only circumstances a responder can observe or obtain on scene are shipped: consist counts and tonnage, speed, track type and class, weather, visibility, temperature, the apparent accident type, carrier class and state.

Evaluation scope: `retrospective_research`. Public validation is development data. The downloadable labeled holdout is public; it is not cryptographically sealed. No final holdout benchmark score is claimed.

## Measured baseline

The existing runner was used unchanged on public validation. See `evaluation.json` for rows, controls, per-year results and limitations.

```json
{
  "full_model": {
    "auc": 0.6852224885803905,
    "brier": 0.044073485641066425
  },
  "majority_prior": {
    "auc": 0.5,
    "brier": 0.046679489571589676
  },
  "calendar_identity": {
    "auc": 0.5261611427162968,
    "brier": 0.052908556665205164
  }
}
```

## Limitations

- U.S. freight rail plant is largely privately owned; this is regulated transport infrastructure rather than publicly owned infrastructure, so the fit to a 'public infrastructure' focus is by regulation and community/environmental exposure, not ownership.
- The label comes from the same retrospective form as the features, so the claim that inputs were available at the decision instant is an inference about scene knowledge, not a documented field-level timestamp; the FRA data has no separate initial-versus-final report structure to prove it.
- Base rate falls sharply over time (about 9-10% for 1975-1999 versus about 3% for 2013+), so the fixed 2013+ holdout has only about 185 positives and metrics there will be noisy.
- Reportable damage thresholds change across years, which changes which accidents enter the population at all and induces level shifts that a chronological split will partly absorb as drift.
- Consist and hazmat fields are self-reported by railroads and subject to revision for up to five years, so recent years (including the partial 2026) are unsettled.
- The extract already excludes grade-crossing collisions, so results do not generalize to the grade-crossing population, and the 'unique train accidents' subset must not be re-joined to per-report rows without deduplication.
- The public-domain designation is a U.S. Government works basis (17 U.S.C. 105) for the federal compilation; it is not a worldwide dedication, and any third-party content quoted inside railroad narratives is not covered by that designation and should not be redistributed.
- Excluding post-outcome quantities (cars derailed, damage, casualties, cause) removes the strongest correlates of release, so the task is deliberately hard and low-ceiling.
- The publisher view is titled Unique Train Accidents (Not at Grade Crossings), but the live snapshot still contains a crossing block: 10,427 records carry a non-null gxid and 10,303 records have accidenttype Hwy-rail crossing or RR grade crossing. Among the 27,244 hazmat-car accidents, 1,797 rows and 45 positives carry a non-null gxid, and 1,756 rows and 38 positives are typed Hwy-rail crossing. This build excludes rows with a non-empty gxid or a crossing accident type before labeling; the gxid and accident-type counts overlap, so the exact union is not enumerated. The resulting population is disjoint from grade-crossing records by construction, not by publisher guarantee.
- The label is recorded on the same retrospective form as the features, so availability of the inputs at first notification is a scene-knowledge inference; the extract has no field-level timestamp separating initial scene knowledge from the final report.
- Reporting railroad class is the documented publisher field Reporting Railroad Class with Class I, Class II, Class III, Not Assigned and Unassigned values, not a fallback to the reporting railroad code. Temperature is complete in the current population and is not frequently missing; these correct prior descriptions.
- The release base rate falls over time, from roughly 9 to 10 percent before 2000 to roughly 3 percent after 2012, so the fixed 2013 onward holdout carries only a few hundred positives and metrics there will be noisy.
- Reportable damage thresholds change across years, which changes population entry at all and induces level shifts that the chronological split only partly absorbs.
- Consist and hazmat fields are self-reported by railroads and remain revisable for up to five years, so recent years including the partial 2026 are unsettled across vintages.
- The explicit crossing exclusion removes the publisher contamination but also changes the population from the title-implied extract; accidents with a non-empty gxid are treated as grade-crossing records even when accidenttype does not say crossing.
- The public-domain designation rests on U.S. Government works status for the federal compilation and does not extend to third-party narrative text, which is excluded from the modelling frame entirely.
- Excluding derailed car counts, damage, casualties and cause removes the strongest correlates of release, so the task has a deliberately low ceiling.
- No per-accident tracking number was verified in the export, so identifiers are composite keys that are stable for a fixed snapshot but not across vintages; the composite now uses the published reporting railroad code and accident month names rather than the earlier misspelled candidates.
- No uncertainty interval; observed differences do not establish universal headroom

## Loading and reproduction

Verify all downloaded files with `verify_dataset.py`. CSV splits live under `extract/`; `meta.json` declares the target and identifiers. `MANIFEST.json` binds data, source snapshot, code and measured evidence.

To reconstruct without network source drift, extract `source-snapshot.tar.gz` into a new cache directory, install `reproduction/requirements.txt` in an isolated Python environment, then run `python reproduction/dataset_run.py --output NEW_EMPTY_DIRECTORY --source-cache CACHE_DIRECTORY`. Compare the qualification artifact digest with this manifest. This performs full validation and baseline evaluation and may need worker resources.

See `LICENSE.md` for source terms and preserved attribution.
