# Consumer study results

Generated 2026-11-15T20:07:39.767597+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- fra-form54-hazmat-release--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- fra-form54-hazmat-release--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- fra-form54-hazmat-release--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- fra-form54-hazmat-release--ordinary: validation AUC 0.669322; holdout AUC 0.731304.
- fra-form54-hazmat-release--r1: validation AUC 0.742984; holdout AUC 0.784087.
- fra-form54-hazmat-release--r1--random: validation AUC 0.710287; holdout AUC 0.751266.
- fra-form54-hazmat-release--r2: validation AUC 0.740494; holdout AUC 0.790175.
- fra-form54-hazmat-release--r2--random: validation AUC 0.702847; holdout AUC 0.750445.
- fra-form54-hazmat-release--r3: validation AUC 0.751952; holdout AUC 0.791063.
- fra-form54-hazmat-release--r3--random: validation AUC 0.700492; holdout AUC 0.747285.
- fra-form54-hazmat-release--released: validation AUC 0.685222; holdout AUC 0.744919.

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
