# Dataset Factory: deployment study and evidence

This repository accompanies **Operating an Agent-Driven Dataset Factory: Discovery,
Construction, and Public Release**, a short experience paper submitted to AGENT 2027. It contains
an 81.53-hour production record with 14 public releases and separate prediction
experiments on the first 12 releases. The repository is public; the evidence guide links the retained records and archives.

- [Read the five-page paper](paper-agent27-short/output/paper.pdf).
- [Download the portable LaTeX source](paper-agent27-short/output/paper-source.zip).
- [Find the evidence for each result](EVIDENCE.md), including the original SBIR
  acceptance packet, consumer programs, transcripts, and frozen models.
- [Check release preparation](paper-agent27-short/RELEASE-CHECK.md).

The public [factory implementation](https://github.com/earino/dataset-factory) is
separate from this study. Production decisions and consumer experiments are
separate records. A completed experiment establishes execution under the stated
predictor contract; it does not by itself establish task validity.

## Rebuild the paper

From a checkout, with `pdflatex` and `bibtex` installed:

```sh
sh paper-agent27-short/build.sh
```

The portable source archive builds without the study data or Python. The source
figures and their numeric inputs are in `paper-agent27-short/scripts/` and
`paper-agent27-short/analysis/`. The [verification receipt](paper-agent27-short/SIGNOFF.md)
records the build, figure, source-identity, and evidence checks.

## Reproduce the study

[PROTOCOL.md](PROTOCOL.md) and [protocol.json](protocol.json) define the experiments;
[agent.md](agent.md) and `run_study.py` define the consumer runner. The
[frozen input snapshot](paper/analysis/final-inputs-2026-11-16.json) selects the
reported records, including retries. [EVIDENCE.md](EVIDENCE.md) links to each
consumer evidence commit, which carries the full experiment files beyond the
compact summaries on `main`.

The longer manuscript and analyses remain in `paper/`; the five-page submission
is in `paper-agent27-short/`. [Monitor operations](MONITOR-OPERATIONS.md) preserves
the collection schedule and local operation instructions. Collection and analysis
commands can launch work; building the paper does not.
