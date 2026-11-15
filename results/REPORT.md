# Consumer study results

Generated 2026-11-15T01:56:15.097152+00:00

Measured records are in summary.json and scores.csv. Failures remain in the denominator.

Requested model: `claude-fable-5-2`. Reported models: claude-fable-5-2.

Registered attempts: 3; frozen: 3; failed/blocked: 0.

Compliance triage (separate from scores):

- caa-fce-hpv-escalation--r1: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- caa-fce-hpv-escalation--r2: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.
- caa-fce-hpv-escalation--r3: no_automatic_access_flag; forbidden asset copies 0; tool-access flags 0. Semantic compliance requires review.

Scores (including flagged attempts; do not treat all as compliant results):

- caa-fce-hpv-escalation--ordinary: validation AUC 0.852449; holdout AUC 0.851909.
- caa-fce-hpv-escalation--r1: validation AUC 0.867686; holdout AUC 0.868417.
- caa-fce-hpv-escalation--r1--random: validation AUC 0.853196; holdout AUC 0.856038.
- caa-fce-hpv-escalation--r2: validation AUC 0.864669; holdout AUC 0.871459.
- caa-fce-hpv-escalation--r2--random: validation AUC 0.858361; holdout AUC 0.862754.
- caa-fce-hpv-escalation--r3: validation AUC 0.868768; holdout AUC 0.860209.
- caa-fce-hpv-escalation--r3--random: validation AUC 0.855139; holdout AUC 0.852253.
- caa-fce-hpv-escalation--released: validation AUC 0.856434; holdout AUC 0.855761.

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
