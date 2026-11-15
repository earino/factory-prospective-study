# Dataset Factory paper draft

The first full draft is [the seven-page PDF](output/paper.pdf).
Its scope is the 64.93-hour production snapshot ending 15 November at 14:24 UTC,
with the original consumer outcomes available at that cutoff. It is an interim
author-review draft, not the final submission. Recovery runs remain separate.

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
`capture_draft.py` refuses to overwrite the first snapshot. A final update should
preserve this snapshot and explicitly select final/recovery evidence.

Before final submission, update the observation cutoff, finish review of the
remaining consumer evidence, integrate completed recovery runs without choosing
between original and retry scores, and complete author prose review. The draft
already states the concrete unresolved cases. It does not claim their resolution.
