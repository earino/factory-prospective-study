# Consumer study results

Generated 2026-11-13T20:13:20.972879+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- phmsa-pipeline-penalty-reduction--r1: requires_review; forbidden asset copies 0; tool-access flags 1. Semantic compliance requires review.
- phmsa-pipeline-penalty-reduction--r2: requires_review; forbidden asset copies 0; tool-access flags 4. Semantic compliance requires review.
- phmsa-pipeline-penalty-reduction--r3: requires_review; forbidden asset copies 0; tool-access flags 2. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- phmsa-pipeline-penalty-reduction--ordinary: validation AUC 0.590756; holdout AUC 0.556968.
- phmsa-pipeline-penalty-reduction--r1: validation AUC 0.788235; holdout AUC 0.635217.
- phmsa-pipeline-penalty-reduction--r1--random: validation AUC 0.657983; holdout AUC 0.587853.
- phmsa-pipeline-penalty-reduction--r2: validation AUC 0.778571; holdout AUC 0.622411.
- phmsa-pipeline-penalty-reduction--r2--random: validation AUC 0.664846; holdout AUC 0.608757.
- phmsa-pipeline-penalty-reduction--r3: validation AUC 0.750280; holdout AUC 0.618362.
- phmsa-pipeline-penalty-reduction--r3--random: validation AUC 0.678571; holdout AUC 0.597081.
- phmsa-pipeline-penalty-reduction--released: validation AUC 0.602661; holdout AUC 0.561111.

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
