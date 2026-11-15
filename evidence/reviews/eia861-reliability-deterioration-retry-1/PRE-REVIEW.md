# PRE-REVIEW — eia861-reliability-deterioration (retry-1)

Bounded pre-scoring contract review. Not an acceptance gate. No model was fitted, nothing in the release was changed.

Release reviewed: `.study/releases/eia861-reliability-deterioration/`, manifest sha256 `050ce58b…1559` (`.prepared.json:2`).

File shorthand used in citations:

| Shorthand | File |
|---|---|
| `build.py` | `reproduction/build.py` |
| `train.py` | `reproduction/train.py` |
| `construction.json` | `reproduction/construction.json` |
| `meta.json` | `extract/meta.json` |
| `README.md`, `evaluation.json`, `SOURCES.json` | release root |

## 0. What I read and what I did not

Read: `README.md`, `evaluation.json`, `SOURCES.json`, `.prepared.json`, `MANIFEST.json`, `extract/meta.json`, `reproduction/build.py`, `reproduction/train.py`, `reproduction/requirements.txt`, `reproduction/construction.json`, and the two public CSVs (`extract/public/train.csv`, `extract/public/eval.csv`) for structural and descriptive counts only.

Not read: holdout rows (`extract/private/holdout.csv` is not in the pinned directory and I did not look for it), raw EIA workbooks or the source snapshot, any other study, any factory private state. No network fetches. Holdout row count and prevalence quoted below come only from the public `meta.json:28-37`.

Evidence labels used below:

- **[CODE]** — read directly in pinned code or contract, with line citation.
- **[DATA]** — counted by me on public train/eval CSVs (descriptive only, no fitting).
- **[ASSUMED]** — asserted by the contract, or inferred by me, without evidence in the pinned files.
- **[NOT CHECKED]** — a check I did not perform.

## 1. Source, task, target

- **Source [CODE]**: 13 annual Form EIA-861 ZIPs, CY2013–CY2025, from `eia.gov` (`build.py:63-77`, loop `build.py:979`). The Reliability schedule workbook is selected per ZIP by filename rank (`build.py:880-894`) and parsed by header text pattern (`build.py:693-743`). All 14 source objects were retrieved in one session on 2026-11-13 UTC (`SOURCES.json:6-104`, `retrieved_at_unix` ≈ 1794546861–1794546877). CY2025 comes from the non-archive URL (`SOURCES.json:101`).
- **Task [CODE]**: binary classification, one row per utility × forecast year Y, Y = 2016…2024 (`build.py:1080-1081`). Declared question: will SAIDI excluding major event days "jump by at least 50 percent above its own recent norm in the next calendar year" (`construction.json:312`).
- **Target [CODE]**: `deteriorated = 1 if y1 >= 1.5 * base else 0` (`build.py:1132`), where `y1` is the CY Y+1 SAIDI-excluding-MED value (`build.py:1117`) and `base` is the median of the CY Y-1, Y-2, Y-3 values (`build.py:1124`). The threshold 1.5 is declared frozen (`construction.json:124-128`). The build re-derives every label from stored lags and asserts zero mismatches (`build.py:1247-1262`).
- **Gap year [CODE]**: CY Y is neither a feature nor part of the label. The four years read are `(Y-3, Y-2, Y-1, Y+1)` (`build.py:1084`). The "recent norm" is therefore 2–4 years before the outcome year. This matches the declared prediction time (31 Dec Y, when CY Y is not yet published; `construction.json:311`) and is not a defect, but "recent norm" should be read with that gap.
- **Outcome value not shipped [CODE]**: `y1` is held in `y1_map` only (`build.py:1134`) and is not in `COLUMNS` (`build.py:30`). `label_source_columns` names `saidi_nomed_y1` (`construction.json:160-162`), `post_hoc_columns` is empty (`construction.json:217`). See §6 for where the same number reappears as a feature of a later row.
- **Scope [CODE]**: `use: retrospective_research` (`construction.json:116`); README states no final holdout benchmark score is claimed (`README.md:26`).

## 2. Declared features versus what the runner consumes

- **Declared predictors [CODE]**: 12 columns (`build.py:16-29`, `construction.json:129-142`): `saidi_nomed_lag1/2/3`, `saidi_nomed_trend`, `saidi_with_med_lag1`, `saifi_nomed_lag1`, `saifi_with_med_lag1`, `caidi_nomed_lag1`, `customers_lag1`, `reporting_standard`, `ownership_code`, `state`.
- **Declared carries [CODE]**: `utility_id`, `forecast_year`, `decision_date` (`construction.json:4-8`); `id_columns` is only `utility_cohort_id` (`construction.json:157-159`, `meta.json:6-8`).
- **Feature construction [CODE]**:
  - All lag-1 measures, customers, state and ownership come from the CY Y-1 record `r1` (`build.py:1102-1103, 1110, 1114, 1144-1148`); lag2/lag3 from `r2`/`r3` (`build.py:1115-1116`). `FEATURE_OFFSETS` max is −1 (`build.py:33-46, 1233`).
  - `saidi_nomed_trend = (lag1 − lag3) / lag3`, NaN when lag3 is 0 (`build.py:1128-1131`).
  - `caidi_nomed` is derived as SAIDI/SAIFI when the reported value is missing and SAIFI > 0 (`build.py:779-780`).
  - State and ownership fall back to another workbook in the same year's ZIP when absent from the Reliability sheet (`build.py:826-877, 990-999`).
  - `reporting_standard` is the single value shared by all four records of the cohort, including CY Y+1 (`build.py:1094-1101, 1149`). See §4.
- **Runner inputs differ from declared features [CODE + ASSUMED]**: `train.py:27` uses every column not in `ID_COLS + [TARGET]`. `ID_COLS` comes from `task.json` (`train.py:16-19`), which is not in the pinned release. **Assuming** `task.json` mirrors `meta.json:6-8`, the baseline model consumes the 12 declared predictors **plus** `utility_id` (numeric), `forecast_year` (numeric) and `decision_date` (string; 4 distinct values in train, so kept as a categorical by `train.py:28-31`). Eval/holdout `decision_date` levels are unseen and become NaN (`train.py:40`); `forecast_year` values are outside the train range.
  - Consequence: the "full_model" baseline in `evaluation.json:5-8` is not a 12-feature model. It can use entity identity and calendar position. I did not run the runner, so I have not confirmed which columns it actually split on. **[NOT CHECKED]**
- **Missingness [DATA]**: train missing counts — `saifi_nomed_lag1` 243, `saifi_with_med_lag1` 246, `caidi_nomed_lag1` 244, `saidi_with_med_lag1` 30, `saidi_nomed_trend` 2 of 2,453. Left as missing, not zero-filled (consistent with `build.py:1200-1207`).

## 3. Timing and vintage

- **Prediction instant [CODE]**: `decision_date = "<Y>-12-31T00:00:00.000"` (`build.py:1137`). One distinct date per cohort.
- **Availability bound [ASSUMED by contract]**: CY Y-1 final file public within 365 days of period end (`construction.json:317-328`). `timing.observations` is empty (`construction.json:323`); the contract says the 365 days is a calendar bound, not a measured lag (`construction.json:325`, `README.md:68`). Every feature's `status` for reported values is `assumed` (`construction.json:16-97`).
- **One observation consistent with the bound [CODE]**: the CY2025 ZIP was retrievable on 2026-11-13 (`SOURCES.json:100-106`), i.e. before 31 Dec 2026. That is one vintage, and it does not show whether the file was the final or an early release. **[NOT CHECKED]**: I did not verify the publisher's "final" designation for 2025 (`construction.json:118`, `README.md:59,70`).
- **Vintage [CODE]**: `current_snapshot` (`construction.json:117-120`). Every year's values, including 2013–2024 archive files, are as published on 2026-11-13, not as first released. Revisions between first release and today are not measured anywhere in the pinned files.
- **Outcome timing [CODE]**: label observed "roughly 9 to 12 months" after CY Y+1 ends (`construction.json:309`). Under the contract's own bound, the label of cohort Y is public by 31 Dec Y+2.
- **Training-label maturity [CODE]**: `training_label_timing: unverified` (`construction.json:115`). Applying the contract's own bound to the fixed split:

| Scored cohort (instant) | Labels not yet public at that instant under the 365-day bound |
|---|---|
| eval 2020 (31 Dec 2020) | train cohort 2019 (needs CY2020) — 611 of 2,453 train rows **[DATA]** |
| eval 2021 (31 Dec 2021) | none in train |
| holdout 2022 (31 Dec 2022) | eval cohort 2021 (needs CY2022); eval cohort 2020 (needs CY2021) is public only exactly at the bound |
| holdout 2023, 2024 | none in train or eval |

  This is arithmetic on declared dates, not a defect under `retrospective_research`. It bounds what can be claimed: the fixed split is chronological by decision date, not an as-of training simulation. It matters for holdout 2022 only if eval labels are used to fit or select the scored model; the pinned files do not say whether they are. **[NOT CHECKED]**

## 4. Population selection

All **[CODE]** unless marked.

- Per year, a utility with more than one Reliability row is removed from that year (`build.py:799-805`, repeated after attribute fill at `build.py:1000-1003`). This drops multi-state filers.
- A cohort needs a surviving record in each of CY Y-3, Y-2, Y-1 and **Y+1** (`build.py:1084-1092`). CY Y presence is not required.
- One resolved reporting standard across all four records, IEEE or OTHER (`build.py:1094-1101`). A per-row standard is unresolved when the explicit indicator conflicts with the populated block or both blocks are populated (`build.py:755-769`).
- State present and ownership in the allowed set, from CY Y-1 (`build.py:1102-1109`); customers ≥ 1,000 in CY Y-1 (`build.py:1110-1113`).
- Finite SAIDI-excluding-MED in all three lag years and in CY Y+1 (`build.py:1118-1123`). Missing outcomes are dropped, not coded 0 (`build.py:1193-1199`).
- **Outcome-year conditioning**: membership depends on three CY Y+1 facts not knowable at 31 Dec Y — the utility files in Y+1, files exactly one row, and keeps the same resolved standard. The contract states this in `construction.json:310` (Y+1 SAIDI required), `construction.json:293` and `meta.json:52` (four filings / four-year window), and `README.md:56`. `construction.json:336` words the eligibility rule as "only CY Y-3 through Y-1 filings … one consistent reporting standard", which is narrower than the code: the code also uses the CY Y+1 standard and row uniqueness. The mechanism is that a utility that changes method, merges, or stops filing in the outcome year is absent, so the scored population is "stable filers through Y+1", not "utilities eligible at decision time". Direction and size of any effect on scores are unknown. **[NOT CHECKED]**: the `diag` drop counts (`build.py:1075-1078, 1168-1173`) live in `source-checks.json`, which is not in the pinned directory.
- **Counts [DATA / meta.json]**: train 2,453 rows, 758 utilities, cohorts 547/624/671/611 for Y = 2016–2019; eval 1,294 rows, 666 utilities, 637/657 for Y = 2020–2021; holdout 2,062 rows (`meta.json:28-32`). Train mix: 1,447 cooperative, 523 municipal, 383 investor-owned, 88 political subdivision, 12 state; 1,828 IEEE, 625 OTHER; 49 states.

## 5. Splits

- **[CODE]** Chronological by `decision_date` string comparison with half-open boundaries: train `< 2020-01-01`, eval `[2020-01-01, 2022-01-01)`, holdout `>= 2022-01-01` (`build.py:31-32, 1158-1160`), asserted non-overlapping (`build.py:1180-1185`). So train = Y 2016–2019, eval = Y 2020–2021, holdout = Y 2022–2024 (`meta.json:38-52`). No random assignment. Unique `utility_cohort_id` asserted (`build.py:1186-1192`); **[DATA]** 0 duplicates in train and eval.
- **[CODE]** Entities are not split-disjoint by design; the same `utility_id` recurs in every split it qualifies for.
- **[DATA]** 610 of 666 eval utilities also appear in train; 93 of 1,294 eval rows come from utilities absent from train. (`evaluation.json:57` reports `calendar_identity_unseen_rows: 103`; the definition of that control is not in the pinned files, so I cannot reconcile the two numbers. **[NOT CHECKED]**)
- **Purge statement is narrower than its wording [CODE]**: `meta.json:52` says "no training row's feature vector contains a year used to compute any eval or holdout label". For the outcome-year term this holds: newest train feature year is CY2018, earliest scored outcome year is CY2021. But each label is also computed from its baseline years. Eval cohort 2020's baseline is CY2017–2019 and cohort 2021's is CY2018–2020 (`build.py:1084, 1124`), and train feature vectors contain CY2017 and CY2018 (cohorts 2018 and 2019). Those baseline values are also the eval row's own features, so this is not leakage; the statement should be read as "no training feature year is an eval or holdout outcome year".
- **Prevalence [meta.json]**: train 0.174, eval 0.145, holdout 0.169 (`meta.json:33-37`). **[DATA]** train by cohort: 0.197, 0.179, 0.176, 0.146.

## 6. Label-derived cross-row history

**Construction [CODE]**. For one utility, cohort Y's outcome value is `rp1['saidi_nomed']` at CY Y+1 (`build.py:1117`). Cohort Y+2 reads the same per-year record as `r1` and ships it as `saidi_nomed_lag1` (`build.py:1114, 1140`); cohort Y+3 ships it as lag2, cohort Y+4 as lag3 (`build.py:1115-1116, 1141-1142`). Both come from the same `year_rows[yy][uid]` lookup (`build.py:1085`). No smoothing, aggregation or cross-utility rate is built: there are no group label rates in the file (`build.py:1240-1246`).

So the raw outcome quantity of row (u, Y) is a shipped feature of rows (u, Y+2), (u, Y+3), (u, Y+4), and row (u, Y) itself ships the three baseline values. Joining on `utility_id` reconstructs the label exactly.

**Confirmed on public data [DATA]**. Adjacent cohorts of the same utility have identical shifted lags in 2,917 of 2,917 pairs. Recomputing `lag1(u, Y+2) >= 1.5 * median(lags(u, Y))` reproduces the shipped label for 2,168 of 2,168 public rows where a Y+2 row exists in train or eval. All 2,168 are train rows (516/547, 511/624, 550/671, 591/611 by cohort). No eval label is reconstructable from train or eval features, because eval outcome years (CY2021, CY2022) exceed the newest public feature year (CY2020).

**Where each outcome value lands, by split [CODE arithmetic]**:

| Outcome of | CY | Reappears as a feature in | Direction |
|---|---|---|---|
| train 2016, 2017 | 2017, 2018 | train 2018–2019, eval | past label → later feature; available at the later instant |
| train 2018, 2019 | 2019, 2020 | eval 2020–2021, holdout 2022–2023 | same |
| eval 2020, 2021 | 2021, 2022 | holdout 2022–2024 | same; eval labels are public anyway |
| **holdout 2022** | **2023** | **holdout 2024 `saidi_nomed_lag1`** | **inside the scored frame** |
| holdout 2023, 2024 | 2024, 2025 | nothing shipped | — |

The forward direction (an earlier outcome becoming a later feature) is ordinary lagged history and is legitimate at the later decision instant under the contract's timing assumption.

## 7. Concrete risk mechanisms

Ordered by how directly they could move a holdout score. None is asserted to have occurred.

**R1. Within-holdout reconstruction of cohort-2022 labels (transductive, conditional on batch access).**
By §6, for any utility present in holdout cohorts 2022 and 2024, the cohort-2022 label equals `lag1(2024 row) >= 1.5 * median(lags of 2022 row)`. A scoring function that receives the holdout frame as a batch and computes anything grouped by `utility_id` across rows (forward shifts, per-utility max, "later lag") reads the answer for one of the three holdout cohorts (cohort 2022, for utilities also present in cohort 2024). The contract declares `access: isolated_rows` (`construction.json:10`) with `probes: []` (`construction.json:13`); the runner interface is `predict_proba(df)` over a whole DataFrame (`train.py:64-65`). The pinned baseline `prepare()` is row-wise (`train.py:35-41`) and does not do this. The file header says `train.py` is the file an agent edits (`train.py:1`), so the exposure depends on the scored `prepare()` and on whether the harness enforces row isolation.
- [NOT CHECKED]: the share of holdout-2022 utilities also in holdout 2024 (needs holdout rows; the public analogue is 94% for train 2016→2018), the scoring harness, and the scored model's code.
- The same engineered feature would look highly predictive in train (§6: 2,168 train labels are reconstructable) and silently be unavailable for cohorts 2023–2024, so a train/eval/holdout inconsistency is a possible symptom.

**R2. Entity identity carried into the model.**
`utility_id` is a numeric model input under the assumption in §2 (`train.py:27`). Labels of one utility are strongly dependent across cohorts: **[DATA]** in train, P(label = 1 in cohort Y+1 | label = 1 in cohort Y) = 0.399 against 0.158 unconditional (1,692 pairs, phi 0.30); gap 2: 0.224 vs 0.146; gap 3: 0.146 vs 0.131. Part of this is mechanical: adjacent cohorts share two of three baseline years (`build.py:1084, 1124`). A tree model can memorize per-utility propensity, and 610 of 666 eval utilities were seen in train. The published identity/calendar control scores AUC 0.617 on eval (`evaluation.json:13-16`) against 0.696 for the full model (`evaluation.json:5-8`), so part of the measured lift over 0.5 may be identity or calendar rather than the declared reliability features. This is a claim-scope issue (generalisation to unseen utilities is not measured), not leakage.

**R3. Immature labels reaching a scored cohort through identity.**
Combines §3 and R2. Train cohort 2019 labels encode CY2020 outcomes, which under the contract's own bound are not public at the eval-2020 instant. A model that memorizes "utility u was positive in cohort 2019" applies CY2020 information to its eval-2020 prediction for u. The analogous holdout path (eval-2021 labels → holdout 2022) exists only if eval labels enter the scored model's fit or selection. Affects the already-reported eval number (`evaluation.json`) and bounds any as-of reading; consistent with `retrospective_research`.

**R4. Small-denominator label mechanics.**
Because the baseline is fully computable from three shipped features, positive rate is a steep function of baseline level. **[DATA]** train positive rate by baseline median: 1.00 for (0, 1] minutes (3 rows), 0.644 for (1, 10] (90 rows), 0.360 for (10, 30] (197 rows), 0.136 above 30 (2,163 rows); eval shows the same gradient (0.552 / 0.268 / 0.122). A large part of achievable AUC is "find low-baseline utilities", which is regression to the mean in a ratio label rather than detection of deterioration. Acknowledged in `README.md:57,67`. Also, `base == 0` makes the label 1 for any `y1 >= 0`, including 0 (`build.py:1132`); **[DATA]** no public row has a zero median (7 rows have at least one zero lag), so this is latent in train/eval and unchecked in holdout.

**R5. Reporting-standard heterogeneity.**
**[DATA]** train positive rate 0.230 for OTHER vs 0.155 for IEEE. Non-IEEE reporters self-define major event days (`README.md:51`), so "excluding MED" is a different quantity by standard, and a change in a utility's own MED practice without a change of declared standard would register as a jump. Pooled metrics mix two label regimes; the contract does not declare a per-standard breakdown.

**R6. Parser and per-vintage mapping.**
Columns are classified by substring: metric variant (`build.py:201-206`), block (`build.py:209-216`), standard indicator (`build.py:718`), customer count (`build.py:195-198`). When several columns match one metric/variant/block, the first finite value wins (`build.py:667-690`). Unit checks exist only for 2024 (national weighted SAIDI inside a broad 50–1,200 / 100–3,000 minute band, `build.py:1032-1043`), Florida 2024 vs 2025 (`build.py:1044-1052`), and 2024 block usage (`build.py:1053-1069`). For 2013–2023 the checks are member found, rows > 0, customer column present (`build.py:1007-1031`). A mis-mapped column in one vintage would create artificial jumps concentrated in the cohort whose Y+1 is that vintage.
- **[DATA]** No sign of this in feature years: per-year saidi_nomed p10 / median / p90 across public rows is stable for CY2013–CY2020 (medians 93.0–101.6 minutes, p90 249–278).
- **[NOT CHECKED]**: CY2021–CY2025 (these appear only in holdout features or as outcomes), the actual workbook headers, whether any vintage has more than one "with MED" SAIDI column per block (which would make `saidi_with_med_lag1` fall back to a different measure when the first is blank), and `source-checks.json`.

**R7. Label revision and holdout integrity.**
Holdout cohort 2024 labels rest on the newest file, CY2025, retrieved 2026-11-13 (`SOURCES.json:100-106`; its publication date is unverified); a re-release moves them (`README.md:70`). The labeled holdout is downloadable and "not cryptographically sealed" (`README.md:26`), and is in any case re-derivable from public EIA files with the pinned `build.py`. Protection of the holdout is procedural only.

**R8. Outcome-year selection** — see §4. Stated here for completeness as a population-definition mechanism rather than a leak.

**R9. Few time clusters.**
The holdout has three decision dates (`build.py:1137`, `meta.json:52`). Any year-level common shock (weather outside declared major event days, reporting-form changes) is a three-cluster effect that no row- or utility-level interval can represent. `README.md:72` already states that no uncertainty interval is reported.

## 8. Dependence unit (see `cluster.json`)

Declared before any holdout scoring and without holdout metrics: **`utility_id`**.

- Source meaning: the row is a utility × forecast-year window; one utility contributes up to three holdout rows whose labels share baseline years by construction (`build.py:1084, 1124`).
- Training metadata **[DATA]**: one-way ANOVA ICC of the training label is 0.219 within `utility_id` (758 groups, mean size 3.2), 0.026 within `state`, 0.023 within `state × forecast_year`, 0.001 within `forecast_year`. Within single cohorts (no utility recurrence) the state ICC is −0.001, 0.049, 0.056, −0.027.
- `utility_cohort_id` is unique per row (`build.py:1133, 1186-1192`) and is not an independence unit.
- The contract also names `utility_id` as `event_key_column` (`construction.json:122`); I reached the same key from the code and training data rather than adopting it.
- Residual dependence not captured is listed in `cluster.json` limitations (state/weather common shocks, three decision dates, corporate parents not in the data).

## 9. Assumptions I am carrying

1. `task.json` used by the runner has the same `id_columns` as `meta.json` (§2).
2. The pinned `build.py` is the code that produced the shipped CSVs. The manifest binds hashes (`MANIFEST.json`), but I did not recompute them or rerun the build.
3. The holdout CSV has the same columns as train/eval (`build.py:963-966, 1163-1165`), so `utility_id` is present there as a carry.
4. The contract's 365-day availability bound, when I use it for the maturity table in §3.

## 10. Checks not performed

- No holdout rows read; nothing in §6/R1 was verified on holdout data.
- No raw EIA workbook, source snapshot, or publisher page read; no publication dates verified; "final" status of the 2025 file not verified.
- No build rerun, no hash recomputation, no runner execution, no model fit, no feature-importance inspection.
- Files named in `MANIFEST.json` but absent from the pinned directory were not reviewed: `source-checks.json`, `qualification.json`, `extract/quality.json`, `reproduction/leakage_battery.py`, `reproduction/validate.py`, `reproduction/dataset_run.py`, `reproduction/source_io.py`, `reproduction/source.json`.
- The definition of the `calendar_identity` control and the holdout scoring harness (row isolation, whether eval is used for refit or selection) are not in the pinned files.
- Drop-reason counts for the eligibility filters (§4) not seen.
