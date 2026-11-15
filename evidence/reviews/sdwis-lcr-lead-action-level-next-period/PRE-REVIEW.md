# PRE-REVIEW — sdwis-lcr-lead-action-level-next-period

Bounded pre-scoring contract review. Not an acceptance gate. No model was fitted, no build was re-run, nothing in the release was changed.

**Release reviewed:** `.study/releases/sdwis-lcr-lead-action-level-next-period/`, version `v-5917644e4c46057e` (`MANIFEST.json:4`). All 11 pinned files that are listed as manifest assets hash-match the manifest, and the manifest hash matches `.prepared.json:2`.

**Evidence labels used below**

- **[CODE]** — read directly in the pinned code or contract; line cited.
- **[DATA]** — counted by me on `extract/public/train.csv` (and, for structure only, `extract/public/eval.csv`) with stdlib scripts. Descriptive counts only.
- **[ASSUMED]** — asserted by the contract or inferred by me; not verified.
- **[NOT DONE]** — a check I did not perform, with the reason.

File shorthands: `build.py` = `reproduction/build.py`, `train.py` = `reproduction/train.py`, `construction.json` = `reproduction/construction.json`, `meta.json` = `extract/meta.json`.

---

## 1. Headline

The construction matches its contract on the points that matter most for scoring: the label never enters its own row's features, eval labels cannot be recovered from any public row, and the split and embargo are implemented as declared. I found no blocking defect.

Five things are worth carrying into scoring. Each is detailed in §8.

1. **Eval is one row per system, and by the same code the holdout should be too.** System-level clustering then collapses to row-level resampling, while training labels show material dependence at the primacy-agency level. This drives the choice in `cluster.json`.
2. **Lagged history two or more periods back is ordered by period start only.** The contract says those records end before the target starts; the code enforces that only for the immediately prior period. Frequency cannot be measured from the released columns.
3. **A unit-magnitude artifact sits in `prior_pb90_mg_l`.** 922 train rows carry values above 1 mg/L, 880 of them from one agency (OH), and they behave like non-exceedances.
4. **The baseline runner treats `target_period_start` as a categorical feature** that is entirely unseen out of time. This weakens the reference model, which matters for any headroom comparison.
5. **The scored population is narrower than the declared one.** The embargo keeps only each system's first post-boundary period, and drops systems whose monitoring cycle straddles the boundary.

---

## 2. Source, task, target

| Item | Fact | Evidence |
|---|---|---|
| Source | One national ZIP, `SDWA_latest_downloads.zip`, from EPA ECHO; 558,010,511 bytes, retrieved once | [CODE] `build.py:11`, `build.py:161`; `SOURCES.json:16-22` |
| Tables used | LCR samples, public water systems, violations/enforcement, events/milestones, reference codes | [CODE] `build.py:174-178` |
| Join key | `PWSID`, required in all four event tables | [CODE] `build.py:187-193` |
| Task | Binary classification, one row per system and target PB90 monitoring period | [CODE] `build.py:484-487`; `meta.json:2-8` |
| Question | Will the next period's reported lead 90th percentile exceed 15 µg/L? | `construction.json:339`; `README.md:20` |
| Target | `next_pb90_exceeds_action_level = (target-period PB90 in mg/L > 0.015)` | [CODE] `build.py:16`, `build.py:322`; `MANIFEST.json:280` |
| Unknown outcomes | Rows with a missing target measurement are dropped, never labelled 0 | [CODE] `build.py:320-321` |
| Claimed use | `retrospective_research`; training label timing `unverified` | `construction.json:133-134`; `README.md:26` |
| Declared scope | No final holdout benchmark score is claimed | `README.md:26`; `evaluation.json:2` |

**Unit handling.** [CODE] Measurements are converted with a factor chosen from the `UNIT_OF_MEASURE` string, and the build aborts on any unrecognized unit (`build.py:269-277`). There is no plausibility bound on the resulting value. See §8.3.

**Strict inequality.** [CODE] The label uses `> 0.015` on the stored value (`build.py:322`). [DATA] 189 train rows have a prior value in (0.015, 0.0155], and 166 train positives whose target value is recoverable (see §7) fall in that band. [ASSUMED] Whether a primacy agency would round such values to 0.015 before the compliance determination is not addressed by the contract and I did not verify it. I record this as a label-definition nuance, not a defect.

---

## 3. Declared features

Fourteen declared features (`build.py:17`; `construction.json:147-162`). `PWSID` is a declared carry column, not a feature (`construction.json:4-6`). `row_id` is the only declared id column (`meta.json:6-8`).

| Feature | Construction | Evidence | Contract status |
|---|---|---|---|
| `prior_pb90_mg_l` | Previous PB90 period by start order, same system | `build.py:306`, `build.py:330` | verified (`construction.json:87-92`) |
| `prior_cu90_mg_l` | CU90 record with the same system and same start as the prior PB90 period | `build.py:299-300`, `build.py:307`, `build.py:331` | verified |
| `prior_pb90_ratio_to_al` | `prior_pb90_mg_l / 0.015` | `build.py:332` | verified |
| `pb90_change_from_previous` | Prior PB90 minus the PB90 two periods back | `build.py:308`, `build.py:333` | verified |
| `n_prior_periods_observed` | Running count of earlier PB90 periods | `build.py:309`, `build.py:334` | verified |
| `ever_exceeded_before` | Any earlier-start PB90 above 0.015 | `build.py:310`, `build.py:335` | verified |
| `gap_days_between_periods` | Target start minus prior end | `build.py:336` | verified |
| `prior_period_length_days` | Prior end minus prior start | `build.py:337` | verified |
| `population_served_count`, `primary_source_code`, `owner_type_code` | Current system-table values, joined on `PWSID` | `build.py:225`, `build.py:339` | **assumed** (`construction.json:39-68`) |
| `primacy_agency_code` | System-table value, else first two `PWSID` characters | `build.py:212-218` | **assumed** (`construction.json:57-62`) |
| `prior_lcr_violations_count` | Count of matched violations with begin date strictly before target start | `build.py:134-138`, `build.py:436` | verified |
| `prior_lslr_milestone` | Earliest matched milestone date strictly before target start | `build.py:141-145`, `build.py:432`, `build.py:437` | verified |

Observations on the public train split [DATA]:

- `prior_cu90_mg_l` is empty in 249,433 of 257,379 rows (96.9%). The contract says missing copper stays missing (`construction.json:258`); it does not state how sparse it is.
- `pb90_change_from_previous` is empty in 20,448 rows (7.9%), exactly the rows with `n_prior_periods_observed == 1`.
- `prior_pb90_ratio_to_al` is an exact rescaling of `prior_pb90_mg_l`; it carries no extra information.
- `ever_exceeded_before >= (prior_pb90_mg_l > 0.015)` holds on every train row, consistent with `build.py:310`.
- Each `PWSID` maps to exactly one tuple of the four system attributes, and `PWSID[:2] == primacy_agency_code` on every train row.

**What the baseline runner actually uses.** [CODE] `train.py:27` takes every column except the id columns and the target. String columns with more than 1,000 distinct training values are dropped (`train.py:30-31`). [DATA] `PWSID` has 48,332 distinct values, so it is dropped. `target_period_start` has only 134 distinct values, so it is kept as a categorical. [ASSUMED] This depends on the runtime `task.json` (`train.py:16-19`), which is not in the pinned release; I assumed its id columns match `meta.json:6-8`. See §8.4.

---

## 4. Timing and vintage assumptions

**Prediction instant.** [CODE] The target period's `SAMPLING_START_DATE` (`build.py:13`, `build.py:329`; `construction.json:338`).

**What the code enforces in time**

- [CODE] The prior period must end strictly before the target period starts (`build.py:314`), end on or after its own start (`build.py:316`), and end no more than four years before the target start (`build.py:312`, `build.py:315`).
- [CODE] Violations and milestones are counted only when dated strictly before target start (`build.py:138` uses `side='left'`; `build.py:145` uses `<`).
- [DATA] In train, `gap_days_between_periods` ranges 1 to 1,461 days, consistent with those bounds.

**What the code does not enforce, and the contract mostly says so**

| Assumption | Evidence | Status |
|---|---|---|
| The prior result had been entered in SDWIS by the target start | Contract declines to assert it: `README.md:57`, `construction.json:347` | [ASSUMED], declared |
| System attributes held their current values historically | `construction.json:119`, `construction.json:135-138` | [ASSUMED], declared |
| The retained PB90 value is the one first reported | [CODE] Duplicates collapse to the *latest* `SAR_LAST_REPORTED_DATE` (`build.py:292-294`), so a later revision replaces an earlier value | [ASSUMED]; revision frequency not measured |
| A violation was known when its compliance period began | [CODE] The date used is `NON_COMPL_PER_BEGIN_DATE` (`build.py:345`), the start of the non-compliance period, not a determination or entry date | [ASSUMED]; contract asserts only that begin dates precede the instant (`construction.json:324`) |
| Milestone dates share one meaning | [CODE] Date is the first non-null of `EVENT_ACTUAL_DATE`, `FIRST_REPORTED_DATE`, `EVENT_DATE` (`build.py:410-414`) | [ASSUMED]; mix of date kinds not measured |
| Train labels were realized before eval prediction times | Declared `training_label_timing: unverified` (`construction.json:133`) | [ASSUMED], declared; see §8.6 |

**Vintage.** One current snapshot, described as 2026Q3 (`construction.json:135-138`; `README.md:55`). [CODE] The community-system filter itself uses the current `PWS_TYPE_CODE` (`build.py:205-207`), so a system reclassified since its historical periods is in or out by its present type.

I am not asking for historical-availability proof here. The contract claims retrospective research, and these are the stated conditions of that claim.

---

## 5. Population selection

Selection steps in order [CODE]:

1. Systems whose current `PWS_TYPE_CODE` is `CWS` (`build.py:205-207`). No activity-status filter (`construction.json:337`).
2. PB90 and CU90 records for those systems (`build.py:250-257`); rows with an unparseable start date dropped (`build.py:285-286`).
3. One record per system, contaminant and start date, keeping the latest reported (`build.py:292-294`).
4. Consecutive PB90 pairs meeting the timing rules in §4, with a non-missing prior value and prior end date (`build.py:313-317`).
5. Known target value (`build.py:320-321`).
6. Agency floor: keep agencies with at least 20 pairs whose prior period ended before 2014-01-01 (`build.py:445-451`).
7. Target start inside a split window (`build.py:454-460`), then the embargo (`build.py:463-468`).

Points to carry forward:

- **Row existence depends on the outcome being reported.** Step 5 means a row exists only when the target PB90 reached SDWIS. The README states that some states report only exceedances or only larger systems (`README.md:56`). [DATA] Train positive rates by agency run from 0.5% (SD, 3,924 rows) and 0.8% (TX, 14,697 rows) to 12.2% (ME, 2,767 rows) and 33.8% (NH, 476 rows, 108 systems). [ASSUMED] I attribute part of that spread to reporting practice; I did not separate it from real differences in lead levels.
- **No broad exceedance-only signature by size and era.** [DATA] The share of train rows with a prior value above the action level is 3–6% in every population band (≤3,300; 3,301–50,000; >50,000) in each of 1995–2001, 2002–2007 and 2008–2013. Selective reporting, where present, looks agency-specific rather than national.
- **The agency floor uses pair counts, not label values.** [CODE] It runs after step 5, so it counts pairs with a known target, including pairs whose target falls in the eval window when the prior ended before 2014 (`build.py:445-446`). That is consistent with "uses no labels" (`build.py:452`) in the sense of label values. [DATA] 63 agencies remain in train, 62 in eval; the smallest has 16 train rows.
- **Same-start records with different end dates collapse.** [CODE] The de-duplication key omits the end date (`build.py:294`). [NOT DONE] How many collapsed records had differing ends is recorded, if anywhere, in `source-checks.json`, which is not in the pinned release.

---

## 6. Splits

| Split | Window on target start | Rows | Evidence |
|---|---|---|---|
| train | 1995-01-01 ≤ start < 2014-01-01 | 257,379 | `build.py:18-19`, `build.py:455`; `meta.json:30` |
| eval | 2014-01-01 ≤ start < 2019-01-01, prior end < 2014-01-01 | 17,368 | `build.py:456`, `build.py:465-467`; `meta.json:31` |
| holdout | 2019-01-01 ≤ start < 2024-01-01, prior end < 2019-01-01 | 17,568 | `build.py:457`, `build.py:466-467`; `meta.json:32` |

- [CODE] Train rows are exempt from the embargo (`build.py:467`). `construction.json:341` says this; the wording in `MANIFEST.json:279` and `meta.json:53` reads as if the embargo applied to every split. The code and `construction.json` agree with each other. Wording only.
- [CODE] `MANIFEST.json:274` describes the horizon limit as four years "after the decision instant"; the code measures four years from the prior period end to the target start (`build.py:312-315`), as `construction.json:336` says. Wording only.
- [DATA] Train target starts span 1995-01-01 to 2013-12-01; 99.1% fall on January 1 or July 1.
- [DATA] Eval target starts span 2014-01-01 to 2017-07-01, 14 distinct dates; the latest eval prior end is 2013-12-31. This matches the embargo.
- [DATA] **Every eval row is a distinct system**: 17,368 rows, 17,368 distinct `PWSID`. 16,884 of those systems also appear in train; 484 do not.
- [CODE] This is structural. Once a system's first post-boundary period becomes a target, the next pair has a prior ending after the boundary and is dropped (`build.py:465-468`). The holdout should therefore also be one row per system. [NOT DONE] I did not read holdout rows, so this is unverified there.
- Eval rows by year: 13,615 in 2014, 2,283 in 2015, 1,030 in 2016, 440 in 2017 (`evaluation.json:22-111`). The four-year limit explains the absence of 2018.

**Unsealed holdout.** `README.md:15` lists `extract/private/holdout.csv` as a split and `README.md:26` says the labeled holdout is downloadable and not sealed. The file is a manifest asset but is not in the pinned release directory. I did not look for it or open it.

---

## 7. Label-derived cross-row history

This is a panel in which one period's label-bearing measurement becomes later rows' features. That is the design, and it runs in time order.

**How it is built** [CODE]

- All lag features are computed on the full per-system period table, sorted by start, before any split is assigned (`build.py:301`, `build.py:304-310`, versus `build.py:454-468`). History therefore crosses split boundaries on purpose: an eval or holdout row's features come from train-era and eval-era measurements of the same system.
- The row's own target value is excluded from every lag feature. `_prior_*` use `shift(1)`, `_prev_pb90` uses `shift(2)`, and `_ever_exceeded` applies `cumsum().shift(1)` (`build.py:304-310`).
- `_n_prior` is a plain running count (`build.py:309`). It includes earlier periods with a missing measurement or missing end date.

**What I confirmed on public rows** [DATA]

- For 209,446 of 257,379 train rows, the target period reappears as the prior period of a later public row for the same system. In all 209,446, the train label equals `prior_pb90_mg_l > 0.015` on that later row. Zero mismatches. Train labels are thus readable from later rows' features, as expected for this design.
- No eval label is readable from any public row. An eval target period could only be a prior for a row whose prior ends in 2014 or later, and the latest prior end is 2013-06-30 in train and 2013-12-31 in eval.

**What follows from the code for the holdout** [CODE reasoning, NOT DONE on rows]

- A holdout target period could reappear as a prior, or as a two-back period, only in a row whose prior ends in 2019 or later. Such rows are dropped by the embargo or fall outside the window (`build.py:457`, `build.py:466-468`). So holdout labels should not be recoverable from released features.
- Holdout rows' `prior_pb90_mg_l` will in many cases be an eval-era label-bearing value. Eval labels are public development data, so this is not a leak.

**Where the history is weaker than the contract wording**

Only the immediately prior period is checked for ending before the target start (`build.py:314`). Periods two or more back are admitted on start order alone (`build.py:308-310`). The contract says of `ever_exceeded_before` that "all contributing records end before the target period starts" (`construction.json:282`; also `construction.json:22`). The code does not establish that. Detail in §8.2.

---

## 8. Concrete risk mechanisms

Ordered by how much I think they bear on interpreting a holdout score.

### 8.1 Dependence above the system level, with one row per system at scoring time

- [DATA] In train, a system has a median of 5 rows (maximum 34). The one-way intraclass correlation of the label is 0.130 by `PWSID`.
- [DATA] By primacy agency it is 0.020 over all train rows, and 0.055 when each system contributes only its last train row. That second figure is the closer analogue of eval and holdout.
- [DATA] Eval has one row per system (§6), so resampling by `PWSID` there is the same as resampling rows.
- Mechanism: the agency is the unit that reports to EPA (`README.md:22`). Reporting completeness (`README.md:56`), base rates (§5) and data-entry conventions (§8.3, one agency accounts for 95% of an artifact) are shared within it. Errors of any model are therefore plausibly correlated within agency.
- Consequence: an interval computed as if rows were independent is likely too narrow. See `cluster.json`.
- [NOT DONE] I did not measure within-agency correlation of model errors; no model was fitted. Label correlation overstates it to the extent a model absorbs agency base rates through the `primacy_agency_code` feature.

### 8.2 Older history ordered by start, not by end

- [CODE] `pb90_change_from_previous`, `ever_exceeded_before` and `n_prior_periods_observed` draw on periods two or more back with no end-date test (`build.py:308-310`).
- Mechanism: suppose a system has a three-year record A, a six-month record B that starts inside A, and a target C that starts the day after B ends. The pair (A→B) is dropped because B starts before A ends. The pair (B→C) is kept. For C, the two-back value is A, whose sampling window runs through C's own period. A's 90th percentile could then rest on samples taken during the target period.
- [DATA] Multi-year periods are common: 81,105 train rows (31.5%) have a prior period of 800–1,200 days.
- [NOT DONE] **Frequency is unmeasured and cannot be measured from the released columns.** A record like A can only ever be the prior of a dropped pair, so its end date never appears in the public files. Measuring this needs the source period table, which is outside this review's bounds.
- [DATA] Loose upper bound only: among 215,598 train rows with at least two prior periods and a prior start in 1995 or later, 21,984 (10.2%) have a prior period that is not itself a retained train target row. That set also includes pairs dropped for a gap over four years, a missing prior value, or a missing end date. The true overlap count is somewhere between zero and that.
- I am not asserting this occurs. It is a gap between contract wording and code that one query on the source table would settle.

### 8.3 Implausible magnitudes in a column declared as mg/L

- [DATA] `prior_pb90_mg_l` reaches 258.0 in train; `evaluation.json:120` shows the same maximum. The 99.9th percentile is 5.0.
- [DATA] 922 train rows (837 systems) have a prior above 1 mg/L. 880 are from agency OH, and 835 fall in target years 2005 and 2008.
- [DATA] Their next-period positive rate is 2.5%. For all rows with a prior above the action level it is 26.2%; for rows at or below it, 2.3%. These rows behave like non-exceedances.
- [ASSUMED] The likeliest explanation is values entered in µg/L under an mg/L unit label. I did not confirm it against the source.
- Effect on features: these rows are 9.1% of all train rows flagged as prior-above-action-level. `ever_exceeded_before` is cumulative (`build.py:310`), so the flag persists for the rest of that system's history. Persistence and threshold references (`construction.json:340`) inherit the same false flags.
- Effect on labels: small in train, as far as it can be seen. Of 6,590 train positives whose target value is recoverable, 35 (0.5%) have a target above 1 mg/L.
- [NOT DONE] Extent in the holdout is unknown; I did not read it.

### 8.4 The baseline uses a time key that never recurs

- [CODE + DATA] `target_period_start` is not an id column (`meta.json:6-8`) and has 134 distinct training values, so `train.py:28-31` keeps it as a categorical. Every eval date is later than every train date, so all eval values map to missing (`train.py:40`). The same will hold for the holdout window.
- Mechanism: the reference model can spend splits on training dates that carry no information out of time. Its measured eval AUC of 0.792 (`evaluation.json:5-8`) may understate what the declared 14 features alone support.
- Consequence for a headroom reading: a candidate that only drops this column could show a gain that reflects the reference's configuration rather than new signal.
- The contract itself lists `target_period_start` as high-cardinality (`construction.json:164-168`), which suggests it was not meant as a predictor.
- [ASSUMED] Depends on the runtime `task.json` matching `meta.json`. [NOT DONE] I did not run the runner to see how much it matters.

### 8.5 Scored population differs from the declared and the training population

- [CODE] The embargo keeps, per system, only the first post-boundary period whose prior ended before the boundary (`build.py:465-468`).
- [DATA] Of 31,308 systems with a train target in 2011–2013, 16,127 (51.5%) have no eval row. 13,514 train rows with a target start of 2012-01-01 or 2013-01-01 belong to systems with no eval row. [ASSUMED] These look like three-year cycles that straddle 2014-01-01; target end dates are not released, so I cannot confirm.
- [DATA] Train counts every consecutive pair, so frequently sampled systems weigh more. The train positive rate is 3.26% against 2.40% in eval (`meta.json:35-36`).
- Consequence: a holdout score describes systems whose cycle happens to align with 2019-01-01, one period each. It is not a score for the declared population in `construction.json:337`.
- Target-year composition is also lopsided: 78% of eval rows are in 2014 (`evaluation.json:22-25`).

### 8.6 Train labels that may mature after eval prediction times

- [CODE] Splits cut on target *start* (`build.py:455-457`). A train target starting 2013-01-01 on a three-year period is not measured until as late as 2015.
- [DATA] For train targets that reappear as a public prior, none ends on or after 2014-01-01. The 13,514 rows in §8.5 are the ones that do not reappear, and they are where late-maturing labels would be.
- The contract already declares this (`construction.json:121`, `construction.json:133`). Under a retrospective-research claim it is a stated condition, not a defect.

### 8.7 Current-vintage attributes that may encode later events

- [DATA] `population_served_count` is 0 in 4,682 train rows (1,185 systems). 67.7% of those systems have their last public row before 2011, against 30.5% of systems with a positive count.
- [ASSUMED] A zero count likely marks a system that has since gone inactive. The contract lists activity status as post hoc (`construction.json:222-227`), and this value may proxy for it.
- [DATA] The association with the label is modest: 3.50% positive at zero against 3.26% otherwise; 3.54% against 2.78% in 2008–2013.

### 8.8 Violation and milestone identification

- [CODE] A violation matches if its code is in the reference-derived set, or its rule code is in the set that always includes `350`, or a description column contains one of three phrases (`build.py:353-357`, `build.py:366-375`). The match is a union, so it is as broad as its loosest arm.
- [CODE] Milestones match on the reference set plus the hard-coded `LSLR` and `LSLI`, a code prefix of `LSLR`, or text matches (`build.py:400-402`, `build.py:416-423`).
- [DATA] 92,019 train rows (35.8%) have at least one prior violation; 689 have a prior milestone.
- [NOT DONE] Which codes were matched and how many records each arm contributed is in `source-checks.json`, not pinned here. I did not verify that `LSLI` denotes a replacement milestone.

### 8.9 Target-record field used as an input

- [CODE] `gap_days_between_periods` is computed from the target period's start date (`build.py:336`). `construction.json:371` says no target-period field is used as an input.
- The start date is the declared decision instant, so this is consistent if the start is fixed by schedule before the period. [ASSUMED] I did not verify that states assign period start dates independently of the result recorded for that period.

### 8.10 Rule drift inside the holdout window

Declared at `README.md:60`. The December 2021 revisions changed site selection within the 2019–2023 holdout window. No action needed beyond reading holdout results with that in mind.

---

## 9. Checks not performed

| Not done | Why |
|---|---|
| Reading holdout rows, or locating `extract/private/holdout.csv` | Out of bounds for this review |
| Opening the source ZIP or any source table | Out of bounds; also not pinned |
| Reading `source-checks.json`, `qualification.json`, `extract/quality.json`, `leakage_battery.py`, `source_io.py` | Manifest assets, but absent from the pinned release directory |
| Re-running `build.py` or the baseline runner | No model fitting or production changes |
| Measuring overlap of older periods with target windows (§8.2) | Not possible from released columns |
| Verifying the µg/L explanation for values above 1 mg/L (§8.3) | Needs source records |
| Confirming holdout is one row per system (§6) | Follows from code; rows not read |
| Checking regulatory rounding practice near 0.015 mg/L (§2) | No source for it in the release |
| Fetching the EPA documentation or terms pages | Not needed to review the construction |

One value I could not avoid seeing: `meta.json:37` publishes the holdout positive rate. I did not use it for the clustering choice or anywhere else in this review.

---

## 10. Clustering decision

Recorded in `cluster.json`: **`primacy_agency_code`, status declared.**

The contract names `PWSID` as its qualification cluster (`construction.json:12`, `construction.json:127`; `build.py:498`). I depart from that for scoring, for three reasons taken from source meaning and training rows only:

1. `PWSID` is unique per row in eval and, by the same code, expected to be in holdout. Clustering on it there would amount to treating rows as independent.
2. Training rows show agency-level dependence that row-level resampling ignores (§8.1), and the agency is the reporting unit that determines which rows exist (§5).
3. `PWSID` is nested inside agency on every train row, so agency clusters also contain any system-level dependence.

The cost is coarseness: 62–63 clusters, about 30 effective by size. Limitations are listed in `cluster.json`.
