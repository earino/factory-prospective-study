# PRE-REVIEW: t100-new-route-survival

Bounded pre-scoring contract review. Not an acceptance gate. No model was fitted and nothing was changed.

Release reviewed: `.study/releases/t100-new-route-survival/` (manifest version `v-d32decf32c315be4`, `MANIFEST.json:4`; gate 1.6.1 `ok: true`, `MANIFEST.json:455-457`).

Paths below are relative to that release directory. `build.py`, `train.py` and `construction.json` live under `reproduction/`; `meta.json` under `extract/`.

## Bottom line

- **No feature reads a month after entry month M.** I traced every feature function in `build.py`; only the label reads M+12..M+14.
- **No scored row's features overlap another scored row's label window**, in validation or holdout, because each scored window is 12 months wide and the label starts at M+12.
- **I found no construction defect.** The risks are about dependence between rows and about what "newly launched route" means in this population.
- **Rows are far from independent.** In train, 83.5% of rows have a reverse-direction twin with the same carrier and month, and twins agree on the label 97.7% of the time.
- **Much of the population is not new service in the everyday sense.** In train, 86.2% of entries are on a pair another carrier flew in the prior three months, and two carrier-month cohorts alone are 12.4% of rows.
- **Cluster declared: `unique_carrier`** (see `cluster.json`). It is coarse: about 18 effective clusters in train.

## What I read and what I did not

| Read | Not read / not done |
|---|---|
| `README.md`, `MANIFEST.json`, `SOURCES.json`, `LICENSE*.{md,json}`, `.prepared.json`, `evaluation.json` | `extract/private/holdout.csv` (listed at `MANIFEST.json:37-41`, absent from the pinned directory) |
| `extract/meta.json` | Raw T-100 archives or `source-snapshot.tar.gz` |
| `reproduction/build.py`, `train.py`, `construction.json`, `requirements.txt` | `qualification.json`, `source-checks.json`, `extract/quality.json`, `source_io.py`, `dataset_run.py`, `leakage_battery.py` (listed in the manifest, not in the pinned directory) |
| `extract/public/train.csv`: keys, features and labels, descriptive counts only | Any model fit, any re-run of `build.py`, any network fetch |
| `extract/public/eval.csv`: keys and blank counts only, no label statistics | Other studies' results, factory private state |

Statements below are tagged **[code]** (observed in pinned code or contract), **[train]** (counted from public `train.csv`), **[eval-keys]** (key structure of public validation), **[assumed]** (contract assumption or my domain recollection, unverified) or **[not checked]**.

## 1. Source, task, target

- **Source [code].** BTS T-100 Domestic Segment (U.S. Carriers) via the TranStats form postback (`build.py:17`, `MANIFEST.json:173-185`). Panel years 2010-2020, cut at 2020-02 (`build.py:18-19`, `build.py:236`, `build.py:353`, `build.py:528`).
- **Unit [code].** One carrier x directed origin city market x directed destination city market x entry month. `episode_id = carrier-origin-dest-YYYYMM` (`build.py:764`).
- **Question.** Will the newly entered service be gone in the anniversary quarter (`MANIFEST.json:277`, `construction.json:330`)?
- **Target [code].** `discontinued = 1` iff the same carrier string's summed all-class `DepPerformed` on the same directed pair over M+12, M+13, M+14 is exactly 0 (`build.py:586-608`, especially `:587`, `:597`, `:607`; `MANIFEST.json:280`). Positive label is 1 (`meta.json:4-5`).
- **Absent rows count as zero [code].** A missing pair-month in the label window is filled with 0 departures (`build.py:597`). The guard is a global month-coverage check, not a per-carrier one (`build.py:531-541`; disclosed at `construction.json:118`).
- **Use.** `retrospective_research` (`construction.json:144`, `README.md:26`). No holdout score is claimed (`evaluation.json:2`).

## 2. Declared features and what the runner actually consumes

**Declared [code].** 14 features (`build.py:24-39`, `construction.json:157-172`, `meta.json:15-28`). Three carry columns, `unique_carrier`, `origin_city_market_id`, `dest_city_market_id` (`build.py:23`, `construction.json:4-8`), plus `entry_month` as the time column (`build.py:22`).

| Feature | Months read | Code |
|---|---|---|
| `distance_miles` | M (modal Class F distance) | `build.py:385-391`, `:760-762` |
| `entry_calendar_month` | M | `build.py:770` |
| `carrier_departures_prior_12m` | M-11..M, all classes | `build.py:676-686`, `:771` |
| `carrier_active_pairs_prior_12m` | M-11..M | `build.py:690-700` |
| `carrier_route_attrition_prior_12m` | M-12 and M | `build.py:704-712` |
| `origin_market_departures_prior_12m` | M-11..M, all carriers | `build.py:716-727` |
| `dest_market_departures_prior_12m` | M-11..M, all carriers | `build.py:716-727` |
| `competing_carriers_prior_3m`, `pair_departures_prior_3m` | M-3..M-1 | `build.py:611-639` |
| `entry_month_departures`, `_seats_per_departure`, `_load_factor` | M, Class F | `build.py:746-759`, `:778-780` |
| `carrier_new_at_origin`, `carrier_new_at_dest` | M-12..M-1 | `build.py:729-735`, `:781-782` |

- **No feature indexes a month after M [code].** This matches the declared availability text (`construction.json:244-322`).
- **The runner uses 18 columns, not 14 [code].** `train.py:27` takes every column except `id_columns` and the target, and `id_columns` is only `episode_id` (`meta.json:6-8`).
  - `unique_carrier` becomes a categorical (`train.py:28-32`).
  - The two market IDs enter as plain numbers [train: both columns parse as numeric].
  - `entry_month` becomes a categorical with 42 train levels [train]; every validation or holdout month is an unseen level and maps to NaN (`train.py:40`).
- **[assumed]** `train.py:16` loads a `task.json` that is not in the pinned files. I assume it mirrors `meta.json`.
- **Semantic nuance, not a defect [code].** `dest_market_departures_prior_12m` sums `DepPerformed` over segments whose destination is the market (`build.py:653-655`), so it counts inbound flights. The declared meaning says "departures performed at the destination city market" (`MANIFEST.json:228`).

## 3. Timing and vintage assumptions

- **Prediction instant [code, assumed].** End of month M plus 90 days (`construction.json:329`, `:342-346`). The 90 days is an assumed availability lag, not a measured publication date (`construction.json:115`, `:117`, `:343`); `timing.observations` is empty (`construction.json:341`).
- **[not checked]** I did not consult any BTS release schedule.
- **Vintage [code].** Current snapshot only (`construction.json:145-147`), retrieved 2026-11-14 UTC (`SOURCES.json:6`). `training_label_timing: unverified` (`construction.json:143`). The release says plainly that this is not proof of what could have been computed live (`README.md:59`, `:61`). I accept that for a retrospective claim and ask for nothing more.
- **Label maturity versus later splits [code, arithmetic mine].** The check requires at least 15 months between splits (`build.py:915-926`); the frozen windows give 16 (`build.py:41-45`, `:70-77`).
  - Last train entry 2014-06, so its label window ends 2015-08. First validation entry is 2015-10.
  - Last validation entry 2016-09, so its label window ends 2017-11. First holdout entry is 2018-01.
  - Every earlier split's labels are therefore knowable two months before the first prediction instant of the next split, for any constant lag.
- **Panel edge [code].** The last holdout label month is 2018-12 + 14 = 2020-02, exactly the panel cut (`build.py:19`, `:528`). No slack, but no month past the cut is needed.
- **Lookback [code].** The first train entry is 2011-01 and the panel starts 2010-01, so the full M-12 lookback exists for every row (`build.py:18`, `:42`, `:569`).
- **Wording tension, not a defect.** `MANIFEST.json:187` describes the decision "at the end of a new route's first month"; `construction.json:298` calls M "the month ending at the decision instant". The contract instant is 90 days later (`MANIFEST.json:276`). Features stop at M, so the tension is in the conservative direction.

## 4. Population selection

Order of operations [code]: candidate filter, then prior-12-month filter, then label, then features (`build.py:789-837`).

1. **Candidate.** Class F departures >= 8, Class F passengers > 0, neither missing, and M inside a split window (`build.py:554-563`).
2. **New-route rule.** The same carrier string has no all-class row with departures > 0 or missing on the directed pair in M-12..M-1 (`build.py:566-583`).
3. **Label observability.** Rows with any missing `DepPerformed` in M+12..M+14 are dropped (`build.py:605-606`).

Consequences:

- **Late-month launches are excluded permanently [code].** A route with fewer than 8 Class F departures in its first calendar month fails step 1 in M. It then fails step 2 in M+1 through M+12 because M is active. A daily route that starts in the last week of a month is never in the population.
  - The release discloses only that the rule "removes genuine but very thin new services" (`README.md:57`; rationale at `construction.json:152-156`).
  - This uses prediction-time information only, so it is not leakage. It narrows who the claim describes.
  - **[not checked]** Magnitude. Measuring it needs raw source rows.
- **Entry and exit thresholds are asymmetric [code].** Entry needs >= 8 Class F departures; survival needs >= 1 departure of any class across three months (`build.py:556` versus `:607`). The class difference is disclosed (`README.md:72`).
  - **[assumed]** T-100 segment records include one-off segments such as diversions and charters. If so, a single stray departure codes a discontinued route as surviving, and a single stray departure in M-12..M-1 removes a real launch from the population. **[not checked]** frequency.
- **Step 3 uses post-decision information [code].** The contract labels selection `prediction_time` and says no outcome value enters eligibility (`construction.json:140-141`), while disclosing the unknown-label drop in the same rule. This is an observability filter, not a filter on the outcome value.
  - **[not checked]** The dropped count. It is recorded by the `label_unknown_excluded` check (`build.py:819-825`), whose output is not in the pinned files.
- **Repeat episodes exist [train].** 44 directed carrier-pairs have two train episodes, minimum gap 13 months, as the rule implies. **[eval-keys]** 42 of 834 validation rows are a directed carrier-pair that also has a train episode.
- **Blanks [train, eval-keys].** `carrier_route_attrition_prior_12m` is blank in 39 train and 12 validation rows; `distance_miles` in 1 train row. These follow the declared missing-aware rules (`build.py:711`).

## 5. Splits

- **Chronological by entry month [code].** Train 2011-01..2014-06, validation 2015-10..2016-09, holdout 2018-01..2018-12 (`build.py:41-45`, `:70-77`; `meta.json:42-55`). Windows are checked per split (`build.py:909-914`).
- **Sizes.** 3,734 / 834 / 1,209 rows; positive rates 0.318 / 0.301 / 0.352 (`meta.json:31-40`).
- **Metadata nit.** `meta.json:50-53` gives the train start as `null`; the code floors it at 2011-01 (`build.py:71`). [train] The observed minimum is 2011-01-01. No effect on rows.
- **Carriers recur across splits [eval-keys].** 35 of 43 validation carriers appear in train. 16 validation rows come from 8 carrier codes unseen in train.
- **Public validation baseline, for context only.** AUC 0.648; Brier 0.268 against a majority-prior Brier of 0.211 (`evaluation.json:5-12`). The baseline ranks better than chance but is worse calibrated than a constant. 827 of 834 rows were unseen by the calendar-identity control (`evaluation.json:57`). I did not use these numbers to choose the cluster.

## 6. Label-derived cross-row history

**Contract position.** "No future or label-derived group rate is shipped" (`construction.json:14`), with no cross-row probes recorded (`construction.json:13`).

**What the code does [code].**

- `DepPerformed` is both the label source (`construction.json:186-188`) and an input to 11 of the 14 features (all but distance, calendar month and load factor).
- `carrier_route_attrition_prior_12m` is a carrier-level group rate over that column: the share of the carrier's pairs active in M-12 that are inactive in M (`build.py:704-712`). It is a lagged analogue of the label. It uses no shipped label and no month after M, as declared (`construction.json:38`, `:268`).
- It does partially encode another row's label in one case. Take an earlier episode A of the same carrier with entry month M_B - 12. A's pair is in the M-12 set, and whether it is active in M_B is the first of the three months in A's label window.

**Where that overlap can occur [code, arithmetic mine].**

| Pairing | Overlap possible? | Why |
|---|---|---|
| Train row and earlier train row | Yes | Train spans 42 months. Train-on-train, so benign. |
| Validation row and train row | No | M-12 lands in 2014-10..2015-09, inside the dropped gap. |
| Validation row and validation row | No | Window is 12 months wide; M-12 falls before it. |
| Holdout row and holdout row | No | Same reason; M-12 lands in 2017. |
| Holdout row and validation or train row | No | 2017 is inside the second dropped gap. |

More generally, every feature of a scored row reads months at or before M, and every same-split label window starts at or after the month following the split window. So the contract's claim holds for scored rows.

**[not checked]** I ran no empirical probe, such as reconstructing labels from features across rows. This conclusion rests on code reading and window arithmetic.

## 7. Concrete risk mechanisms

Ordered by expected effect on how a holdout score should be read.

### R1. Directed mirror rows double-count routes

- **[code]** The unit is directed (`build.py:764`), so one new nonstop usually produces an A-to-B row and a B-to-A row in the same month.
- **[train]** 3,118 of 3,734 rows (83.5%) have a same-carrier, same-month reverse row. Label agreement among them is 97.7%. Train has 2,177 undirected carrier-pair-month units.
- **[eval-keys]** 707 of 834 validation rows (84.8%) have such a twin; 481 undirected units.
- **Effect.** Row-level confidence intervals on the holdout will be too narrow, by roughly the square root of two before any carrier-level dependence. Row-level cross-validation inside train would put near-duplicates on both sides of a fold. The shipped chronological split is not affected, since twins share an entry month.

### R2. Carrier-code events create both "entries" and "exits"

- **[code]** The prior-service filter and the label both match on the carrier string (`build.py:570-578`, `:588-594`). When a carrier's reporting code changes, the old code's recent entries become `discontinued = 1` and the new code "enters" every inherited pair. The exit side is disclosed (`README.md:54`, `construction.json:120`); the entry side is not spelled out.
- **[train]** Two cohorts make up 12.4% of train: `EV` 2012-01 with 343 rows (11 positive) and `UA` 2012-01 with 119 rows (6 positive). All 462 rows have `pair_departures_prior_3m > 0`.
- **[train]** Four codes are 100% positive: `XE (1)` 78, `XJ` 55, `0JQ` 29, `CO` 26. That is 188 rows, 15.8% of train positives.
- **[assumed]** These look like the ExpressJet/Atlantic Southeast and Continental/United reporting consolidations. That is my recollection, not verified against the source.
- **[not checked]** Whether the 2018 holdout window contains a similar event. I did not look.
- **Effect.** Part of any measured skill is recognising recode or transfer cohorts, not forecasting commercial survival of a launch. A cohort of hundreds of rows with one shared outcome can move a pooled metric on its own.

### R3. Most "new routes" are on pairs someone else was already flying

- **[train]** 3,219 of 3,734 rows (86.2%) have at least one other carrier code with departures on the same directed pair in M-3..M-1.
- **[assumed]** T-100 `UniqueCarrier` is the reporting, operating carrier, so flying moved between regional operators under one marketing brand would appear as an exit for one code and an entry for another. The top train carriers are regional operators (`EV` 598, `OO` 313, `9E` 214, `S5` 163 [train]), which is consistent with this but does not prove it.
- **Effect.** `competing_carriers_prior_3m` may often measure a predecessor, not a competitor (declared meaning at `MANIFEST.json:234`). The headline question (`README.md:20`) reads as market entry; the population is broader than that.

### R4. Carrier identity as a predictor under drift

- **[code]** The unchanged runner uses `unique_carrier` as a categorical (`train.py:27-32`), and the calendar-identity control is built on carrier (`construction.json:331`).
- **[train]** Carrier explains a large share of label variance: one-way ANOVA intraclass correlation 0.32 over 66 carriers. Per-carrier train rates run from 0.00 (`AS`, 30 rows) to 1.00.
- **Effect.** Carrier-level rates learned from 2011-2014 events need not hold in 2018. This is non-stationarity, not leakage. It is consistent with the calibration result in section 5, though I did not test that link.

### R5. Carrier codes are spelled with hindsight

- **[code]** The contract notes that `UniqueCarrier` is "reusable across years with numeric suffixes" (`construction.json:109`).
- **[train]** Three suffixed codes appear: `CP (2)`, `OH (1)`, `XE (1)`, 278 rows. **[eval-keys]** A bare `XE` appears in validation and is a different level from train's `XE (1)`.
- **[assumed]** BTS adds suffixes after the fact when a code is reused. If so, a suffix on a row tells you something about the carrier's later history that was not knowable at M.
- **Effect.** Bounded. The baseline only memorises exact levels, so it cannot exploit this unless the same suffixed level recurs. A hand-built "has suffix" feature would be a current-vintage leak. **[not checked]** whether holdout rows carry suffixed codes.

### R6. Per-carrier reporting gaps are not checked

- **[code]** Absence is zero for both the prior filter and the label, guarded only by global month coverage (`build.py:531-541`, `:572`, `:597`). A carrier-level reporting gap would create false exits and, later, false entries. Disclosed in general terms (`construction.json:118`, `README.md:57`).
- **[not checked]** Whether any such gap exists.

### R7. Seasonal and metro-level definitions

Disclosed and unchanged by this review: seasonal suspension counts as exit (`README.md:53`), and a move between airports in one metro counts as continuous service (`README.md:58`). No new finding.

## 8. Clustering decision

Declared in `cluster.json`: **`unique_carrier`**.

- **Source meaning.** Continuation is the reporting carrier's decision, and carrier-wide events set many labels at once (R2). The label and the prior-service filter are both keyed on the carrier string.
- **Contract.** The release already names it: `event_key_column: unique_carrier` (`construction.json:150`), and states that entries are not independent within a carrier (`construction.json:121`, `README.md:55`).
- **Train metadata.** Carrier intraclass correlation 0.32; carrier-month 0.55; mirror twins (R1) and repeat episodes all nest inside carrier.
- **Alternatives rejected.**
  - `episode_id`: unique per row, but rows are demonstrably not independent.
  - Carrier plus the two market IDs: splits mirror twins into separate clusters. An undirected-pair key would have to be manufactured.
  - Carrier plus `entry_month`: captures twins and batch launches, but adjacent months share two of three label months and carrier events span months.
- **Cost.** Few, uneven clusters. Train has 66 carriers, largest share 16.0%, top five 40.4%, about 18 effective clusters by inverse Herfindahl. Validation has 43, about 19 effective. The holdout count was not inspected.

## 9. Checks not performed

- No model fit, no re-run of `build.py`, no verification of file hashes against `MANIFEST.json`.
- No read of holdout rows, raw T-100 rows or the source snapshot.
- No read of `qualification.json`, `source-checks.json` or `extract/quality.json`, so recorded check outputs (for example the unknown-label drop count and the observed embargo gap) are unconfirmed.
- No verification of the 90-day lag, of BTS suffix conventions, or of which corporate events sit behind the train cohorts in R2.
- No empirical cross-row leakage probe.
- No measurement of the late-month-launch exclusion or of stray-departure label noise.

## 10. Non-binding suggestions before scoring

These use prediction-time columns only and need no holdout labels to define.

1. Report holdout uncertainty with carrier-clustered resampling, and state the cluster count alongside it.
2. Fix in advance a descriptive slice on `pair_departures_prior_3m == 0` (previously unserved pairs), so the reader can see how much skill sits in transfer-type entries.
3. Report the largest carrier-month cohort's share of holdout rows, so one consolidation event cannot pass unnoticed.
