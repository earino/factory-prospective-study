# Selected-code and conduct review

Current scope: all 36 selected solutions. The initial review and the two recovery
additions below preserve the order of inspection. All recovery postchecks are complete.

## Initial 32-solution scope

Codex inspected the fitting and prediction preparation functions of the 32 frozen
solutions listed in `selected-code-inventory.json`, plus their label-statistic
helpers and active settings where conditional behavior mattered. The review
covered supplied inputs, fitted preprocessing state, target encoding, training
subsets/augmentation, and data access. This is a bounded code and trace review,
not a security audit or a line-by-line review of every exploratory program.
This initial scope included Seattle r2/r3. The later Seattle r1 and three utility
solutions are documented below.

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

## Recovery additions

The four recovered solutions and their probe/trace results follow. The final
review scope belongs in the paper; request-level details remain in this record.

## Seattle r1 recovery — 15 November, 23:19 UTC freeze

The new selected module (`73a90309…1259d`) was inspected in full. It builds
row-local covariate transforms, fixed geographic region flags, and categories
learned from training covariates. Labels enter classifier fitting only. There is
no target encoder or file/network access in the selected module. Protected inputs
are unchanged. The existing scanner found 165 unique Bash requests over 20 CLI
continuations, no original access flags, and two access-reference matches. The
first reads the run's published contract, baseline code and public training rows;
the second edits and tests its own scratch code. Their recorded outputs match
those actions. No prohibited holdout read is established. Post-scoring probes
remain pending; this addition does not claim those checks have passed.

The reviewed selected-code count is now 33. Only the three utility recovery
solutions remain to be added. The earlier 32-solution observations remain intact.

Seattle postchecks completed at 23:40 UTC: 25 sampled validation rows passed
batch/order checks with no external preparation events; both own-label tests
changed zero feature cells. The three-run analysis combines the fresh r1 with
unchanged r2/r3 and retains the old blocked r1 separately. Fixed baseline
predictions agree byte-for-byte after decompression across the two executions.
A transient Git HTTP 408 was resolved by pushing the same frozen commit and
resuming scoring; freeze manifests remained unchanged.


## Utility recovery — 16 November, 01:15 UTC freeze

All three selected modules were inspected in full and matched the recorded
SHA-256 digests. They use 10, 8 and 7 row-local features, respectively; labels
enter classifier fitting only. Their imports are numpy, pandas and xgboost.
No selected module reads files, uses a network, identifies utilities, or computes
features from other scoring rows. Protected-file checks report no changes.

The sealed scanner covers 655 unique tool requests over 70 CLI invocations.
All ten attention requests were inspected with recorded results. The three
original flags are r1 writes to its own report, including a note containing the
published holdout path; none opens holdout data. Other attention matches concern
published metadata/public training rows, own notes or code, and the CLI's own
cached diagnostic output. Original scanner files are retained under
`evidence/reviews/eia861-reliability-deterioration-retry-1/post/`; the manually
collected result excerpts and receipt are in `utility-recovery-conduct/`.

Targeted follow-up also inspected broad process listing and local commit-reset
requests. A process listing exposed shared-environment command lines. Run r2
stopped its diagnostic with `pkill -f "lab/s6.py"`; that relative pattern is not
an enforced per-run boundary, although the result reports the diagnostic stopped.
Runs r1 and r3 reset local commits to remove study-owned files from staging.
Protected-file checks show no content change. These events reinforce the stated
procedural isolation limit; they are not evidence of a holdout read. This review
does not certify every exploratory program or every process that might match.

All four posttools completed. Each selected artifact passed batch/single-row and
reverse-order checks on 25 validation rows, with no external preparation events.
Changing either tested training label changed zero cells in that row's features.
The ordinary/random controls use the same 12 permitted raw predictors. Bootstrap
grouping was declared before scoring: 734 utilities over 2,062 holdout rows.
All three paired intervals are positive against both controls. Utility clustering
does not address every common year/weather shock.

The selected-code review now covers all 36 final solutions. Earlier original
failures, probe errors and their documented resolutions remain preserved. No
inspected request/result establishes prohibited holdout access; this bounded
negative finding is not a universal compliance guarantee.
