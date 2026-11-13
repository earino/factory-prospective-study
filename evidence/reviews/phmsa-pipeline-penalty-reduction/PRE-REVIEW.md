# PRE-REVIEW: phmsa-pipeline-penalty-reduction

Bounded pre-scoring contract review, written 2026-11-13. Not an acceptance gate. No model was fitted and nothing in the release was changed.

**Bottom line.** I found no label-derived cross-row feature and no post-outcome column in the shipped schema. Four things limit what a holdout score can be taken to mean:

1. The publisher defines `Notice_Sent_Date` as the "original or most recent" notice letter, so the declared prediction instant is not guaranteed to be the original notice (R1).
2. The label mixes "penalty reduced" with "case closed within 36 months" (R2).
3. The unmodified baseline runner uses `notice_date` as a tenth, categorical feature that is entirely unseen outside train (R3).
4. The release says cases cluster by operator, but no operator key is shipped, so the dependence unit cannot be keyed (`cluster.json` is `unresolved`).

Paths below are relative to `.study/releases/phmsa-pipeline-penalty-reduction/`. Line numbers for `MANIFEST.json` and `reproduction/construction.json` refer to the `json.dumps(indent=1)` rendering, because both files are stored minified.

## 1. What was read and what was not

| Read | Not read |
|---|---|
| `README.md`, `LICENSE.md`, `LICENSE-EVIDENCE.json`, `SOURCES.json`, `MANIFEST.json`, `.prepared.json`, `evaluation.json` | `extract/private/holdout.csv` (not present in the pinned directory; not fetched) |
| `extract/meta.json`, `reproduction/build.py`, `reproduction/train.py`, `reproduction/construction.json`, `reproduction/requirements.txt` | The raw PHMSA enforcement file and `source-snapshot.tar.gz` (raw source outcomes) |
| `extract/public/train.csv` (670 rows), profiled for schema, missingness, category levels, ID structure | Other studies' results and factory private state |
| `extract/public/eval.csv` (139 rows), used only for schema, category levels and the ID-year check | Manifest assets that are not in the pinned directory: `extract/quality.json`, `qualification.json`, `source-checks.json`, `validate.py`, `dataset_run.py`, `qualify_dataset.py`, `leakage_battery.py`, `source_io.py` (`MANIFEST.json:52-66,97-156`) |
| Publisher data dictionary PDF, fetched from the URL in `SOURCES.json:10`; its SHA-256 `372b4a9e…34fcaf` matches `SOURCES.json:12` | |

One consequence: the row counts emitted by the build's checks (WMS rows removed, closed-but-unassessed count, excluded populations) are not available to this review.

## 2. Source, task and target

**Source (observed).**
- A single tab-delimited PHMSA file, `PHMSA Pipeline Enforcement Raw Data.txt` (`build.py:10-11`), SHA-256 `ac29ec42…a8992`, 1,977,064 bytes (`SOURCES.json:16-21`).
- The publisher labels it "data as of 11/03/2026" (`construction.json:196`). It was retrieved at unix time 1794555640, which is 2026-11-13.
- No joins are made. The dictionary describes the extract as compiled from the SMART and WMS systems.

**Task (observed).**
- Binary classification: "Will a PHMSA Notice of Probable Violation with a proposed civil penalty be closed within 36 months with a lower assessed penalty than proposed?" (`meta.json:3`, `README.md:20`).
- The declared decision user is operator compliance counsel (`construction.json:283`).
- The declared use is `retrospective_research` (`construction.json:85`, `README.md:26`).

**Target (observed, `build.py:254-257`).**
- `horizon_end = notice + DateOffset(months=36)`.
- `closed_ok` = Closed_Date parsed, on or after the notice, and on or before `horizon_end`.
- `assessed_ok` = Assessed_Penalties parsed and strictly less than Proposed_Penalties.
- `penalty_reduced = closed_ok & assessed_ok`. This matches the prose in `construction.json:346`.

Everything else is coded 0. That covers four different situations:
- closed in the horizon with assessed at or above proposed;
- closed in the horizon with a blank assessment;
- closed after 36 months, whatever the eventual outcome;
- still open.

The build hard-fails if any kept row has an unparseable nonblank closure or assessment (`build.py:247,251`) or a closure before its notice (`build.py:252-253`). Since a release exists, those counts were zero at build time.

**Public validation baseline (observed, `evaluation.json:5-16`).**

| Model | AUC | Brier |
|---|---|---|
| `full_model` | 0.617 | 0.1874 |
| `calendar_identity` control | 0.621 | 0.1824 |
| `majority_prior` | 0.500 | 0.1885 |

- On public validation the full model does not beat the calendar/identity control on either metric.
- The 2017 slice has `full_model` AUC 0.432 on 44 rows (`evaluation.json:19-25`).
- No interval is reported (`evaluation.json:77-79`).
- I did not inspect how the `calendar_identity` control is built; `validate.py` is not pinned.

## 3. Declared features

Nine features are declared: `FEATURES = OUT_COLUMNS[2:-1]` (`build.py:17-18`), listed in `construction.json:98-108`. All are computed row-wise at `build.py:261-268`.

| Feature | Raw field (alias priority) | Construction | Train profile (observed) |
|---|---|---|---|
| `proposed_penalty_usd` | Proposed_Penalties (`build.py:26`) | `_parse_money` (`:126-134`); must be > 0 (`:223`) | 0 blank; min 2,000, median 42,000, max 3,699,200 |
| `violation_category_count` | Violation_Category, then Proposed_Violations (`:29`) | token count split on `; , \n`, not distinct (`:137-147,261`) | 1 blank; values 1–8 |
| `cited_regulation_count` | Cited_Regulations, then Proposed_Cited_Regulations (`:30`) | distinct token count (`:262`) | 1 blank; values 1–27 |
| `integrity_management_flag` | Violation_Category | substring "integrity management" (`:150-157`) | 102 ones, 567 zeros, 1 blank |
| `pipeline_type` | Pipeline_Type (`:31`) | trimmed text (`:173-175`) | 12 levels |
| `region` | Region (`:32`) | trimmed text | 5 levels |
| `discovery_route` | How_Discovered? (`:33`) | trimmed text | 6 levels |
| `notice_actions` | Notice_Actions (`:34`) | trimmed text, whole string as one level | 34 levels |
| `proposed_compliance_order` | Proposed_Compliance_Order_Ind (`:35`) | Y/N mapped to 1/0, anything else NA (`:160-170`) | 355 ones, 315 blank, no zeros |

`case_id` is an ID column (`meta.json:6-8`). `notice_date` is the time column (`construction.json:351`) and is not a declared feature.

Other observations from the public files:
- **`proposed_compliance_order` duplicates `notice_actions` in train.** It is blank exactly when `notice_actions` has neither a `CO` nor a `CO/CP` token (315 of 315), and 1 otherwise (355 of 355). Blank therefore behaves as "no" in practice. The README wording "blank or unknown remains missing rather than zero" is accurate about the code; I did not check it against raw values.
- **`case_id` is structured.** All 809 public IDs are nine digits: a region digit, a four-digit year and a sequence. The first digit maps one-to-one to `region` with zero mismatches, and the embedded year equals the `notice_date` year in 809 of 809 rows. The runner excludes it as an ID (`train.py:19,27`), and anything derived from it would only duplicate `region` and calendar year.
- **The dictionary does not contain the field names the build uses for three features.** The 2023 dictionary has `Proposed_Violations` and `Proposed_Cited_Regulations`, not `Violation_Category` or `Cited_Regulations`. `construction.json:382` says the 2026 header carries the latter names. The dictionary lists 53 fields and the recipe says the header has 53, which fits a rename, but I did not read the raw header. The `"status": "verified"` entries that cite the dictionary for these features (`construction.json:18-22,28-32,63-67`) therefore rest on a name mapping the dictionary does not state.

## 4. Timing and vintage assumptions

**Declared.**
- Prediction time is `Notice_Sent_Date`, "before the operator response, hearing or any order" (`README.md:24`, `construction.json:342`).
- Vintage is `current_snapshot` (`construction.json:86-89`).
- `training_label_timing` is `"unverified"` (`construction.json:84`).
- `features_documented_at` is `"prediction_time"` (`construction.json:109`).
- Every feature's availability note ends "historical availability assumed" or equivalent (`construction.json:13-67`).
- The README states there is no historical availability ledger (`README.md:51,58,64`).

These declarations are consistent with a retrospective claim. I do not ask for point-in-time evidence beyond what that claim needs.

**Observed.**
- **Outcome maturity holds on dates.** The last holdout notice date is before 2023-07-01 (`build.py:15,236`), so the latest horizon end is 2026-06-30, before the 2026-11-03 data date. Whether closures and assessments are recorded within about four months is an assumption.
- **Training labels were not all knowable at the split boundary.** Labels for train notices after 2014-01-01 mature after the eval window opens on 2017-01-01, and eval labels mature through 2022, inside the holdout window. The split note "No embargo is needed" (`meta.json:47`) is correct about feature leakage, because no feature uses another row's outcome. It does not make the split a real-time simulation. That matches the declared `unverified` label timing and limits interpretation only.

**Assumptions the public files do not establish.**
- That `Proposed_Penalties`, the violation and regulation fields, `Notice_Actions`, `Pipeline_Type` and `How_Discovered?` in a 2026 snapshot still hold their notice-stage values. This applies to rows up to 24 years old.
- That `Notice_Sent_Date` is the original notice date (see R1).

## 5. Population selection

Observed order of operations in `build.py`:

1. Keep rows whose normalised `Case_Type` contains `noticeofprobableviolation` or `nopv` (`:178-180,208,211`).
2. Keep rows with parsed `Proposed_Penalties > 0` and a parsed notice date (`:223-224`). Blank, zero, negative and unparseable penalties are dropped.
3. Drop rows with a blank `WMS_Activity_Seq` (`:231-234`).
4. Keep notice dates in `[2002-01-01, 2023-07-01)` (`:236-238`).
5. Sort by notice date, WMS and CPF, then keep the first row per `WMS_Activity_Seq` (`:241-242`).
6. Build `case_id` from CPF, falling back to WMS when blank and adding a `-WMS` suffix when duplicated (`:272-275`). No public ID has a suffix, so no CPF number repeats among the 809 kept public rows.

Selection uses only `Case_Type`, `Proposed_Penalties`, `Notice_Sent_Date` and `WMS_Activity_Seq`. `Closed_Date` and `Assessed_Penalties` are not used to select rows, and the deduplication tie-break does not use the label. This agrees with `construction.json:80-83`.

Not established:
- **What `WMS_Activity_Seq` identifies.** The dictionary says only "Work Management Sequence Number". The claim that it groups related cases from one inspection (`meta.json:47`) is the builder's reading. If the reading is right, step 5 silently drops sibling cases and keeps the earliest. If the field is unique per case, step 5 does nothing. The removal count is computed at `build.py:243`, but that output is not pinned.
- **How many rows steps 1–4 exclude.** The public files give 958 kept rows (670 + 139 + 149, `meta.json:23-27`) and nothing about exclusions.
- **Whether the snapshot's population is stable.** Selection is "prediction-time" only on the assumption that withdrawn or superseded notices stay in the extract with their notice-stage `Case_Type` and `Proposed_Penalties`.

## 6. Splits

Observed:
- Fixed half-open windows on notice date (`build.py:12-15,300-303`; `meta.json:33-47`).

| Split | Window | Rows | Positive rate |
|---|---|---|---|
| train | 2002-01-01 to 2016-12-31 | 670 | 0.184 |
| eval | 2017-01-01 to 2019-12-31 | 139 | 0.245 |
| holdout | 2020-01-01 to 2023-06-30 | 149 | 0.396 |

- Public notice dates run 2002-02-06 to 2016-12-15 in train and 2017-01-17 to 2019-12-30 in eval, with no overlap.
- Deduplication runs before split assignment (`:242` before `:300`), so no `WMS_Activity_Seq` straddles splits.
- Operators can recur across splits. Entity overlap is expected in a temporal design, and no operator field is shipped or used, so there is no operator-memorisation path.
- `meta.json:28-32` publishes the holdout positive rate (0.396) in a public file, and `README.md:26` says the labelled holdout is public and unsealed. Holdout Brier scores should be read with that in mind: the base rate is disclosed and the train prior of 0.184 is far from it. AUC is unaffected.
- Train positive rate by notice year ranges from 0.059 (2006, n=34) to 0.333 (2015, n=36), so there is base-rate drift inside train as well.

## 7. Label-derived cross-row history construction

**None found (observed).**
- `build.py` contains no `groupby`, `shift`, `rolling`, `expanding`, `cumsum`, `transform`, `merge` or rank operation. A grep for these returns only string joins.
- The only cross-row operations are the Case_Type value count used for a check (`:209`), the sort and `drop_duplicates` on WMS (`:241-242`), and `duplicated()` for ID disambiguation (`:274-275`). None reads the label.
- The label is computed at `:254-257`, after deduplication. Every feature at `:261-268` is a function of its own row's notice-stage fields.
- No auxiliary files are written beyond the three split CSVs (`:318-323`), consistent with `construction.json:6-11`.
- `references.entity_columns` is empty and `persistence_column` is null (`construction.json:377-381`).

The source does contain direct outcome encodings: `Penalty_Reduction_Ind`, `Basis_for_penalty_reduction`, `Final_Order_Ind`, `Case_Status`, `Collected_Penalties` and many post-notice dates (dictionary). `build.py` does not resolve any of them (`:21-36`), so they cannot reach the output. The guard at `build.py:310` only checks three column names against `out.columns` and passes by construction; the real protection is the fixed `OUT_COLUMNS` list.

## 8. Concrete risk mechanisms

Each item is marked **[O]** observed fact, **[A]** assumption or inference, or **[N]** check not performed.

**R1. The prediction instant may be the most recent notice, not the original.**
- [O] The dictionary defines `Notice_Sent_Date` as "Date of the original or most recent notice letter".
- [O] The build uses that field as the prediction instant, the horizon start and the split key (`build.py:25,214,254,300-303`).
- [A] If an amended notice is issued after the operator responds, the row's notice date moves later, the 36-month clock restarts, and `Proposed_Penalties` and the action and violation fields may hold amended values. For such rows the claim "before the operator response" (`README.md:24`) would not hold, and an amended, usually lower, proposal would lower the chance that assessed is below proposed.
- [O] Partial bound: the year embedded in the case number equals the notice year in all 809 public rows, so no public row was re-dated into a later calendar year. Same-year amendments and overwritten amounts are not excluded by this.
- [N] I did not compare against `Opened_Date` or `Operator_Response_Date` in the raw file.

**R2. The label mixes reduction with closure speed.**
- [O] `closed_ok` uses `Closed_Date` (`build.py:255`), not `Final_Order_Date`, although the source has both.
- [A] If closure waits on compliance-order completion or penalty collection, cases with compliance-order items close later and are coded 0 regardless of whether the penalty was reduced. `notice_actions` and `proposed_compliance_order` would then predict closure lag. That is a legitimate part of the frozen target, but it changes what a score means for the "contest or negotiate" user.
- [A] Contested cases, the ones most likely to win a reduction, are also the ones most likely to run past 36 months.
- [O] The right-censoring is declared (`README.md:52,59`).
- [N] Agreement between the label and `Penalty_Reduction_Ind` was not checked.

**R3. The unmodified runner uses `notice_date` as a tenth, categorical feature.**
- [O] `train.py:27` takes every column not in `id_columns` or the target. `id_columns` is `["case_id"]` (`meta.json:6-8`).
- [O] `notice_date` is read as strings (`train.py:23`), has 558 distinct train values, passes the 1000-level cap (`train.py:30`), and gets its category levels from train (`train.py:32`).
- [O] Unseen levels become NaN (`train.py:40`). 0 of 139 eval dates are train levels, and the same holds for holdout by the split windows.
- [O] The runner does not read `time_column` or `high_cardinality_columns` (`construction.json:110-113,351`; `train.py:16-19`).
- Mechanism: in training, trees can split on a near-row-unique date level and absorb year-level base-rate differences. At scoring, every row takes the missing-value branch. This is train/serve skew and a mismatch with the nine declared features. It is not label leakage, and it can only weaken the baseline.
- [A] I assume `task.json` mirrors `meta.json`.
- [N] I did not check whether the non-pinned harness removes the column before calling the runner, and I did not execute anything.

**R4. Blank assessments on closed cases are coded 0.**
- [O] `assessed_ok` requires a parsed assessment (`build.py:256`).
- [O] The source has `Region_Withdrawn_Date` (dictionary).
- [A] A withdrawn notice with a blank assessed amount is the strongest form of "eliminated", yet it is labelled 0.
- [O] This is declared (`README.md:52,60`).
- [N] The count is computed at `build.py:259` but that output is not pinned.

**R5. Calendar confounding through covariate shift.**
- [O] In train, `discovery_route` is "First Operating" for 450 of 670 rows, concentrated before 2014. "Integrated" is 19 of 39 rows in 2016 and 92 of 139 in eval. Eval also has a level unseen in train ("OPA Activity", 1 row).
- [O] The positive rate rises across the splits (section 6).
- Mechanism: features that proxy for era can score as signal when they only track the base-rate trend. The `calendar_identity` control is the right comparison, and the full model does not clear it on public validation (section 2).
- [A] The era pattern in `How_Discovered?` may partly reflect retrospective recoding in the current snapshot. I did not check this.

**R6. Dependence between rows.**
- [O] The release states cases cluster by operator and that "evaluation should account for operator clustering" (`README.md:54`).
- [O] No operator field is resolved or shipped (`build.py:17,21-36`; `construction.json:4,378`), although the source has `Operator_ID` (dictionary).
- [O] In train, 202 of 670 rows share a notice date with another row, and 131 share both date and region.
- Row-level resampling intervals on 149 holdout rows are therefore likely to be too narrow. See `cluster.json`.

**R7. Small samples.**
- [O] Holdout is 149 rows with about 59 positives implied by the published rate; eval is 139 rows with 34 positives.
- [O] `evaluation.json` reports no interval.
- Small AUC differences are not interpretable without clustered uncertainty.

**Not found.** No post-outcome column in the shipped schema, no label-derived or cross-row feature, no outcome-based row selection, no split overlap on the deduplication key, and no duplicate IDs in public rows.

## 9. Clustering decision

`cluster.json` is `status: "unresolved"` with no columns.

- The dependence unit implied by the source and by the release's own limitations is the operator, and secondarily a shared inspection.
- `Operator_ID` is not carried in any split.
- `case_id` is unique per row and, after deduplication, one-to-one with `WMS_Activity_Seq`. That covers inspection-level dependence at most. It does not show rows are independent, and the release says they are not.
- `region` has five levels and identifies the enforcing office, not the respondent.
- Groupings by date and region would be a manufactured key.

The choice was made from source meaning and train metadata, before any holdout scoring and without reading holdout rows or metrics.

A fix is available upstream, outside this review's remit: carry `Operator_ID` as a non-predictor column in a rebuilt release.

## 10. Checks not performed

- The raw 2026 header was not read. The 53-field claim and the rename of the violation and regulation fields are taken from `construction.json:382`.
- No raw-row checks were made on amended notices, withdrawn cases, WMS multiplicity, or agreement between the label and `Penalty_Reduction_Ind`.
- Manifest hashes of the pinned files were not recomputed. `.prepared.json` records a verification at 2026-11-13T18:32:34Z, which I did not repeat. Only the documentation PDF hash was confirmed.
- Nothing was executed: not `train.py`, `build.py`, or any non-pinned harness script. Statements about runner behaviour are from reading the code plus the observed column cardinality.
- Holdout rows, holdout metrics and the composition of the `calendar_identity` control were not inspected.
- No historical-vintage comparison was made, and none is required for the declared retrospective scope.
