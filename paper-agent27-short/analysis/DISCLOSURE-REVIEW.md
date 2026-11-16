# Disclosure check against pinned releases

Scope: the twelve evaluated releases, their frozen README and construction descriptor, and only the findings selected for the short-paper table. This is a document comparison, not a new dataset-validity audit. All documents match the original pinned manifest hashes.

Five of six listed conditions have stated restrictions. Carrier-code exits are disclosed; apparent entries are not. For both history-feature tasks, `isolated_rows` explicitly states an access restriction but does not explain the cross-row exposure mechanism. The SBIR documents disclose some exclusions while asserting that outcome fields do not select rows.

`disclosure-review.json` contains exact passages or JSON pointers, manual rationales, pin identities and hashes. Complete inspected documents and their manifests are preserved in `disclosure-documents/`. A not-found judgment is limited to these inspected documents; a generic caveat does not count as full disclosure of a specific mechanism.

## fjc-civil-trial-36m

- Post-filing jury information; retrospective use: **stated**. The card explicitly warns that JURY may reflect later corrections and does not establish historical availability.

## eia861-reliability-deterioration

- Lagged outcomes require restricted scoring access: **stated**. The descriptor expressly requires isolated_rows. This states the access restriction, although it does not explain recovery of earlier targets from later rows.

## phmsa-pipeline-penalty-reduction

- Original-notice timing is unverified: **partly stated**. Historical notice-date availability is expressly assumed and revisions after closure are disclosed. The specific original-or-most-recent meaning of Notice_Sent_Date is not stated in either document.

## fda-510k-five-year-recall

- Undated recalls can become negatives; incidence unverified: **not found**. The documents describe missing recall linkage, date boundaries and parse checks, but do not state that an undated linked recall can leave a clearance negative. A date-parse check is not disclosure of this label consequence.

## t100-new-route-survival

- Carrier-code changes can count as entries or exits: **partly stated**. Both documents explicitly disclose the exit side; neither spells out inherited routes appearing as new entries. This agrees with review R2.

## sbir-phase1-to-phase2-conversion

- Selection declaration conflicts with later-record exclusions: **conflicting statements**. The release discloses missing-phase and agency exclusions, while its selection rule asserts that no outcome field selects rows. Disclosure does not reconcile these statements. The broad any-year exclusion behavior is not fully described.
- Award-amount timing: **partly stated**. The card says award amounts may have been corrected after the award. It does not describe the reviewer's unverified Phase I option mechanism or resolve that mechanism. The feature evidence calls the amount verified.

## caa-fce-hpv-escalation

- Earliest episode-resolution rule; incidence unverified: **not found**. Construction notes describe collapsing resolved episodes but omit the choice of the earliest date when dates differ. Neither document states the resulting possibility that an active episode passes the exclusion.

## wser-effluent-exceedance

- Prior-year outcome requires restricted scoring access: **stated**. The descriptor explicitly requires isolated_rows. The access restriction is stated; the reverse-label exposure mechanism across years is not explained. This does not validate an unrestricted batch interface.

## faa-wildlife-strike-substantial-damage

- Retrospective reports with known damage outcomes: **stated**. The card expressly describes retrospective reconstruction and the post-event known-damage filter.

## seattle-building-permit-completion

- Post-issuance field updates are unverified: **stated**. The card names mutable cost and housing fields, and the descriptor says issuance-time availability is assumed, not proven. This states the concern; it does not resolve it.

## fra-form54-hazmat-release

- Retrospective accident-report fields: **stated**. Both documents state that first-notification availability is inferred and that no field timestamps separate initial knowledge from the final report.

## sdwis-lcr-lead-action-level-next-period

- Older-history overlap: **not found**. The descriptor instead asserts that all contributing historical records end before the target period. Neither document states that older periods are admitted by start order without an end-date test; incidence remains unverified.
- Implausible unit magnitudes: **not found**. The descriptor specifies conversion to mg/L but neither document identifies the implausible high magnitudes or the unverified unit-label explanation observed by review.
- Embargo narrows the scored population: **partly stated**. The split policy explicitly requires the prior period to end before the split starts. The documents do not explain its consequence: only first post-boundary periods survive and some monitoring cycles disappear from scoring.
