# Consumer study results

Generated 2026-11-15T18:28:56.682763+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 2; failed/blocked: 1.

Compliance triage (separate from scores):

- seattle-building-permit-completion--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- seattle-building-permit-completion--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- seattle-building-permit-completion--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- seattle-building-permit-completion--ordinary: validation AUC 0.619376; holdout AUC 0.617937.
- seattle-building-permit-completion--r2: validation AUC 0.656601; holdout AUC 0.647392.
- seattle-building-permit-completion--r2--random: validation AUC 0.644286; holdout AUC 0.634720.
- seattle-building-permit-completion--r3: validation AUC 0.656591; holdout AUC 0.655183.
- seattle-building-permit-completion--r3--random: validation AUC 0.641562; holdout AUC 0.632832.
- seattle-building-permit-completion--released: validation AUC 0.626825; holdout AUC 0.619947.

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
