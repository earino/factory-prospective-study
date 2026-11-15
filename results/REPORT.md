# Consumer study results

Generated 2026-11-15T16:43:44.716211+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- faa-wildlife-strike-substantial-damage--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- faa-wildlife-strike-substantial-damage--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- faa-wildlife-strike-substantial-damage--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- faa-wildlife-strike-substantial-damage--ordinary: validation AUC 0.885059; holdout AUC 0.893779.
- faa-wildlife-strike-substantial-damage--r1: validation AUC 0.905409; holdout AUC 0.912823.
- faa-wildlife-strike-substantial-damage--r1--random: validation AUC 0.896039; holdout AUC 0.909133.
- faa-wildlife-strike-substantial-damage--r2: validation AUC 0.902683; holdout AUC 0.919553.
- faa-wildlife-strike-substantial-damage--r2--random: validation AUC 0.896185; holdout AUC 0.904875.
- faa-wildlife-strike-substantial-damage--r3: validation AUC 0.906888; holdout AUC 0.908116.
- faa-wildlife-strike-substantial-damage--r3--random: validation AUC 0.897842; holdout AUC 0.904242.
- faa-wildlife-strike-substantial-damage--released: validation AUC 0.889853; holdout AUC 0.893618.

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
