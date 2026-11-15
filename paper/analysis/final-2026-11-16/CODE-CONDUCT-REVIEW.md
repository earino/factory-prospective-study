# Selected-code and conduct review

## Scope completed before the last recoveries

Codex inspected the fitting and prediction preparation functions of the 32 frozen
solutions listed in `selected-code-inventory.json`, plus their label-statistic
helpers and active settings where conditional behavior mattered. The review
covered supplied inputs, fitted preprocessing state, target encoding, training
subsets/augmentation, and data access. This is a bounded code and trace review,
not a security audit or a line-by-line review of every exploratory program.
The single Seattle recovery and three utility recoveries require additions when
they finish. Current Seattle entries are the retained original r2/r3 only.

All selected modules import only NumPy, pandas, XGBoost, and (one module) `re`.
AST screening found no file/network access or dynamic execution calls in those
modules. The apparent matches for `eval` and `system` are column names in pandas
expressions. Protected-input checks record no changes. Those observations support
the inspected paths; they do not establish OS isolation.

## Label use and prediction state

- Civil trials, penalties, grant conversion, and air enforcement use supplied
  training labels for fitting or fold-excluded encodings. Encoding priors and
  parent tables are calculated from the same excluded folds.
- Device recalls use product/group target statistics and count-window histories.
  In r2, the initial ordered blocks can use a global prior, but those blocks are
  excluded from fitting (`drop_first=2`, `lag_max=0`, `te_random=False`). Retained
  rows use earlier blocks. Full-training tables are saved for new predictions.
- Airline routes use label-free augmentation in r1/r2. Run r3 removes training
  cohorts with uniform positive labels. This is training-only sample selection,
  not removal of validation or holdout rows. Its fitted features use supplied
  predictors. The original probe's row-count assumption was inappropriate here.
- Wastewater uses supplied historical predictors and fitted preprocessing.
  The separately documented source/interface limitation is not removed by these
  consumer checks.
- Wildlife r1 augments a fixed random subset with a masked size feature. Run r3
  contains an optional augmentation path that could reuse full-data encodings,
  but the frozen settings disable both that augmentation and target encodings.
- Seattle r2/r3 use training-derived category and feature summaries. The optional
  zip target encoder in r3 is disabled in its frozen settings (`zip="cat"`).
- Railway r3 uses a training-label-derived base margin with the row's own label
  subtracted from both local rate and prior. Its saved predictor uses a fixed
  training-derived base score. The other railway encoders exclude each fold.
- Drinking-water encoders use fold-excluded or strictly earlier-block labels;
  other agency summaries use training covariates. Prediction preparation uses
  saved maps and the supplied row.

The three earlier own-label probe errors arose from assuming that a fitted matrix
contains an integer number of complete copies of the training rows. The corrected
probe maps retained rows and augmentation copies back to their source rows,
checks that captured labels agree, and compares two retained source rows per
solution. All three cases had zero changed feature cells for the tested rows.
Original reports remain intact. No model was retrained or rescored for this fix.

## Requests and observed results

The existing scanner identified 424 access-reference requests in these selected
executions. Of these, 354 contain an explicit path to the requesting run; none
names another run. The remaining 70 matched lines concern own trial paths,
documentation, checks for forbidden strings, own environment variables, or
relative paths within research subdirectories. Those matched lines were inspected.
This classification is screening evidence, not a proof about every possible path.

All eight original access flags were inspected with their recorded results:
seven PHMSA flags concern file hashes, local private-file existence checks, or
scans of the agent's own code; the wastewater flag is a grep over its scratch
files, returning no matches. They do not show holdout contents being read.

The four recorded web requests retrieve publisher documentation: two PHMSA data
dictionaries, the SBIR dictionary, and the FAA field list. The five flagged Read
paths outside attempt directories are the CLI's own cached tool outputs (three
PDF responses and two process logs). Wastewater also reads its own cached builder
output. These are not external training labels or another run's results.

Process records do show a limit of the procedural setup: long diagnostic commands
were moved into the background by the CLI. Several agents stopped or waited for
them. PHMSA r1 used temporary copies of its own code under `/tmp`. CAA r2 issued a
kill command matching the shared dataset environment, broader than its own run;
the captured process list shows its own replay process, but is not an exhaustive
record of every process that could have matched. No selected artifact change or
holdout read is established by that event. Do not call this perfect procedural
compliance or fully isolated execution.

No inspected request/result establishes a prohibited holdout read. This is a
bounded negative finding. Diagnostics outside the fixed evaluator were not part
of the CPU budget matched by random search; the manuscript's comparison already
states that restriction. Neither code screening nor absence of an access flag
proves that all exploratory work complied.

## Follow-up required

Append the final four recovered solutions and their probe/trace results. Preserve
these findings even if later runs add a different issue. Report the final scope
in the paper in a few sentences; do not move this request-level inventory into
the manuscript.
