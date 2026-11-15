# PRE-REVIEW — caa-fce-hpv-escalation

Bounded pre-scoring contract review, written 2026-11-15 before any holdout scoring. It is not an acceptance gate.

**Summary.** I found no path by which a row's own label value, or any holdout label, reaches a declared feature. The main things to carry into scoring are:

- Rows are not independent. Label rates differ by an order of magnitude between states, and facilities recur within and across splits.
- Row selection and labels both depend on HPV dates as recorded in a single 2026 snapshot.
- The "active HPV" exclusion in code uses the earliest resolution date of an episode, which is narrower than the contract wording (R1).
- A facility-disjoint robustness variant is described in the contract but is not implemented or reported in any pinned file (R5).

**Scope.** Paths are relative to `.study/releases/caa-fce-hpv-escalation/`.

- Read: `README.md`, `MANIFEST.json`, `SOURCES.json`, `evaluation.json`, `extract/meta.json`, `LICENSE*.{md,json}`, `.prepared.json`, `reproduction/{build.py,train.py,construction.json,requirements.txt}`.
- Read for structure: `extract/public/train.csv` in full, and three columns of `extract/public/eval.csv` (`evaluation_id`, `state`, `evaluation_end_date`). No eval labels were used.
- Not read: `extract/private/holdout.csv` (absent from the pinned directory), the raw ECHO archive, other studies, factory private state.
- No model was fitted and nothing in the release was changed.

Each statement below is one of three kinds:

- **[code]**: read directly from pinned code or contract text.
- **[data]**: measured by me on public train (or eval identifiers only).
- **[assumed]**: stated by the contract or inferred by me, not verified.

## 1. Source, task, target

- **Source [code].** One ZIP, `https://echo.epa.gov/files/echodownloads/ICIS-AIR_downloads.zip` (`build.py:10-11`). Eight members are used (`build.py:50-59`). The archive hash and a retrieval time of 1794692779 (2026-11-14 21:46 UTC) are in `SOURCES.json:16-22`.
- **Task [code].** "After a Clean Air Act source completes a full compliance evaluation with no active High Priority Violator episode, will that source enter HPV status within the next 12 months?" (`README.md:20`, `MANIFEST.json:301`). The declared use is `retrospective_research` (`construction.json:353`, `README.md:26`).
- **Unit of observation [code].** One full compliance evaluation (FCE) activity: `COMP_MONITOR_TYPE_CODE` in {FOO, FFO} (`build.py:590`), identified as `PGM_SYS_ID:ACTIVITY_ID` (`build.py:611`).
- **Target [code].** `hpv_escalation_12m` (`build.py:13`, `meta.json:4-5`) is 1 if any HPV day-zero for the facility falls in (t, t+365 days], else 0 (`build.py:605`, `620-622`, `630`, `744`).
  - Day-zero equal to t is neither a positive nor a negative; the row is excluded (`build.py:619`, `642`).
  - The 365 is a day count, asserted at `build.py:865-877`.
- **HPV episodes [code].** Violation-history rows are kept when `HPV_DAYZERO_DATE` parses (`build.py:399`) and collapsed to one episode per (facility, day-zero) (`build.py:401-407`).
  - There is no filter on `ENF_RESPONSE_POLICY_CODE`.
  - **[assumed]** Rows for federally reportable violations that are not HPVs carry a blank `HPV_DAYZERO_DATE`. The live documentation page says the file holds both HPV and FRV case files, but I did not inspect raw rows.
- **Baseline [code].** The baseline is `train.py` unchanged: XGBoost with 30 trees and depth 6 (`train.py:49-57`). Public-validation AUCs (`evaluation.json:4-21`):

  | Model | AUC |
  |---|---|
  | Full model | 0.856 |
  | Persistence (`prior_hpv_count`) | 0.722 |
  | Calendar/identity reference | 0.685 |

  No holdout score exists (`evaluation.json:2`).

## 2. Declared features

There are 18 declared features (`build.py:14-33`, `meta.json:13-30`). `construction.json:244-333` marks every one of them `assumed`; none is `verified`.

| Group | Features | Construction | As-of status |
|---|---|---|---|
| Static facility snapshot | `state`, `epa_region`, `sic_2digit`, `naics_2digit`, `facility_type_code`, `air_pollutant_class_code` | One facilities row per `PGM_SYS_ID`, keep first (`build.py:294-301`), joined at `build.py:746` | 2026 snapshot, not as of t |
| Snapshot membership counts | `program_count`, `pollutant_count` | Distinct codes per facility (`build.py:324-330`, `337-338`), joined at `build.py:747-750` | 2026 snapshot, not as of t |
| Triggering evaluation | `comp_monitor_type_code`, `state_epa_flag` | From the FCE row itself (`build.py:372-373`) | Event attribute, current vintage |
| Evaluation history | `prior_evaluations_3y`, `days_since_last_evaluation` | All FCE and PCE rows of the facility, dated in [t-1095, t) or before t (`build.py:679-696`) | Strictly before t |
| Stack tests | `prior_stack_test_failures_3y` | Status `FAI`, dated in [t-1095, t) (`build.py:698-706`) | Strictly before t |
| HPV history | `prior_hpv_count`, `days_since_hpv_resolution` | Day-zero before t, with no lookback limit (`build.py:623`); latest resolution before t (`build.py:624-626`, `740-742`) | Strictly before t; same source fields as the label |
| Formal actions | `prior_formal_actions_3y`, `prior_penalties_3y` | Settlement date in [t-1095, t) (`build.py:708-718`); penalty is zero only when there are no actions (`build.py:736-738`) | Strictly before t |
| Title V | `prior_tv_deviations_3y` | Flag starts with `Y` (`build.py:519-520`), dated in [t-1095, t) (`build.py:720-728`) | Strictly before t |

**Columns shipped but not declared as features [code].**

- `evaluation_id` is declared an ID (`meta.json:6-8`) and the baseline drops it (`train.py:19`, `27`).
- `evaluation_end_date` is written out (`build.py:44`) but is neither a declared feature nor an ID. `train.py:27` treats it as a candidate. The baseline drops it only through the rule that string columns with more than 1,000 distinct values are excluded (`train.py:30`).
  - **[data]** Train has 1,162 distinct dates, so it is dropped, but by that margin and not by declaration.
- `carry_columns` is empty (`construction.json:52`).

**Stack-test and Title V date columns [code].** The builder probes a candidate list and takes the first header present (`build.py:420-434`, `478-494`). Which one was chosen is recorded only in `source-checks.json`, which is not in the pinned directory. The live documentation page lists `ACTUAL_END_DATE` as the only date column in both tables, which is the last fallback in both lists. I did not check this against the archive headers.

## 3. Timing and vintage assumptions

- **Prediction time [code].** t is `ACTUAL_END_DATE` normalised to a date (`build.py:371`, `construction.json:192`). The live documentation defines the field as "the calendar date of the listed inspection".
- **Feature windows [code].** Every history feature uses a strict `< t` comparison (`build.py:652`, `684`, `686`, `704`, `713`, `726`, `623`, `625`). I found no `<=` on the feature side.
- **Vintage [code].** One current snapshot (`construction.json:354-357`). `training_label_timing` is `unverified` (`construction.json:352`), and the contract says no row-level availability ledger exists (`README.md:66`).
  - **[assumed]** Every date reflects what the record says now, not what was entered by t. Back-entry and later corrections are disclosed (`README.md:55`, `construction.json:205-209`).
- **Extract boundary [code].** `EXTRACT_DATE` is hard-coded as 2026-11-07 (`build.py:12`), described as the publisher index's last-modified date (`construction.json:211`, `356`).
  - The archive was retrieved on 2026-11-14 (`SOURCES.json:20`). Nothing in `build.py` ties the constant to the archive actually read.
  - The consequence is small: the latest horizon end is 2026-06-30 (`meta.json:56`), so the maturity filter (`build.py:607`) holds for either date.
- **Label maturity [assumed].** The filter requires t+365 to be on or before the extract date (`build.py:607`, checked at `776-783`). It does not allow for delay between an HPV day-zero and its entry into ICIS-Air.
- **History depth [data].** In train, `days_since_last_evaluation` reaches 14,375 days. The share of rows with no prior evaluation is steady at 9–10% across 2015–2018, and mean `prior_evaluations_3y` is steady at 3.1–3.3. I see no sign that lookbacks are cut off at the 2014 system migration mentioned in `README.md:56`.

## 4. Population selection

The filters run in this order **[code]**:

1. Full evaluations only: FOO or FFO (`build.py:590`), after de-duplicating on (facility, activity) and keeping the earliest date (`build.py:376-383`).
2. The facility has at least one row in the current programs table (`build.py:323`, `600-602`).
3. t falls in a split window (`build.py:603-604`).
4. t+365 is on or before 2026-11-07 (`build.py:605-607`).
5. No HPV episode active at t, and no day-zero equal to t (`build.py:616-619`, `642`).
6. No other full evaluation at the facility in [t-365, t), tested against all full evaluations in any year (`build.py:644-656`).
7. One row per facility per day, keeping the lowest `ACTIVITY_ID` by string order (`build.py:657-661`).

Stage counts are written to a check (`build.py:662-677`), but that output is not in the pinned directory, so I do not know how many rows each stage removed.

**[data]** In train:

- No two rows for the same facility are closer than 366 days (17,089 gaps, none at or below 365).
- 97% of rows are FOO; 3% are FFO.
- Lead agency is state for 87%, local for 11%, EPA for 1.3%.

**[code]** `construction.json:348-351` says selection is `prediction_time` and that labels are never used to select rows. That is accurate for the label value. Steps 4 and 5 do, however, read the label's source fields (`construction.json:59-62`) as they stand in the 2026 snapshot.

## 5. Splits

Windows are half-open on t (`build.py:45-49`, `198-202`), with no shuffling.

| Split | Window (t) | Rows | Positive rate |
|---|---|---|---|
| train | 2015-01-01 to 2018-12-31 | 58,183 | 1.064% |
| embargo | 2019 | none | n/a |
| eval | 2020-01-01 to 2022-12-31 | 36,500 | 1.142% |
| embargo | 2023 | none | n/a |
| holdout | 2024-01-01 to 2025-06-30 | 20,011 | 0.745% |

Rows and rates are from `meta.json:32-41`. The holdout figures are the published aggregate, not something I computed. They imply roughly 149 holdout positives.

- **[code]** Each embargo year equals the label horizon. Train label windows close by 2019-12-31 and eval label windows by 2023-12-31, so no label window reaches into a later split's prediction dates.
- **[data]** Train has 619 positives and its date range is 2015-01-02 to 2018-12-31.
- **[data]** The split is not facility-disjoint:
  - Train has 41,094 distinct facilities, and 55% of train rows belong to a facility with more than one train row.
  - 81% of eval rows (29,637 of 36,500) belong to a facility that also appears in train.
  - 36% of eval rows share a facility with another eval row.

## 6. Label-derived cross-row history

**Observed [code].**

- `prior_hpv_count` and `days_since_hpv_resolution` are computed from the same two source fields as the label (`construction.json:59-62`; `build.py:620-626`).
- The three roles are separated by strict date comparisons within one merge:
  - label: day-zero after t and no later than t+365 (`build.py:620-622`);
  - history: day-zero before t (`build.py:623`);
  - excluded: day-zero equal to t (`build.py:619`).
- Because same-facility rows are at least 366 days apart (step 6), their label windows cannot overlap. One day-zero can be a positive for at most one row per facility.
- An earlier row's positive event always precedes the facility's next retained row. At that next row it is either still active, which removes the row (`build.py:616-618`, `642`), or resolved, which adds one to `prior_hpv_count`. So every positive label becomes dated history for the same facility's later rows, within a split and across splits. This is ordinary temporal history and is disclosed (`README.md:73`). It is also the reason the facility is a dependence unit.
- I found no target encoding or group rate. The target is aggregated only for check counts (`build.py:752-774`). `cross_row_audit.probes` is empty (`construction.json:228-232`), so the contract's statement on this rests on its rationale text, not on a recorded probe.
- `prior_hpv_count` is cumulative with no window (`build.py:623`), and it is the persistence reference (`construction.json:361-362`).

**Measured [data].**

- 22.7% of train rows have `prior_hpv_count` above zero. The maximum is 127, and 62 rows across 42 facilities have 20 or more.
- Train positive rate rises with the count:

  | `prior_hpv_count` | Train positive rate |
  |---|---|
  | 0 | 0.50% |
  | 1 | 1.71% |
  | 2 | 2.56% |
  | 3 or more | 6.18% |

- Two train rows have a count above zero with a blank `days_since_hpv_resolution`. That is consistent with a resolution dated exactly t, which `build.py:617` treats as not active and `build.py:625` does not count as prior.

## 7. Concrete risk mechanisms

None of these is shown to be a defect. Each is a mechanism I can point to in code or contract, with what I did and did not check.

**R1. "Active" uses the earliest resolution date of an episode [code].**
- Rows sharing a facility and day-zero are collapsed with `res_min` (`build.py:402`), which is used when every row in the group has a resolution date (`build.py:406`).
- If such a group has different resolution dates, the episode is treated as closed at the earliest one. An evaluation between the earliest and latest resolution passes the filter (`build.py:616-618`).
- The contract text reads "`HPV_RESOLVED_DATE` is null or > t" (`MANIFEST.json:299`). `construction.json:2` describes the collapse as conservative but does not mention the minimum.
- Effect if such groups exist: the population is slightly wider than the wording, and `days_since_hpv_resolution` is measured from the earliest date. Labels are unaffected.
- Not checked: how often this occurs. That needs the raw violation table.

**R2. Selection and labels depend on back-dated HPV records [code + assumed].**
- The exclusions for active and same-day episodes (`build.py:616-619`) and the label (`build.py:620-622`) use day-zero as recorded in 2026.
- My understanding of EPA's HPV policy is that day-zero is tied to the discovering activity, so it can be dated at or before the end of the evaluation that found the violation and entered later. I did not verify this against a pinned document.
- If so, some evaluations whose own findings produced an HPV are removed from the population, and positives with day-zero shortly after t reflect the triggering evaluation's findings, not later conduct.
- The contract says the decision is made "after the evaluation report is entered" (`README.md:24`), which is later than t by an unknown entry delay. The label window opens at t.
- This is within the declared retrospective scope (`README.md:55`). It limits how the result should be read, not whether it stands.

**R3. Holdout labels are less mature than train labels [assumed].**
- Train label windows closed seven to eleven years before the snapshot. The latest holdout window closed 2026-06-30, about four months (130 days) before it.
- Any delay in entering HPV records therefore pushes holdout labels towards zero more than train labels.
- The published holdout rate is 0.745% against 1.06% and 1.14% (`meta.json:37-41`). That is also consistent with the falling eval-year trend of 1.28%, 1.13%, 1.03% (`evaluation.json:25`, `47`, `69`). I cannot separate the two explanations from pinned files.
- Consequence for scoring: Brier comparisons against a training-prior reference will mix skill with a base-rate shift.

**R4. Snapshot attributes are observed 1 to 12 years after t, unevenly across splits [code].**
- The eight snapshot features (`build.py:746-750`) and the programs-row filter (`build.py:600-602`) are as of 2026.
- For train rows that is 8 to 12 years after t; for holdout rows it is 1.4 to 2.9 years.
- If enforcement activity after t changes a facility's programs, pollutants or emission class in the system, those features carry post-t information, and more of it in train than in holdout. Whether ICIS-Air does this is my hypothesis, not a verified fact.
- `README.md:59` says the build should report a variant without these features. `evaluation.json` contains no such variant.

**R5. Facility identity is recoverable from the ID, and the facility-disjoint variant is not in the pinned files [code + data].**
- `evaluation_id` is `PGM_SYS_ID:ACTIVITY_ID` (`build.py:611`). **[data]** Every train and eval ID has exactly one colon, so the facility is the text before it.
- The baseline ignores the ID (`train.py:19`, `27`). The file header says `train.py` is the file a modelling agent edits (`train.py:1`). A modified version could parse the ID and learn facility-level label memory, with 81% of eval rows covered by train facilities. The contract's `access` is `isolated_rows` (`construction.json:227`).
- `MANIFEST.json:303`, `meta.json:56` and `README.md:60` describe a "fixed robustness variant" that assigns each facility to the split of its earliest evaluation. `construction.json:195` says the design "is not facility-disjoint". `build.py` contains no such assignment and `evaluation.json` reports no such result.
- Not checked: whether a non-pinned script implements it (`MANIFEST.json:97-121` lists several that are not in the pinned directory).
- Not checked: whether `ACTIVITY_ID` order tracks data-entry order, which would make the ID suffix a proxy for entry timing.

**R6. Much of the signal is between agencies [data + code].**
- The contract states that HPV designation is discretionary and varies by agency (`README.md:57`).
- Train positive rate by state ranges from zero (NJ, 0 of 1,938) to 7.7% (CA, 125 of 1,632):

  | State | Train rows | Positives | Rate |
  |---|---|---|---|
  | CA | 1,632 | 125 | 7.66% |
  | IN | 1,788 | 95 | 5.31% |
  | PA | 5,999 | 62 | 1.03% |
  | CO | 3,332 | 3 | 0.09% |
  | NJ | 1,938 | 0 | 0.00% |

- Five states (CA, IN, PA, AR, NC) hold 54% of train positives. Pearson chi-square for equal rates across the 53 states is 1,194 on 52 degrees of freedom.
- A pooled AUC therefore rewards knowing which agency designates HPVs. The calendar/identity reference reaches 0.685 on public validation (`evaluation.json:13-16`); its definition is not in the pinned files.
- This is disclosed, not hidden. It bears on interpretation and on the choice of cluster.

**R7. Within-facility dependence [data].**
- Among train rows whose facility has another positive train row, 57 of 441 are positive (12.9%), against 1.2% for all rows in multi-row facilities.
- Part of that is the state effect in R6. I did not separate them.

**R8. Calendar information is available to a modified model [code + data].**
- `evaluation_end_date` is a shipped, non-ID column (`build.py:44`; section 2).
- It is known at t, so this is not leakage. A model using calendar year would extrapolate to holdout years it has not seen, and the 2020–2022 window overlaps the COVID disruption (`README.md:61`).

**R9. Contract statements with no counterpart in pinned files [code].**
- "The build must report the first year with national coverage before accepting the frozen splits" (`MANIFEST.json:447`). There is no such check in `build.py`. **[data]** Train-year row counts are 15,324, 15,508, 14,021 and 13,330, which show no obvious coverage ramp.
- `construction.json:222` describes eligibility as "prior program membership". The code uses current-snapshot membership with no date (`build.py:323`, `600-602`). `MANIFEST.json:299` words it accurately.

## 8. Checks performed and not performed

**Performed (public train; eval identifiers and state only).**

- ID format, facility counts, rows per facility and minimum same-facility gap.
- State completeness: zero missing in train and in eval; 53 states in train; no eval state absent from train.
- State constant within facility: zero facilities with two state values.
- Agreement between the ID's first two characters and `state`: 99.5%. The mismatches are numeric or tribal prefixes such as `08` and `SU`.
- Per-state and per-year train label rates, `prior_hpv_count` distribution, history-depth indicators.
- Train-to-eval facility overlap.
- One fetch of the publisher's public data-dictionary page for field definitions. I did not compare it with the hashed documentation snapshot in `SOURCES.json:9-15`.

**Not performed.**

- Any read of holdout rows or computation of holdout metrics.
- Any read of the raw archive. The following are therefore unverified: R1 incidence, the blank-day-zero assumption for non-HPV rows, the date columns actually selected, record entry delays, and the stage counts in section 4.
- Any model fit, ablation, within-state metric or facility-disjoint rescoring.
- Verification of the assets listed in `MANIFEST.json:6-172` that are not in the pinned directory (`qualification.json`, `source-checks.json`, `extract/quality.json`, `source-snapshot.tar.gz`, runner scripts).
- Verification that the runner's `task.json` (`train.py:16`) matches `extract/meta.json`.
- Hash re-verification of pinned files against the manifest.

## 9. Clustering declaration

See `cluster.json`: `state`, status `declared`, chosen before any holdout scoring.

- **Why state.** The label is partly an agency-practice outcome (`README.md:57`), the contract's own reference block names `state` as an entity column (`construction.json:363-366`), and train label rates are heavily state-dependent (R6).
- **Why not facility.** The facility is the finer dependence unit (R7), but it is not shipped as a column; it exists only inside `evaluation_id`. I did not manufacture a derived key.
- **Why state still covers it.** State is a per-facility snapshot attribute (`build.py:294-296`, `746`) and is constant within facility in train, so clustering on state also absorbs within-facility dependence.
- **What it costs.** There are 53 clusters of very unequal size, and positives are concentrated in a few of them. Cluster-level intervals will be wide and driven by CA, IN and PA.
