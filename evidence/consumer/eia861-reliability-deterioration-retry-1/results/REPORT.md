# Consumer study results

Generated 2026-11-16T01:20:33.734646+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- eia861-reliability-deterioration--r1: requires_review; forbidden asset copies 0; tool-access flags 3. Semantic compliance requires review.
- eia861-reliability-deterioration--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- eia861-reliability-deterioration--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- eia861-reliability-deterioration--ordinary: validation AUC 0.679016; holdout AUC 0.697510.
- eia861-reliability-deterioration--r1: validation AUC 0.732992; holdout AUC 0.736249.
- eia861-reliability-deterioration--r1--random: validation AUC 0.711179; holdout AUC 0.714071.
- eia861-reliability-deterioration--r2: validation AUC 0.733129; holdout AUC 0.739761.
- eia861-reliability-deterioration--r2--random: validation AUC 0.711116; holdout AUC 0.718515.
- eia861-reliability-deterioration--r3: validation AUC 0.731239; holdout AUC 0.739425.
- eia861-reliability-deterioration--r3--random: validation AUC 0.698429; holdout AUC 0.716242.
- eia861-reliability-deterioration--released: validation AUC 0.685944; holdout AUC 0.711227.

## Limits

- Five selected factory releases; three attempts are descriptive, not agent rankings.
- Pinned consumer scaffold and deterministic downloads are provided assistance.
- CLI-reported model IDs are not independent provider attestation.
- Public holdout isolation and semantic compliance are procedural, not enforced by an OS sandbox.
- CFPB holdout was used in earlier pilot work outside this study.
- Random search matches observed eligible primary-trial fitting CPU, not unlogged diagnostics or token work.
- Fresh Claude trajectories are nondeterministic; frozen artifact replay is reproducible.
- No factory-wide publication yield or spend is inferred from this consumer study.

No automatic claim of leakage freedom, novelty, significance or agent superiority is made.
Review the archived code and sanitized transcripts before using results in a paper.
