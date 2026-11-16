# Dataset Factory paper

The completed seven-page manuscript is [paper.pdf](output/paper.pdf), with
[portable LaTeX source](output/paper-source.zip). It includes 22 references.
The paper has not been submitted, and the evidence repository remains private.

The observation window closed on 16 November 2026 at 07:00 UTC. It contains
14 public releases and 540 stage attempts over 81.53 hours. Estimated recurring
production cost is $38.23–$38.33, or $2.73–$2.74 per publication, with explicit
exclusions for development and labor. The independent consumer cohort is the
first twelve releases: 36 scored models, three per release. All 49 physical
research attempts remain recorded, including original failures and recoveries.

The paper separates production, consumer use and task validity. Untuned XGBoost
measures modeling headroom; tuned random search tests added agent benefit.
Figure 3 shows every available grouped comparison, ordered by median gain over
the untuned reference. The detailed SBIR acceptance reconstruction explains how
the population mismatch survived review, without claiming an untested cause.
Service maintenance is distinguished from manual dataset decisions.

- [Claim-to-evidence sign-off](SIGNOFF.md)
- [LaTeX manuscript](draft/main.tex)
- [Final cost evidence](../evidence/costs/2026-11-16/REPORT.md)
- [SBIR acceptance audit](analysis/final-2026-11-16/SBIR-ACCEPTANCE-AUDIT.md)
- [Selected-code and conduct review](analysis/final-2026-11-16/CODE-CONDUCT-REVIEW.md)
- [Qualification receipts for twelve exact artifacts](analysis/final-2026-11-16/qualification-coverage.json)
- [Verified literature notes](materials/VERIFIED-LITERATURE-NOTES.md)

## Rebuild and verify

From the repository root:

```sh
python3 paper/analysis/render_figures.py
sh paper/build.sh
python3 paper/analysis/verify_revision.py
python3 paper/analysis/verify_bundle.py
```

The renderer requires matplotlib 3.10.8; the build requires pdfLaTeX and BibTeX.
The portable source includes the IEEE class/style, bibliography, generated table,
vector figures and its own build script. No model fitting is needed to rebuild
this manuscript or verify its numerical tables.

Analysis reads immutable compact snapshots. The original, afternoon and evening
snapshots preserve earlier evidence. `consumer-complete-inputs-2026-11-16.json`
adds all consumer recoveries; `final-inputs-2026-11-16.json` adds the fixed closing
production export. The original scores, failed attempts and checker errors remain
available alongside explicit derived resolutions. Final costs use all fourteen
window publications; consumer analysis uses only the first twelve.

Frozen artifact replay is reproducible; a fresh language-model research trajectory
is not expected to be identical. The paper states the remaining source-timing,
population, grouping and procedural-isolation limits. Author approval and the
submission/publication steps remain with Eduardo.
