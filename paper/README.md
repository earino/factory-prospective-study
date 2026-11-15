# Dataset Factory paper draft

The revised full draft is [the seven-page PDF](output/paper.pdf).
The draft includes all 12 cohort publications and 29 scored consumer models from
ten datasets, including all three quota-recovery evaluations completed by 20:08 UTC
on 15 November. Nine datasets have three models; Seattle has two and one blocked
attempt. Drinking-water evaluation is running; utility-reliability access failures
remain. Production costs still use the 64.93-hour export ending at 14:24 UTC that
day and its 11-publication denominator.

The accepted-review revision is complete, with three full-paper review passes
recorded in [REVISION-REVIEW.md](REVISION-REVIEW.md). The paper separates operation,
independent use, and source validity while retaining the integrated factory as its
contribution. Cost is a bounded operating-window ratio, not total construction cost.

The current interpretation centers the factory's datasets. Untuned XGBoost is the
primary performance comparison for modeling headroom; tuned random search is a
secondary control for added agent benefit. Both appear side by side in the main
figure. Source-quality findings remain separate. The agreed reasoning is saved in
[PAPER-DIRECTION.md](PAPER-DIRECTION.md#use-independent-consumption-to-assess-output-value).

This remains an interim author-review draft. Its 20 references support the
methods, production reliability, artifact evaluation, and human-work discussion.

- [LaTeX manuscript](draft/main.tex)
- [Portable LaTeX source bundle](output/paper-source.zip)
- [Evidence and verification record](SIGNOFF.md)
- [Current editorial direction](PAPER-DIRECTION.md)
- [Literature corrections](materials/VERIFIED-LITERATURE-NOTES.md)

Rebuild the PDF from this directory's parent with `sh paper/build.sh`.
It requires pdfLaTeX and BibTeX. The source bundle includes the IEEE class/style,
bibliography, generated table, vector figures, and a standalone build script.

Tables and figures come from the captured compact inputs, not current mutable
study files. To regenerate them, install matplotlib 3.10.8 in a separate Python
environment and run `python paper/analysis/render_figures.py` before the build.
`capture_draft.py` preserves the first snapshot. `capture_update.py` preserves
`analysis/update-inputs-2026-11-15.json`, which selects the completed wildlife-strike
recovery without replacing original failures. The additive `analysis/evening-inputs-2026-11-15.json` adds Seattle and railway
recoveries. All three snapshots feed the renderer.
The original worker qualification report was checked against the complete saved
wildlife-strike splits; the receipt is in `analysis/update-2026-11-15/`.

To check the paper aggregates against the retained snapshots, run
`python3 paper/analysis/verify_revision.py` from the repository root.

Before final submission, update the observation cutoff, finish review of the
remaining consumer evidence, integrate completed recovery runs without choosing
between original and retry scores, and complete author prose review. The draft
already states the concrete unresolved cases. It does not claim their resolution.

The Seattle and railway worker reports were also checked against the complete
saved study artifacts. `analysis/evening-2026-11-15/` retains those receipts and
scripts. The Seattle probes were rerun in a separate view of its two already-frozen
models, preserving the original missing-model errors and blocked attempt.
