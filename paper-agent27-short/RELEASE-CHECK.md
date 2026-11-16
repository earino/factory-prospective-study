# Submission and evidence release check

Prepared 16 November 2026. The manuscript and evidence index are ready for the
submission release; the repository remains private and no submission was made.

## Completed preparation

- Five-page IEEE manuscript, including references and AI-assistance disclosure.
- Explicit design rationale and Hermes runtime identification in Section II.
- *Identical Runs, Different Results* cited in the repeated-run method.
- Seventeen cited works checked against primary records. Access exceptions and
  the official venue requirements are recorded in [reference-check.json](analysis/reference-check.json).
- Model names checked against saved production usage and consumer invocation
  records: [model-identifiers.json](analysis/model-identifiers.json). Provider
  aliases are recorded as reported, without claiming model-weight attestation.
- Main README points to the manuscript and [evidence guide](../EVIDENCE.md).
  The SBIR prompt, response, builder, declaration and downstream review are direct links.
- All 1,957 files listed in retained consumer integrity manifests match both
  local SHA-256 checks and Git blob identities in 17 recorded remote commits:
  [evidence-release-check.json](analysis/evidence-release-check.json). This checks
  evidence availability through authenticated access, not anonymous publication.
- The portable LaTeX package and the separate-checkout record verification are
  recorded in [QA.json](output/QA.json). The longer paper remains unchanged.

## At submission

1. Make `earino/factory-prospective-study` public under the agreed release plan.
2. From an unauthenticated client, open the README, paper, SBIR packet, and pinned
   consumer evidence links. Download a frozen-model file and one archive part and
   compare their recorded hashes. These checks cannot pass while the repo is private.
3. Submit the final five-page PDF through the official workshop submission site.

The [official call](https://conf.researchr.org/home/icse-2027/agent-2027) specifies
five pages including references, single-anonymous review, and 20 November 2026 AoE.
Submission portal: https://icse2027-agent.hotcrp.com/ .
