# Consumer study results

Generated 2026-11-13T09:43:32.168721+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- fjc-civil-trial-36m--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- fjc-civil-trial-36m--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- fjc-civil-trial-36m--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- fjc-civil-trial-36m--ordinary: validation AUC 0.737844; holdout AUC 0.710631.
- fjc-civil-trial-36m--r1: validation AUC 0.769171; holdout AUC 0.747690.
- fjc-civil-trial-36m--r1--random: validation AUC 0.743187; holdout AUC 0.722939.
- fjc-civil-trial-36m--r2: validation AUC 0.768517; holdout AUC 0.746069.
- fjc-civil-trial-36m--r2--random: validation AUC 0.746293; holdout AUC 0.728787.
- fjc-civil-trial-36m--r3: validation AUC 0.768109; holdout AUC 0.749459.
- fjc-civil-trial-36m--r3--random: validation AUC 0.753468; holdout AUC 0.723860.
- fjc-civil-trial-36m--released: validation AUC 0.734586; holdout AUC 0.703010.

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
