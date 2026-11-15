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

# Will a reported U.S. wildlife strike substantially damage the aircraft? Forward severity prediction from strike-time circumstances in the FAA National Wildlife Strike Database

Given only what is known when a wildlife strike is reported, will the aircraft be assessed as substantially damaged or destroyed (ICAO major damage)?

Derived from Federal Aviation Administration (FAA) and U.S. Department of Agriculture, Wildlife Services (USDA/WS), National Wildlife Strike Database. This is not its official product.

Prediction time: At the strike report, on the day of the strike, before the post-flight maintenance inspection and before laboratory species identification. Features are aircraft descriptors, encounter geometry, pilot observations, date/location and operator class; DAMAGE and all post-strike fields are excluded.

Evaluation scope: `retrospective_research`. Public validation is development data. The downloadable labeled holdout is public; it is not cryptographically sealed. No final holdout benchmark score is claimed.

## Measured baseline

The existing runner was used unchanged on public validation. See `evaluation.json` for rows, controls, per-year results and limitations.

```json
{
  "full_model": {
    "auc": 0.8898529197621798,
    "brier": 0.010477789247973546
  },
  "majority_prior": {
    "auc": 0.5,
    "brier": 0.011044156929686171
  },
  "calendar_identity": {
    "auc": 0.6029831198605038,
    "brier": 0.012772930582160788
  }
}
```

## Limitations

- Strike reporting is voluntary and FAA states an overall bias toward reporting damaging strikes, so the 1.2% positive rate is a reporting artefact and not an aircraft-level risk of damage.
- SPECIES is excluded even though the FAA's own analysis finds body mass the best single predictor of damage, because identification is usually done after the strike (Smithsonian Feather Lab, 24 hours to 10 days); SIZE is a coarse pilot-perceived proxy, so the frozen feature set is deliberately weaker than published species-based models.
- The label is an adjudicated code selected by the NWSD manager from the report and can be revised; the snapshot is current-vintage, so this shows what can be reconstructed retrospectively, not that the damage code was available to an operator at the time.
- Dropping rows with blank DAMAGE is a label-availability filter applied after the event and may correlate with reporting quality, so the modelling population is not a random sample of strikes.
- 17 U.S.C. Sec. 105 is a U.S. domestic basis only; no worldwide dedication is asserted and some jurisdictions may still protect the compilation, so non-U.S. re-users must check local law. Nothing here overrides any third-party right.
- Strike reports are third-party submissions; to avoid personal data and third-party text the release drops REPORTED_NAME, REPORTED_TITLE, REG, FLT, REMARKS and COMMENTS, and uses only coded and numeric fields.
- Fleet mix and reporting practice drift heavily across 1990-2022 (reports rise roughly tenfold and the damaging share falls from 18% to about 4%), so the chronological holdout tests transport under drift rather than stationarity.
- Positives are rare enough that the 2019-2022 holdout should be expected to contain only several hundred positive events, so subgroup and calibration estimates there will be noisy.
- Current-vintage FAA export; no full-row availability ledger. Historical availability of strike-report fields is assumed, so training label timing is unverified.
- Voluntary reporting is biased toward damaging strikes, so the positive rate is not an aircraft-level risk estimate.
- DAMAGE is an adjudicated code selected after the event; it is used only as the target and is not a feature.
- Blank DAMAGE rows are dropped, which is an outcome-availability filter and not a random sample; the prior build measured a realized positive rate near 2.3 percent (3,311 of 142,871) in the frozen population, above the FAA's published 1 percent, because unlabelled rows are removed before the rate is formed.
- NUM_STRUCK and NUM_SEEN are ordinal bands on the report form, so the animal-number features carry band membership rather than an exact count; a strike with 3 animals and one with 10 animals share a single category, and a raw integer entered in the workbook is folded into the band containing it.
- SPECIES and other post-strike or part-inspection fields are excluded even though species mass is a strong damage predictor.
- The selected member in this snapshot is Public.xlsx sheet Sheet1; the builder still resolves roles by normalised alias and fails with the selected member, the observed header list and the unresolved role names if the publisher renames a field.
- Rows with OPID tokens that are not three-letter airline codes and not BUS, PVT, GOV or MIL are counted, left missing and never guessed into a class, so operator information is lost for that share; no emitted value falls outside the documented vocabulary.
- No persistence reference applies because each row is an independent strike event; the calendar/identity reference uses state, month and ac_mass and must be fit on training labels only.
- No label-derived group-rate features are shipped; any reference rate must use only training labels whose outcome windows closed before each scored row.
- No uncertainty interval; observed differences do not establish universal headroom

## Loading and reproduction

Verify all downloaded files with `verify_dataset.py`. CSV splits live under `extract/`; `meta.json` declares the target and identifiers. `MANIFEST.json` binds data, source snapshot, code and measured evidence.

To reconstruct without network source drift, extract `source-snapshot.tar.gz` into a new cache directory, install `reproduction/requirements.txt` in an isolated Python environment, then run `python reproduction/dataset_run.py --output NEW_EMPTY_DIRECTORY --source-cache CACHE_DIRECTORY`. Compare the qualification artifact digest with this manifest. This performs full validation and baseline evaluation and may need worker resources.

See `LICENSE.md` for source terms and preserved attribution.
