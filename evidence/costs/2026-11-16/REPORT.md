# Final recurring production costs — 16 November 2026

The factory published **14 datasets** during the **81.53-hour** window.
Estimated recurring expenditure was **$38.23–$38.33**,
or **$2.73–$2.74 per publication**.
This is a resource-based operating ratio, not an invoice, full construction cost,
cost per validated benchmark, or measured saving over human work.

## Scope and provenance

Window: 2026-11-12T21:27:59.319944+00:00 through 2026-11-16T07:00:00+00:00.
The script-only close export was collected at 07:00:01 UTC and committed to
`earino/dataset-factory` as `bf052c4c84cc3e55cae4f8fe4a7a8df2b48d76c0`.
`inputs/provenance.json` retains hashes for all thirteen original export files.
The raw export's `cutoff` is null; its declared `window_close` supplies the fixed
07:00 boundary. Original export bytes remain unchanged.

All fourteen publications enter the cost denominator. Only the first twelve,
selected by publication order, enter the separate consumer experiment. Unsuccessful
attempts and non-cohort production work remain in expenditure. Records crossing
the opening boundary include their whole observed session/worker lifetime;
worker exposure is capped at the closing boundary.

## Components

- Inference: **$19.10–$19.21** from
  516 unique usage sessions and 3,404 calls.
  Token categories: 32,387,979 uncached input,
  129,523,918 cached input and 21,086,547 output.
  Dated rates and provider-specific tariff windows are in `inputs/rates.json`.
  Start/end tariff ambiguity produces the reported range; all-peak pricing is
  retained as a sensitivity calculation, not asserted actual spend.
- Workers: **€15.26 / $16.86** from
  259 CPX32 server lifetimes. Each is rounded separately to whole
  billed hours: 260 billed hours from
  25.24 observed server-hours. The recorded gross rate
  includes primary IPv4. No included worker remained active at cutoff.
- Hosting: **$2.26**, allocated from the operator-supplied $20
  monthly plan over November's thirty days.

All-peak inference pricing gives **$54.92** total,
or **$3.92 per publication**.

## Reconciliation and limits

Five in-window attempts lack usage rows. They are the same five pre-generation
HTTP 402 failures confirmed in the earlier readback, retained verbatim in
`inputs/scout-accounting-readback.json`; missing usage is not inferred to be zero.
There are no new unresolved in-window usage records. One construction stage is
still marked running, but its model session ended at 06:07:33 UTC with final
counters before the cutoff. The later worker started at 07:00:05 UTC and is outside
this window. See `inputs/final-readback.json` for Scout's read-only database check.

Two generic service changes occurred: inference routing and worker-reservation
accounting. The final export and readback confirm no later changes or manual
dataset/source/label/acceptance decisions. The close-export job is completed and
disabled with no next run. The stale sentence in the original `repairs.md` saying
no workflow change is superseded by its own two-commit inventory and the inspected
maintenance patches; the original file is preserved as received.

Development, author/operator labor, upstream collection, unmetered external
services, paper preparation and independent consumer evaluation are excluded.
The consumer fields in this cost summary are null, not zero. Nous-routed tokens
are valued at direct DeepSeek equivalent rates; no invoice reconciliation is
claimed. Token and worker records support a recurring operating estimate only.

Recalculate with:

```sh
python3 scripts/calculate_interim_costs.py --output evidence/costs/2026-11-16 --summary-only
```
