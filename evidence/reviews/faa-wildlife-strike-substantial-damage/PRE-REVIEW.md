# PRE-REVIEW — faa-wildlife-strike-substantial-damage

Bounded pre-scoring contract review. Not an acceptance gate. No model was fitted, no production file was changed, and nothing was committed.

Release reviewed: `.study/releases/faa-wildlife-strike-substantial-damage/`, manifest version `v-d654c9f4ddfcf60c` (`MANIFEST.json:4`), manifest SHA-256 `1ddf9894…d040` (`.prepared.json:2`, recomputed and matching).

Each statement below is tagged:

- **[observed]** — read directly in pinned code, contract or training data.
- **[assumed]** — asserted by the release, or inferred by me, without evidence in the pinned files.
- **[not checked]** — a check I did not perform, with the reason.

Paths are relative to the release directory. `build.py`, `train.py` and `construction.json` live under `reproduction/`; `meta.json`, `train.csv` and `eval.csv` under `extract/`.

## 0. What I read and what I did not

**Read**

- All pinned files: `README.md`, `MANIFEST.json`, `SOURCES.json`, `evaluation.json`, `LICENSE.md`, `LICENSE-EVIDENCE.json`, `.prepared.json`, `extract/meta.json`, `reproduction/build.py`, `reproduction/construction.json`, `reproduction/train.py`, `reproduction/requirements.txt`.
- `extract/public/train.csv` in full, labels included, for descriptive counts only (stdlib scripts, no model).
- `extract/public/eval.csv` for label-free structure only: header, row count, date range, ID overlap with train, and (incident_date, state) group sizes. I did not read its label column; the eval-year rates quoted below come from `evaluation.json`.
- The publisher field list `https://wildlife.faa.gov/assets/fieldlist.pdf`. The fetched bytes hash to `e36ac5cf…fd9b`, identical to the documentation snapshot pinned in `SOURCES.json:9-15`.

**Not read**

- `extract/private/holdout.csv`. It is absent from the pinned directory and I did not look for it elsewhere.
- The raw workbook (`database_excel.zip`, `source-snapshot.tar.gz`), other studies' results, and factory private state.

**Disclosure.** The pinned public metadata itself publishes two holdout aggregates: row count 25,425 and positive rate 0.004208 (`meta.json:32-41`), about 107 positives. I saw those two numbers because they are in a file I was told to read. They did not enter the clustering choice, which rests on source meaning and `train.csv` only.

**Integrity [observed].** The SHA-256 of `train.csv`, `eval.csv`, `build.py`, `construction.json`, `train.py`, `meta.json`, `README.md` and `evaluation.json` each match their `MANIFEST.json` entries (`MANIFEST.json:17-51, 82-91, 142-146`).

**Pinned set is partial [observed].** The manifest lists files that are not in the pinned directory, including `extract/quality.json`, `qualification.json`, `source-checks.json`, `reproduction/dataset_run.py`, `leakage_battery.py`, `qualify_dataset.py`, `source_io.py`, `validate.py` and `validate.sh` (`MANIFEST.json:52-66, 97-156, 157-161`). Anything those files would establish is **[not checked]** here: the recorded build-check outputs, the calendar/identity reference fit, and the scoring harness.

## 1. Source, task, target

**Source [observed]**

- One publisher ZIP, `https://wildlife.faa.gov/assets/database_excel.zip` (`build.py:15`, `SOURCES.json:16-22`). The largest `.xlsx` member is selected (`build.py:308-311`) and the header is resolved by normalised alias (`build.py:44-65, 234-255, 362-371`).
- Retrieved 2026-11-15T09:04Z (`SOURCES.json:20`, unix 1794733458). It is a current-vintage export, not a historical register (`construction.json:132-135`).
- The publisher's manager consolidates reports into one record per strike (quote at `construction.json:276-278`). The field list says the same from the other side: `SOURCE` is "Type of report… for multiple types of reports this will be indicated as Multiple", and `LUPDATE` is "Last time record was updated".

**Task [observed]**

- Binary classification on strike reports, "given only what is known when a wildlife strike is reported" (`meta.json:3`).
- Declared prediction time: "At the strike report, on the day of the strike, before the post-flight maintenance inspection and before laboratory species identification" (`README.md:24`, `construction.json:439`).
- Declared scope: `retrospective_research`. The labelled holdout is public and not sealed, and no final holdout benchmark score is claimed (`README.md:26`, `construction.json:131`).

**Target [observed]**

- `substantial_damage`, positive label 1 (`meta.json:4-5`).
- Code rule: `allowed = {'N': 0, 'M': 0, 'M?': 0, 'S': 1, 'D': 1}` (`build.py:403`), applied at `build.py:511`. The damage token is normalised at `build.py:437`.
- A nonblank code outside that set inside the population fails the build (`build.py:459-464, 522-523`).
- Publisher definitions (field list): DAMAGE is "Level of damage selected by the Database Manager"; Blank = "Unknown"; N = "No damage was reported"; M? = "The aircraft was damaged, but details as to the extent of the damage are lacking".
- So the negative class is "no damage reported", minor, or damaged-but-extent-unknown. The M?→0 choice is disclosed (`construction.json:2`, `construction.json:443`).

**Not checked.** The contract says the header is on `Sheet1` of `Public.xlsx` and that `DAMAGE_LEVEL`, `NUM_STRUCK`, `NUM_SEEN`, `PHASE_OF_FLIGHT` and `PRECIPITATION` are the live column names (`construction.json:243`). The field list uses different names (`DAMAGE`, `BIRDS_STRUCK`, `BIRDS_SEEN`, `PHASE_OF_FLT`, `PRECIP`). The alias table covers both spellings (`build.py:52, 56-57, 62, 64`), but I did not open the workbook to confirm which resolved.

## 2. Declared features

**[observed]** 18 features in `FEATURES` (`build.py:17-21`), identical to `construction.json:139-158`. The emitted header is `index_nr`, `incident_date`, the 18 features, then the target (`build.py:22`, `meta.json:9-31`). Each record is assembled at `build.py:505-512`.

| Feature | Source role and parser | Code | Missing in train |
|---|---|---|---|
| `ac_mass`, `ac_class` | coded category via `_cat` | `build.py:451-452` | 0.1%, 0.1% |
| `num_engs` | numeric via `_num` | `build.py:507` | 0.2% |
| `type_eng`, `phase_of_flt` | coded via `_cat` | `build.py:507-508` | 0.3%, 1.0% |
| `height_agl`, `speed_kts`, `distance_nm` | numeric via `_num` | `build.py:508-509` | 11.5%, 37.2%, 42.6% |
| `birds_struck`, `birds_seen` | ordinal band via `_band` | `build.py:198-231, 476-489` | 0.3%, 42.7% |
| `size`, `warned`, `time_of_day`, `sky` | coded via `_cat`; `NONE` treated as missing | `build.py:38, 490-493` | 2.5%, 32.6%, 10.0%, 20.6% |
| `precip` | coded; `NONE` kept as a value | `build.py:39, 494-495` | 23.1% |
| `month` | `dt.month`, derived from `incident_date` | `build.py:510` | 0% |
| `state` | 50 states plus DC via `_state` | `build.py:177-184, 447` | 0% |
| `operator_class` | derived from OPID: BUS, PVT, GOV, MIL, or `airline` for any other three-letter token | `build.py:187-195, 470-475` | 4.6% |

Further **[observed]** facts:

- Excluded post-strike fields are listed at `construction.json:224-239` (DAMAGE, SPECIES, AOS, EFFECT, costs, `DAM_*`, `STR_*`, `ING_*`, `REMAINS_*`, and others). `build.py` resolves only the roles in `SOURCE_ALIASES` (`build.py:44-65`), so none of those columns, nor `INDICATED_DAMAGE`, `REPORTED_DATE` or `LUPDATE`, can reach the output.
- In `train.csv`, `month` equals the month of `incident_date` on every row. `operator_class` takes the values airline, BUS, PVT, GOV or blank; MIL does not occur.
- **`incident_date` is not a declared feature, but the runner does not exclude it by contract.**
  - `meta.json:6-8` declares only `index_nr` as an ID.
  - `train.py:27` takes every non-ID, non-target column as a candidate feature, so `incident_date` is a candidate.
  - The baseline drops it only through the cardinality heuristic at `train.py:30-31` (object column with more than 1,000 distinct values). Train has 8,627 distinct dates.
  - `construction.json:4` has `carry_columns: []`; the column appears as `time_column` and `event_key_column` (`construction.json:137, 586`) and under `high_cardinality_columns` (`construction.json:160-163`).

**[assumed]**

- 15 of the 18 features carry availability status `assumed` (`construction.json:12-113`). The three marked `verified` (`birds_seen`, `birds_struck`, `precip`) cite "FAA Form 5200-7 … (review evidence)" (`construction.json:25, 30, 75`). That form is not among the pinned sources (`SOURCES.json`), so I cannot confirm it.
- The pinned field list itself describes BIRDS_SEEN and BIRDS_STRUCK only as "Number of birds/wildlife seen by pilot / struck" and does not mention bands. The band vocabulary is nonetheless visible in train (`1`, `2-10`, `11-100`, `>100`).

## 3. Timing and vintage

**[observed]**

- The event clock is `incident_date`. The source's `REPORTED_DATE` ("Date report was written") and `LUPDATE` exist per the field list but are not read by `build.py`.
- Vintage is declared `current_snapshot` (`construction.json:132-135`) and `training_label_timing` is declared `unverified` (`construction.json:130`).
- The prediction instant is declared `event_time` with no lag fields (`construction.json:594-599`).
- Outcome horizon: the label is coded "usually within days" and "subsequently revised (LUPDATE)" (`construction.json:437`).
- The last scored incident date is 2022-12-31 (`build.py:33`). The snapshot was retrieved 2026-11-15 (`SOURCES.json:20`), so the adjudication buffer is at least about 3.9 years.

**[assumed] (by the release, and disclosed)**

- That every feature value in the consolidated current-vintage record equals what was on the report at strike time (`README.md:59`, `construction.json:115`). The tag `features_documented_at: prediction_time` (`construction.json:159`) is an assertion; the per-feature statuses behind it are `assumed`.
- That "the snapshot [is] current to August 2026" (`meta.json:56`, `construction.json:442`). The pinned retrieval timestamp is November 2026. I cannot tell from the pinned files whether "August 2026" describes the workbook's content or is stale text. The buffer conclusion does not depend on it.

**Reviewer position.** The release claims retrospective reconstruction, not historical operational availability (`README.md:53`). I am not asking for a historical forecasting ledger for that claim. The vintage points in section 7 are about which specific fields are most likely to differ from their strike-time values, not a demand for universal proof.

## 4. Population selection

**[observed]** Filters are applied per row in this order:

1. Parseable date (`build.py:441-443`).
2. Date within 1990-01-01 … 2022-12-31 (`build.py:32-33, 444-446`).
3. State in the 50 states or DC (`build.py:447-450`).
4. At least one of `ac_class` / `ac_mass` present (`build.py:451-455`).
5. DAMAGE nonblank (`build.py:456-458`).
6. DAMAGE in the allowed set, else build failure (`build.py:459-464`).
7. Nonempty `INDEX_NR`, else build failure (`build.py:465-469, 535-543`).

Other **[observed]** facts:

- `INDEX_NR` uniqueness across all splits is enforced (`build.py:545-564`). I confirmed 84,196 unique IDs in train and 33,250 in eval, with zero overlap between them.
- Result: 142,871 rows = 84,196 + 33,250 + 25,425 (`meta.json:32-36`). Positives are 2,851 + 353 + 107 = 3,311 by arithmetic from `meta.json:37-41`, matching the figure at `README.md:62`.
- **Filter 5 conditions on the outcome's availability.** The release says so in prose ("The one later quantity used in eligibility is the damage code itself", `construction.json:438`; `README.md:54, 62`). The machine-readable tag nevertheless reads `selection.kind: prediction_time` (`construction.json:126-129`). Tag and rule disagree; the prose is the accurate one.

**[not checked]**

- How many rows each filter removes. The counts are recorded by the build (`build.py:405, 516-531`) but land in files outside the pinned set. For rough scale only: the publisher reports 343,556 strikes for 1990–2025 (`construction.json:271-273`), so well over half of the 1990–2022 reports are excluded by filters 3–5 combined. I cannot split that between unknown aircraft, non-U.S. location and blank DAMAGE.
- Whether blank-DAMAGE frequency varies by year. This matters for section 7, R1.

## 5. Splits

**[observed]**

- Fixed half-open cuts on `incident_date` (`build.py:34-36, 645-647`; `meta.json:42-55`):
  - train: before 2014-01-01
  - eval: 2014-01-01 up to but excluding 2019-01-01
  - holdout: 2019-01-01 up to but excluding 2023-01-01
- No random component. Every record is assigned exactly once and each split must contain a positive (`build.py:648-662`).
- Train and eval go to `public/`, holdout to `private/` (`build.py:664-668`). All three share one header (`build.py:672, 684-692`), so the holdout file carries the label and the same columns as train.
- Output rows are sorted by (date, numeric ID) (`build.py:265-269, 673`).
- Confirmed in the data: train dates run 1990-01-02 … 2013-12-31; eval dates run 2014-01-01 … 2018-12-31; headers are identical.
- No embargo between splits. The stated rationale is that each row is an independent strike with features fixed at strike time (`meta.json:56`). Because nothing in the build carries labels across rows (section 6), a missing embargo creates no label leak through features in the shipped data.

**[observed] Prevalence falls steeply across the split boundaries**

| Period | Rows | Positives | Positive rate | Source |
|---|---|---|---|---|
| Train 1990–1998 | 1,514–2,541 per year | 87–156 per year | 4.4%–7.2% | `train.csv` |
| Train 2009–2013 | 5,103–5,535 per year | 103–147 per year | 1.9%–2.7% | `train.csv` |
| Eval 2014 | 6,815 | 140 | 2.05% | `evaluation.json:19-21` |
| Eval 2015 | 6,899 | 104 | 1.51% | `evaluation.json:37-39` |
| Eval 2016 | 6,520 | 53 | 0.81% | `evaluation.json:55-57` |
| Eval 2017 | 6,036 | 28 | 0.46% | `evaluation.json:73-75` |
| Eval 2018 | 6,980 | 28 | 0.40% | `evaluation.json:91-93` |
| Holdout 2019–2022 | 25,425 | about 107 | 0.42% | `meta.json:35, 40` |

Eval positive counts are rows × rate. Every train year has at least 85 positives; from 2017 there are about 27 per year.

## 6. Label-derived cross-row history

**[observed]**

- `build.py` builds each record from that row's own cells only (`build.py:432-512`). There is no group-by, lag, rolling window, target encoding or join.
- The only cross-row operations are the duplicate-ID scan (`build.py:545-556`), value and coverage tallies for the checks (`build.py:566-643`), the split, and the sort.
- The contract agrees: "No cross-row joins, aggregate rates or label-derived features are shipped", with an empty probe list (`construction.json:7-11`).
- The baseline runner is row-isolated. `prepare()` selects columns and applies category levels learned from train (`train.py:32, 38-40`). It holds no state from eval or holdout rows.
- One label-derived quantity exists outside the shipped data: the `calendar_identity` reference, a group rate over (`state`, `month`, `ac_mass`) (`construction.json:614-619`). It is said to be fit on training labels only (`README.md:67-68`), and 144 eval rows fell in groups unseen in train (`evaluation.json:111`).

**[not checked]** Whether that reference is in fact fit on train labels only. The code that computes it is not in the pinned set. It is a reference control, not a model feature, so it cannot leak into `predict_proba`. It could only misstate the baseline comparison.

**[observed] Aggregate holdout label information is public.** `meta.json:37-41` publishes the holdout positive rate. That is consistent with the declared unsealed scope (`README.md:26`), but see section 7, R6.

## 7. Concrete risk mechanisms

Ordered by how much I think each could move or distort a holdout score. None is asserted as a defect. Each is a mechanism with the evidence I have and the check that would resolve it.

### R1. Label regime shift near 2016–2017 (prevalence drops about 5× inside the eval window)

- **[observed]** The table in section 5. Annual positives sit between 85 and 156 for 24 years, then go 140 → 104 → 53 → 28 → 28. The holdout aggregate continues at about 27 per year. Row volume is flat at roughly 6–7 thousand per year over the same stretch.
- **Candidate mechanisms [assumed, none verified]:**
  - (a) A real decline in substantial damage.
  - (b) A change in how the database manager assigns codes. M? ("damaged, extent unknown") is mapped to 0 (`build.py:403`), so growth in M? usage would move truly substantial events into the negative class.
  - (c) Interaction with the blank-DAMAGE filter (`build.py:456-458`), if recent damaging strikes are more often left blank pending details.
- **Consequences for scoring:**
  - The holdout has about 107 positives, so AUC intervals will be wide. `README.md:58` and `construction.json:309` still say "several hundred positive events", which the release's own metadata contradicts. That is stale documentation, not a data error.
  - Brier and calibration will be dominated by prior shift. The release's own numbers show it: the unmodified baseline's Brier is worse than the constant train-prior reference in 2017 (0.00652 vs 0.00547, `evaluation.json:79, 83`) and in 2018 (0.00556 vs 0.00489, `evaluation.json:97, 101`).
  - Under (b) or (c), the holdout label measures a partly different construct from the train label.
- **[not checked]** The year-by-code DAMAGE inventory (N / M / M? / S / D / blank). The build records the overall inventory (`build.py:516-521`) in an unpinned file, and I did not read raw source outcomes. A year × code table computed from train and eval years alone would separate (a) from (b) and (c).

### R2. `size` may not be a strike-time pilot observation in the consolidated record

- **[observed, documentation]** The field list defines SIZE as "Size of bird as reported by pilot… the perceived size as opposed to a scientifically determined value".
- **[observed, train]** `size` is filled on 97.5% of rows. The other pilot-observation fields are far sparser: `birds_seen` 57.3%, `warned` 67.4%, `sky` 79.4%.
  - `size` is filled on 95.2% of rows where `birds_seen` is blank.
  - `size` is filled on 93.9% of the 4,272 rows where `birds_seen`, `warned`, `sky`, `precip`, `height_agl` and `speed_kts` are all blank.
  - The fill rate is at least 98.9% in every year 1990–2009, then steps down to 89.5%–91.9% in 2010–2013.
- **Mechanism [assumed].** A field this complete on records with no other pilot observation, and with a step change in completeness, behaves like a value that is at least partly entered or back-filled during consolidation. Remains or species identification is one possible source. The release excludes SPECIES precisely because it arrives after the strike (`README.md:52`). If `size` is partly species-derived, it reintroduces part of that post-strike information under a feature whose availability is only `assumed` (`construction.json:78-82`).
- **This is not shown.** The data are also consistent with non-pilot reporters (airport operations, maintenance) entering a perceived size on the form.
- **[not checked]** Agreement between SIZE and species mass class, or REPORTED_DATE / SOURCE by size-fill pattern. Either would need source columns the build does not emit.

### R3. Feature values and completeness come from the consolidated current-vintage record

- **[observed]** Records merge multiple report types and are updated (field list: SOURCE, LUPDATE, COMMENTS "types of reports received, updates"; `construction.json:276-278`).
- **[observed, train; not adjusted for era]** Rate of the positive label when a field is missing versus present:

| Field | Missing: n, rate | Present: rate |
|---|---|---|
| `ac_class` | 104, 21.2% | 3.4% |
| `birds_struck` | 259, 15.8% | 3.4% |
| `num_engs` | 196, 11.2% | 3.4% |
| `type_eng` | 278, 10.4% | 3.4% |
| `warned` | 27,447, 4.4% | 2.9% |
| `sky` | 17,307, 4.2% | 3.2% |
| `precip` | 19,416, 4.0% | 3.2% |
| `phase_of_flt` | 812, 1.1% | 3.4% |
| `size` | 2,097, 1.8% | 3.4% |

- **Mechanism [assumed].** Which fields are filled depends on who reported and how much follow-up the event got, and that is settled after the strike. A tree model can use missingness patterns as a proxy for report type or follow-up intensity. The strongest associations sit in small groups, and the large-group effects are modest and confounded with era, so I rate this as a moderate, plausible contributor to the baseline's 0.89 eval AUC (`evaluation.json:6`), not a demonstrated leak.
- **[not checked]** Any ablation. It would need model fitting, which is out of scope.

### R4. Outcome-availability selection (blank DAMAGE dropped)

- **[observed]** Section 4, filter 5. Disclosed at `README.md:54, 62`.
- **Mechanism.** At the declared prediction time nobody knows whether DAMAGE will be coded, so the scored population is not the population an intake-triage user (`construction.json:326`) would face. Scores estimate P(substantial | DAMAGE coded), not P(substantial | reported).
- The direction of the bias is unknown without the blank-row counts (**[not checked]**, section 4). The `selection.kind: prediction_time` tag (`construction.json:128`) overstates this.

### R5. `incident_date` and `index_nr` are usable as undeclared predictors

- **[observed]** Section 2. The baseline excludes `incident_date` only by the cardinality heuristic (`train.py:30-31`). Any edited `train.py` can parse it to a year.
- A date is legitimately known at prediction time, so this is not leakage. But year is outside the 18 declared features (`README.md:24`, `build.py:17-21`) and directly tracks the trend in R1.
- `index_nr` is excluded as an ID (`train.py:19, 27`). Its values run 608,244–1,937,119 in train and the files are date-sorted (`build.py:673`). If used, it would be a proxy for record entry order.
- **Suggested contract clarification.** State whether date-derived features beyond `month` are in scope. If they are not, list `incident_date` as a carry or ID column.

### R6. Holdout prevalence is published

- **[observed]** `meta.json:40`.
- **Mechanism.** A developer can shift the model intercept to 0.42% without touching holdout rows. That improves Brier and calibration mechanically and leaves AUC unchanged. Given R1, this is the single largest lever on any proper-score comparison.
- It is consistent with the declared unsealed `retrospective_research` scope. It matters only if Brier or calibration comparisons on the holdout are read as forecasting skill.

### R7. Rows are not strictly one independent event each

- **[observed, train]** See section 8: 135 exact-duplicate groups and a modest excess of same-day, same-state positive pairs.
- The contract's "each row is an independent strike event" (`construction.json:10`, `README.md:67`) is a good approximation, not an identity.
- The effect is on uncertainty estimates, not point metrics. It is handled by the cluster declaration.

### R8. Documentation inconsistencies that do not change the data

- **[observed]** "Several hundred" holdout positives versus about 107 (see R1).
- **[observed]** "Current to August 2026" versus retrieval on 2026-11-15 (section 3).
- **[observed]** `README.md:51` quotes a 1.2% positive rate for all reports, while the frozen population is 2.3% (`README.md:62`). Both are explained in the text, but they are easy to misread side by side.

### Looked for and not found

- **[observed]** No post-strike column in the output: only alias-resolved roles are read (`build.py:44-65, 379-398`).
- **[observed]** No label-derived or cross-row feature (section 6).
- **[observed]** No ID overlap or date overlap between train and eval.
- **[observed]** `precip` `NONE` survives as a value in `train.csv` (58,790 rows), as the repair notes claim (`construction.json:2`).
- **[observed]** No mixed-label exact duplicates in train.

## 8. Clustering decision (written to `cluster.json`)

**Declared: `["incident_date", "state"]`.**

**Why this unit**

- The row is one consolidated strike record. Unique `index_nr` is enforced (`build.py:545-564`), but uniqueness does not establish independence, and the training data show it is not exact.
- **Exact duplicates [observed, train].**
  - 135 groups (292 rows, 0.35%) are identical on `incident_date` and all 18 features under different `index_nr`.
  - 22 of the groups have IDs within 5 of each other. Some duplicate groups are well-populated rows that agree on day, state, phase, height, speed and distance; 99 of the 135 have five or more blank features, where coincidence is more plausible.
  - Labels are concordant in all 135 groups: 133 all-negative, 2 all-positive, 0 mixed.
  - At these rows' own 1.4% positive rate, independence predicts about 0.03 all-positive pairs and about 3.6 mixed groups. This reads as the same physical event, or tightly linked events, recorded more than once.
- **Same-day, same-state positives [observed, train].**
  - 42 positive–positive pairs share a (date, state) group.
  - Permuting labels within strata gives null means of 33.3 (year × state), 31.6 (year × month × state) and 30.7 (year × state × `ac_mass`), with standard deviations of 5.3–5.9 and one-sided p of 0.08, 0.02 and 0.03.
  - This is modest evidence of local same-day dependence (flock or migration pulses, shared conditions, multi-report events).
  - Grouping on `incident_date` alone shows no excess: 589 observed against a null mean of 588.
- The physically meaningful unit would be airport-day or airframe. The release drops `AIRPORT_ID`, `REG`, `FLT` and `OPID` (`README.md:56`; `build.py:44-65` emits only `operator_class`). State-day is the finest released key that nests airport-day and every exact-duplicate group.
- Both columns are in every split file (`build.py:22, 672`). In the baseline, `incident_date` is a non-predictor carry and `state` is a predictor.
- The key is a function of `incident_date`, so no cluster straddles a split boundary (`build.py:645-647`).
- It costs little if dependence is in fact negligible. In train there are 62,963 clusters for 84,196 rows, with 57% of rows in singleton clusters and a maximum size of 16. In eval there are 21,107 clusters for 33,250 rows, with 42.5% of rows in singletons and a maximum size of 31 (label-free count).

**Limits of this choice**

- It does not capture repeated strikes on the same airframe, operator or airport on different days.
- It does not capture the era-level shared adjudication regime in R1. A year-level key would leave four holdout clusters and is unusable.
- The holdout cluster structure was not inspected.

## 9. Checks not performed

- No holdout rows, holdout metrics, raw workbook, source snapshot or other studies were read.
- No model was fitted. `train.py` was not executed (pandas and xgboost are not installed in this environment), so the 0.8899 eval AUC (`evaluation.json:6`) is taken as reported.
- `build.py` was not run, so the row counts it would produce from the source are taken from `meta.json`.
- Unpinned manifest files were not read: `qualification.json`, `source-checks.json`, `extract/quality.json`, `leakage_battery.py`, `dataset_run.py`, `qualify_dataset.py`, `validate.py`, `validate.sh`, `source_io.py`. This covers the build-check outputs, the reference-control fit, and how holdout scoring feeds rows to `predict_proba`.
- Year × DAMAGE-code inventory, blank-DAMAGE counts, REPORTED_DATE lag, LUPDATE distribution, and SIZE-versus-species agreement were not computed. All of them need source columns the build does not emit.
- FAA Form 5200-7, cited as "review evidence" for the band and precipitation semantics, was not consulted. Only the pinned field list was.
- Licence applicability was not reviewed.
- The missingness and dependence figures above are descriptive and unadjusted, apart from the stratified permutation nulls. They were computed on `train.csv` only, with ad hoc stdlib scripts that are not part of the release.
