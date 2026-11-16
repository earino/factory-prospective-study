# arXiv upload package

Upload `dataset-factory-arxiv.zip` as the source archive. Select `main.tex` as
the main file and PDFLaTeX as the compiler if asked. The ZIP contains only the
LaTeX source, compiled bibliography, bibliography sources/style, IEEE class,
three figures, and two generated table fragments. Do not upload `preview.pdf`
as a separate source file; it is the local reference for checking arXiv's output.

The preprint has the same five-page body as the submitted conference version.
Its only addition is the IEEE submission notice in the first-page footer.
The submitted conference files are unchanged.

Suggested metadata:
- Primary category: Computer Science / Software Engineering (`cs.SE`).
- Title: Operating an Agent-Driven Dataset Factory: Discovery, Construction, and Public Release
- Authors, in order: Eduardo Ariño de la Rubia; Szilard Pafka.
- Comments: `5 pages, 3 figures. Code and evidence: https://github.com/earino/factory-prospective-study`
- Journal reference and DOI: leave blank; no acceptance/publication is claimed.

Use the abstract from the manuscript. Copyright notices belong in the article,
not in arXiv's Comments field. This package includes the notice in the article.
The user completes the submission agreement, license selection and final submission.

Validation is in `verification.json`. Three PDFLaTeX passes from the extracted
archive succeeded using the included `main.bbl`, without BibTeX or shell escape.
The body text matches the submitted PDF after removing the notice; pages 2–5
are pixel-identical. Page 1 was inspected for footer placement and all fonts
are embedded. arXiv's own compiled preview still needs to be checked after upload.

Rebuild this package with `python3 paper-agent27-short/scripts/package_arxiv.py`.

Policy sources:
- https://info.arxiv.org/help/submit_tex.html
- https://info.arxiv.org/help/prep.html
- https://conferences.ieeeauthorcenter.ieee.org/get-published/post-your-paper/
