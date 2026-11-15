# Consumer study results

Generated 2026-11-15T03:52:34.053843+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- wser-effluent-exceedance--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- wser-effluent-exceedance--r2: requires_review; forbidden asset copies 0; tool-access flags 1. Semantic compliance requires review.
- wser-effluent-exceedance--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- wser-effluent-exceedance--ordinary: validation AUC 0.896045; holdout AUC 0.892794.
- wser-effluent-exceedance--r1: validation AUC 0.909352; holdout AUC 0.901261.
- wser-effluent-exceedance--r1--random: validation AUC 0.907182; holdout AUC 0.900215.
- wser-effluent-exceedance--r2: validation AUC 0.907783; holdout AUC 0.901260.
- wser-effluent-exceedance--r2--random: validation AUC 0.907059; holdout AUC 0.899236.
- wser-effluent-exceedance--r3: validation AUC 0.908506; holdout AUC 0.901548.
- wser-effluent-exceedance--r3--random: validation AUC 0.907495; holdout AUC 0.901166.
- wser-effluent-exceedance--released: validation AUC 0.898259; holdout AUC 0.895930.

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
