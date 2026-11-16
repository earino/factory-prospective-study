# Consumer performance in the short paper

The author requested evidence about predictive performance in addition to artifact
use and source-review findings. Figure 3 uses the existing final selection of all
twelve evaluated releases and all three frozen consumer models per release.
It introduces no new model fits, trials, cohort selection, or holdout scoring.

`consumer-results.json` preserves exact scores, summary-file hashes, qualification
acceptance receipts, and derived medians/ranges. The generator checks the retained
summary files against the frozen long-paper snapshot. Seattle uses the existing
composite of recovered r1 and unchanged r2/r3; utility reliability uses its recorded
recovery selection. All twelve original full-artifact acceptance receipts pass.

The comparator is the consumer study's fixed untuned XGBoost model, not the
factory's shipped baseline or tuned random search. The fixed settings are 100
trees, depth 6, learning rate 0.1, with native categorical handling, as recorded in
`run_study.py`'s starter. The separate agents can change features, preprocessing,
and model parameters within the task contract. The comparison does not isolate
the contribution of feature engineering or establish superiority over tuning.

Consumer median AUC spans 0.600657 to 0.912823. All three models exceed the fixed
reference on eleven tasks; route survival has two lower and one higher score.
Among those eleven tasks, median gains span 0.008467 to 0.072277 AUC. The plot
sorts by consumer median. Its bars span observed runs, not confidence intervals;
no statistical-significance claim is made. Existing grouped-bootstrap analyses
remain in the preserved longer-paper evidence. Source timing, selection, and
scoring-access limitations remain in the short-paper table and case analysis.

Two references were restored from the existing bibliography and checked against
their publisher pages on 16 November 2026:

- Cawley and Talbot, JMLR 11 (2010), 2079–2107:
  https://www.jmlr.org/papers/v11/cawley10a.html
  Supports separating model selection from final performance evaluation.
- Huang et al., MLAgentBench, ICML/PMLR 235 (2024), 20271–20309:
  https://proceedings.mlr.press/v235/huang24y.html
  Positions agent-based ML experimentation; this paper uses consumers to describe
  the factory's outputs rather than rank consumer-agent systems.

The manuscript stays within five pages. The longer-paper files retain all their
original hashes. Figure generation and the revised record checks passed in a
separate checkout; ignored historical paper renders were supplied only for the
existing preservation checks. The portable LaTeX archive builds separately with
matching extracted PDF text.
