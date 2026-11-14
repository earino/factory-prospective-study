# Consumer study results

Generated 2026-11-14T12:43:29.086255+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- t100-new-route-survival--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- t100-new-route-survival--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- t100-new-route-survival--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- t100-new-route-survival--ordinary: validation AUC 0.627247; holdout AUC 0.601343.
- t100-new-route-survival--r1: validation AUC 0.685543; holdout AUC 0.600657.
- t100-new-route-survival--r1--random: validation AUC 0.647841; holdout AUC 0.617652.
- t100-new-route-survival--r2: validation AUC 0.701482; holdout AUC 0.595948.
- t100-new-route-survival--r2--random: validation AUC 0.642736; holdout AUC 0.592860.
- t100-new-route-survival--r3: validation AUC 0.705535; holdout AUC 0.610162.
- t100-new-route-survival--r3--random: validation AUC 0.641397; holdout AUC 0.587830.
- t100-new-route-survival--released: validation AUC 0.624552; holdout AUC 0.595969.

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
