# SBIR semantic review experiment

Status: execution in progress. No result is claimed yet.

This isolated experiment tests the review-packet and explicit-comparison changes
specified in [PROTOCOL.md](PROTOCOL.md). The historical release and submitted
manuscript are unchanged. The two cases and three conditions have five scheduled
reviews each. Smoke tests are separate.

## Files

- `inputs/`: frozen historical evidence, two cases, six prompts, diffs, and hashes.
- `freeze.json`: protocol, schedule, and harness hashes fixed before execution.
- `schedule.json`: randomized run order and condition assignments.
- `runtime/`: actual runtime identity, configuration, and exposed tool definitions.
- `runs/`: exact prompts, HTTP bodies without headers, session records, and status.
- `smoke/`: infrastructure-only smoke tests, including failures.
- `verify.py`: offline identity and capture checks.

## Reproduction

The runner expects Hermes at `~/.hermes/hermes-agent`, with its Python environment
at `venv/bin/python`. The observed runtime revision is in `runtime/preflight.json`.
It reads only `OLLAMA_API_KEY` from `~/.hermes/.env`; this credential is not included
here. Web tools use keyless Firecrawl. No factory credentials or workers are used.

In a separate copy, preserve the existing results and choose a new output root
before a new experiment. `run_reviews.py` refuses to overwrite existing run
folders and will not replace a completed failure. The recorded run is checked with:

```sh
python3 experiments/sbir-semantic-review/verify.py --complete
```

The original execution commands were:

```sh
python3 experiments/sbir-semantic-review/run_reviews.py preflight
python3 experiments/sbir-semantic-review/run_reviews.py smoke
python3 experiments/sbir-semantic-review/run_reviews.py run
```

Input preparation is in `prepare.py`; it refuses to overwrite the input manifest.
Model responses need not reproduce exactly. The retained HTTP requests and
responses, rubric, excerpts, and aggregates permit inspection of the actual run.
