# Interim operating costs — 15 November 2026

Factory cost at published token rates: **$27.84–$27.94**,
or **$2.53–$2.54 per publication** across 11 new releases.
Charging all recorded inference at peak rates gives **$39.27**, or **$3.57 per publication**.
These are reproducible operating-cost estimates, not invoices or lifetime costs of each dataset.

## Window and components

Observation: 2026-11-12T21:27:59.319944+00:00 through 2026-11-15T14:24:01+00:00 (64.93 hours).

- DeepSeek inference: **$13.84–$13.95** with provider-specific peak/off-peak schedules; **$25.28** if every token is priced at the peak rate.
- Workers: **€11.03 / $12.19**; 187 CPX32 job lifetimes, 188 billed hours, 18.53 elapsed server-hours. Each lifetime is rounded up separately. Recorded rate is €0.05868/hour including primary IPv4 and VAT. One worker was still running; include its accrued rounded hours through cutoff.
- Nous hosting: **$1.80**, allocated from Eduardo's $20/month plan over November's 30 days.
- All recorded failed production attempts are included; successful builds are not the only costs counted.

Token counts across 374 sessions: 21,694,498 uncached input,
91,107,712 cached input, 15,184,763 output;
2,412 recorded API calls. Input and cache counts are disjoint, confirmed
by Scout against Hermes normalization code. Five additional attempts failed with HTTP 402
before generation; Scout confirmed zero-token session records. Their diagnostics remain in
the pinned attempt export. There are no cache-write tokens in this production selection.

## Independent consumer study, separate from factory production

- Research sessions: **$498.10** in CLI-reported list-price equivalents, including failed runs.
- Prescoring reviews: **$28.52**.
- Combined reported model cost: **$526.61**.

Use the last cumulative cost and model-token counters once per unique CLI session.
Do not sum cumulative values across resumes. This includes 33 research attempts: 21 frozen
and 12 failed. The original post-review cost summaries omit runs without frozen artifacts;
this calculation reads their original attempt states too. In particular, the wildlife-strike
research sessions consumed tokens before failure. These figures are model-price equivalents,
not an additional Claude subscription invoice. Local Mac electricity/depreciation is not
measured. Deterministic model fitting on that Mac creates no recorded cloud-worker charge.
Deadline-truncated invocations may have usage beyond their last CLI result.

## Scope and reproducibility

This measures factory workflow tasks and workers, plus hosting. It excludes development,
interactive operator/Scout coordination, author time, paper preparation, and unmetered
external services. It does not value upstream agencies' data collection. There are no
separately metered search charges in this exported task record; do not assume that would
hold for every deployment.

For a conservative boundary allocation, include the complete usage of two model sessions
and one worker that began before the window but ended within it. Other pre-window work on
carry-in candidates is excluded. Thus cost per publication is the operating-window ratio,
not a claim about each release's entire construction history. Publication does not certify
benchmark quality; that is evaluated separately.

The inference estimate uses current Ollama prices for Ollama-routed sessions. Earlier
Nous-routed DeepSeek sessions use direct DeepSeek price equivalents, not a claimed Nous
invoice. Aggregate session timestamps cannot locate every call within a tariff boundary;
the narrow range assigns boundary-crossing sessions the two possible rates. The all-peak
figure is an alternative that does not depend on tariff timing. It is not an upper bound
on omitted development or other unmeasured costs. No additional subscription is added to
token-equivalent prices, avoiding double counting inference credits.

Recalculate offline from this repository with:

```sh
python3 scripts/calculate_interim_costs.py
```

Inputs are pinned in `inputs/provenance.json`; detailed model and worker calculations are
in `factory-model-costs.json` and `factory-worker-costs.json`. Consumer session extracts
retain source paths and SHA256 hashes; original states remain on their frozen study branches.
Scout's accounting clarification is recorded separately as readback evidence.

## Price sources

- [Ollama pricing](https://ollama.com/pricing): peak $0.30 uncached input, $0.006 cached input, $1.20 output per million; half off-peak; weekday peak 12:00–18:00 UTC.
- [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing/): same token rates; weekday peak 01:00–04:00 and 06:00–10:00 UTC. All dates here fall outside Chinese public holidays.
- [Hetzner billing](https://docs.hetzner.com/cloud/billing/faq/): whole-hour rounding per server. Rates are the provider API values saved when each worker launched, not budget ceilings. `factory/worker.py:check_price` at deployment 215715771b1c93f474cc7a8a223c732bf4710266 sums gross server and IPv4 prices.
- [ECB reference rate](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html): 13 November 2026, €1 = $1.1052.
- Hosting: Eduardo supplied $20/month Nous Research plan.

Prices checked 15 November 2026. See `inputs/rates.json` for the machine-readable assumptions.
