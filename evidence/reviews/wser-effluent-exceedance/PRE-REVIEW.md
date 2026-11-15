# PRE-REVIEW: wser-effluent-exceedance

Bounded pre-scoring contract review. Not an acceptance gate. No model was fitted, nothing in the release was changed, and no holdout rows, raw source files, other study results or factory private state were read.

Release reviewed: `version v-3ceae5479cda761c` (`MANIFEST.json:4`), manifest sha256 `79b53e65…7258f`, which matches `.prepared.json:2`.

## Summary

- The release is a system-year panel: one row per wastewater system per target year 2015–2024, split by year into train (2015–2019), validation (2020–2022) and holdout (2023–2024).
- The declared use is `retrospective_research` with `training_label_timing: unverified` (`construction.json:135-136`). I read the release against that claim, not against a deployable-forecast claim.
- I found no feature that reads the target year's own monitoring rows. The year filter in `build.py:625` and `build.py:631` is strict.
- The main thing to control at scoring is cross-row history. `prior_year_exceedance` is the label rule applied to the same system one year earlier, so each 2024 holdout row carries the 2023 holdout label of its system (R1).
- Clustering is declared on `system_id` (see `cluster.json`).

## Scope and evidence labels

Files read, all under the pinned release directory:

| File | Hash check against `MANIFEST.json` |
|---|---|
| `README.md`, `LICENSE.md`, `LICENSE-EVIDENCE.json`, `SOURCES.json`, `evaluation.json` | match |
| `extract/meta.json`, `extract/public/train.csv`, `extract/public/eval.csv` | match |
| `reproduction/build.py`, `construction.json`, `train.py`, `requirements.txt` | match |

`extract/public/eval.csv` is the public validation split (`README.md:12-13`, `README.md:26`), not the holdout. I used it for structure only (keys, overlap, lag identity, composition). I computed no predictive metric on it.

Labels used below:

- **[code]** read directly from a cited line.
- **[data]** counted by me on the public train or validation CSV.
- **[declared]** stated by the contract; I did not test it.
- **[assumption]** needed for the claim to hold; not established by anything I read.
- **[not checked]** a check I did not perform, with the reason.

## 1. Source, task and target

**Source.** Three ECCC WSER CSVs, fetched as a current-vintage download:

- monitoring, identification and acute lethality (`build.py:9-11`, `build.py:401-403`; `SOURCES.json:16-36`) **[code]**
- retrieved at unix 1794704453, which is 2026-11-15 UTC (`SOURCES.json:20`) **[code]**
- `MANIFEST.json:182-185` lists only the monitoring and identification URLs under `source.urls`; the acute lethality URL is fetched by the build and present in `SOURCES.json` but absent from that list **[code]**

**Task.** Binary classification, target `next_year_exceedance`, positive label 1 (`meta.json:4-5`; `build.py:13`). The question is whether a system reports at least one year-Y period with average CBOD or suspended solids strictly above its applicable limit (`construction.json:323`).

**Target construction [code].**

- Per monitoring row, an exceedance is `limit > 0`, average present, and `average > limit`, for CBOD (`build.py:465-467`) and suspended solids (`build.py:470-472`).
- The row flag is the OR of the two (`build.py:477`).
- The system-year label is the max of that flag over the year's rows (`build.py:343`, `build.py:609`).
- The label uses the average and limit columns, not the source compliance column (`construction.json:326`). The compliance columns are listed as post hoc and are never read by the build (`construction.json:201-205`; `build.py:427`).
- All limit-based flags are forced false or missing for years before 2015 (`build.py:486-488`).

**Target meaning [declared].** The label is an any-period indicator, not ECCC's 75-percent compliance determination (`README.md:56`). Exposure differs by sampling regime and is not removed from the label (`README.md:57`).

## 2. Declared features

Fifteen features (`build.py:16`; `construction.json:144-160`), plus carries `target_year` and `system_id` (`build.py:17`) and the time column `decision_date` (`build.py:15`).

| Feature | Source and window | Code | Contract status |
|---|---|---|---|
| `prior_year_exceedance` | label rule on year Y-1, same system | `build.py:631`, `643-644` | verified (`construction.json:62-66`) |
| `prior_year_worst_margin` | max of average minus limit in Y-1, floored at 0 | `build.py:645-649` | verified |
| `ever_exceeded_before` | max of the label rule over all evaluable years before Y | `build.py:664-668` | verified |
| `history_years_reported` | distinct years before Y with any monitoring row | `build.py:625-626` | verified |
| `periods_reported_prior_year` | distinct period keys in Y-1 | `build.py:451`, `650` | verified |
| `reporting_frequency` | last Y-1 row, else inferred from period tokens | `build.py:651-659` | verified |
| `system_type`, `avg_daily_effluent_volume_m3`, `owner_type_operator_type`, `province` | Y-1 monitoring rows; province falls back to identification | `build.py:660-663`, `670-671` | verified |
| `treatment_family`, `hydraulic_retention_ge_5_days`, `chlorine_use`, `receiving_water_type` | identification snapshot, joined on `system_id` with no year | `build.py:669-675` | assumed (`construction.json:22-26`, `42-46`, `77-81`, `107-111`) |
| `prior_year_acute_lethality_failures` | failed trout tests in Y-1 | `build.py:676-679` | assumed (`construction.json:57-61`) |

Observations:

- **[data]** The four identification attributes and `province` are constant within every system across train years (0 systems with more than one value). `system_type`, `reporting_frequency` and `owner_type_operator_type` vary within 306, 194 and 360 systems.
- **[code]** The baseline runner excludes only `id_columns` and the target from its inputs (`train.py:27`), and `id_columns` is `record_id` alone (`meta.json:6-8`). So `system_id`, `target_year` and `decision_date` are model inputs in the measured baseline.
- **[data]** `system_id` is all digits, so it enters as a numeric feature. `decision_date` has 5 string levels in train, and all 3 validation levels are unseen, which the runner maps to missing (`train.py:40`).
- **[assumption]** `train.py:16` reads a `task.json` that is not in the pinned directory. I assumed its `id_columns` equal those in `meta.json`.

## 3. Timing and vintage assumptions

**Declared timing.**

- The decision instant is 1 March of Y, built as a string `Y-03-01` (`build.py:680`) **[code]**.
- It rests on the 45-day statutory reporting deadline, used as a publication proxy; actual publication dates are not verified (`construction.json:27-31`, `337-342`) **[declared]**.
- The latest feature period is Y-1 (`construction.json:349`) **[declared]**, and the code agrees (`build.py:625`, `631`, `677`) **[code]**.

**Vintage.** `current_snapshot` (`construction.json:137-140`). Everything, features and labels, is as filed at the 2026-11 download.

- **[assumption]** Year Y-1 monitoring rows in the snapshot equal what was on file at 1 March Y. The build resolves no filing or amendment date (`build.py:427`), so late-filed and corrected Y-1 reports are indistinguishable from on-time ones.
- **[assumption]** Identification attributes are quasi-static. They carry no year stamp (`construction.json:138`), and the release says they can reflect post-decision upgrades (`README.md:55`).
- **[assumption]** Acute lethality results for Y-1 are on file by 1 March Y. The contract marks this feature assumed.
- **[declared]** Target year 2025 is excluded as immature (`build.py:20`; `README.md:62`). At download, 2024 reports had about 21 months to mature.

**Outcome window versus decision instant [code/declared].** The label window is the full calendar year Y, 1 January to 31 December (`construction.json:320`), and the decision instant is 1 March of Y (`construction.json:322`). The decision instant therefore sits about two months inside the outcome window. No feature reads year-Y rows, so this is a framing fact about "next year", not a leak.

## 4. Population selection

**[code]** A system-year enters when all of the following hold:

1. The year is 2015–2024 (`build.py:595`).
2. The system-year has a positive-limit row and a row with a positive limit and a reported average (`build.py:608`).
3. It is not an unresolved negative: no exceedance seen and at least one positive-limit row with a missing average (`build.py:610-611`).
4. The system has at least one earlier year with any monitoring row (`build.py:626-628`).

Further facts:

- **[code]** Current-vintage operational status is computed for diagnostics only and excludes nothing (`build.py:597-600`).
- **[declared]** The cohort is defined from year-Y reports, so it is outcome-conditioned and is not a deployable 1 March roster (`construction.json:128`; `README.md:78`).
- **[code]** Rule 3 is one-sided. A year with a missing average is dropped when no exceedance is seen and kept as a positive when one is.
- **[not checked]** How many system-years rule 3 or rule 4 removed. Those counts are not in the pinned files, and I did not read the source.

## 5. Splits

- **[code]** Fixed by target year: train 2015–2019, validation 2020–2022, holdout 2023–2024 (`build.py:697-699`). This agrees with the `decision_date` windows in `meta.json:41-54`.
- **[declared]** No embargo year, because label years do not overlap and features end at Y-1 (`meta.json:55`).
- **[data]** One row per (`system_id`, `target_year`) in train and validation; `record_id` is exactly `wser-{system_id}-{target_year}`.

| Split | Rows | Systems | Rows per system |
|---|---|---|---|
| train | 8,244 | 2,080 | 1,334 systems have all 5 years; 346 have 1 |
| validation | 5,894 | 2,090 | 1,831 systems have all 3 years |

- **[data]** 1,989 of 2,090 validation systems are also in train, covering 5,712 of 5,894 validation rows. The remaining 182 rows match `calendar_identity_unseen_rows` in `evaluation.json:91`.
- **[code]** The holdout is the same panel two years on (`build.py:699`), so the same systems recur there. I did not read it.

**Composition changes at 2019 [data].** `meta.json:55` says reporting-completeness strata and province are kept balanced across periods "by construction of the year windows". No code implements a balance, and the public rows show a regime change inside train:

| Year | Rows | Quebec share | `system_type` missing | Retention flag missing |
|---|---|---|---|---|
| 2015 | 1,475 | 0.207 | 2 | 3 |
| 2016 | 1,529 | 0.196 | 10 | 0 |
| 2017 | 1,567 | 0.174 | 9 | 0 |
| 2018 | 1,693 | 0.217 | 99 | 3 |
| 2019 | 1,980 | 0.326 | 630 | 254 |
| 2020 | 1,966 | 0.335 | 643 | 263 |
| 2021 | 1,966 | 0.336 | 672 | 262 |
| 2022 | 1,962 | 0.330 | 656 | 257 |

- Of the 319 first-history rows in 2019, 287 are Quebec.
- Train contains one year of the post-2019 regime; validation is entirely in it.
- **[assumption]** The holdout years continue the post-2019 regime. Not checked.

## 6. Label-derived cross-row history

Three features are built by applying the label rule to the same system's earlier years:

- `prior_year_exceedance` is `any_exc` for Y-1 (`build.py:644`), the same quantity that becomes the Y-1 label (`build.py:609`).
- `prior_year_worst_margin` is positive exactly when that flag is 1 (`build.py:645-647`). **[data]** This holds on every train row with the flag present.
- `ever_exceeded_before` is the running max of the same flag (`build.py:666`).

**[data]** Whenever the Y-1 row of the same system exists in the public files, the feature equals that row's label:

| Pair | Agree | Disagree |
|---|---|---|
| train row to earlier train row | 6,104 | 0 |
| validation 2020 to train 2019 | 1,919 | 0 |
| validation 2021 to validation 2020 | 1,884 | 0 |
| validation 2022 to validation 2021 | 1,893 | 0 |
| total | 11,800 | 0 |

Consequences, by the same code path and not inspected in the holdout:

- Holdout 2023 rows carry validation 2022 labels, which are public.
- Holdout 2024 rows carry holdout 2023 labels, so about half of the holdout labels appear verbatim in another holdout row's features.
- This is legitimate under the declared timing: the 2023 outcome is on file by 1 March 2024. It is a leak only if the prediction for a 2023 row can see the 2024 row of the same system.

Contract wording:

- `construction.json:14` says "no label-derived group rates are shipped". That is accurate: there are no group or cross-entity rates, and each row's history is filtered by its own system (`build.py:612`, `622-625`) **[code]**. It should not be read as "no label-derived features".
- The contract declares `access: isolated_rows` with an empty `probes` list (`construction.json:10`, `13`).
- **[not checked]** How the scorer enforces row isolation. `validate.py` and `leakage_battery.py` are named in `MANIFEST.json` but absent from the pinned directory.

**Feature and label disagree on unresolved years [code].** The feature is 0 for a Y-1 with an evaluable row and no exceedance (`build.py:643-644`), even when another positive-limit row has a missing average. The label rule excludes exactly that system-year (`build.py:610-611`). The feature matches its declared meaning (`construction.json:232`), so this is an asymmetry, not a defect.

**Feature present without a cohort row [data].** 537 train rows and 73 validation rows have the lag feature but no Y-1 row in the public files. The code allows this through rule 3 and rule 4 above. I did not split the count between the two.

**Structural missingness [data].** All 1,475 target-2015 rows have the three lag features missing, as the build asserts (`build.py:777`). Lag-missing rows number 1,603 in train and 125 in validation (`evaluation.json:94-95`).

## 7. Concrete risk mechanisms

Each item states a mechanism and what I do or do not know about its size. None is asserted as a defect.

**R1. Within-holdout label exposure through lag features.** See section 6. A batch-level transform such as a group-by on `system_id` over the holdout frame would recover 2023 labels from 2024 rows. `train.py:35-41` is row-wise as shipped, but `train.py:36-37` invites feature engineering inside `prepare(df)`, which receives the whole frame. Size: every 2023 holdout row whose system also has a 2024 row.

**R2. Current-vintage identification attributes.** Treatment family, retention, chlorine use and receiving water describe the plant as of 2026 and are joined to every year back to 2015 (`build.py:669-675`). A plant upgraded after chronic exceedance would show its upgraded design on its earlier rows. Direction and size unknown. `README.md:55` says the build "should also report a version that drops them entirely"; the pinned `build.py` writes one version with them included (`build.py:781-783`), and I found no dropped-attribute result in the pinned files.

**R3. Late and amended filings.** The snapshot holds Y-1 reports whenever they were filed. `README.md:60` cites 26% of systems missing a required report in 2018. A report filed after 1 March Y would still feed `prior_year_exceedance` and `periods_reported_prior_year`. Size unknown; no filing date is used.

**R4. Outcome-conditioned cohort with a one-sided exclusion.** See section 4. Scores describe systems that filed evaluable year-Y reports, not the 1 March roster. Declared (`construction.json:128`).

**R5. Decision instant inside the outcome window.** See section 3. Declared values, not a leak.

**R6. Exposure in the label.** A system with 12 periods has more chances to exceed than one with 1 (`README.md:57`). **[data]** Train period counts are 1 (3,921 rows), 4 (3,486) and 12 (619). Part of any score reflects sampling regime.

**R7. Regime shift between train and later splits.**
- Composition: see the 2019 table in section 5.
- History depth: `history_years_reported` spans 1–6 in train and 1–9 in validation **[data]**, and can reach 11 in the holdout by construction (`build.py:626`).
- Calendar inputs: `target_year` and `decision_date` take only unseen values after train.
- Categories: `reporting_frequency` has a `monthly` level in validation (2 rows) that never occurs in train.
- Base rate: train positive rate rises from 0.157 (2015) to 0.229 (2018) and 0.205 (2019) **[data]**.

**R8. Identity and calendar carry most of the measured signal.** On public validation the release reports AUC 0.899 for the full model, 0.853 for the calendar-identity control and 0.833 for persistence (`evaluation.json:5-20`). **[data]** In train, 713 of 2,080 systems hold all 1,616 positives, and 1,279 of 1,734 multi-year systems have a constant label. Any holdout result should be read against those two controls, since `system_id` is a baseline input (section 2).

**R9. Header binding by fuzzy match.** Source columns are chosen by a substring score (`build.py:126-153`), with broad synonyms such as bare `dbo5` (`build.py:415`), bare `result` (`build.py:23`, `565`) and bare `date` (`build.py:564`). The chosen headers are recorded in a check (`build.py:720-722`) whose output, `source-checks.json`, is absent from the pinned directory. **[not checked]** Which source columns were actually bound.

**R10. The prior-years check cannot fail.** `feature_source_violations` counts cases where `prior` contains a year at or after Y (`build.py:629-630`), but `prior` is already filtered to earlier years one statement before (`build.py:625`). The check at `build.py:751` therefore adds no independent evidence; the guarantee is the filter itself.

**R11. Identification de-duplication.** Duplicated system identifiers are resolved by `sort_values('system_id')` then `keep='last'` (`build.py:559-560`). The sort is not declared stable, so which duplicate survives is not pinned by the code. This matters only if the duplicate count is non-zero. **[not checked]** The count is in the absent `source-checks.json`.

**R12. Acute lethality vocabulary.** Failure is a substring test on the result text (`build.py:583-587`), after an optional trout filter (`build.py:578-581`). The contract says these vocabularies are only partly verified (`construction.json:2`). **[data]** The feature is missing on 6,333 of 8,244 train rows.

**R13. Year parsing.** The target year is the first four-digit year found in the year column, else in the period string (`build.py:181-188`, `437-443`). **[not checked]** Whether any source period string spans two years.

## 8. Checks not performed

- No holdout row, holdout metric or `extract/private/` content was read. Statements about the holdout come from `build.py` and `meta.json` only.
- No raw source CSV was read, so header resolution, removed-row counts, duplicate identifiers and late-filing prevalence are unverified.
- The WSER regulation text was not consulted. The 45-day deadline is taken as declared.
- The build was not re-run and the split CSVs were not reproduced. Hashes of the twelve pinned files match the manifest; 21 manifest assets are absent from the pinned directory, including `source-checks.json`, `qualification.json`, `extract/quality.json`, `validate.py` and `leakage_battery.py`.
- No model was fitted and no metric in `evaluation.json` was recomputed.
- The stability of `system_id` across re-registration or ownership change was not checked.
- The licence was not reviewed beyond noting the files.
