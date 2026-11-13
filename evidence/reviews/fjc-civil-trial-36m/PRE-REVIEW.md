# PRE-REVIEW: fjc-civil-trial-36m

Bounded pre-scoring contract review. This is not an acceptance gate. Nothing was fitted, rebuilt or changed.

## Summary

- **No label-derived cross-row features are shipped.** Every shipped column is a function of its own source row (`build.py:593-606`).
- **The split is a clean forward chronological design.** The windows are disjoint with a 36-month embargo, and train and public validation share no `CASE_ID`.
- **Rows are not statistically independent.** One district-by-nature-of-suit cell holds 63,592 training rows with 7 positives. `cluster.json` declares `DISTRICT` as the dependence unit.
- **`JURY` carries post-filing information.** Values `B` and `D` record a defendant jury demand in a population that excludes removed cases; they carry about 3x the trial rate.
- **The `ORIGIN = 1` population changes meaning in July 2016.** The codebook introduces a separate code for MDL-originating cases then, so train and the later cohorts are selected differently by the same rule.
- **Base rates halve between train and public validation.** The baseline's Brier score on public validation is worse than the constant prior.
- **Two build paths are fragile but I found no evidence either fired.** These are the headerless column fallback and the duplicate-record rule. The recorded build checks that would settle it are not in the pinned directory.

All of these sit inside the release's declared scope (`retrospective_research`, feature status `assumed`, label timing `unverified`). None is a newly discovered defect that contradicts the contract; several are concrete forms of limitations the release already states in general terms.

## Scope of this review

**Read**
- `MANIFEST.json`, `README.md`, `LICENSE.md`, `LICENSE-EVIDENCE.json`, `SOURCES.json`, `evaluation.json`, `.prepared.json`
- `extract/meta.json`, `extract/public/train.csv`, `extract/public/eval.csv`
- `reproduction/build.py`, `reproduction/construction.json`, `reproduction/train.py`, `reproduction/requirements.txt`
- The publisher codebook PDF cited by the release. The fetched bytes hash to `57c1ab72…c81adf`, matching `SOURCES.json:12`.

**Verified**
- `MANIFEST.json` hashes to the value in `.prepared.json:2`.
- `train.csv`, `eval.csv`, `build.py`, `construction.json`, `train.py`, `meta.json`, `README.md` and `evaluation.json` hash to their manifest entries.

**Not read or not done**
- The holdout file. It is not present in the pinned directory, and I did not look for it elsewhere.
- The raw source archive or snapshot.
- Manifest assets that are not in the pinned directory: `source-checks.json`, `qualification.json`, `extract/quality.json`, `leakage_battery.py`, `qualify_dataset.py`, `dataset_run.py`, `source_io.py`.
- Any other study's results or factory private state.
- Any model fit, any rerun of `build.py`, any historical IDB vintage.

**How the data checks were done**
- Descriptive counts over `train.csv` and `eval.csv` with a standard-library CSV scan.
- Public validation labels were read for descriptive counts only. The holdout was not read.

In the sections below, **Observed** means I read it in code, contract or public data. **Assumed** means it is inferred from source semantics or declared by the release without my verification.

## 1. Source, task and target

**Source (observed)**
- FJC Integrated Database civil cumulative file `cv88on.zip` (`build.py:12`; `SOURCES.json:16-22`).
- Retrieved 2026-11-13 02:11 UTC (`SOURCES.json:20`), 329,665,474 bytes.
- The release describes it as the cumulative file through 2026-06-30 (`construction.json:91`). I did not verify that coverage date.

**Task (observed)**
- Question: "Will a newly filed federal civil case reach trial within 36 months?" (`construction.json:226`; `meta.json:3`).
- Binary classification, positive label 1 (`meta.json:4-5`).
- Declared use is `retrospective_research` (`construction.json:89`).
- The README states no final holdout benchmark score is claimed and the holdout is not cryptographically sealed (`README.md:26`).

**Target (observed)**
- Label rule: `PROCPROG` in {6, 7, 8, 9} and `TERMDATE` present and `TERMDATE <= FILEDATE + 36 months` (`build.py:588-591`).
- This matches the contract text (`MANIFEST.json:251`; `construction.json:127`).
- The codebook defines 6-9 as during/after court or jury trial, recorded as procedural progress at termination.
- Everything else is 0: non-trial terminations, cases pending at the snapshot, trials terminating after 36 months, and missing `PROCPROG`.
- Label source columns are `PROCPROG` and `TERMDATE` (`construction.json:120-123`). Neither is shipped (`build.py:27`).

**What the target measures (assumed, from codebook semantics)**
- It is a property of the original-proceeding record in the filing district, not of the dispute.
- A case transferred out, MDL-transferred, or closed and later reopened ends its `ORIGIN = 1` record without a trial. Any later trial sits on a record with a different `ORIGIN` code, which the population excludes.
- The horizon is measured to termination date, not trial start. The release discloses this (`README.md:54`).
- I did not measure how many rows these paths affect; that needs the raw source.

**Label checks in the build (observed)**
- `trial_horizon_days` (`build.py:707-719`) and `label_rule` (`build.py:721-727`) recompute the same expression that defines the label, so they cannot fail independently of it.
- No check requires `TERMDATE >= FILEDATE`. A termination date earlier than the filing date would satisfy `term.le(horizon)`.
- I could not test for such rows because `TERMDATE` is not shipped.

## 2. Declared features

Nine features are declared (`build.py:16-26`; `construction.json:102-112`). `CASE_ID` is the identifier (`meta.json:6-8`) and `FILEDATE` is a carried time column (`construction.json:4-6`, `:229`).

| Feature | Construction | Observed in `train.csv` | Declared status |
|---|---|---|---|
| `NOS` | zero-padded 3-digit code (`build.py:596`) | 87 values; none in excluded ranges | assumed (`construction.json:60-64`) |
| `JURIS` | 1-digit code (`build.py:597`) | 5 values; code 5 has 10 rows | assumed (`:50-54`) |
| `DISTRICT` | text code (`build.py:66-79`, `:598`) | 94 values; each maps to exactly one `CIRCUIT` | assumed (`:35-39`) |
| `CIRCUIT` | 2-digit code (`build.py:599`) | 12 values; no `MISSING` | assumed (`:25-29`) |
| `JURY` | upper-cased, blank to `MISSING` (`build.py:563-568`) | B 12.2%, D 4.4%, N 32.5%, P 50.8%; no `MISSING` | assumed (`:55-59`) |
| `DEMANDED` | integer string, negatives to `MISSING` (`build.py:569-571`) | 2,798 values; `0` is 81.4%; `9999` is 2.1%; no `MISSING` | assumed (`:30-34`) |
| `FILEDATE_YEAR_MONTH` | `%Y-%m` of `FILEDATE` (`build.py:586`) | 48 values; always equals `FILEDATE[:7]` | verified (`:45-49`) |
| `RESIDENC` | 2-digit code or `MISSING` (`build.py:572-579`) | 36 values; present on exactly the 211,227 `JURIS = 4` rows | assumed (`:65-69`) |
| `ARBIT` | upper-cased or `MISSING` (`build.py:580-585`) | `MISSING` 95.6%; E, M, V, Y present | assumed (`:15-19`) |

**Excluded post-outcome fields (observed)**
- The contract lists `DISP`, `JUDGMENT`, `NOJ`, `AMTREC`, `TRCLACT`, `TRIBEGAN`, `TRIALEND` as post hoc (`construction.json:138-146`).
- None appears in `OUT_COLUMNS` (`build.py:27`) or in the public file headers.
- Party names and judge fields are not shipped. The codebook says judge fields are blank on public-use files.

**How the baseline runner treats the columns (observed in `train.py`)**
- Features are every column except the identifier and target (`train.py:27`).
- String columns with at most 1,000 distinct training values become categoricals with training levels; unseen levels become NaN (`train.py:28-32`, `:40`).
- `FILEDATE` has 1,461 distinct training values, so it is dropped by the 1,000-level rule. This is a consequence of the threshold, not an explicit exclusion.
- `FILEDATE_YEAR_MONTH` has 48 training levels, so it is kept as a categorical.
- `NOS`, `JURIS`, `CIRCUIT` and `DEMANDED` contain only digits in train and public validation, so a default CSV read types them as numbers.
- Assumed: the runner's `task.json` carries the same identifier list as `meta.json`. `task.json` is not in the pinned files.

**Documentation that does not match the public splits (observed)**
- The README says many records have missing jury-demand values, kept as an explicit category (`README.md:58`, `:67`). `JURY` has zero `MISSING` rows in train and public validation.
- The contract says missing `DEMANDED` values are kept as an explicit category (`construction.json:31`). `DEMANDED` has zero `MISSING` rows in both files; `0` holds 81%.
- Assumed: the source encodes unrecorded values as `N` and `0`, so those levels mix "not recorded" with true negatives. I did not verify this against the raw file.

## 3. Timing and vintage assumptions

**Prediction instant (observed)**
- At case filing, using only cover-sheet and case-opening fields (`construction.json:225`, `:237-242`).
- Feature documentation is declared at `prediction_time` (`construction.json:113`), with selection evidence stated as an assertion (`construction.json:84-87`).

**Vintage (observed)**
- Declared `current_snapshot` (`construction.json:90-93`).
- Feature status is `assumed` for every source field (`construction.json:14-70`).
- `training_label_timing` is `unverified` (`construction.json:88`).
- The release states there is no full-row historical availability ledger (`construction.json:82`; `README.md:71`).

**What this means for interpretation (assumed)**
- Feature values are whatever the 2026 snapshot holds, not what a clerk had entered on the filing date.
- The claim supported is retrospective: association between snapshot-vintage "filing" fields and a matured outcome. It is not evidence of historical filing-time availability, and the release does not claim that.

**Label maturity (observed arithmetic)**
- Train filings end 2014-09-30, so their horizon ends 2017-09-30, one day before validation starts.
- Validation filings end 2018-09-30, so their horizon ends 2021-09-30, one day before the holdout starts.
- Holdout filings end 2022-09-30, so their horizon ends 2025-09-30 (`meta.json:47`).
- The embargo allows zero days for publication lag. That is consistent with a retrospective claim and is flagged by `unverified` label timing.

**Asymmetric snapshot maturity (assumed)**
- Train cohorts have had at least 8.75 years after their horizon for records to be posted and corrected.
- The holdout cohort has about 9 months, if the file runs through 2026-06-30.
- Late-posted trial terminations or late field corrections would therefore affect the holdout more than train. Direction: holdout positives undercounted.
- Magnitude is unknown; I did not check it.

## 4. Population selection

**Rule in code (observed, `build.py:412-420`)**
- `ORIGIN == 1` (`build.py:380`).
- `FILEDATE`, `NOS`, `JURIS` and `DOCKET` non-missing; `DISTRICT` matches the code mask (`build.py:38`, `:379`).
- `NOS` between 1 and 999; `JURIS` between 1 and 5.
- `NOS` not in 460-465, 510-560 or 861-865.
- `FILEDATE` inside one of the three windows (`build.py:407-411`).
- One record per (`CIRCUIT`, `DISTRICT`, `OFFICE`, `DOCKET`), keeping the highest `TAPEYEAR` (`build.py:511-521`).

**Rule in contract (observed)**
- `construction.json:224` and `:243-253` state the same rule.
- The contract text does not list the `DOCKET` non-missing condition or the numeric range conditions on `NOS` and `JURIS`. This is a small wording gap, not a behavioural difference I can show matters.
- `EXCLUDED_NOS_RANGES` (`build.py:39`) is defined but never referenced; the filter hard-codes the same ranges.

**Selection uses no outcome field directly (observed)**
- The row filter reads `ORIGIN`, `FILEDATE`, `NOS`, `JURIS`, `DOCKET`, `DISTRICT` only.
- The one outcome-adjacent step is the duplicate rule, which orders by `TAPEYEAR` (see section 6).

**Malformed rows (observed)**
- The parser silently skips malformed lines (`build.py:325`) and the check that reports this is hard-coded to pass with no count (`build.py:441`).
- I did not measure how many lines were skipped.

**Checks on public data (observed)**
- Train: 600,136 rows, 5,426 positives (0.904%), `FILEDATE` 2010-10-01 to 2014-09-30, 0 duplicate `CASE_ID`.
- Public validation: 124,885 rows, 628 positives (0.503%), `FILEDATE` 2017-10-01 to 2018-09-30, 0 duplicate `CASE_ID`.
- Both match `meta.json:23-32`.
- `CASE_ID` always parses as circuit-district-office-docket, and its district and circuit tokens always equal the shipped columns.
- 671 training rows have a docket year prefix that differs from the filing year. The codebook says the docket year is "usually" the filing year, so this is expected.

## 5. Splits

**Design (observed)**
- Fixed half-open `FILEDATE` windows (`build.py:33-37`, `:535-544`; `construction.json:147-160`; `meta.json:33-47`).
- Train FY2011-FY2014, validation FY2018, holdout FY2022. Gap years are discarded. No random shuffling.
- Output rows are sorted by `FILEDATE` then `CASE_ID` (`build.py:665`), so row order carries no label information.

**Checks (observed)**
- Train and public validation share no `CASE_ID` and no filing month.
- Both contain the same 94 district codes.
- Public validation has two `NOS` codes absent from train (376, 835) and 283 `DEMANDED` values absent from train.

**Not checked**
- Holdout window bounds, district set, identifier overlap with train or validation, and the declared holdout row count and positive rate (`meta.json:26`, `:31`).

**Composition shift between train and public validation (observed)**

| Quantity | Train | Public validation |
|---|---|---|
| Positive rate | 0.904% | 0.503% |
| District `25` share of rows | 10.80% | 0.23% |
| `NOS` 365 share of rows | 16.77% | 0.97% |
| `JURIS` 4 (diversity) share | 35.2% | 19.1% |
| `JURIS` 3 (federal question) share | 56.1% | 73.2% |
| Positive rate excluding `NOS` 365/367 | 1.120% | 0.510% |

## 6. Label-derived cross-row history construction

**None is shipped (observed).** Every output column is computed from the same source row (`build.py:593-606`). There are no group rates, lags, prior-outcome counts or target encodings in `build.py`. The contract agrees: no entity columns, no persistence column (`construction.json:256-260`), and "no cross-row group rates or persistence features are shipped" (`construction.json:12`). The public directory contains only `train.csv` and `eval.csv`, matching `construction.json:10`.

**Every cross-row operation in the build (observed)**
- Diagnostic counters (`build.py:336-405`). These feed checks only.
- Sort and de-duplication on the docket key, keeping the highest `TAPEYEAR` (`build.py:511-521`).
- Per-row split assignment (`build.py:535-544`).
- Uniqueness check and output sort (`build.py:658-666`).

**The one outcome-adjacent step**
- Observed: `TAPEYEAR` missing is filled with 0, rows are sorted ascending, and the last row per key is kept (`build.py:511-521`).
- Observed: the codebook defines `TAPEYEAR` as the statistical-year label and states it is 2099 on pending case records.
- Assumed: if a key had both a terminated record and a pending record among in-window `ORIGIN = 1` rows, the pending record would win and the label would be 0.
- Not checked: whether any such duplicates exist. The build records the duplicate count in its `dedup_key_duplicates` check (`build.py:524-533`), which lands in `source-checks.json`; that file is not in the pinned directory.

**Baseline runner (observed)**
- Categorical levels come from training feature values, not labels (`train.py:32`).
- The model is fitted on training labels only (`train.py:60`).

**Downstream label-derived history (assumed)**
- The manifest names train-label group rates as simple references: filing-year, `NOS` x `JURY` and district base rates (`MANIFEST.json:249`).
- These are forward-valid for validation and holdout rows under the embargo, given the retrospective assumption that a label is knowable once its horizon closes.
- Inside the training window they are not forward-valid: a case filed in 2014 has a label that matures in 2017, after every other training filing. This only affects a modeller's internal validation.
- The contract declares access as `isolated_rows` (`construction.json:8`) with no audit probes recorded (`construction.json:11`). The term is not defined in the pinned files. I read it as each scored row being predicted without reference to other scored rows.

## 7. Concrete risk mechanisms

Each item gives the mechanism, the evidence class, and a check that would resolve it. None is asserted as a defect.

### R1. `JURY` values `B` and `D` encode a post-filing event
- **Observed:** the codebook defines `B` as both parties demanding a jury and `D` as the defendant demanding one.
- **Observed:** the population is original proceedings only (`build.py:380`), so removed cases, where a defendant acts at opening, are excluded.
- **Observed in train:** `B`/`D` are 16.7% of rows with a 2.13% trial rate; `N`/`P` have 0.66%. `B`/`D` rows hold 39.3% of training positives.
- **Observed in public validation:** `B`/`D` 1.12% versus `N`/`P` 0.39%.
- **Assumed:** a defendant's demand is normally made with or after the answer, so `B`/`D` mark cases that survived to the answer stage. Cases that end before an answer cannot have a trial.
- **Disclosed in general terms:** the snapshot "may reflect later corrections" (`construction.json:56`; `README.md:51`).
- **Consequence:** scores using `JURY` as shipped cannot be read as filing-time-available performance. Within the declared retrospective scope this is a stated limitation.
- **Check not performed:** comparison against an earlier IDB vintage. A label-free sensitivity is to collapse `JURY` to a plaintiff-demand indicator and report the change.

### R2. `ORIGIN = 1` does not select the same population before and after July 2016
- **Observed:** the codebook lists `ORIGIN` 13 as "multi district litigation originating in the district (valid beginning July 1, 2016)".
- **Observed:** the filter is a constant `ORIGIN == 1` across all windows (`build.py:380`, `:412`).
- **Observed in train:** district `25` (West Virginia Southern in the codebook) with `NOS` 365 has 63,592 rows and 7 positives. Its share falls from 10.8% of train to 0.23% of public validation.
- **Assumed:** before July 2016, cases filed directly into an MDL court were coded `ORIGIN = 1`; afterwards they are coded 13 and excluded. The observed shift is also consistent with that litigation simply winding down. I cannot separate the two without the raw source.
- **Consequence:** train contains a large near-zero-rate mass-tort block that the later cohorts mostly lack. This is covariate and prior shift, not leakage.

### R3. Base-rate shift and calibration
- **Observed:** positive rate is 0.904% in train and 0.503% in public validation; the declared holdout rate is 0.477% (`meta.json:28-32`).
- **Observed:** the baseline's Brier score on public validation (0.005388) is worse than the constant prior's (0.005019) (`evaluation.json:5-12`). The prior's Brier value is consistent with predicting the training rate.
- **Observed:** excluding `NOS` 365/367, the rate is 1.23%, 1.10%, 1.09%, 1.06% across training years, then 0.51% in validation. Most of the headline within-train decline (1.12% to 0.75%) is mass-tort composition.
- **Not determined:** why the rate halves between FY2014 and FY2018 filings.
- **Consequence:** AUC is insensitive to a uniform prior shift; Brier, PR-based and threshold metrics are not. Probability-scale comparisons against the prior will largely measure the shift.

### R4. `FILEDATE_YEAR_MONTH` has disjoint support across splits
- **Observed:** train months run 2010-10 to 2014-09 and validation months 2017-10 to 2018-09, with no overlap.
- **Observed:** the baseline treats the column as a categorical with training levels and maps unseen levels to NaN (`train.py:30-32`, `:40`). Every scored row therefore has NaN for this feature.
- **Assumed:** in training the feature can absorb the composition trend from R3, and at scoring every row follows whatever default branch the fitted trees assign to missing. I did not inspect a fitted model.
- **Consequence:** the feature contributes training-period structure that cannot transfer. Any model that parses it as a number is extrapolating 3 to 8 years.

### R5. Duplicate rule prefers pending records
- See section 6. Conditional on duplicates existing among in-window `ORIGIN = 1` rows, which I did not check.
- **Resolving check:** the `dedup_key_duplicates` entry in `source-checks.json`.

### R6. Headerless column fallback is fragile
- **Observed:** if the first line is not recognised as a header, `TERMDATE` is taken as the second date-like column by position (`build.py:140-150`).
- **Observed:** in the codebook's field order, the column after `FILEDATE` is `FDATEUSE`, a second filing date, not `TERMDATE`.
- **Observed:** in the same path `ARBIT` is inferred as a column whose values fall within M, V, E, Y (`build.py:234-269`). The codebook's arbitration-at-termination field `TRMARB` uses M, V, E.
- **Observed:** the header path maps every field by name (`build.py:97-135`).
- **Evidence the header path ran:** `RESIDENC` is present on exactly the `JURIS = 4` rows, as the codebook specifies; `ARBIT` includes `Y`, which the codebook lists only for the at-filing field; `DEMANDED` spans 0 to 9999 with 2,798 values. A positional mis-map would not produce all three.
- **Not checked:** the recorded `header_detection` result (`build.py:312-317`) in `source-checks.json`, or the raw file's first line.

### R7. Target is narrower than the headline question
- See section 1. Transfers, MDL transfers and reopenings end the selected record without a trial; the horizon is to termination; missing `PROCPROG` is 0.
- The release discloses the termination-date horizon and missing `PROCPROG` (`README.md:53-54`) and the `ORIGIN` restriction (`README.md:57`).
- **Not measured:** how many trials occur on excluded follow-on records.

### R8. Asymmetric snapshot maturity
- See section 3. Assumed mechanism, unknown magnitude, direction is undercounted holdout positives.

### R9. Rows are not independent
- **Observed:** the contract's audit rationale is "Each row is an independent case" (`construction.json:12`; `MANIFEST.json:264`).
- **Observed in train:** 14.6% of rows sit in district-by-`NOS`-by-month cells of 200 or more. The largest single-day cell is 764 filings in one district and `NOS`.
- **Observed in train:** the largest district is 10.8% of rows and the top five are 28.6%. District trial rates range from 0.04% to 3.59%.
- **Observed in public validation:** one district has 2,414 filings in `NOS` 446 alone.
- **Assumed:** these are consolidated or serial litigations whose outcomes move together, and the trial label is produced and coded by the district's judges and clerk's office.
- **Consequence:** row-level resampling will understate uncertainty. See section 8.

### R10. Baseline runner depends on four columns staying all-digit
- **Observed:** the build can write the literal `MISSING` into `DEMANDED` (`build.py:569-571`) and `CIRCUIT` (`build.py:546-549`, `:599`).
- **Observed:** neither column contains `MISSING` in train or public validation, so a default read types them as numbers.
- **Observed:** `prepare()` converts only columns that were strings in train (`train.py:38-41`).
- **Assumed:** if the holdout contained a single `MISSING` in either column, a default read would type the column as text and the baseline would fail or mis-handle it.
- **Not checked:** the holdout. A feature-only, label-free scan resolves this.

## 8. Clustering decision

Declared in `cluster.json`: `DISTRICT`.

**Basis**
- The outcome is generated and recorded at the court: trial calendars, case-management orders, court closures and the clerk's coding of procedural progress are all district-level.
- The dependence groups visible in train (R9) are contained within districts.
- Finer natural units are not available. Judge fields are blank on public-use files; the MDL docket number and party names are not shipped.
- `CASE_ID` is unique per row, but uniqueness does not establish independence here, and the evidence in R9 contradicts it.
- `CIRCUIT` is coarser with only 12 groups, and each district sits in exactly one circuit.
- `DISTRICT` is both a predictor and the grouping column. Train and public validation have the same 94 codes.

**How the choice was made**
- From source meaning and training concentration.
- Public validation was used to confirm the district set is stable and to size a limitation. No holdout row or metric was read.

**Limitations**
- Cluster sizes are very uneven. The effective number of clusters is about 33 in train and 38 in public validation by rows, and about 44 and 36 by positives.
- Positives are sparse per cluster in a single-year cohort. In public validation, 7 of 94 districts have no positive and the median district has 4.
- Dependence that crosses districts is not captured: nationwide shocks during the horizon, serial filers active in several districts, and circuit-level law.
- Holdout district codes and sizes were not inspected.

## 9. Checks not performed

- Any read of the holdout: rows, features, labels or metrics.
- Any read of the raw archive, including the header line, duplicate keys, skipped malformed lines, and `TERMDATE` or `PROCPROG` distributions.
- `source-checks.json`, `qualification.json`, `extract/quality.json` and the leakage battery code or results.
- Any rerun of `build.py` or the runner; any model fit; any reproduction of `evaluation.json`.
- Comparison of any field against an earlier IDB vintage.
- The claim that the source file runs through 2026-06-30.
- The meaning of `calendar_identity` and `calendar_identity_unseen_rows` in `evaluation.json:13-16`, `:57`; the code that computes them is not in the pinned directory.
- Licence applicability.
