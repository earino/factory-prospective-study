# Consumer study results

Generated 2026-11-15T21:52:25.042307+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- sdwis-lcr-lead-action-level-next-period--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- sdwis-lcr-lead-action-level-next-period--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- sdwis-lcr-lead-action-level-next-period--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- sdwis-lcr-lead-action-level-next-period--ordinary: validation AUC 0.795113; holdout AUC 0.759547.
- sdwis-lcr-lead-action-level-next-period--r1: validation AUC 0.812465; holdout AUC 0.775135.
- sdwis-lcr-lead-action-level-next-period--r1--random: validation AUC 0.805419; holdout AUC 0.775284.
- sdwis-lcr-lead-action-level-next-period--r2: validation AUC 0.812416; holdout AUC 0.773770.
- sdwis-lcr-lead-action-level-next-period--r2--random: validation AUC 0.809361; holdout AUC 0.767572.
- sdwis-lcr-lead-action-level-next-period--r3: validation AUC 0.809659; holdout AUC 0.766062.
- sdwis-lcr-lead-action-level-next-period--r3--random: validation AUC 0.809081; holdout AUC 0.776533.
- sdwis-lcr-lead-action-level-next-period--released: validation AUC 0.799826; holdout AUC 0.769738.

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
