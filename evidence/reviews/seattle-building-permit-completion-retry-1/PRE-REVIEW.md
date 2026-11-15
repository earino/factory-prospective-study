# Pre-scoring contract review: seattle-building-permit-completion (retry-1)

Bounded pre-scoring review, written before any holdout scoring. It is not an acceptance gate.

**Overall reading.** The build code matches the declared contract: features are row-local, no label-derived cross-row history is constructed, splits are disjoint calendar windows on `issueddate`, and the release already discloses its main vintage limits. I found no defect in the build. I found four things worth carrying into interpretation of the holdout score:

1. A blank `numberreviewcycles` is almost always a negative label (1 positive in 61 train rows, 1 in 25 validation rows). The mechanism is unverified; it is small in scale (R1).
2. The pinned baseline runner appears to consume `issueddate` as an undeclared categorical feature that is 100% unseen outside train (R2).
3. `totaldaysplanreview` is essentially absent before 2018Q2, so its presence marks record era, not project attributes (R3).
4. Rows are not independent: same-day sibling permits share labels far above chance (R4). This drives the `cluster.json` choice.

Tags used below: **[CODE]** observed in pinned code or contract text; **[DATA]** observed by me in `extract/public/train.csv` or `extract/public/eval.csv`; **[ASSUMED]** assumption made by the release or by me; **[NOT CHECKED]** a check I did not perform.

Paths are relative to `.study/releases/seattle-building-permit-completion/`. `build.py`, `train.py` and `construction.json` are under `reproduction/`.

## Scope of what I read

- Read: `README.md`, `SOURCES.json`, `LICENSE.md`, `LICENSE-EVIDENCE.json`, `.prepared.json`, `MANIFEST.json`, `evaluation.json`, `extract/meta.json`, `reproduction/{build.py,train.py,construction.json,requirements.txt}`, and the two public CSVs.
- Not read: no holdout rows (`extract/private/holdout.csv` is not present in the pinned directory), no raw source snapshot, no other study results, no factory private state. I did not open `pre-review.jsonl` or `mcp.json` in the review directory.
- No model was fitted. Data work was limited to counts, missingness shares, label rates and intraclass correlations on the public train and validation files, using the standard library.
- Several assets named in `MANIFEST.json` are not in the pinned directory (`qualification.json`, `source-checks.json`, `source-snapshot.tar.gz`, `leakage_battery.py`, `qualify_dataset.py`, `extract/quality.json`). **[NOT CHECKED]** Their contents, and any checks they record, are outside this review.

## Source, task and target

- **Source [CODE].** City of Seattle SDCI "Building Permits", Socrata resource `76t5-zqzr` (`build.py:9`). One CSV page of 8,817,799 bytes was fetched at unix time 1794739939 = 2026-11-15 10:52 UTC (`SOURCES.json:16-21`). The fetch selects 22 columns (`build.py:10-17`) with a server-side filter on issue date and cost (`build.py:67`).
- **Task [CODE].** "Will a newly issued Seattle building permit for a substantive construction project reach final inspection sign-off within four years of issuance?" (`construction.json:90`, `meta.json:3`). The unit is the permit as issued (`construction.json:91`). Declared use is `retrospective_research` (`construction.json:435`, `README.md:26`).
- **Target [CODE].** `completed_within_48_months` = 1 when `completeddate` is non-null and no later than `issueddate` plus 48 calendar months, inclusive; otherwise 0 (`build.py:182-183`). Month arithmetic clips to month end (`build.py:40-47`). Dates are normalized to day precision (`build.py:149-150`). A null `completeddate` maps to 0 (`build.py:250-251`, `construction.json:419`).
- **Documentation drift, not a defect [CODE].** `MANIFEST.json:346` describes the month arithmetic as "dateutil relativedelta"; the code uses its own `_add_months`. Both clip to month end, so I expect the same labels. **[NOT CHECKED]** I did not compare the two on real dates.
- **Label ignores record status [CODE].** `statuscurrent` is fetched (`build.py:16`) but only appears in a name-set check (`build.py:301`). The label uses `completeddate` alone. `MANIFEST.json:346` says y = 0 covers "expired permits and withdrawn permits". **[ASSUMED]** That holds only if such permits never carry a `completeddate`. **[NOT CHECKED]** I could not cross-tabulate `completeddate` against `statuscurrent` without raw source rows.
- **Positive rate [CODE/DATA].** 0.779 train, 0.749 validation, 0.757 holdout as published in `meta.json:44-48`. I reproduced the train and validation rates from the public files; the holdout figure is quoted metadata only.

## Declared features

25 features (`build.py:21-30`, `construction.json` feature list, `meta.json:13-37`). All are computed from the row's own source fields:

| Group | Features | Construction |
|---|---|---|
| Passed through | `permitclass`, `permitclassmapped`, `permittypedesc`, `estprojectcost`, `housingunitsadded`, `housingunitsremoved`, `housingunits`, `totaldaysplanreview`, `numberreviewcycles`, `daysoutcorrections`, `dependentbuilding`, `standardplan` | numeric coercion only (`build.py:143-148`) |
| Date-derived | `applied_to_issued_days`, `issue_month_sin`, `issue_month_cos` | `build.py:184`, `build.py:202-204` |
| Text-derived | `description_length` and six `description_*` token flags | `build.py:185-201` |
| Presence flags | `parent_permit_flag`, `related_mup_flag` | `build.py:205-206` |
| Fitted mapping | `originalzip` mapped to top-20 train ZIPs, `other`, `missing` | `build.py:207-221` |

- **[CODE]** No feature derivation reads `completeddate`, `statuscurrent` or the target. `expiresdate` is not fetched at all (`build.py:10-17`).
- **[CODE]** The `no_outcome_feature_leak` check compares feature names against three literal names (`build.py:301-302`). It cannot detect a derived leak; the conclusion above rests on my reading of `build.py:184-221`, not on that check.
- **[CODE]** Feature availability is declared `assumed` for all 25 features and `verified` only for `permitnum` and `issueddate` (`construction.json` feature evidence: 25 `assumed`, 2 `verified`).
- **[CODE]** Output columns are ID, time, target, then features (`build.py:31`). `issueddate` is shipped as a non-feature carry. `carry_columns` is empty (`construction.json:37`), so raw `parentpermitnum`, `relatedmup`, address and contractor fields are not shipped.

## Timing and vintage assumptions

- **Prediction time [CODE].** The permit's `IssuedDate` (`construction.json:92`, `construction.json:255-257`).
- **Vintage [CODE].** `current_snapshot` from a live endpoint with no archive (`construction.json:436-439`, `README.md:53`, `README.md:63-64`). Every feature value is the value on the 2026-11-15 snapshot, not the value at issuance.
- **[ASSUMED by the release]** Fields are available at issuance "from field semantics and current-snapshot presence, not proven" (`construction.json:421`). `EstProjectCost` and housing units are documented as mutable (`README.md:52`, `construction.json:423`).
- **Label finality [CODE].** The last 48-month window closes 2026-09-30 (`meta.json:63`); the snapshot was fetched 2026-11-15 (`SOURCES.json:20`), a 46-day buffer. **[ASSUMED]** Completions are recorded within that buffer and `completeddate` is not back-dated later. Only holdout permits issued near the end of the window and completed in its last weeks are exposed.
- **Training-label timing [CODE].** Declared `unverified` (`construction.json:434`). The split text says "No embargo is applied or needed" because features are row-local (`meta.json:63`).
  - Train label windows close between 2020-01 and 2022-12. Validation windows close 2023-01 to 2024-12. Holdout prediction instants run 2021-01-01 to 2022-09-30.
  - So some train labels, and all validation labels, were not final at the holdout prediction instants. This is consistent with the declared `retrospective_research` scope and I do not treat it as a defect. It does mean the holdout score measures temporal transfer with fully matured labels, not an as-of-2021 deployable forecast.
- **Snapshot date wording [CODE].** The contract speaks of "2026-11-14 publisher evidence" (`construction.json:420`, `construction.json:437`); the retrieval timestamp is 2026-11-15. These are compatible (publisher last-updated date versus fetch time).

## Population selection

- **Rule [CODE].** `issueddate` in [2016-01-01, 2022-10-01) and `estprojectcost` >= 50000 (`build.py:67`, `build.py:153`), then `permittypemapped` equal to "building" case-insensitively (`build.py:155-158`), then drop rows where issue precedes application or completion precedes issue (`build.py:170-179`).
- **Counts [CODE].** 24,750 rows before the chronology drop is a hard assertion (`build.py:165`), with per-year counts asserted at `build.py:168`.
- **Label-source field used in selection [CODE].** The chronology drop reads `completeddate`, which is the label source (`construction.json:38-40`, `construction.json:261-268`). The contract still labels selection `prediction_time` (`construction.json:430`) while disclosing the exclusion (`construction.json:431-432`).
  - **Scale [CODE, inferred from pinned counts].** Train has 11,286 rows (`meta.json:40`) against 3841 + 3779 + 3669 = 11,289 pre-drop (`build.py:168`): three rows dropped. Validation (7,135) and holdout (6,326) equal their pre-drop year sums, so no validation or holdout row was removed by this rule.
  - **[NOT CHECKED]** Which of the two chronology conditions removed the three rows.
- **Mutable eligibility field [CODE].** The cost floor is applied to the current-vintage `estprojectcost`, both server-side and locally (`build.py:67`, `build.py:153`); disclosed at `README.md:57` and `construction.json:423`. **[DATA]** 653 train rows (5.8%) sit at exactly 50000 with label rate 0.786 against 0.779 overall, so I see no label discontinuity at the floor. **[NOT CHECKED]** Rows below the floor are never fetched, so retroactive entry or exit cannot be counted from these files.
- **Non-binding checks [CODE].** `invalid_chronology_rows` passes for any count (`build.py:174-178`) and `excluded_permit_type_codes` passes whenever any row remains (`build.py:159-164`). They record values but constrain nothing. The exact-count assertions at `build.py:165-169` are the binding ones.

## Splits

- **[CODE]** Fixed calendar windows on `issueddate`: train [2016-01-01, 2019-01-01), validation [2019-01-01, 2021-01-01), holdout [2021-01-01, 2022-10-01) (`build.py:32-35`, `build.py:223-234`, `construction.json:51-64`). Window integrity is asserted (`build.py:335-349`). Rows are sorted by date then ID (`build.py:317`).
- **[DATA]** Train spans 2016-01-04 to 2018-12-31 over 856 distinct issue days; validation spans 2019-01-02 to 2020-12-31 over 625 days. `permitnum` is unique within each file and no ID appears in both.
- **[CODE]** Access is `isolated_rows` with no probes (`construction.json:274-278`). Only the three split files are written (`build.py:308-319`).
- **[CODE]** `evaluation.json:2` reports the baseline on public validation only, with no holdout scoring.

## Label-derived cross-row history construction

- **[CODE]** None is constructed. The target is referenced only where it is created (`build.py:183`) and in checks (`build.py:245-251`, `build.py:284-293`, `build.py:350-355`). There is no group-by, lag, rolling window or target encoding anywhere in `build.py`.
- **[CODE]** The only cross-row operation is the top-20 ZIP list. It is a frequency count over train-window rows (`build.py:207-211`) and does not read the label. **[DATA]** Both public files show 22 ZIP levels, consistent with 20 plus `other` and `missing`.
- **[CODE]** The contract's statement matches the code: "No label-derived rates, prior-permit outcomes, holdout-based feature choices or post-outcome fields are shipped" (`construction.json:452`), with persistence declared not applicable (`construction.json:443`).
- **[DATA]** Cross-row label dependence still exists in the data even though no feature encodes it; see R4.

## Concrete risk mechanisms

Each item states what I observed, what I am assuming, and what I did not check. None is asserted as a defect.

### R1. Blank `numberreviewcycles` nearly determines a negative label

- **[DATA]** Train: 61 rows have a blank `numberreviewcycles`; 1 is positive (1.6%) against 78.3% for the other 11,225 rows. Validation: 25 blank rows, 1 positive (4.0%) against 75.1%.
- **[DATA]** In train, all 61 are also blank on `daysoutcorrections` and `totaldaysplanreview`, none has `parent_permit_flag` = 1, they spread across 2016 (25), 2017 (20) and 2018 (16), and they cut across permit classes and types.
- **[CODE]** The contract describes the field as "recorded before issuance; null left blank" with availability `assumed` (`construction.json:151`, `construction.json:336`). Blanks are passed through unfilled (`build.py:148`, `construction.json:422`).
- **[ASSUMED, mine]** A blank that predicts the outcome this sharply is more consistent with the blank reflecting a record state (for example a permit that was voided, cancelled or never worked) than with a project attribute known at issuance. If that state is written after issuance, the blank is a post-issuance signal on the current snapshot. A benign reading is also possible: a rare issuance pathway with no plan review and intrinsically low closure.
- **[NOT CHECKED]** I could not test either reading; that needs `statuscurrent` for these rows from the raw source.
- **Scale.** The blank rows are 0.54% of train and 0.35% of validation. They account for 60 of about 2,496 train negatives (2.4%) and 24 of about 1,791 validation negatives (1.3%). By arithmetic, perfectly ranking 1.3% of negatives can add at most roughly 0.007 AUC; this is a bound, not a measured effect. Holdout prevalence was not inspected.

### R2. The baseline runner appears to use `issueddate` as an undeclared feature

- **[CODE]** `train.py:27` takes every column except ID columns and the target as a feature. `meta.json:6-8` lists only `permitnum` as an ID column. `issueddate` is shipped in the split files (`build.py:31`) but is not in the declared feature list (`build.py:21-30`).
- **[CODE]** String columns with at most 1000 distinct train values are kept as categoricals (`train.py:28-31`); levels unseen in train become missing (`train.py:40`).
- **[DATA]** `issueddate` has 856 distinct values in train, under the 1000 threshold. Every validation date is later than every train date, so every validation value is an unseen level; the same must hold for holdout by the split windows.
- **[ASSUMED]** The runner's `task.json` (`train.py:16`) is not in the pinned files; I assume its `id_columns` mirrors `meta.json`. The contract does list `issueddate` under `high_cardinality_columns` (`construction.json:46-49`), so the harness may drop it before the runner sees it.
- **Mechanism if the assumption holds.** The baseline has 26 effective features, not the declared 25. One is a per-day identity fully populated in train and entirely missing at scoring. It cannot leak labels across splits. It can spend tree splits on train-only day effects, and scored rows then follow whatever default branch those splits have, which was never trained on missing values.
- **[NOT CHECKED]** Whether the fitted baseline actually splits on `issueddate`; that requires fitting, which is out of scope. This bears on how the 0.6355 validation AUC (`evaluation.json:5-8`) and any baseline comparison should be read, not on the dataset's validity.

### R3. Plan-review day field marks record era

- **[DATA]** `totaldaysplanreview` is blank for 100% of 2016 rows, 99.5% of 2017 rows and 99.3% of 2018Q1 rows, then 67% in 2018Q2 and 32% to 35% in 2018Q3-Q4. Validation years are 30% (2019) and 26% (2020) blank. Only 1,566 of 11,286 train rows carry a value, almost all issued from 2018Q2 onward.
- **[CODE]** The release notes the field is "frequently null in 2016-era rows" (`README.md:52`, `construction.json:145`).
- **[DATA]** I checked for label-correlated missingness and did not find it: within quarters where both groups exist in volume (2018Q2 to 2020Q4), label rates for blank and non-blank rows differ by a few points in both directions, with no consistent sign.
- **Mechanism.** In train, presence of this field is close to an "issued after early 2018" indicator. A model learns its relationship to the label from roughly nine months of train data and applies it to a holdout where the field is presumably mostly populated. This is covariate shift from record vintage, not leakage.
- **[ASSUMED, mine]** The step in 2018Q2 looks like a change of permitting record system. I recall SDCI changing systems in spring 2018 but did not verify it.
- **[DATA]** Related drift: `dependentbuilding` = 1 is 5.9% of train with label rate 0.752, but 1.05% of validation with label rate 0.480. `standardplan` = 1 never occurs in train and occurs 22 times in validation. `Tenant Improvment` (all `-BK` permit numbers) is 151 train rows and 369 validation rows.
- **[NOT CHECKED]** Holdout missingness and level frequencies.

### R4. Sibling permits share outcomes; rows are not independent

- **[CODE]** The release says so itself: "rows are not strictly independent across sibling permits of one project" (`README.md:58`, also `README.md:67`, `construction.json:278`, `construction.json:424`). The linking fields are reduced to presence flags (`build.py:205-206`).
- **[DATA]** Using a label-free signature (same issue day, ZIP level, class, type, description length and application-to-issue days), 673 train rows (6.0%) fall in 263 groups of two or more, up to 14 rows. 48% of those rows have `parent_permit_flag` = 1, against 3.4% elsewhere, so the signature is picking up real sibling structure.
- **[DATA]** 88% of those groups have a unanimous label, against 57% expected under independence at the same base rate and group sizes. The intraclass correlation of the label within signature group is 0.68. Validation shows the same pattern: 259 rows (3.6%), 81% unanimous against 60% expected.
- **[DATA]** Intraclass correlation of the label by issue day is 0.022 in train (mean 13.2 rows per day, design effect about 1.27) and 0.014 in validation (about 1.15). Keeping one row per signature group lowers it to 0.011 and 0.010, so day-level dependence is partly siblings and partly something else shared by the day.
- **[DATA]** Some sibling structure crosses days. Among train rows with `parent_permit_flag` = 1, a looser date-free signature gives 41 groups (123 rows) spanning different issue days, median span 258 days, maximum 975, with 76% unanimous labels. This signature is weaker and may include coincidental matches.
- **Mechanism.** Uncertainty statements that treat each permit as independent will be too narrow. Siblings issued far apart can also sit on opposite sides of a split boundary, so a holdout permit may have a train or validation sibling with a correlated label. No feature identifies the sibling, so this is dependence, not feature leakage.
- **[NOT CHECKED]** True project membership; the raw `parentpermitnum` and `relatedmup` values are not shipped. I did not examine holdout rows for any of this.

### R5. Overlapping outcome windows and regime shift

- **[CODE]** Train outcome windows cover calendar time 2016 to 2022, validation 2019 to 2024, holdout 2021 to 2026 (`build.py:32-37`). Calendar-wide shocks to inspection and construction activity therefore affect labels in more than one split. The release flags the 2021-2022 regime difference as part of the task (`README.md:56`, `construction.json:425`).
- **[DATA]** Base rates drift by issue year: 0.818 (2016), 0.752 (2017), 0.765 (2018), 0.765 (2019), 0.729 (2020). Month-level intraclass correlation is 0.007 in train with about 313 rows per month, a large design effect that reflects this drift.
- **Mechanism.** Issue-day clusters do not absorb month- or year-scale common shocks. A single holdout score is one draw from one regime.

### R6. Smaller items

- **Issue date as recorded [CODE/DATA].** The pinned sample permit `6071900-CN` was applied for on 2005-12-20, issued 2016-01-12 and completed the same day (`build.py:252-257`). Same-day completions are disclosed (`README.md:60`). **[DATA]** Only 7 train rows have application-to-issue gaps over five years (label rate 0.143). **[ASSUMED, mine]** Such rows may reflect re-issuance or administrative closure, where the snapshot `issueddate` is not the original issuance. **[NOT CHECKED]** The scale is tiny either way.
- **Permit number content [DATA].** The suffix distinguishes `-CN`, `-BK`, `-PH` and `-CC` records, and the number encodes application order. It is an ID column and the baseline excludes it (`train.py:27`). Both pieces of information exist at issuance, so this is not a leak; a consumer that parses the ID gains an era proxy.
- **Administrative outcome [CODE].** The label measures closure of the permit record as much as completion of work (`README.md:51`, `construction.json:418`). No further check performed.

## Checks I did not perform

- Any read of holdout rows or holdout metrics, including holdout missingness, level frequencies and cluster counts.
- Any cross-tabulation against raw source fields (`statuscurrent`, `completeddate`, `parentpermitnum`, `relatedmup`).
- Any model fit, feature-importance read or re-run of the baseline; `evaluation.json` numbers are quoted, not reproduced.
- Byte or hash verification of the pinned files against `MANIFEST.json`.
- Review of the publisher's field documentation or terms beyond the excerpts quoted in the pinned files.
- Historical availability of any feature at issuance. The release declares this unproven, and I do not require it for a retrospective claim.
