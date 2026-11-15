# Utility-reliability source-review follow-up

Codex checked the new pre-scoring review against the pinned builder, task
contract, and the study's actual engine. This is a bounded check before the three
consumer models finish. No holdout rows, scores, research instructions, or
production state were changed.

- **Predictor inputs:** the review's possible utility-ID/calendar exposure is an
  assumption about the released baseline trainer, not the study's consumer and
  control interface. The actual engine uses the explicit `quality.features` list
  after removing IDs, carry columns, outcome fields, and the target. All three
  consumer runs and the ordinary/random controls receive the same twelve allowed
  predictors. Utility ID, forecast year, and decision date are not among them.
  The separately reproduced released baseline is not the paper's untuned control.
  Confirm the post-run control-feature receipt when available.
- **Scoring access:** the engine calls the saved preparation function once per
  row, with a reset index. The review correctly identifies how later lag values
  could expose earlier outcomes under unrestricted batch access. That mechanism
  does not establish that our row-wise scored models used such information.
  Selected code and probes must still be reviewed after freezing.
- **Selection:** builder lines 1084–1101 require records in Y−3, Y−2, Y−1 and Y+1
  and a common reporting standard across all four. The structured eligibility
  statement describes only earlier filings plus an observed future outcome;
  the broader contract also discloses dropping utilities that switch standards
  or file multiple state rows. These details warrant a stable-filer interpretation.
  Do not describe every use of a future outcome record as undisclosed selection,
  or claim a score effect that has not been measured.
- **Timing:** the task explicitly declares current-snapshot retrospective use,
  assumed historical feature availability, and unverified training-label timing.
  Its chronological splits do not establish an as-of historical forecasting
  experiment. This is a claim limit, not a new reason to suppress the consumer
  results.
- **Uncertainty:** the pre-scoring reviewer selected utility ID for dependence
  grouping. The three holdout calendar years and possible shared regional shocks
  remain outside a one-way utility bootstrap. The final interpretation must keep
  intervals conditional on the declared grouping.

The paper can keep SBIR as its detailed acceptance-failure case. These utility
observations belong in the retained source review and the existing general
limits on historical claims and group-resampled uncertainty; they do not justify
adding a second lengthy failure narrative.
