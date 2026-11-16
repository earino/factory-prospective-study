# Evidence guide

The five-page paper reports a fixed production window and twelve consumer tasks.
The [frozen selection](paper/analysis/final-inputs-2026-11-16.json) identifies the
records used in the reported results. Retried and unsuccessful attempts remain
available. Files on `main` include compact results and reviews; the pinned consumer
commits below contain the complete experiment archives and frozen models.

## Inspect the SBIR acceptance failure

Start with the [acceptance analysis](paper/analysis/final-2026-11-16/SBIR-ACCEPTANCE-AUDIT.md).
The original evidence is directly available:

- [Published population/selection declaration](paper/analysis/final-2026-11-16/sbir-acceptance/published-construction.json).
- [Builder returned by construction](paper/analysis/final-2026-11-16/sbir-acceptance/build-3/response.json), including `build_py`.
- [Complete prompt sent to the semantic reviewer](paper/analysis/final-2026-11-16/sbir-acceptance/evaluate-1/prompt.txt).
- [Original acceptance response](paper/analysis/final-2026-11-16/sbir-acceptance/evaluate-1/response.json)
  and [transcript](paper/analysis/final-2026-11-16/sbir-acceptance/evaluate-1/transcript.json).
- [Separate pre-scoring review](evidence/reviews/sbir-phase1-to-phase2-conversion/PRE-REVIEW.md).
- [Retrieved-file hashes](paper/analysis/final-2026-11-16/sbir-acceptance/retrieval.json)
  and [identity/claim verification code](paper/analysis/final-2026-11-16/verify_sbir_acceptance.py).

The record establishes what the reviewer received and accepted. It does not
establish whether a complete declaration would have changed that decision.

## Follow the other results

- Production window, stages and costs: [cost record](evidence/costs/2026-11-16/),
  [frozen analysis inputs](paper/analysis/final-inputs-2026-11-16.json), and
  [stage-cost calculation](paper-agent27-short/scripts/draw_stage_costs.py).
- Table II: [complete attempt accounting](paper-agent27-short/analysis/attempt-accounting.json),
  [reproducible calculation](paper-agent27-short/scripts/prepare_attempt_accounting.py),
  and [pinned controller/history excerpts](paper-agent27-short/analysis/operational-source-excerpts.json).
- Table I: [release records](paper-agent27-short/analysis/release-records.json),
  [disclosure comparisons](paper-agent27-short/analysis/disclosure-review.json),
  and [pinned release documents](paper-agent27-short/analysis/disclosure-documents/).
- Figure 3: [paired results](paper-agent27-short/analysis/consumer-results.json),
  [interpretation and source map](paper-agent27-short/analysis/CONSUMER-RESULTS.md),
  and [figure script](paper-agent27-short/scripts/draw_consumer_results.py).
- Model identifiers and runtime: [recorded routes and consumer model names](paper-agent27-short/analysis/model-identifiers.json).
- Verification: [short-paper receipt](paper-agent27-short/SIGNOFF.md) and
  [record checks](paper-agent27-short/analysis/record-checks.json).

## Public access

The repository is public. [Anonymous release checks](paper-agent27-short/analysis/public-evidence-verification.json)
cover the paper, SBIR evidence, all 17 pinned consumer links and integrity manifests,
and checksum-verified downloads of one consumer model and one archive part.

## Full consumer archives

Each link uses the commit retained in its outcome record, rather than a moving
branch. Within an evidence directory, `frozen/` contains model files and freeze
manifests; `attempts/` contains state and split archive files. An `archive.json`
records the ordered parts, checksums, and contents. Concatenate its parts in the
listed order to reconstruct the gzip tar archive; inspect it before extraction.
Archives contain trial code, notes, sanitized CLI transcripts, and local Git
history. The scoring code and pinned release identities are in each study commit.

The [release check](paper-agent27-short/analysis/evidence-release-check.json)
verified 1,957 manifest-listed files against their local SHA-256 hashes and remote
Git blobs across 17 retained consumer commits. This includes retries, not seventeen
different tasks. Seattle's reported results use the documented
[composite selection](paper/analysis/final-2026-11-16/seattle-composite/summary.json).

- [caa-fce-hpv-escalation](https://github.com/earino/factory-prospective-study/tree/1f4600d942d308db066c465442b125dc6584de55/evidence) — `1f4600d942d3`. [Outcome](evidence/outcomes/caa-fce-hpv-escalation.json).
- [eia861-reliability-deterioration-retry-1](https://github.com/earino/factory-prospective-study/tree/6d6926dcb712fbdbaf5c54b3f45a1eabae783d38/evidence) — `6d6926dcb712`. [Outcome](evidence/outcomes/eia861-reliability-deterioration-retry-1.json).
- [eia861-reliability-deterioration](https://github.com/earino/factory-prospective-study/tree/19735c640ca0e7330e5113f4cd5a19fbc1f7069f/evidence) — `19735c640ca0`. [Outcome](evidence/outcomes/eia861-reliability-deterioration.json).
- [faa-wildlife-strike-substantial-damage-retry-1](https://github.com/earino/factory-prospective-study/tree/ba071829395194aed1eeb6567534ccda25cc3976/evidence) — `ba0718293951`. [Outcome](evidence/outcomes/faa-wildlife-strike-substantial-damage-retry-1.json).
- [faa-wildlife-strike-substantial-damage](https://github.com/earino/factory-prospective-study/tree/49de5907b0fcb37161020cb606ddaf510ef5f5c3/evidence) — `49de5907b0fc`. [Outcome](evidence/outcomes/faa-wildlife-strike-substantial-damage.json).
- [fda-510k-five-year-recall](https://github.com/earino/factory-prospective-study/tree/f5bf774a9a6f49d51786a84738eda794a1c27494/evidence) — `f5bf774a9a6f`. [Outcome](evidence/outcomes/fda-510k-five-year-recall.json).
- [fjc-civil-trial-36m](https://github.com/earino/factory-prospective-study/tree/1dcb191cb5eb2c75fef6b5e107c427de897641b2/evidence) — `1dcb191cb5eb`. [Outcome](evidence/outcomes/fjc-civil-trial-36m.json).
- [fra-form54-hazmat-release-retry-1](https://github.com/earino/factory-prospective-study/tree/16e5ba920f95ccda9516f5b3e5d30d1810e7baf4/evidence) — `16e5ba920f95`. [Outcome](evidence/outcomes/fra-form54-hazmat-release-retry-1.json).
- [fra-form54-hazmat-release](https://github.com/earino/factory-prospective-study/tree/498e4818e18fa3ac55b9e24f7b7e88127b233288/evidence) — `498e4818e18f`. [Outcome](evidence/outcomes/fra-form54-hazmat-release.json).
- [phmsa-pipeline-penalty-reduction](https://github.com/earino/factory-prospective-study/tree/6cc1f4f10fc650333eb54a737994129ee69359ba/evidence) — `6cc1f4f10fc6`. [Outcome](evidence/outcomes/phmsa-pipeline-penalty-reduction.json).
- [sbir-phase1-to-phase2-conversion](https://github.com/earino/factory-prospective-study/tree/943f7482d687e6688fc0ae7ba12377a20d73b2de/evidence) — `943f7482d687`. [Outcome](evidence/outcomes/sbir-phase1-to-phase2-conversion.json).
- [sdwis-lcr-lead-action-level-next-period](https://github.com/earino/factory-prospective-study/tree/36fd086ecba894cd157f862536a412d6cdfb27c5/evidence) — `36fd086ecba8`. [Outcome](evidence/outcomes/sdwis-lcr-lead-action-level-next-period.json).
- [seattle-building-permit-completion-retry-1](https://github.com/earino/factory-prospective-study/tree/b6e207596570efb9bb80d3aca208fa54b09021ed/evidence) — `b6e207596570`. [Outcome](evidence/outcomes/seattle-building-permit-completion-retry-1.json).
- [seattle-building-permit-completion-retry-2](https://github.com/earino/factory-prospective-study/tree/d63aa6895c4e36d08ba79931b39ce10ca4de3a22/evidence) — `d63aa6895c4e`. [Outcome](evidence/outcomes/seattle-building-permit-completion-retry-2.json).
- [seattle-building-permit-completion](https://github.com/earino/factory-prospective-study/tree/2ff2d43b1c3da5c3111cb6b11105e0def1454165/evidence) — `2ff2d43b1c3d`. [Outcome](evidence/outcomes/seattle-building-permit-completion.json).
- [t100-new-route-survival](https://github.com/earino/factory-prospective-study/tree/82a6bc9d5f72775191e29231e7cb6c66c19b34b5/evidence) — `82a6bc9d5f72`. [Outcome](evidence/outcomes/t100-new-route-survival.json).
- [wser-effluent-exceedance](https://github.com/earino/factory-prospective-study/tree/5e12c495e62fbbf56b133fe340923e54885020d8/evidence) — `5e12c495e62f`. [Outcome](evidence/outcomes/wser-effluent-exceedance.json).
