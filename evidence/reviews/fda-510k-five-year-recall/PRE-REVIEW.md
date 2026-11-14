# PRE-REVIEW — fda-510k-five-year-recall

Bounded pre-scoring contract review, written 2026-11-14. Not an acceptance gate. No model was fitted, no production file was changed, and no holdout row, raw source record, other study result or factory private state was read.

Release reviewed: `.study/releases/fda-510k-five-year-recall/` (manifest `v-68e59a5ac91ad404`, `MANIFEST.json:4`).

Short paths used below, all relative to that directory:

| Short | File |
|---|---|
| `build.py` | `reproduction/build.py` |
| `train.py` | `reproduction/train.py` |
| `construction.json` | `reproduction/construction.json` |
| `meta.json` | `extract/meta.json` |

Evidence labels used throughout:

- **[CODE]** read directly in pinned code or contract text.
- **[TRAIN]** descriptive count on `extract/public/train.csv` (labels included; no model).
- **[EVAL-STRUCT]** `product_code` and `decision_date` columns of `extract/public/eval.csv` only; eval labels were not read.
- **[ASSUMED]** stated by the contract or inferred by me, not verified here.
- **[NOT CHECKED]** a check I did not perform.

## 1. Summary

- The shipped features contain **no label-derived cross-row quantity**. The single cross-row feature, `applicant_prior_clearances`, is built only from 510(k) records and strictly earlier dates. I found no label leakage path in the pinned code.
- The contract declares itself `retrospective_research` with `training_label_timing: unverified` (`construction.json:82-83`, `README.md:26,63`). The label-maturity facts in section 4 are consistent with that declaration and are not raised as a defect.
- The main open issue for scoring is **dependence, not leakage**. One recall event labels several 510(k) numbers, and one firm recurs across rows and across splits. Neither the firm nor the recall event is shipped, so the natural cluster key is unavailable. `cluster.json` declares `product_code` as a partial key with its limits stated.
- Three things are worth knowing before reading the scores:
  1. One discrepancy between a check's description and what the code does (R5); its size is unknown.
  2. `advisory_committee` is described in the contract as a review panel, but behaves as a product-code attribute in train (R3).
  3. The measured baseline does not use `product_code` (R7).

## 2. Source, task, target

**Source [CODE].** Two openFDA bulk archives, device/510k and device/recall (`build.py:13-14`, `SOURCES.json:16-29`), retrieved 2026-11-13 23:20 UTC (`SOURCES.json:20,27`). Downloads go through `source_io.fetch` (`build.py:11,246-247`); that module is listed in `MANIFEST.json:137` but is not in the pinned directory.

**Task [CODE].** Binary classification, one row per 510(k) clearance. The question is whether the device appears in a recall record initiated within five years of clearance (`meta.json:3`, `construction.json:209`).

**Target `recall_5y` [CODE].**

- Recall records are indexed by each normalised (stripped, upper-cased) entry of `k_numbers`, keeping `event_date_initiated` (`build.py:409-429`, `build.py:89-91`).
- A row is positive when the earliest recall date on or after `decision_date` is at most `decision_date + 1826 days`, both ends inclusive (`build.py:18,512,518-523`).
- A recall dated before `decision_date` does not count (`bisect_left` at `build.py:521`).
- Otherwise the label is 0 (`build.py:519`).
- This matches the prose target at `MANIFEST.json:251`.

**Horizon [CODE].** 1826 days stands in for five calendar years. The build tolerates a one-day difference (`build.py:659-669`); a decision date whose five-year span holds two leap days gives 1827 calendar days, inside that tolerance.

**Wording note [ASSUMED].** `README.md:20` says "device recall enforcement reports"; the code reads the device/recall endpoint (`build.py:14`). My understanding is that openFDA publishes device/enforcement as a separate endpoint. I did not verify this in pinned files. It affects wording only.

**Sizes and rates.**

| Split | Rows | Positive rate | Source |
|---|---|---|---|
| train | 30,563 | 0.0872 | `meta.json:24,29`; reproduced [TRAIN]: 2,666 positives |
| eval | 9,046 | 0.0909 | `meta.json:25,30` |
| holdout | 9,014 | 0.0791 | `meta.json:26,31` |

## 3. Declared features

Nine features (`build.py:23-33`, `construction.json:91-101`), plus `k_number` as id and `decision_date` as time column (`build.py:20-21,35`). The shipped columns are exactly these plus the target (`build.py:550,591-596`; confirmed on the train and eval headers).

| Column | Construction [CODE] | Train facts [TRAIN] | Contract status |
|---|---|---|---|
| `product_code` | raw field, stripped (`build.py:323`) | 1,819 levels, 0 missing | verified (`construction.json:56`) |
| `advisory_committee` | raw field (`build.py:324`) | 18 levels, 723 missing; exact function of `product_code` | verified (`:16`) |
| `device_class` | `openfda.device_class`, falling back to top-level (`build.py:285-294`) | `2`: 27,385; `1`: 2,244; `U`: 720; `3`: 210; missing: 4; exact function of `product_code` | **assumed**, current vintage (`:44-46`) |
| `clearance_type` | raw (`build.py:326`) | Traditional 22,653; Special 6,712; Abbreviated 1,198 | verified (`:31`) |
| `decision_code` | raw; population filter makes it constant (`build.py:315-317,327`) | `SESE` only | verified (`:36`) |
| `review_days` | `decision_date − date_received`, missing if negative or absent (`build.py:524-529`) | 1 to 3,037, median 89, 0 missing | verified (`:61`) |
| `third_party_flag` | raw (`build.py:328`) | N 28,512; Y 2,051 | verified (`:66`) |
| `applicant_prior_clearances` | cross-row count, see section 7 | 0 to 847, median 5, 6,560 zeros | verified (`:26`) |
| `applicant_country_code` | raw `country_code` (`build.py:329`) | 54 levels, US 25,116 | verified (`:21`) |

Points that follow from the table:

- **`applicant` is used inside the build but never shipped** (`build.py:330`, absent from `OUTPUT_COLUMNS` at `build.py:35`; `construction.json:8`). `carry_columns` is empty (`construction.json:4`).
- **`decision_date` is not an id column** (`meta.json:6-8`), so the runner treats it as a candidate feature (`train.py:27`). See R7 for what the baseline does with it.
- **`k_number`** embeds the submission year and sequence. It is excluded as an id, provided the runner's `task.json` matches `meta.json` (`train.py:16-19`). `task.json` is not in the pinned files. [NOT CHECKED]
- **"verified" status.** The evidence cited for it is a field-documentation URL or a build-time presence assertion (`construction.json:13-67`, `build.py:333-353`). I read it as establishing that the field exists and where it comes from, not that today's value equals the value on the decision day. That reading is mine. The contract separately declares the whole source `current_snapshot` (`construction.json:84-86`).

## 4. Timing and vintage assumptions

**Prediction instant [CODE].** `decision_date` (`construction.json:208`). The contract itself notes the record is published after the decision, so the value "was not necessarily visible on the decision day" (`construction.json:222`).

**Vintage [CODE].** `current_snapshot` for both files (`construction.json:84-86`, `README.md:57`). Every feature value is as of the 2026-11 download. No historical vintage of either file is consulted.

**Window closure [CODE + arithmetic].**

- The population ends 2020-01-01, exclusive (`build.py:17`).
- The latest possible window end is 2019-12-31 + 1826 days = 2024-12-30.
- The stated snapshot is 2026-11-12 (`build.py:66`, `meta.json:47`), a margin of 682 days.
- So the drop rule at `build.py:515-517` should remove nothing. The observed count is in `source-checks.json`, which is not pinned. [NOT CHECKED]
- The snapshot is read from the first 64 KB of the recall member, falling back to a hard-coded date (`build.py:215-238,503-506`). Which branch ran is not visible in pinned files. [NOT CHECKED] Either branch gives the same rows given the 682-day margin.

**Label maturity against split boundaries [CODE + TRAIN].** A negative label is only knowable when the window closes; a positive is knowable from the recall date.

| Train rows by window close | Rows | Share |
|---|---|---|
| Before 2014-01-01 (decided by 2008-12-31) | 15,617 | 51.1% |
| During the eval decision period, 2014–2016 | 8,842 | 28.9% |
| During the holdout decision period, 2017–2019 | 6,104 | 20.0% |

- The last train window closes 2018-12-31.
- Eval windows close 2019-01-01 to 2021-12-31, all after the holdout decision period begins on 2017-01-01.
- The contract states that no embargo is applied (`meta.json:47`). Its reasoning (no feature uses a recall outcome) is correct for features [CODE]. It does not address label overlap, which the contract covers separately through `training_label_timing: unverified` (`construction.json:76,82`).
- This is consistent with the declared retrospective scope. It bounds what the scores can be read as: retrospective discrimination under chronological splitting, not what a forecaster holding only matured labels would have achieved.

**Recall-side timing [ASSUMED].** `event_date_initiated` is the firm's action date (`README.md:53`). A recall initiated inside a window but entered in FDA's database after the snapshot would be a false negative. With a margin of at least 682 days this should be small, and it falls on the latest holdout rows first. [NOT CHECKED]

**Recall coverage start [ASSUMED].** Train windows start 2004-01-01. I assume the recall database covers that date onward. [NOT CHECKED]

## 5. Population selection

**Rule [CODE].** A record is kept when:

- `decision_date` parses and lies in [2004-01-01, 2020-01-01) (`build.py:16-17,308-309`),
- `k_number` is non-empty (`build.py:312-314`),
- `decision_code` upper-cased equals `SESE` (`build.py:315-317`).

After labelling, rows are de-duplicated on `k_number`, keeping the earliest date (`build.py:548-549`). [TRAIN] `k_number` is unique in train, and every value is `K` plus six digits.

**Selection is label-blind [CODE].** Candidates are fixed at `build.py:275-331`, before the recall file is opened at `build.py:400`. The only later filter is the window-closure drop, which depends on dates alone. This agrees with `construction.json:78-81`.

**Scope of "510(k)-cleared" [CODE + ASSUMED].**

- Only `SESE` is kept, so other substantially-equivalent decision codes are outside the population.
- The three splits total 48,623 rows. The build constant for in-window records is 49,270 (`build.py:64`), accepted within ±10% (`build.py:371-376`).
- If the actual count is near that constant, about 98.7% of in-window records are retained. The actual `n_in_window` is in the unpinned `source-checks.json`. [NOT CHECKED]
- The title at `README.md:18` is broader than the `SESE` population; `construction.json:207` states the restriction.

**Declared and unchanged by this review.** Never-marketed devices count as negatives (`README.md:56`). Recalls with no `k_numbers` are invisible, stated as 20,792 of 59,705 records (`README.md:51`); the build constant agrees, 59,705 − 20,792 = 38,913 (`build.py:65`).

## 6. Splits

- **Rule [CODE].** Fixed half-open chronological windows on `decision_date`, with no sampling: train 2004–2013, eval 2014–2016, holdout 2017–2019 (`build.py:52-56,555-572`; `meta.json:33-46`).
- **Train dates [TRAIN].** 2004-01-02 to 2013-12-31, sorted by date.
- **Eval dates [EVAL-STRUCT].** 2014-01-02 to 2016-12-30.
- **Train yearly positive rate [TRAIN].** 0.075 (2004) to 0.099 (2011), with 2010–2013 all at or above 0.091. Yearly row counts run 2,780 to 3,326.
- **Holdout is not sealed.** The labelled holdout is described as public and "not cryptographically sealed" (`README.md:26`), and its positive rate is printed in public metadata (`meta.json:31`). Holdout integrity is therefore procedural. See R8.
- **Holdout file.** `extract/private/holdout.csv` is listed in `MANIFEST.json:37` and is absent from the pinned directory. I did not look for it elsewhere.

## 7. Label-derived cross-row history construction

**Shipped features contain none [CODE].**

- Recall data lands in `recall_dates` (`build.py:398,429`).
- `recall_dates` is read in exactly two places: the label (`build.py:518-523`) and the label re-check (`build.py:617-622`).
- No feature expression references it (`build.py:530-543`).
- The build's own guard (`build.py:598-605`) compares column **names** against recall field names. It could not detect a renamed derived feature; my conclusion rests on reading the feature code, not on that guard.

**The one cross-row feature is label-free [CODE].** `applicant_prior_clearances`:

- **Input set.** `(applicant, decision_date)` pairs are collected for every 510(k) record with a non-empty applicant and a parseable date (`build.py:304-306`). This happens **before** the population filter at `build.py:308`. The count therefore includes pre-2004 records, non-`SESE` records and records without a `k_number`, and it is computed before any split (`construction.json:123`).
- **Strictly earlier.** Per applicant, dates are sorted and the stored value is the running total **before** the same-day count is added (`build.py:472-482`). Same-day clearances by the same applicant are excluded.
- **Key.** The exact stripped string, case-sensitive, with no normalisation (`build.py:82-86,304`). The contract declares the resulting undercount (`README.md:55`).
- **Self-check.** Five candidates are re-counted against the same in-memory `prior_pairs` list (`build.py:484-501`). That confirms the running-sum arithmetic. It is not an independent check of source semantics or of the applicant key.
- **Crossing split boundaries.** Eval and holdout rows count earlier clearances that sit in train. This is legitimate because the quantity uses decision dates only.

**Evaluation-side references [NOT CHECKED].** `evaluation.json:13-16,75` reports a `calendar_identity` reference with 2,068 "unseen rows", and `construction.json:239-243` names `product_code`, `advisory_committee` and `clearance_type` as entity columns. That implies a lookup derived from train labels and applied to eval. Its code (`validate.py`, `qualify_dataset.py`; `MANIFEST.json:117,147`) is not pinned, so I could not review it.

**Downstream modelling surface [CODE].**

- `train.py:1` says the runner is the file a modeller edits, and `train.py:36-37` routes feature engineering through `prepare()`.
- A modeller can therefore add group rates from train labels, such as a `product_code` base rate. That is ordinary within the retrospective scope, and it inherits the label-maturity facts of section 4.
- The contract declares `access: isolated_rows` (`construction.json:6`). Whether the scorer calls `predict_proba` one row at a time, or passes the holdout as a batch (which would allow label-free statistics across holdout rows), is not visible in pinned files. [NOT CHECKED]

## 8. Concrete risk mechanisms

None of these is asserted as a demonstrated defect unless marked [CODE]. Sizes are unknown where stated.

**R1. Shared recall events, within and across splits.** [ASSUMED mechanism; declared at `README.md:52`]

- One recall record lists several 510(k) numbers. Each listed number is labelled positive independently (`build.py:421-429`).
- A firm's original clearance and its later modifications are plausibly listed together. A 2013 train row, a 2016 eval row and a 2018 holdout row can therefore all owe their positive label to the same 2018 event.
- Consequences: positives are not independent draws; a holdout positive can share its outcome event with a train positive; row-level intervals are too narrow.
- Train context [TRAIN]: Special clearances, which are modifications of a firm's own device, are 22% of rows with a positive rate of 0.114, against 0.080 for Traditional.
- Weak direct evidence [TRAIN]: 419 groups (873 rows) share the same day, product code, country and prior-clearance count, so are probably same-firm bundles. 25 of them have mixed labels, against about 36 expected under independence at the group rate; 6 are all-positive.
- I did not measure co-listing in the recall source, which is off limits here.

**R2. Unmatured training labels at eval and holdout decision times.** [CODE + TRAIN; declared]

- See section 4: 48.9% of train labels close after the eval period begins.
- This restricts interpretation. It is consistent with `retrospective_research` and is not a defect.

**R3. Product-code-level attributes are current vintage.** [TRAIN + ASSUMED]

- In train, `device_class` and `advisory_committee` each take exactly one value per `product_code`, across 1,819 codes. All 720 `U` rows have a missing committee.
- `device_class` is declared current vintage (`construction.json:44-46`). If FDA reclassified a device type after safety problems, the shipped class carries post-clearance information for older rows. Train rates by class: `3` 0.233 (n=210), `2` 0.092, `U` 0.040, `1` 0.033. How much of that gradient, if any, comes from reclassification is unknown.
- `advisory_committee` is described as a review panel "assigned during review" (`construction.json:14,161`). A documentation search I ran outside the pinned files indicates openFDA defines this field as the panel under which the product was originally classified, based on product code, with `review_advisory_committee` being the separate review-panel field. I could not open the primary field page (HTTP 403), so treat this as corroboration from a search summary, not verification. The train functional dependence is consistent with it.
- Consequence: the column adds little beyond `product_code`, and its timing depends on product-code vintage, not on the review.
- Whether `product_code` itself is ever re-coded on old records is [NOT CHECKED].

**R4. Label ascertainment may vary by era, firm or device type.** [ASSUMED]

- Only recalls carrying a 510(k) number are visible (`README.md:51`).
- If linkage completeness differs by recall year or device type, the label noise correlates with calendar time and with features.
- Observable context: train yearly rate 0.075 to 0.099 [TRAIN]; eval 0.091; holdout 0.079 (`meta.json:29-31`).
- This matters more for Brier and calibration across splits than for AUC. It is not measurable from pinned files.

**R5. Recalls with no initiation date become label 0.** [CODE; size unknown]

- The check text says missing event dates "are counted rather than treated as a negative label" (`build.py:465`).
- The code adds a date only when one parses (`build.py:428-429`).
- A 510(k) whose only recall records lack `event_date_initiated` has no dates, and is labelled 0 and kept (`build.py:518-523`).
- The check fails only on unparseable dates, not on missing ones (`build.py:466`).
- The count (`recall_missing_event`) is in the unpinned `source-checks.json`, and may be zero. [NOT CHECKED]

**R6. `applicant_prior_clearances` measurement and fingerprinting.** [CODE + TRAIN]

- Exact-string keying splits one firm across spelling variants and renames, and does not carry history across acquisitions (declared, `README.md:55`).
- The strings are current vintage. Whether FDA edits applicant names retroactively is [NOT CHECKED].
- The count rises monotonically per applicant. Combined with `product_code`, `applicant_country_code` and `decision_date`, it partly re-identifies the withheld firm. That gives a flexible model a route to firm-level memorisation, which interacts with R1.

**R7. The measured baseline omits `product_code` and `decision_date`.** [CODE + TRAIN]

- The runner drops string columns with more than 1,000 train levels (`train.py:30-31`).
- Train has 1,819 product codes and 2,518 distinct dates, so both are dropped.
- `device_class` contains `U`, so it loads as a string and is treated as a 4-level categorical.
- The `full_model` AUC of 0.680 (`evaluation.json:5-8`) therefore excludes the column the contract calls "the strongest single categorical" (`construction.json:210`).
- This is not a defect. It is context for reading the gap between the baseline and any later model that encodes `product_code`.
- I derived this from the code and train cardinalities. I did not run `train.py`.

**R8. Holdout prevalence is public.** [CODE]

- `meta.json:31` prints the holdout positive rate.
- A modeller can shift predicted probabilities to that prevalence, which improves Brier without any gain in discrimination. AUC is unaffected.
- Together with the unsealed holdout (`README.md:26`), this means holdout Brier needs a procedural guarantee that the published prevalence was not used.

**R9. Calendar extrapolation.** [CODE]

- A modeller who parses `decision_date` gets features whose holdout values (2017–2019) lie outside the training range.
- This is expected for a chronological split and is noted with R4.

## 9. Checks not performed

- No holdout row was read. No recall or 510(k) source record was read. `source-snapshot.tar.gz` was not opened.
- Eval labels were not read. Only eval `product_code` and `decision_date` were used.
- Nothing was executed from the release: not `build.py`, not `train.py`, no verifier. File hashes were not re-verified against `MANIFEST.json`; `.prepared.json:2-3` records a prior verification, which I took as given.
- Listed in `MANIFEST.json` but absent from the pinned directory, and so not reviewed: `source_io.py`, `dataset_run.py`, `qualify_dataset.py`, `leakage_battery.py`, `validate.py`, `validate.sh`, `source-checks.json`, `qualification.json`, `extract/quality.json`, and the runner's `task.json`.
- Not measured:
  - recall-event co-listing rates;
  - firm-level dependence;
  - linkage completeness over time;
  - the count of recalls with missing dates;
  - retroactive edits to product codes or applicant strings;
  - how the scorer enforces row isolation.
- The documentation lookup in R3 came from a web-search summary. The primary openFDA field page was not retrieved.

## 10. Clustering decision

Recorded in `cluster.json`: `product_code`, status `declared`.

**Why this key.** The dependence units named by the source (recall event, firm) are not shipped. `product_code` is the only shipped column that is a real source entity above the row and has enough groups to resample.

| Measure | Train [TRAIN] | Eval [EVAL-STRUCT] |
|---|---|---|
| Clusters | 1,819 | 1,128 |
| Missing values | 0 | 0 |
| Largest cluster | 868 rows | 224 rows |
| Effective number of clusters | about 209 | about 184 |
| Label intra-cluster correlation (one-way ANOVA) | 0.078 | not computed |
| Approximate design effect | 2.2 | not computed |

**What it does not cover.** It is a partial correction. Firm-wide dependence across product codes and dependence shared with the training split remain unmodelled. Intervals clustered on `product_code` should be read as a lower bound on the true uncertainty.

**Rejected alternatives.**

- `k_number`: unique per row, but the contract itself states that rows are not independent (`README.md:52`).
- `advisory_committee`: 18 clusters, with missing values.
- `applicant_country_code`: dominated by one value.
- Any firm proxy assembled from `applicant_prior_clearances` and other columns: that would be a manufactured key.

The key was chosen from source meaning and training metadata only. No eval or holdout metric was consulted.

Sources for the R3 documentation lookup:

- [openFDA 510(k) field reference](https://open.fda.gov/fields/deviceclearance_reference.pdf)
- [FDA file layout for releasable 510(k)s](https://www.fda.gov/medical-devices/510k-clearances/file-layout-releasable-510ks)
- [openFDA device recall field definitions](https://open.fda.gov/fields/devicerecall.yaml)
