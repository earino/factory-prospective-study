# Experiment progress

## 20 November 2026

- Verified the original builder and descriptor against the frozen public manifest.
- Confirmed the original packet omitted the disputed selection declaration while
  including the builder, qualification summary, and 17 passing source checks.
- Prepared and hashed two cases, six prompts, a 30-review randomized schedule,
  scoring protocol, and isolated harness.
- Verified local model access through Ollama Cloud and web extraction through
  keyless Firecrawl. No Scout coordination, worker launch, or budget transfer was
  needed. Historical-runtime differences are explicit in the protocol.
- Completed three infrastructure smoke attempts. Two exposed an extraction
  configuration issue; one also exposed a database serialization error. Both
  harness issues were fixed before experimental execution. The third smoke passed.
- Launched the 30-review batch with two concurrent fresh Hermes sessions. Process
  output is retained in the execution session; run folders have process handles,
  exact requests, streaming responses, and final status when finished.
- Protocol/input commit: `8c06a5bc07c640dbe2d0a83d891058e42ac06ba6`.
  Exact-commit CI run `44785371938` passed.

## Completed results

- All 30 scheduled sessions finished, 17:37:46–18:23:42 UTC. No replacement runs,
  process failures, or timeouts. One final response contains malformed JSON; its
  readable decision is reported separately from valid structured decisions.
- Read and scored all 30 responses under shuffled IDs. Frozen initial assessment
  hash was saved before joining assignments. All original-case reviews accepted;
  neither complete-packet nor explicit-comparison condition detected the target
  contradiction (0/5 each). No comparison-case target false allegation occurred.
- Wire/session usage reconciles exactly. The review batch used 83 substantive
  calls plus 30 title calls. No worker resources or factory budget changes.
- Indexed all 83 tool results; no study/audit retrieval identified in requested
  URLs, returned repository links, or the recorded text screen. No runs excluded.
- `verify.py --complete` and `check_capture.py` pass: frozen inputs and submitted
  artifacts unchanged, 30 unique sessions, exact prompts/final responses, and 183
  lossless wire archives. Outcome aggregates retain the malformed-response count.
- [FINDINGS.md](FINDINGS.md) records the negative intervention result, alternative
  explanations, limits, and recommendation. The submitted paper stays unchanged.

## Final verification

- Exported a clean Git tree containing the exact staged files. No uncompressed
  response bodies or private Hermes configuration were present. Restored only the
  ignored `main.pdf` alias from the byte-identical tracked `paper.pdf`.
- All four offline evidence commands passed. Their six generated reports matched
  the working records byte for byte. Study self-tests (20) and controller tests
  (8) passed. See `results/verification-summary.json` for the tested tree.
- The actual inference credential was absent from all inspected experiment files,
  including decompressed response bodies. No authentication headers were captured.
- All plan deliverables are present. No further inference or production changes
  are needed. The final pushed commit's CI result is attached to that commit on
  GitHub and checked before reporting completion to Eduardo.
