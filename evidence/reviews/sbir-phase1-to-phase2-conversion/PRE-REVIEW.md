# Pre-scoring contract review: sbir-phase1-to-phase2-conversion

Bounded review of the pinned release before holdout scoring. It is not an acceptance gate.

- Release: `v-0d2e623e604ecf78`, manifest sha256 `7d593685…20c5` (`.prepared.json:2`), gate 1.6.1 `ok: true` (`MANIFEST.json:388-391`).
- Reviewed 2026-11-14. Paths below are relative to `.study/releases/sbir-phase1-to-phase2-conversion/`.
- Line numbers refer to the pinned files as shipped (`build.py` = `reproduction/build.py`, `construction.json` = `reproduction/construction.json`, `train.py` = `reproduction/train.py`).

## Summary

1. **Highest-priority risk: `award_amount` for DoD rows looks outcome-conditioned.** In train, Army and Navy rows at the higher amount tier convert at 86–98% and rows at the base tier at 29–37%, and the gap holds within single award years (§8.1). This fits a Phase I option being added to the published amount after Phase II selection. It is an observed train-data association plus an unverified mechanism, not a proven defect.
2. **Firm identity is resolved per record, not per firm**, using UEI first. UEI replaced DUNS only in 2022, so it is a back-filled identifier on every 2005–2018 record. Label linkage and the "first-ever" rule both depend on back-fill coverage I could not inspect (§8.2).
3. **Row selection uses records that postdate the index award**, which contradicts the contract sentence "no outcome field is used to select rows" (§5, §8.3). Magnitude is not reported in the pinned files.
4. **The fiscal-year-end date fallback is not HHS-only.** 1,658 of 4,627 non-HHS train rows are dated 09-30, concentrated in FY2005–2010 (§3, §8.4).
5. No label-derived cross-row feature is built or shipped (§7). The chronological split is implemented as declared (§6).
6. Clustering is declared as `agency` + `branch` + `award_year` (§9, `cluster.json`).

Everything else matches the contract's own declared scope, `retrospective_research` with `training_label_timing: unverified` (`construction.json:95-96`). I do not treat the absence of historical-vintage evidence as a defect for that claim.

## 0. What I read and what I did not

Read:
- `README.md`, `MANIFEST.json`, `.prepared.json`, `SOURCES.json`, `LICENSE.md`, `LICENSE-EVIDENCE.json`, `evaluation.json`, `extract/meta.json`
- `reproduction/build.py`, `reproduction/construction.json`, `reproduction/train.py`, `reproduction/requirements.txt`
- `extract/public/train.csv` (6,574 rows), for descriptive tabulations only, including train labels

Not read or not done:
- `extract/private/holdout.csv` is not present in the pinned directory and was not fetched.
- `extract/public/eval.csv` was not opened. Only its aggregate results in `evaluation.json` were read.
- The raw SBIR.gov award CSV and `source-snapshot.tar.gz` were not opened.
- No model was fitted and nothing was run from `reproduction/`.
- `pre-review.jsonl` and `mcp.json` in the review directory were not opened.
- These manifest-listed assets are absent from the pinned directory, so I could not inspect them: `extract/quality.json`, `qualification.json`, `source-checks.json`, `reproduction/source_io.py`, `reproduction/leakage_battery.py`, `reproduction/validate.py`, `reproduction/dataset_run.py` (`MANIFEST.json:52`, `:97`, `:137`). The build's check outputs (exclusion counts, key-kind counts, `max_year`) live in those files.

One external lookup: I fetched the live data dictionary page (`https://www.sbir.gov/data-resources/data-dictionary/award`) once. The text came back through a summarising model, and I did not hash-compare the live page to the pinned snapshot (`SOURCES.json:9-15`). Treat it as secondary evidence.

## 1. Source, task, target

**Source (observed).** One file: `award_data_no_abstract.csv` from SBIR.gov, 91,646,156 bytes, sha256 `c141711f…1086`, retrieved at unix 1794630149 = 2026-11-14 04:22 UTC (`SOURCES.json:16-22`). `build.py:10-11` reads only this file. The contract declares it a current snapshot (`construction.json:97-100`).

**Task (declared).** Binary classification, one row per firm: will a firm's first-ever SBIR/STTR Phase I award be followed by a Phase II from the same agency within four fiscal years (`extract/meta.json:3-5`, `construction.json:249`). Declared use is `retrospective_research` (`construction.json:96`). The README claims no holdout benchmark score and says the holdout is not sealed (`README.md:26`).

**Target (observed code).**
- First pass: every Phase II record with a non-blank agency adds its `award_year` to `phase2[(firm_key, agency)]` (`build.py:350-352`).
- Label: `1` if any year in `y+1 … y+4` is in that set for the index record's agency, else `0` (`build.py:501-502`).
- The label is re-derived and asserted equal at `build.py:713-741`. That check recomputes the same expression from the same dictionaries, so it confirms internal consistency, not correctness of the linkage.
- The label is firm × agency, not award-to-award. A Phase II that follows a later Phase I of the same firm at the same agency also counts. The contract declares this (`construction.json:83`).
- The horizon is in fiscal-year units. In elapsed time it runs from one day (Phase I on 30 Sep of FY y, Phase II on 1 Oct) to almost five years.
- A Phase II in the same fiscal year as the index award is never a positive. In practice such a firm is removed from the population (§5).

## 2. Declared features

Declared list: `agency`, `branch`, `program`, `award_year`, `award_amount`, `topic_code`, `state`, `number_employees`, `hubzone_owned`, `women_owned`, `socially_economically_disadvantaged` (`construction.json:104-116`, `build.py:15-19`). Shipped columns add `record_id`, `award_date` and the target (`build.py:20`, `extract/meta.json:9-24`).

Observed code facts:
- Every feature value is copied from the single chosen index Phase I record (`build.py:453-467`, `505-519`). No other record contributes a feature value.
- `state` is canonicalised to USPS codes (`build.py:153-161`, `239-240`). Y/N/U flags are normalised (`build.py:180-188`).
- The runner uses every column except id and target, not the declared list (`train.py:27`). String columns with more than 1,000 train levels are dropped (`train.py:30-31`).
  - In train, `award_date` has 1,083 distinct values and `topic_code` has 2,376, so the unmodified baseline uses neither.
  - `award_date` is only 83 levels over the threshold. A modified runner could parse it into features, although it is not a declared feature.
- `award_year` is a numeric feature. Holdout values (2017–2018) lie outside train support (2005–2014). This is extrapolation, not leakage.

Observed in `train.csv`:

| Column | Observation |
|---|---|
| `agency` | Full names such as `DEPARTMENT OF DEFENSE`. The contract describes a "two-to-four character code" (`construction.json:182`) and marks it verified (`:16`). Harmless for modelling, but the "verified" status was not checked against shipped values. |
| `branch` | Blank on 2,477 rows (all NSF, DOE, USDA, NASA, DHS, ED, DOT, EPA rows; 27 of 59 DOC rows; 3 DoD rows). 17 non-blank levels. |
| `topic_code` | Blank on 1,271 rows, 913 of them HHS. |
| `number_employees` | Blank on 805 rows, 740 of them in FY2005–2009. 394 rows equal 0. One row exceeds the documented 0–500 range. |
| `award_amount` | Blank on 5 rows. Maximum 3,418,440. Nominal dollars. |

Contract evidence status: `award_date` and `number_employees` are `assumed`; all other features are `verified` (`construction.json:13-77`), with `features_documented_at: prediction_time` (`:117`). §8.1 bears on the `verified` status of `award_amount`.

## 3. Timing and vintage assumptions

**Prediction instant (declared).** The Phase I award date (`construction.json:248`, `README.md:24`).

**`award_date` construction (observed code).** `proposal_award_date` is used if it parses and falls inside `[1 Oct y-1, 1 Oct y)`. Otherwise the value is 30 Sep of `award_year` (`build.py:217-224`).
- The fallback fires for missing dates and for dates outside the fiscal year. No flag records which rows used it.
- The check "award_date within award fiscal year" (`build.py:645-660`) cannot fail, because `_award_date` forces the value inside the window.

**Fallback prevalence (observed in train).** 3,570 of 6,574 rows are dated 09-30.

| Group | Rows dated 09-30 |
|---|---|
| HHS | 1,912 / 1,947 |
| USDA | 297 / 297 |
| DOE | 196 / 340 |
| NSF | 660 / 1,303 |
| DoD | 324 / 2,121 |
| Non-HHS, FY2005–2010 | 1,526 / 2,872 |
| Non-HHS, FY2011–2014 | 132 / 1,755 |

The contract attributes the fallback to HHS (`construction.json:81`, `:85`). I cannot separate true 30 Sep awards from fallbacks without the raw file.

**Dictionary lookup (secondary evidence).** The live page describes Award Year as "The Fiscal year of the award" / "4 digit Federal Fiscal Year" and Proposal Award Date as "The first day of contract performance", required "Yes, Except HHS". This agrees with `construction.json:265`. It gives no timing basis for Number Employees.

**Assumption I could not check.** That agencies actually report `award_year` as a fiscal year. Among train rows with a real date, only 212 of 3,004 fall in October–December. If some agencies report a calendar or solicitation year, their autumn awards would fail the window test and be re-dated to a 30 Sep that precedes the true award. Split assignment would be unaffected, because it uses `award_year` (`build.py:662`).

**Label window closure (observed code).** A firm needs `year + 4 <= max_year`, where `max_year` is the largest parseable `award_year` on any keyed record (`build.py:342-343`, `415`). The contract wording is "last complete award year" (`construction.json:252`); the code does not test completeness. This is immaterial here. The last cohort's window ends at FY2022 and the file was retrieved in November 2026. I did not observe the actual `max_year`.

**Vintage (declared).** Current snapshot, later corrections possible, historical availability not proven (`construction.json:80`, `97-100`; `README.md:51`). Features and labels come from the same 2026 vintage. For a retrospective claim this is a stated scope limit, not a defect. §8.1 and §8.2 are the two places where I see a concrete mechanism by which vintage could be correlated with the outcome.

## 4. Firm key

Observed code (`build.py:191-204`): the key is computed **per record** as `uei:` if UEI is non-blank, else `duns:` if DUNS has digits, else `name:` + normalised company + `|` + canonical state. Records link only if they resolve to an identical string.

- DUNS keeps digits only, with no zero-padding or DUNS+4 handling (`build.py:193`).
- The name key strips legal suffixes (`build.py:44`, `123-128`) and includes the record's state, so a relocation splits a name-keyed firm.
- `record_id` is the first 24 hex characters of SHA-1 of the key (`build.py:503`). The key kind cannot be recovered from the shipped file.
- Counts by key kind are computed (`build.py:364-374`) but written only to check output that is not in the pinned directory.

## 5. Population selection

Observed code:

1. First pass over all records. For each key, keep the minimum `award_year` and the set of phases seen in that year (`build.py:345-349`).
2. Eligibility (`build.py:406-417`):
   - the first-year phase set equals `{1}`;
   - `2005 <= year <= 2018`;
   - `year + 4 <= max_year`;
   - the key is not in `firm_missing_year`, `phase2_firm_ambiguous` or `unknown_phase_firm_ambiguous`.
3. Second pass collects Phase I records in the first year (`build.py:448-452`).
   - One record: use it.
   - Several: use the unique earliest parsed `proposal_award_date`. Drop the firm if any date is missing or the earliest is tied (`build.py:476-488`).
4. Drop if the chosen record has no agency (`build.py:490-492`).
5. Drop if an unknown-phase record from the same agency falls in `y+1 … y+4` (`build.py:493-500`).

Where the code is broader than the declared rule:
- The declared rule excludes firms "whose earliest record is Phase II" (`construction.json:247`). The code works at year granularity: a firm with a Phase I and then a Phase II in the same first fiscal year has phase set `{1, 2}` and is excluded (`build.py:348-349`, `411`). A Phase 3 or unparsed phase in the first year has the same effect.
- The three firm-level exclusion sets are filled from records of any year, including years after the index award (`build.py:338-340`, `350-359`, `409`).

Exclusions that depend on records after the prediction instant:
- same-year Phase II (item 2);
- same-year additional Phase I (item 3);
- unknown phase in the label window (item 5);
- any later record with a missing year, or a missing agency on a Phase II or unknown-phase record (item 2).

The contract declares `selection.kind: prediction_time` (`construction.json:91-94`) and says "no outcome field is used to select rows" (`:281`). `phase` is the declared label source and post-hoc column (`:127-129`, `:154-156`), and it drives two of these exclusions. Limitations `:86-87` disclose items 3 and 5. The same-year Phase II exclusion and the any-year firm-level exclusions are not disclosed.

Magnitude is unknown. The `excluded` counter (`build.py:470`) is only surfaced for `unknown_phase_in_window` (`build.py:750`), and that output is not pinned. Train holds 572–790 rows per award year.

## 6. Splits

Observed code:
- Assignment is by `award_year` alone: train 2005–2014, eval 2015–2016, holdout 2017–2018 (`build.py:244-251`, `662`).
- Windows are hard-coded and asserted (`build.py:669-701`). They match `extract/meta.json:35-48` and `construction.json:157-170`.
- Row counts are 6,574 / 1,408 / 1,704, with positive rates 0.444 / 0.442 / 0.442 (`extract/meta.json:25-34`).
- The id-disjointness check (`build.py:757-768`) holds by construction, since each key yields one row. It does not show that one real firm cannot appear under two keys.

No embargo is applied (`extract/meta.json:49`, `construction.json:251`).
- Label windows for train cohorts 2013 and 2014 (1,320 rows) close at FY2017 and FY2018, after the holdout window opens on 2016-10-01.
- All eval label windows (to FY2020) close after the holdout period ends.
- This is consistent with the retrospective claim and with `training_label_timing: unverified`. It means scores are not a simulation of a model trained with labels known at the holdout start.

`evaluation.json:18-73` reports "by_year" with a 2014 bucket of 23 rows, although eval is FY2015–2016. The buckets appear to be the calendar year of `award_date`, not fiscal cohorts. The harness code that produces them is not pinned.

## 7. Label-derived cross-row history

Observed code facts:
- **None is built.** The output row holds index-record fields plus the row's own label (`build.py:505-521`). There is no group rate, target encoding, lag or prior-outcome column. Only three CSVs are written (`build.py:772-778`). This matches `construction.json:7-11` and `:88`.
- **The runner adds none.** `train.py:27-41` does no target encoding. Categorical levels come from train only (`train.py:32`), and unseen levels become missing (`train.py:40`).
- The `references` block is empty (`construction.json:285-289`). The "agency-by-award-year conversion base rate" reference (`construction.json:250`) is named but not implemented in pinned code. If built later for holdout years, it would need holdout labels.
- The `calendar_identity` control (`evaluation.json:13-16`, AUC 0.503 on eval) comes from unpinned harness code. I could not inspect how it is built.

Cross-row operations that do exist, all within one firm key:
- minimum year and first-year phase set (`build.py:345-349`);
- the Phase II year set (`build.py:350-352`);
- same-year tie-breaking (`build.py:476-488`).

These define the population and label. They are not predictors. They are the route by which the key-resolution risk in §8.2 would reach the labels.

## 8. Concrete risk mechanisms

Each item separates what I observed from what I infer.

### 8.1 `award_amount` on DoD rows may include a post-selection Phase I option

**Observed (train only, descriptive).** Cells are positives / rows, FY2005–2014 pooled, by published amount band.

| Branch | Lower band | Higher band |
|---|---|---|
| Army | $60–90k: 57 / 156 (37%) | $110–140k: 108 / 110 (98%) |
| Navy | $60–90k: 112 / 385 (29%) | $140–160k: 96 / 112 (86%) |
| DARPA | $90–110k: 72 / 148 (49%) | $140–160k: 22 / 24 (92%) |

- The gap is not a calendar-time effect. In every Army year 2005–2010, rows near $70k convert at 14–56% and rows near $120k at 97–100%. In Navy FY2012, rows near $80k convert 1 / 33 and rows near $150k convert 15 / 18.
- Navy rows at $90–110k sit in between at 105 / 147 (71%).
- HHS and NSF show no such step. Every amount band with at least 20 rows sits at 33–40%.
- DoD is 2,121 of 6,574 train rows.

**Mechanism (my inference, not verified in any pinned file).** DoD components have structured Phase I as a base contract plus an option that is exercised for firms chosen for Phase II. The tiers match that pattern (Army about $70k + $50k, Navy about $80k + $70k). If the published amount is updated when the option is exercised, the feature encodes the selection decision.

**Alternatives I cannot exclude.** Components may set a larger Phase I up front for some topics or firms. The pattern may have a reporting cause unrelated to selection.

**Contract position.** The limitation that amounts "may have been corrected after the award" is declared (`README.md:51`). The feature is nonetheless marked `verified` and described as Phase I money "stored as published" (`construction.json:18-22`, `:204-207`).

**What it would affect.** Any score from a model that uses `award_amount`, mostly on DoD rows. The baseline already uses it. I did not measure its contribution, because that needs model fitting.

**Checks not performed.**
- Compare the same award records across archived source vintages, or against contract-action data.
- Read component solicitations for the base and option amounts by year.
- Run a scoring-stage sensitivity without `award_amount`, or report DoD and non-DoD separately.

### 8.2 Per-record key priority with a back-filled identifier

**Observed.** UEI takes precedence on each record independently (`build.py:197-200`).

**Inference from general knowledge.** UEI replaced DUNS as the federal entity identifier in 2022. A UEI on a 2005–2018 record must have been back-filled, plausibly only for firms still registered.

**Consequences if back-fill is uneven across one firm's records.**
- A Phase I record keyed `duns:` and a later Phase II keyed `uei:` do not link, giving a false negative.
- The later-keyed records look like a new firm, so a repeat awardee enters as "first-ever" and the same real firm can sit in two splits.
- Linkage quality then correlates with survival to 2022, and so with the outcome.

**Consequences if back-fill is uniform per firm.** None of the above applies.

**Not checked.** Key kinds are hashed away in the shipped file, and the key-kind counts are in unpinned check output. The contract acknowledges merge and split risk only generically (`construction.json:84`).

### 8.3 Selection on post-index records

Code facts are in §5. The effect is to remove the fastest converters (a Phase II in the first fiscal year) and firms with several first-year Phase I awards that lack distinct dates.

The second removal is uneven across time. It hits all HHS multi-award entrants. It hits non-HHS entrants much more in FY2005–2010, where about half of rows lack a usable date, than in later years. That is a route to population drift between early train years and the eval and holdout years. I did not measure either effect.

### 8.4 Imputed dates and same-day clustering

`event_key_column` is `award_date` (`construction.json:102`). In train, 54% of rows share a 30 Sep date across unrelated agencies. The largest single-date group is 548 rows, and 617 dates are singletons. Day-level grouping therefore mixes an imputation artefact with real timing. This is why I did not adopt it as the dependence unit (§9).

A 09-30 indicator also carries signal about record completeness, not about the firm. NSF rows dated 09-30 convert at 33.8% against 42.8% for other NSF rows, partly because the two groups come from different years.

### 8.5 Reporting-era signals in optional fields

**Observed.** `number_employees` is blank on 18–27% of rows in FY2005–2009 and under 3% from FY2010. Blank rows convert at 31.8% and rows reporting 0 at 22.1%, against 46.2% for all non-blank rows.

**Not known.** Whether the field is an as-of-award value or a later company-level value. The contract marks it `assumed` (`construction.json:43-47`), and the dictionary lookup gives no timing basis. I have no evidence that it is outcome-conditioned.

### 8.6 Cohort-level dependence

**Observed in train.** Conversion rates for the same awarding component move far more between years than sampling noise allows: NSF 0.23–0.56, Navy 0.33–0.58, Army 0.45–0.77, counting only cohorts of at least 30 rows. NIH is stable at 0.35–0.42. Rows in one component-year share budget and selection conditions, so row-level uncertainty intervals would be too narrow. `evaluation.json:77-79` already states that no interval is reported.

## 9. Clustering decision

Declared in `cluster.json`: **`["agency", "branch", "award_year"]`**, the awarding component's fiscal-year Phase I cohort. A blank `branch` is a level in its own right.

Reasoning, fixed from source meaning and train metadata only:
- Each row is one firm by construction (`build.py:471-521`, uniqueness asserted at `:635-643`). There is no repeated firm to group, and the shipped file has no firm-level carry (`construction.json:4`).
- The outcome is a decision by the awarding component about a cohort competing for one Phase II budget. The year-to-year swings in §8.6 show the shared shock is large. A unique `record_id` therefore does not make rows independent.
- Topic-level competition is nested inside this unit, so the unit absorbs it. A topic-level key alone would leave 2,192 of 2,780 train groups as singletons.
- `agency` × `award_year` alone would give about 11 clusters a year. DoD components and HHS divisions (NIH, CDC, FDA) run separate budgets, so `branch` is the more accurate level and gives 17–24 clusters a year in train (206 in total).
- `award_date` was rejected for the reason in §8.4.

Limitations are listed in `cluster.json`. The main ones: few and unequal clusters (the largest is 23–33% of each train year); remaining dependence between cohorts whose four-year windows overlap; no way to group one real firm split across identifier namespaces. I estimated cluster counts from train only and did not count holdout clusters.

## 10. Checks not performed

- Any read of holdout rows, `eval.csv` rows, the raw source file or the source snapshot.
- Any model fit, feature-importance run or ablation.
- Verification of `max_year`, exclusion counts or key-kind counts.
- Verification that `award_year` is a fiscal year in practice for every agency.
- Verification of the DoD option mechanism against solicitations or an earlier source vintage.
- Hash comparison of the live dictionary page against the pinned snapshot.
- Inspection of the gate, leakage battery, validation scripts or `calendar_identity` control, none of which are pinned here.
- Licence and redistribution terms, which are outside this review.
