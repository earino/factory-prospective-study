# Consumer study results

Generated 2026-11-13T20:03:43.983186+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- phmsa-pipeline-penalty-reduction--r1: requires_review; forbidden asset copies 0; tool-access flags 1. Semantic compliance requires review.
- phmsa-pipeline-penalty-reduction--r2: not yet audited; forbidden asset copies unknown; tool-access flags unknown. Semantic compliance requires review.
- phmsa-pipeline-penalty-reduction--r3: requires_review; forbidden asset copies 0; tool-access flags 2. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- phmsa-pipeline-penalty-reduction--r1: validation AUC 0.788235; holdout AUC not scored.
- phmsa-pipeline-penalty-reduction--r2: validation AUC 0.778571; holdout AUC not scored.
- phmsa-pipeline-penalty-reduction--r3: validation AUC 0.750280; holdout AUC not scored.

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
