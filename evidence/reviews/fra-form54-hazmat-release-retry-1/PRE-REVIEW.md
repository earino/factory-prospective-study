# PRE-REVIEW — fra-form54-hazmat-release (retry-1)

Bounded pre-scoring contract review. Not an acceptance gate. No model was fitted, no production file was changed.

Paths below are relative to
`.local/studies/fra-form54-hazmat-release-retry-1/.study/releases/fra-form54-hazmat-release/`.

## 0. What I read and what I did not

**Read:** `README.md`, `SOURCES.json`, `LICENSE.md`, `LICENSE-EVIDENCE.json`, `.prepared.json`, `MANIFEST.json` (structure and contract block), `evaluation.json`, `extract/meta.json`, `reproduction/build.py`, `reproduction/train.py`, `reproduction/construction.json`, `reproduction/requirements.txt`, and the two public splits `extract/public/train.csv` and `extract/public/eval.csv` (stdlib `csv` profiling only).

**Not read or done:**

- `extract/private/holdout.csv` is not in the pinned directory and was not sought. The only holdout facts used are the declared row count and positive rate in `extract/meta.json:31,36`.
- No network access: the Socrata view, its metadata JSON and the Form 54 data dictionary were not fetched. Statements about what Form 6180.54 means are domain knowledge, marked as assumptions.
- `build.py` and `train.py` were not executed. No asset hash was re-verified.
- Files referenced but absent from the pinned release could not be reviewed: `source_io` (`build.py:13`), `validate.py` and `validate.sh` (`evaluation.json:260-264`), `task.json` (`train.py:16`), and `verify_dataset.py`, `dataset_run.py`, `source-snapshot.tar.gz` (`README.md:73-75`).
- `evaluation.json` holds public-validation metrics only (`evaluation.json:2`). I read it; it played no part in the cluster choice.

Labels: **[observed]** = seen in pinned code, contract or public rows. **[assumed]** = inference or domain knowledge, not verified here. **[not checked]** = out of bounds or not possible with the pinned files.

## 1. Source, task, target

| Item | Fact | Cite |
|---|---|---|
| Source | Socrata view `byy5-w977` on data.transportation.gov, FRA Form 54 "unique train accidents" subset | `build.py:15-18`, `SOURCES.json:3,24` |
| Fetch | Projected SoQL CSV, `$where=hazmatcars != '0'`, `$limit=50000`, no `$order` | `build.py:205-217`, `SOURCES.json:24` |
| Snapshot | Retrieved unix 1794740500 = 2026-11-15 11:01 UTC, 5,129,737 bytes | `SOURCES.json:25-27` |
| Task | Binary classification: will at least one hazmat car release, for a hazmat-bearing non-crossing train accident | `extract/meta.json:3`, `README.md:20` |
| Target | `hazmat_release = 1` iff `hazmatreleasedcars >= 1` | `build.py:398-405`, `construction.json:151-153` |
| Prediction time | "First notification", before the form is prepared | `README.md:24`, `construction.json:313` |
| Claimed use | `retrospective_research`; no holdout benchmark score claimed | `construction.json:114`, `README.md:26` |
| Baseline | Unmodified XGBoost runner, 30 trees, depth 6, fit on train only | `train.py:49-60` |

**[observed]** The target and every feature come from the same form record; the label source column is excluded from the shipped frame (`build.py:495`), and a check asserts no overlap with four named post-outcome fields (`build.py:117-122,655-663`). That check is satisfied by construction, since the shipped column list is hard-coded at `build.py:495`.

## 2. Declared features

Fourteen predictors (`build.py:20-35`, `extract/meta.json:12-25`), plus `accident_id` (id) and `accident_date` (time/carry, `construction.json:4-6,319`).

| Group | Columns | Parsing |
|---|---|---|
| Numeric | trainspeed, hazmatcars, loadedfreightcars, emptyfreightcars, grosstonnage, temperature | `pd.to_numeric(..., errors='coerce')`, `build.py:37-44,480-481` |
| Categorical | equipmenttype, tracktype, trackclass, weathercondition, visibility, accidenttype, reporting_railroad_class, stateabbr | stripped text, empty → NA, `build.py:483-484` |

**[observed]** Baseline handling in `train.py`:

- Features are all columns except `id_columns` and the target (`train.py:27`). `accident_date` is not an id column, so it is a feature candidate.
- It is dropped only by the cardinality heuristic (string column with more than 1000 distinct values, `train.py:30-31`). In `train.csv` it has 6,576 distinct values, so the baseline uses exactly the 14 declared predictors.
- Category levels come from train feature values only; unseen levels become NaN (`train.py:32,40`). No target encoding.

**[observed]** Availability status: 12 of the 14 predictors are `assumed`; only `reporting_railroad_class` is `verified` (`construction.json:25-93,216-308`). The contract nonetheless sets `features_documented_at: prediction_time` (`construction.json:143`).

**[observed]** Public-row facts relevant to feature meaning:

- `grosstonnage == 0` in 2,009 of 12,541 train rows and 2,019 of 7,697 eval rows, concentrated in `Yard/switching` and `Cut of cars`. `trainspeed == 0` in 455 train and 324 eval rows. Zeros are kept as numbers (`build.py:481`).
- `temperature == 0` in 64 train and 10 eval rows, including 24 train rows dated April–November. This contradicts the contract text "none is zero" (`construction.json:66`). The build check reports the zero count but gates only on non-null presence (`build.py:682-697`). Train temperature ranges from -40 to 754.
- `hazmatcars` exceeds `loadedfreightcars + emptyfreightcars` in 31 train and 4 eval rows.

**[assumed]** Zero tonnage and off-season zero temperature are zero-coded "not recorded" values rather than measurements. I could not confirm this without the data dictionary.

## 3. Timing and vintage assumptions

**[observed]**

- Prediction instant is event time, with no field-level timestamps (`construction.json:327-330`). Availability at first notification is stated as an inference (`README.md:52,60`).
- `training_label_timing: unverified` (`construction.json:113`).
- Vintage is `current_snapshot` from the live endpoint, with five-year revisability and a partial 2026 acknowledged (`construction.json:115-117`, `README.md:55,64`).
- `accident_date` is composed from year/month/day, falls back to the publisher `date` column, then to January 1 of the year (`build.py:407-442`). The build check requires only `day_precision > 0` and zero unresolved dates (`build.py:757-771`), so it does not bound how many rows took the January 1 fallback.
- In public rows the fallback is not visible as a spike: 16 train and 11 eval rows are dated January 1, against about 34 and 21 expected under a uniform spread. All dates match `YYYY-MM-DDT00:00:00.000`.

**[assumed]**

- All features are final-form values as revised to the 2026-11-15 snapshot, not first-notification values. For `trainspeed` ("Recorded or estimated", `construction.json:215`) and `accidenttype` (final classification) the two can differ.
- Railroads file Form 54 some weeks after the month of the accident, so the last months of 2026 are under-populated in the holdout. This is domain knowledge, not verified against the pinned files.

**[not checked]** Which date path each row took (composed vs. `date` fallback); the exact count of January 1 fallbacks; any holdout date distribution.

## 4. Population selection

**[observed]** Sequential filters in `build.py`:

1. Server-side `hazmatcars != '0'` (`build.py:205-217`), then local `hazmatcars >= 1` (`build.py:361-364`).
2. `year` between 1975 and 2026 (`build.py:52-53,367-370`).
3. Drop rows with a non-empty `gxid` or a crossing `accidenttype` (`build.py:58-63,374-388`).
4. Drop rows whose release count is not parseable (`build.py:398-400`).
5. Drop rows with no usable date (`build.py:436-438`).

**[observed]** Filter 4 conditions on the label field's missingness. The contract discloses it (`construction.json:111`). The number dropped is emitted in a check string (`build.py:595-596`) that is not persisted in the pinned release, so its size is **[not checked]**.

**[observed]** No filter conditions on the label's value. The crossing exclusion counts positives for reporting only (`build.py:379-386`).

**[observed]** Row counts in the public files match the declaration: 12,541 train with 1,372 positives and 7,697 eval with 342 positives (`extract/meta.json:29-30,34-35`).

**[observed]** `extract/meta.json:52` still carries pre-exclusion approximations ("~13,100", "~8,000", "~5,900" accidents) beside the actual 12,541 / 7,697 / 5,189 (`extract/meta.json:29-31`). Documentation staleness only.

**[assumed]** Entry into Form 54 at all requires damage above the reporting threshold in force that year. The contract acknowledges threshold changes (`README.md:54,63`) but labels selection `kind: prediction_time` (`construction.json:110`). Reportability is a post-event quantity, so the population is not fully identifiable at first notification. This limits forward interpretation; it does not bear on the retrospective claim.

## 5. Splits

**[observed]**

- Chronological, half-open, on `accident_date`: train before 2000-01-01, eval from 2000-01-01 to before 2013-01-01, holdout from 2013-01-01 (`build.py:50-51,491-493`, `extract/meta.json:38-51`).
- Rows are sorted by date then id before masking (`build.py:487`). Public rows confirm the order and the windows: train spans 1975-01-01 to 1999-12-31, eval 2000-01-02 to 2012-12-31.
- No embargo, justified by the label being realized inside the same record (`construction.json:316`).
- Declared positive rate falls from 10.9% (train) to 4.4% (eval) to 3.4% (holdout) (`extract/meta.json:33-37`). Train years run from 16.6% (1976) down to 4.5% (1995).
- Because the split key is the calendar date, rows sharing a date can never straddle a split boundary.

**[not checked]** Whether the factory scores the holdout with a model fit on train only or on train plus eval. `train.py:60` fits on train only.

## 6. Label-derived cross-row history construction

**[observed]** None exists in the pinned code.

- `build.py` has no lag, rolling, group-mean or prior-outcome feature. The target is written once per row from that row's own release count (`build.py:405,485`).
- The only cross-row operations are concatenation and sorting (`build.py:397,487`), ID-string duplicate handling (`build.py:469-472`), and aggregate counters for check messages (`build.py:381-386,506-508`). None feeds a feature.
- `train.py` derives category levels from train feature values (`train.py:32`) and nothing from labels outside `model.fit` (`train.py:60`).
- The contract declares `access: isolated_rows` with no probes (`construction.json:8-12`) and no persistence column (`construction.json:352`). That matches the code.

**[not checked]** How the `majority_prior` and `calendar_identity` reference controls in `evaluation.json:9-16` were computed. They come from `validate.py`, which is not pinned. They are label-derived aggregates by nature; I cannot confirm which rows fed them. `calendar_identity_unseen_rows: 192` (`evaluation.json:255`) suggests a train-fitted lookup, but that is inference.

## 7. Concrete risk mechanisms

Ordered by how directly each bears on interpreting a holdout score. None is asserted as a defect of the retrospective claim unless stated.

**R1. Residual multiple rows per physical event; ID uniqueness holds by construction.**

- **[observed]** No publisher ID is used: every public ID carries the `F54` composite prefix, so the `accidentnumber` candidate (`build.py:93-102`, selected in `SOURCES.json:24`) failed the non-empty-and-unique test at `build.py:454-458`.
- **[observed]** The composite key is railroad code, year, month, day, state, station, milepost and accident type (`build.py:106-115`). Colliding keys are made unique by appending a sequence suffix (`build.py:469-472`).
- **[observed]** The uniqueness check (`build.py:621-634`) and `expected_duplicate_ids: 0` (`construction.json:121`) therefore cannot detect a repeated event.
- **[observed]** Public rows contain 7 suffixed pairs in train and 4 in eval. Three train pairs are identical on every shipped feature. One train pair is label-discordant (0 and 1), the other six are both 0.
- **[observed]** A broader match (same date, state, temperature, weather, visibility and accident type) finds 14 train pairs and 5 eval pairs. Members differ in consist fields, and in `reporting_railroad_class` for 3 train pairs and 1 eval pair. Train labels in these pairs: 13 pairs both 0, 1 pair both 1, none discordant.
- **[assumed]** These are separate consist or railroad reports of one accident, or duplicate records, in a view titled "unique train accidents". Chance coincidence cannot be excluded for the broader match.
- Consequence: "each accident appears exactly once" (`extract/meta.json:52`), "Each row is a distinct accident" (`construction.json:12`) and "no repeated entity" (`construction.json:315`) hold approximately, not exactly. Scale in public rows is about 0.1–0.2% of rows, so the effect on point metrics is negligible. It does mean rows are not provably independent, which is why `cluster.json` does not use the row ID.

**R2. Same-form, revised features against a first-notification framing.**

- **[observed]** Timing is unverified and availability is assumed for 12 of 14 predictors (section 2, section 3).
- **[observed]** `accidenttype` has two outcome-adjacent levels. In train, `Fire/violent rupture` has 99 rows at 14.1% positive and `Explosion-detonation` has 5 rows at 40%, against a 10.9% base rate. Neither is a near-deterministic proxy for the label in the training rows.
- **[assumed]** The final accident type and recorded speed can incorporate post-event investigation. The size of that effect cannot be measured from one snapshot.
- Consequence: a holdout score supports "final-form circumstances discriminate release", which is what `retrospective_research` claims. It does not by itself support the forward wording in the README title (`README.md:18`).

**R3. Selection on post-event quantities.**

- **[observed]** Label-missing rows are dropped (`build.py:398-400`); count not available here.
- **[assumed]** Source entry depends on the damage threshold (section 4).
- Consequence: scores describe reportable accidents with a recorded release count.

**R4. Vintage and revision of recent holdout years.**

- **[observed]** Single live snapshot dated 2026-11-15, revisable for five years, partial 2026 (`construction.json:115-117`).
- **[observed]** Composite IDs are not stable across vintages (`README.md:68`). Suffix order additionally depends on fetched row order, and the SoQL request has no `$order` (`SOURCES.json:24`, `build.py:471`); this touches only the suffixed rows.
- Consequence: holdout rows from roughly 2022 onward may change label or features in later snapshots. A rescoring on a later vintage is not row-comparable by ID.

**R5. Base-rate and reporting-regime drift across a long gap.**

- **[observed]** The model is trained on 1975–1999 and scored on 2013 onward, with the positive rate falling by a factor of about three (`extract/meta.json:33-37`).
- Consequence: calibration-type metrics (Brier) will be driven largely by the level shift. With roughly 175 holdout positives (5,189 × 0.0337), ranking metrics will be noisy, as the contract already states (`README.md:53,62`).

**R6. Zero-coded values and one contradicted contract sentence.**

- **[observed]** See section 2: zeros in tonnage, speed and temperature are treated as measurements, and `construction.json:66` says no temperature is zero while 74 public rows are.
- Consequence: low materiality for a tree model; the contract sentence is inaccurate as written.

**R7. Holdout is not sealed.**

- **[observed]** `README.md:26` states the labeled holdout is public and not cryptographically sealed.
- **[not checked]** Whether any study participant accessed it. I did not.

## 8. Cluster declaration (see `cluster.json`)

- **Declared:** `["accident_date"]`.
- **Unit:** the physical accident. Form 54 is a per-railroad, per-consist report **[assumed]**, and R1 shows the shipped rows are not strictly one per event **[observed]**.
- **Why this key:** no shipped column identifies the event exactly, because railroad code, station and milepost are used for the ID hash and then discarded (`build.py:106-115,495`). `accident_date` is the finest shipped column that is constant across every report of one event. The contract itself names it `event_key_column` and a non-predictor carry (`construction.json:4-6,120`). It also cannot straddle a split (`build.py:491-493`).
- **Alternative considered:** `accident_date` plus `stateabbr` is tighter and is nested inside the declared key. I chose the coarser key because it stays valid if two reports of one event disagree on state; over-merging unrelated same-day accidents costs a little efficiency and no validity.
- **Rejected:** `accident_id` alone (unique by construction, R1); `reporting_railroad_class` × `stateabbr` (`construction.json:347-351`: one class holds about 80–88% of public rows, so it gives no usable replication and is a covariate stratum, not an event).
- **Basis:** source meaning, contract metadata and public train/eval row structure only. No holdout row or holdout metric was consulted.

Training-row shape under the declared key: 6,576 date clusters for 12,541 rows; 3,008 singletons; largest cluster 10 rows.
