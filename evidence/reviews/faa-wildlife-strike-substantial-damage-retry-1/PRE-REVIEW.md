# PRE-REVIEW — faa-wildlife-strike-substantial-damage (retry 1)

Bounded pre-scoring contract review, written 2026-11-15 before any holdout scoring.
This is not an acceptance gate. No model was fitted and nothing in the release was changed.

**Summary.** I found no label-derived or cross-row feature in the shipped data and no
post-strike source column in the emitted files. The release's own contract already
declares the main weaknesses (current-vintage snapshot, label-availability filter,
unverified label timing, retrospective scope). The items worth acting on before
scoring are narrower:

1. `index_nr` is shipped to candidate code and is associated with the label inside
   every public year (section 8, M1). It is a declared ID, so this matters only if a
   candidate uses it.
2. `incident_date` has no declared role as ID, feature or carry, and the baseline
   excludes it only through a cardinality rule (M2).
3. Positive prevalence falls from about 6% to 0.4%, and the published
   `majority_prior` is the training prevalence, so holdout Brier comparisons will be
   dominated by calibration level (M3).
4. Clustering is declared on `incident_date`; see section 9 and `cluster.json`.

Paths below are relative to the release root
`.study/releases/faa-wildlife-strike-substantial-damage/`.

Evidence labels used throughout:

- **[code]** — read directly from pinned code or contract, with line numbers.
- **[data]** — descriptive count I computed on `extract/public/train.csv` and
  `extract/public/eval.csv` only (standard-library CSV reads, no model).
- **[doc]** — the publisher field list. I fetched
  `https://wildlife.faa.gov/assets/fieldlist.pdf`; its SHA-256
  (`e36ac5cf…2fd9b`, 356,743 bytes) equals the documentation snapshot pinned at
  `SOURCES.json:9-15`.
- **[assumption]** — stated by the contract or by me, not verified.
- **[not checked]** — a check I did not perform.

## 1. What was and was not read

Read: `README.md`, `MANIFEST.json`, `SOURCES.json`, `LICENSE.md`,
`LICENSE-EVIDENCE.json`, `.prepared.json`, `evaluation.json`, `extract/meta.json`,
`extract/public/train.csv`, `extract/public/eval.csv`, `reproduction/build.py`,
`reproduction/train.py`, `reproduction/construction.json`,
`reproduction/requirements.txt`, plus the field list above.

Not read:

- Holdout rows. `extract/private/holdout.csv` is named at `README.md:15` and
  `MANIFEST.json:37-41` but is absent from the pinned tree (`extract/` holds only
  `meta.json` and `public/`).
- The raw FAA workbook or any source outcome field.
- Other studies' results or factory private state. While looking for a Python
  interpreter I listed the top-level file names of the study repository root; I
  opened none of them.

The SHA-256 of every pinned file I relied on (`train.csv`, `eval.csv`, `build.py`,
`train.py`, `construction.json`, `meta.json`, `evaluation.json`, `README.md`) matches
`MANIFEST.json:6-171`, and `MANIFEST.json` matches `.prepared.json:2`.

Several assets listed in the manifest are not in the pinned tree, so I could not use
them: `extract/quality.json` (`MANIFEST.json:52-56`), `qualification.json` (62-66),
`source-checks.json` (157-161), `reproduction/qualify_dataset.py` (117-121),
`reproduction/validate.py` (147-151), `reproduction/leakage_battery.py` (107-111),
`reproduction/source_io.py` (137-141).

## 2. Source, task, target

**Source [code].** One publisher file,
`https://wildlife.faa.gov/assets/database_excel.zip` (`build.py:15`), 133,416,473
bytes, SHA-256 `20e53113…c4dbf3`, retrieved at Unix 1794733458, which is
2026-11-15T09:04Z (`SOURCES.json:16-22`). The builder takes the largest `.xlsx`
member (`build.py:308-311`), reads cached cell values (`build.py:326`), and finds the
header row by requiring `INCIDENT_DATE` and a damage column (`build.py:347`). Source
roles are resolved by alias (`build.py:44-65`, `362-371`).

**Unit [doc].** `INDEX NR` is "Individual record number". `SOURCE` is "Type of
report. Note: for multiple types of reports this will be indicated as Multiple." So
one row is one database record that may consolidate several reports of one strike.

**Task [code].** "Given only what is known when a wildlife strike is reported, will
the aircraft be assessed as substantially damaged or destroyed" (`meta.json:3`).
The decision user is an airport operations officer or wildlife biologist receiving
the report (`construction.json:326`). Scope is `retrospective_research`
(`construction.json:131`, `README.md:26`); no holdout benchmark score is claimed
(`README.md:26`).

**Target [code].** `substantial_damage` with positive label 1 (`meta.json:4-5`).
The mapping is `{'N': 0, 'M': 0, 'M?': 0, 'S': 1, 'D': 1}` (`build.py:403`), applied
to the damage cell after uppercasing and stripping everything except letters, digits
and `?` (`build.py:437`). Blank is not mapped; it is dropped (`build.py:456-458`).
A non-blank code outside the map inside the population aborts the build
(`build.py:459-464`, `515-523`).

**Label meaning [doc].** `DAMAGE` is "Level of damage selected by the Database
Manager"; `Blank` is "Unknown"; `M?` is "The aircraft was damaged, but details as to
the extent of the damage are lacking."

**Observed label counts.**

| Split | Rows | Positives | Rate | Date range | Basis |
|---|---|---|---|---|---|
| train | 84,196 | 2,851 | 3.386% | 1990-01-02 to 2013-12-31 | [data], agrees with `meta.json:33,38` |
| eval | 33,250 | 353 | 1.062% | 2014-01-01 to 2018-12-31 | [data], agrees with `meta.json:34,39` |
| holdout | 25,425 | 107 (derived) | 0.421% | 2019-01-01 to 2022-12-31 | `meta.json:35,40,47-50` only; rows not read |

The holdout count is 25,425 × 0.004208456 = 107.0, my arithmetic from published
aggregates.

## 3. Declared features

**[code]** Eighteen features are declared at `build.py:17-21` and again at
`construction.json:139-158`. The emitted header is `index_nr`, `incident_date`, the
18 features, then the target (`build.py:22`), 21 columns. The public CSV headers
match exactly **[data]**. Each record tuple is assembled from one source row at
`build.py:505-512`.

| Feature | Source role (first alias, `build.py` line) | Construction | Contract evidence status |
|---|---|---|---|
| `ac_mass` | `AC_MASS` (49) | category token, missing tokens blanked (451-452, 106-113) | assumed |
| `ac_class` | `AC_CLASS` (48) | same | assumed |
| `num_engs` | `NUM_ENGS` (50) | numeric parse (116-128) | assumed |
| `type_eng` | `TYPE_ENG` (51) | category | assumed |
| `phase_of_flt` | `PHASE_OF_FLT` (52) | category | assumed |
| `height_agl` | `HEIGHT` (53) | numeric, missing stays missing | assumed |
| `speed_kts` | `SPEED` (54) | numeric | assumed |
| `distance_nm` | `DISTANCE` (55) | numeric | assumed |
| `birds_struck` | `NUM_STRUCK` (56) | ordinal band encoder (198-231, 476-489) | verified |
| `birds_seen` | `NUM_SEEN` (57) | same | verified |
| `size` | `SIZE` (58) | category (490) | assumed |
| `warned` | `WARNED` (59) | category (491) | assumed |
| `time_of_day` | `TIME_OF_DAY` (60) | category (492) | assumed |
| `sky` | `SKY` (61) | category (493) | assumed |
| `precip` | `PRECIP` (62) | field-specific missing set keeps `NONE` (39, 494-495) | verified |
| `month` | derived | `dt.month` of the row's own date (510) | assumed |
| `state` | `STATE` (47) | 50 states plus DC only (67-69, 177-184) | assumed |
| `operator_class` | `OPID` (63) | three letters → `airline`; `BUS`/`PVT`/`GOV`/`MIL` kept; else blank (187-195, 470-475) | assumed |

Status values are from `construction.json:12-112`: 15 of the 18 features are
`assumed`, three are `verified`. The contract sets
`features_documented_at: prediction_time` (`construction.json:159`).

**Excluded source fields [code].** The contract lists `DAMAGE`, `SPECIES`, `AOS`,
`EFFECT`, `NR_INJURIES`, `NR_FATALITIES`, `REMARKS`, `COMMENTS`, `COST_REPAIR`,
`COST_OTHER`, `DAM_*`, `STR_*`, `ING_*`, `REMAINS_*` as post hoc
(`construction.json:224-239`). None is resolved by `build.py:44-65` except the damage
code, and none is written (`build.py:22`, `674`). `REG`, `FLT` and the reporter
fields are dropped for privacy (`README.md:56`).

**Columns shipped without a feature role [code].**

- `index_nr` is the only declared ID (`meta.json:6-8`, `construction.json:164-166`).
- `incident_date` is the time column and event key (`construction.json:137`, `586`).
  It is listed as high-cardinality (`construction.json:160-163`), is not an ID, is
  not in the feature list, and `carry_columns` is empty (`construction.json:4`).
  `README.md:24` nevertheless describes the features as including "date/location".

**Small encoding facts [data].** The `0` band of `birds_struck` and the `MIL`
operator class never occur in train or eval. Eval contains no category level unseen
in train for any categorical feature. `month` equals the month of `incident_date` on
every public row.

## 4. Timing and vintage assumptions

**Declared prediction instant [code].** "At the strike report, on the day of the
strike, before the post-flight maintenance inspection and before laboratory species
identification" (`README.md:24`, `construction.json:439`); kind `event_time`
(`construction.json:594-599`).

**Declared vintage [code].** `current_snapshot`: "records are edited and
consolidated after reporting, and the download is a current snapshot rather than a
historical register" (`construction.json:132-135`). `training_label_timing` is
`unverified` (`construction.json:130`). The contract states there is "no full-row
availability ledger" (`README.md:59`).

**Declared outcome horizon [assumption, from contract].** Severity is "coded by the
NWSD manager, usually within days; records are subsequently revised (LUPDATE)"
(`construction.json:437`). No pinned file measures the lag.

What follows from the code:

- **[code]** Every feature value is the value in the November 2026 workbook. Nothing
  in `build.py` distinguishes a value first reported on the strike day from one
  added or edited later.
- **[code]** The time key is the strike date, `INCIDENT_DATE` (`build.py:46`,
  `436`), not a report date.
- **[doc] + [code]** The source has `REPORTED_DATE` ("Date report was written") and
  `LUPDATE` ("Last time record was updated"). Neither is among the resolved roles
  (`build.py:44-65`). So "report on the day of the strike" is an assumption that the
  source could test but the build does not.
- **[assumption]** Aircraft descriptors (`ac_mass`, `ac_class`, `num_engs`,
  `type_eng`) are fixed properties of the aircraft type and are insensitive to
  vintage. I did not verify how the publisher fills them.

**Snapshot age.** The source was retrieved 2026-11-15 (`SOURCES.json:20`). The last
holdout strike date is 2022-12-31 (`build.py:33`), so holdout labels have had about
3.9 years to be coded and revised. `meta.json:56` says "about 3.7 years against a
snapshot current to August 2026"; the pinned retrieval is later, so the stated
buffer is conservative.

For a retrospective claim, these assumptions are consistent with the declared scope.
They would not support a claim that the same feature values or labels were available
to an operator on the strike day, and the contract does not make that claim
(`README.md:53`).

## 5. Population selection

**[code]** Filters are applied in this order inside the row loop
(`build.py:432-469`):

1. Unparseable date dropped (`441-443`).
2. Date outside 1990-01-01 to 2022-12-31 dropped (`444-446`; bounds at `32-33`).
3. State not one of the 50 states or DC dropped (`447-450`).
4. Both `ac_class` and `ac_mass` missing dropped (`451-455`).
5. Blank damage code dropped (`456-458`).
6. Unexpected damage code: row skipped and the build later fails (`459-464`,
   `515-523`).
7. Missing `INDEX_NR`: row skipped and the build later fails (`465-469`, `535-543`).

Duplicate `index_nr` values fail the build (`545-564`). **[data]** IDs are unique
within train and within eval, and the two sets do not overlap.

**[code]** The contract labels selection as `prediction_time` and states its one
exception: eligibility uses "nonblank DAMAGE" (`construction.json:126-129`), "the
one later quantity used in eligibility" (`construction.json:438`). `README.md:54`
and `README.md:62` repeat this as a limitation.

**[code]** The blank-damage count is tallied only for rows that passed filters 1–4,
so it is a conditional count (`build.py:441-458`).

**[not checked]** How many rows each filter removed. The counts are written into the
check record at `build.py:526-531`, which lives in assets not present in the pinned
tree. I therefore cannot state what share of strikes the blank-damage filter
removes, in total or by year.

**[data]** Labelled rows per year rise from 1,514 (1990) to 6,980 (2018). Positives
per year stay between 85 and 156 from 1990 to 2014, then fall to 104 (2015),
53 (2016), 28 (2017) and 28 (2018). The positive rate goes from 5.75% (1990) to
0.40% (2018).

## 6. Splits

**[code]** Fixed half-open cuts on the strike date (`build.py:645-647`), boundaries
at `build.py:34-36`:

- train: date < 2014-01-01
- eval: 2014-01-01 ≤ date < 2019-01-01
- holdout: 2019-01-01 ≤ date < 2023-01-01

Every surviving row is assigned to exactly one split, and each split must be
non-empty with at least one positive (`build.py:648-662`). The same windows are
recorded at `meta.json:42-55`. Train and eval go to `public/`, holdout to
`private/` (`build.py:664-668`). Rows are written sorted by date, then ID
(`build.py:265-269`, `673`).

**[data]** Public rows respect the windows: train spans 1990-01-02 to 2013-12-31,
eval spans 2014-01-01 to 2018-12-31.

**[code]** The contract claims no embargo is needed "because each row is one
independent strike and every feature is fixed at strike time, so a later row cannot
reveal an earlier label" (`meta.json:56`). Assessment:

- For the shipped features this holds by construction, because no feature is built
  from another row (section 7).
- If a candidate fits on labels near a boundary, the only exposure is the coding lag
  of strikes in the last days before the cut. The contract's "usually within days"
  is unverified, but the affected row count is small relative to a four-year
  holdout. **[assumption]**
- The baseline fits on train only (`train.py:60`), which leaves a five-year gap
  before the holdout.

**[code]** The holdout is not sealed: "The downloadable labeled holdout is public;
it is not cryptographically sealed" (`README.md:26`). `index_nr` is the publisher's
own record number, so holdout labels can also be recovered from the public FAA
file. Holdout integrity is procedural, not enforced by secrecy.

**[code]** `meta.json:40` publishes the holdout positive rate. This is an aggregate
of holdout labels visible to anyone building a candidate (see M3).

## 7. Label-derived cross-row history

**[code] None is constructed in the release.**

- Each output record is built from a single source row (`build.py:505-512`). The
  only derived feature, `month`, comes from that row's own date (`build.py:510`).
- The cross-row operations in `build.py` are the duplicate-ID check (`545-564`),
  audit counters, value-distribution summaries, the split assignment (`645-647`) and
  the output sort (`673`). None feeds a feature value.
- The contract states the same: `carry_columns` is empty
  (`construction.json:4`), cross-row probes are empty, and "No cross-row joins,
  aggregate rates or label-derived features are shipped"
  (`construction.json:7-11`). No persistence reference exists
  (`construction.json:620`).

**Label-derived quantities outside the features.**

- The `calendar_identity` reference uses group rates over `state`, `month`,
  `ac_mass` (`construction.json:615-619`) and "must be fit on training labels only"
  (`README.md:67`). Its implementation is not in the pinned tree, so I could not
  confirm it. **[not checked]** `evaluation.json:111` reports 144 eval rows with an
  unseen group.
- The `majority_prior` reference is the training prevalence used as a constant.
  **[data]** With p = 0.010617 (eval rate) and q = 0.033861 (train rate),
  p(1−q)² + (1−p)q² = 0.0110442, which reproduces `evaluation.json:11` to all
  printed digits. The same formula reproduces the 2017 and 2018 values
  (`evaluation.json:83`, `101`).

**Candidate-side history [code].** The harness passes whole data frames to candidate
code: `prepare(df)` and `predict_proba(df)` receive every row of a split at once
(`train.py:35-41`, `64-65`), and `train.py` is the file candidates edit
(`train.py:1`). The contract declares `access: isolated_rows`
(`construction.json:6`). Nothing in the pinned code enforces row isolation.
**[not checked]** Whether the scoring harness enforces it; `validate.py` is not in
the pinned tree.

**Same-encounter repeat rows [data].** Rows sharing date, state, aircraft
descriptors, operator class, phase, height, speed and light condition form 446
groups covering 942 train rows (1.1%) and 374 groups covering 802 eval rows (2.4%).
Most of these matches rest on blank height or speed and are weak evidence of a
shared encounter; with both present there are 73 groups in train and 31 in eval.
Ten of 2,851 train positives and one of 353 eval positives sit in any such group.
Repeat records are not a material source of label dependence in the public data.

## 8. Concrete risk mechanisms

Ordered by how directly they could affect a pre-scoring decision. None of these is
asserted as a defect in the release.

### M1. `index_nr` is associated with the label and is available to candidate code

- **[code]** `index_nr` is written to all three splits (`build.py:22`, `674`). The
  baseline excludes it only because it is listed in `id_columns` (`train.py:19`,
  `27`; `meta.json:6-8`). Candidates receive the raw frame including it
  (`train.py:35-41`).
- **[data]** It is not a chronological counter. Its rank correlation with
  `incident_date` over train plus eval is 0.70, and its ranges interleave across
  splits (train 608,244–1,937,119; eval 708,307–1,936,702).
- **[data]** It is associated with the label within year. Splitting each year's
  rows into quartiles of `index_nr`, the positive rates are 2.95%, 2.55%, 3.05%,
  4.99% in train and 1.02%, 0.71%, 0.67%, 1.84% in eval. Rows with `index_nr` ≥
  1,300,000 have a rate of 7.34% against 2.96% for rows below 1,000,000 in train
  (1.92% against 0.89% in eval). The higher range has the higher rate in 24 of 24
  train years and 5 of 5 eval years.
- **Mechanism.** A record number is assigned when a record enters the database, not
  at the strike. The pattern suggests number ranges track how or when a record was
  entered, and that entry route correlates with damage. **[assumption]** I do not
  know what the ranges mean; the field list says only "Individual record number".
- **[not checked]** Whether the association holds in the holdout.
- **Scope.** The contract treats `index_nr` as an ID, so the release is consistent.
  The risk is realised only if a candidate reads `index_nr` as a predictor. That is
  checkable by reading the candidate's `train.py` before scoring.

### M2. `incident_date` has no declared role, and the baseline excludes it by accident of cardinality

- **[code]** It is not in `id_columns` (`meta.json:6-8`), not in the feature list
  (`build.py:17-21`), and `carry_columns` is empty (`construction.json:4`). The
  baseline's feature list starts as every column except IDs and target
  (`train.py:27`); `incident_date` is then removed because it is a string column
  with more than 1,000 distinct training values (`train.py:28-31`).
- **[data]** Train has 8,627 distinct dates, so the rule does remove it.
- **Mechanism.** A candidate can parse the year. The date is known at prediction
  time, so this is not leakage, and `README.md:24` lists "date/location" among the
  features. But with prevalence falling from about 6% to 0.4% (section 5), a year
  term works as an extrapolated intercept. A gain from it reflects the trend in
  which strikes get a damage code, not better severity discrimination.
- **Scope.** An interpretation issue. If a candidate uses year or trend terms, its
  holdout result should be described as including trend extrapolation.

### M3. Prevalence drift makes Brier comparisons mostly about calibration level

- **[code]** In the published by-year results, the full baseline model has a worse
  Brier score than the constant training-prevalence reference in 2017 (0.00652
  against 0.00547) and 2018 (0.00556 against 0.00489) (`evaluation.json:73-107`).
- **[data]** A constant equal to the eval prevalence would score p(1−p) = 0.010504
  over all of eval. The baseline scores 0.010478 and the training-prevalence
  constant 0.011044 (`evaluation.json:5-12`). Almost all of the baseline's Brier
  margin over the published reference is the size of the prevalence shift.
- **[code]** Holdout prevalence is 0.42% (`meta.json:40`), close to 2017–2018, and
  that number is published to candidates.
- **Mechanism.** On the holdout, any candidate that lowers its probabilities — via a
  year term, recalibration on recent eval years, or the published holdout rate —
  gains Brier without ranking strikes better. AUC is unaffected by this, but rests
  on about 107 positives.
- **Scope.** Not a data defect. A Brier improvement over `majority_prior` on the
  holdout would not by itself show useful discrimination. Comparing against a
  constant set from the most recent pre-holdout years would separate the two
  effects.

### M4. Population is conditioned on a post-event label field whose use changes over time

- **[code]** Rows with blank damage are dropped (`build.py:456-458`). **[doc]**
  Blank means "Unknown".
- **[data]** Labelled rows grow 4.6-fold from 1990 to 2018 while annual positives
  are flat until 2014 and then fall about five-fold in three years (section 5).
- **Mechanism.** Whether a non-damaging strike receives `N` or is left blank is a
  database-manager decision made after the event. If that practice changes, the
  denominator changes independently of physical risk, and inclusion itself carries
  outcome information. The contract acknowledges the filter (`README.md:54`, `62`).
- **Unexplained [not checked].** The fall in positives after 2014 could be a real
  decline, a change in how `S` is assigned relative to `M` or `M?`, or an
  interaction with the state and aircraft filters. The pinned files cannot
  distinguish these. `README.md:57` describes a fall in the "damaging share" from
  18% to about 4%, which is a different quantity from the substantial-damage rate
  measured here.

### M5. `M?` is coded as a negative

- **[code]** `'M?': 0` (`build.py:403`). **[doc]** `M?` means the aircraft was
  damaged and the extent is unknown.
- **Mechanism.** Strikes with real but undocumented substantial damage are labelled
  0. Because `M?` arises when details are lacking, sparse reports are pushed toward
  0, and a model can learn report sparsity as a negative signal.
- **[not checked]** The number of `M?` rows; code counts are in an absent asset
  (`build.py:516-521`). The contract acknowledges the coding
  (`construction.json:2`).

### M6. "Strike-time" feature values are current consolidated values

- **[code]** Vintage is `current_snapshot` and records are "edited and consolidated
  after reporting" (`construction.json:132-135`). **[doc]** A record can merge
  multiple report types.
- **[data]** Field completeness differs by label, modestly. In eval, `birds_seen` is
  missing for 32.6% of positives and 50.6% of negatives; `size` 8.2% and 17.1%;
  `speed_kts` 41.6% and 50.4%; `height_agl` 13.9% and 20.1%. In train the gaps are
  smaller and run both ways: `warned` is missing for 42.2% of positives and 32.3% of
  negatives; `distance_nm` 38.5% and 42.8%.
- **[data]** `size` is populated on 97.5% of train rows, while two other
  pilot-observation items, `birds_seen` and `warned`, are populated on 57.3% and
  67.4%.
- **Mechanism.** Damaging strikes attract follow-up reports, so whether a pilot or
  airport field is filled, and possibly its value, can depend on what happened
  after the strike. Missingness patterns then carry some outcome information that
  would not exist on the strike day.
- **[assumption] / [not checked].** The field list says `SIZE` is "as reported by
  pilot". I have no evidence that it is filled from species identification, and I
  am not asserting that. The completeness gap is consistent with multi-source
  completion but does not establish it. Testing it would need `SOURCE`,
  `REPORTED_DATE`, `LUPDATE` or `SPECIES` from the raw workbook, which I did not
  read.
- **Scope.** Consistent with the declared retrospective scope; limits any reading
  of the result as strike-day triage performance.

### M7. Candidate code can compute statistics across the scored batch

- **[code]** `predict_proba(df)` receives the whole holdout frame
  (`train.py:64-65`); the contract says `isolated_rows` (`construction.json:6`).
- **Mechanism.** A candidate's `prepare()` could derive features from the unlabelled
  holdout batch, such as rows per day, rows per state-day, or the rank of
  `index_nr`. These use no holdout labels but break the declared row isolation.
  **[data]** One such quantity already shows an association in public data: rows
  that are the only labelled strike in their state on their day have a positive
  rate of 3.91% in train against 2.68% for rows sharing a state-day (1.27% against
  0.91% in eval).
- **Scope.** Checkable by reading the candidate's `prepare()` for grouping, ranking
  or length operations over the input frame.

### Minor documentation inconsistencies

These do not affect the data.

- `README.md:58` expects "several hundred" holdout positives; `meta.json:35,40`
  implies 107.
- `README.md:51` cites a "1.2% positive rate"; the frozen population is 2.3% overall
  (`README.md:62`), and 3.39%, 1.06%, 0.42% by split (`meta.json:38-40`).
- `meta.json:56` dates the snapshot to August 2026; the pinned retrieval is
  2026-11-15 (`SOURCES.json:20`).

## 9. Clustering decision

Declared: `["incident_date"]`. Full statement in `cluster.json`.

**Source meaning.** A row is one consolidated strike record. The entities that
recur across rows are the airframe, the airport and the operator. None is usable:
`REG` is dropped (`README.md:56`), `AIRPORT_ID` is never resolved
(`build.py:44-65`), and `OPID` is collapsed to a five-value class
(`build.py:187-195`). What the release does carry is the strike date, which is the
declared event key (`construction.json:137`). Rows on one calendar day share
whatever is common to that day: possible repeat records of one encounter, several
aircraft meeting the same flock, and the same weather or migration conditions.

**Training metadata [data].** I counted pairs of positives falling in the same
cluster and compared with the count after shuffling labels within strata
(300 shuffles; 200 for the `state` + `incident_date` row).

| Cluster key | Shuffle within | Train observed / expected ± sd (z) | Eval observed / expected ± sd (z) |
|---|---|---|---|
| `incident_date` | year-month | 589 / 523.4 ± 23.1 (2.84) | 65 / 55.8 ± 7.2 (1.27) |
| `incident_date` | state × year-month | 589 / 540.0 ± 23.3 (2.10) | 65 / 56.2 ± 7.6 (1.16) |
| `incident_date` | year | 589 / 587.2 ± 24.6 (0.07) | 65 / 61.5 ± 8.5 (0.42) |
| `state` + `incident_date` | state × year-month | 42 / 31.8 ± 5.0 | 3 / 3.1 ± 1.9 |
| `state` | year-month | 189,390 / 190,748 ± 5,153 (−0.26) | 2,988 / 3,190 ± 259 (−0.78) |

Reading:

- Within a month, positives fall on the same day somewhat more often than chance:
  about 12% more pairs in train and 16% more in eval, with the eval result within
  noise.
- Against a within-year shuffle the excess disappears. Positives are spread more
  evenly across months than row volume is, which offsets the within-month effect.
  The evidence for day-level dependence is therefore modest.
- Narrowing to state plus day adds nothing detectable beyond day alone.
- `state`, the only persistent geographic column, shows no label clustering once
  month is controlled.

A one-way ANOVA intraclass estimate for `state` + `incident_date` came out at
0.19–0.26. I am not relying on it: single-row state-days have a higher positive
rate than multi-row ones (M7), which inflates that estimator without any
within-cluster dependence. The pair counts above are the usable evidence.

**Why day rather than row or state.**

- Row-level clustering would need each row to be independent. The source has
  recurring airframes, airports and operators that I cannot observe, and unique
  record numbers do not show independence.
- `state` would give 51 very unequal clusters, is itself a predictor, and shows no
  measured dependence.
- `incident_date` is a real source field, never missing (`build.py:441-443`),
  present in the holdout by construction (`build.py:22`, `674`), is not a declared
  predictor, contains every state-day grouping, and gives about 1,461 holdout
  clusters averaging about 17 rows (25,425 rows over four years).

This was chosen without reading holdout rows or any holdout metric.

## 10. Checks not performed

- No holdout row, holdout score or raw source outcome was read.
- No model was fitted; no baseline was re-run. Published `evaluation.json` numbers
  were used as given, apart from the constant-reference arithmetic in section 7.
- `build.py` was read, not executed. I did not confirm that it reproduces the
  pinned CSVs.
- Per-filter exclusion counts, damage-code counts (including `M?`), and
  unrecognised-`OPID` counts were not available (absent assets).
- The `calendar_identity` reference implementation and the scoring harness
  (`qualify_dataset.py`, `validate.py`, `leakage_battery.py`) were not available, so
  train-only fitting of the reference and row isolation at scoring are unconfirmed.
- Report-date lag, last-update dates, report source type, and any relation between
  `SIZE` and species were not examined, because they need raw source fields.
- The meaning of `index_nr` ranges was not established.
- Licence applicability was not reviewed.
- No candidate `train.py` was inspected; M1, M2 and M7 describe what to look for in
  one.
