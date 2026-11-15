#!/usr/bin/env python3
"""Recalculate interim costs from pinned compact records; no network or mutations to study evidence."""
import argparse, collections, datetime as dt, hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=ROOT / 'evidence/costs/2026-11-15',
                    help='Cost evidence directory containing pinned inputs/')
parser.add_argument('--summary-only', action='store_true',
                    help='Write numeric records only; keep the dated interim narrative unchanged')
args = parser.parse_args()
OUT = args.output.resolve()
IN = OUT / 'inputs'
def read(name): return json.loads((IN / name).read_text())
def date(x): return dt.datetime.fromisoformat(x.replace('Z', '+00:00'))
def write(name, obj): (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
summary = read('summary.json'); rates = read('rates.json')
start = date(summary['cohort_definition']['window_start']); end = date(summary['cutoff'] or summary['cohort_definition']['window_close'])
usage = read('model_usage.json')
zero_usage = set(read('scout-accounting-readback.json')['zero_usage_attempts'])
rows = []; missing = []; seen = set()
for key, row in usage.items():
    if not row.get('started'): continue
    began = date(row['started']); finished = date(row['finished']) if row.get('finished') else end
    if began > end or finished < start: continue
    group = 'started_in_window' if began >= start else 'carryover_full_session'
    u = row.get('usage')
    if not u:
        missing.append({'attempt':key,'stage':row['stage'],'group':group,
                        'reason':'HTTP 402 before generation; zero tokens per Scout database readback' if key in zero_usage else 'unresolved'})
        continue
    sid = u['session_id']; assert sid not in seen, ('duplicate session',sid); seen.add(sid)
    tokens = collections.Counter()
    for t in u['tasks']:
        assert 'deepseek' in t['model'].lower() and 'flash' in t['model'].lower(), t['model']
        for field in ['input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','calls']:
            tokens[field] += t.get(field,0)
    assert tokens['cache_write_tokens'] == 0
    peak = (tokens['input_tokens']*.30 + tokens['cache_read_tokens']*.006 + tokens['output_tokens']*1.20)/1e6
    providers = sorted({t['provider'] for t in u['tasks']})
    # Session-level timestamps only: use a bounded price range for sessions crossing a tariff boundary.
    provider = providers[0] if len(providers)==1 else 'mixed'
    def is_peak(t):
        if t.weekday() >= 5: return False
        hour = t.hour + t.minute/60 + t.second/3600
        return 12 <= hour < 18 if provider == 'ollama-cloud' else (1 <= hour < 4 or 6 <= hour < 10)
    flags = {is_peak(began), is_peak(finished)}
    tick = began.replace(minute=0,second=0,microsecond=0) + dt.timedelta(hours=1)
    while tick < finished:
        flags.add(is_peak(tick)); tick += dt.timedelta(hours=1)
    factors = [1 if f else .5 for f in flags]
    rows.append({'attempt':key,'session_id':sid,'stage':row['stage'],'group':group,'providers':providers,
                 'started':row['started'],'finished':row.get('finished'),**tokens,
                 'peak_rate_usd':peak,'off_peak_rate_usd':peak/2,
                 'time_priced_low_usd':peak*min(factors),'time_priced_high_usd':peak*max(factors)})
workers=[]
for job in read('jobs_ledger.json'):
    if not job.get('created_at') or not job.get('server_id'): continue
    began=date(job['created_at']); finished=date(job['deleted_at']) if job.get('deleted_at') else end
    if began>end or finished<start: continue
    elapsed=(min(finished,end)-began).total_seconds(); hours=max(1,math.ceil(elapsed/3600))
    rate=float(job['provider_hourly_eur'])
    workers.append({'job':job['attempt'],'candidate':job.get('candidate'),'stage':job['stage'],
                    'server_type':job['server_type'],'location':job['location'],'status':job['status'],
                    'group':'started_in_window' if began>=start else 'carryover_full_lifetime',
                    'created_at':job['created_at'],'deleted_at':job.get('deleted_at'),
                    'observed_lifetime_hours':elapsed/3600,'billed_hours':hours,
                    'provider_hourly_eur_gross_server_ipv4':rate,'cost_eur':hours*rate})
consumer_available = (IN / 'consumer_sessions.json').exists()
assert consumer_available or args.summary_only, 'A dated narrative requires its consumer accounting input'
consumer=read('consumer_sessions.json') if consumer_available else []
assert len({x['session_id'] for x in consumer if x.get('session_id')}) == len([x for x in consumer if x.get('session_id')])
consumer_groups={}
for category in ['research','pre_review']:
    rr=[x for x in consumer if x['category']==category]
    counter=collections.Counter()
    for r in rr:
        for m in (r.get('modelUsage') or {}).values():
            for field in ['inputTokens','cacheReadInputTokens','cacheCreationInputTokens','outputTokens']:
                counter[field]+=m.get(field,0)
    consumer_groups[category]={'sessions':len(rr),'reported_cost_usd':sum(x.get('total_cost_usd') or 0 for x in rr),
                              'no_cost_result':sum(x.get('total_cost_usd') is None for x in rr),'tokens':dict(counter),
                              'statuses':dict(collections.Counter(x['status'] for x in rr))}
by_stage={}
for stage in sorted({r['stage'] for r in rows}):
    rr=[r for r in rows if r['stage']==stage]
    by_stage[stage]={'sessions':len(rr),'peak_rate_usd':sum(r['peak_rate_usd'] for r in rr),
                     'time_priced_low_usd':sum(r['time_priced_low_usd'] for r in rr),
                     'time_priced_high_usd':sum(r['time_priced_high_usd'] for r in rr)}
hosting=20*(end-start).total_seconds()/(30*86400)
worker_eur=sum(x['cost_eur'] for x in workers); worker_usd=worker_eur*rates['usd_per_eur']
peak=sum(r['peak_rate_usd'] for r in rows)
low=sum(r['time_priced_low_usd'] for r in rows); high=sum(r['time_priced_high_usd'] for r in rows)
total=peak+worker_usd+hosting
result={'window_start':start.isoformat(),'cutoff':end.isoformat(),'elapsed_hours':(end-start).total_seconds()/3600,
        'published_datasets':summary['published_in_window_total'], 'model_sessions_with_usage':len(rows),
        'missing_model_usage':missing,'tokens':dict(sum((collections.Counter({k:r[k] for k in ['input_tokens','output_tokens','cache_read_tokens','calls']}) for r in rows),collections.Counter())),
        'model_peak_rate_usd':peak,'model_all_off_peak_usd':peak/2,'model_time_priced_usd_range':[low,high],
        'workers':{'jobs':len(workers),'running_at_cutoff':sum(x['status']!='deleted' for x in workers),
                   'lifetime_hours':sum(x['observed_lifetime_hours'] for x in workers),'billed_hours':sum(x['billed_hours'] for x in workers),
                   'eur':worker_eur,'usd':worker_usd},
        'hosting_usd':hosting,'factory_total_peak_rate_usd':total,
        'factory_total_time_priced_usd_range':[low+worker_usd+hosting,high+worker_usd+hosting],
        'factory_peak_usd_per_release':total/summary['published_in_window_total'],
        'factory_time_priced_usd_per_release_range':[(low+worker_usd+hosting)/summary['published_in_window_total'],(high+worker_usd+hosting)/summary['published_in_window_total']],
        'model_by_stage':by_stage,'consumer':consumer_groups,
        'consumer_total_reported_usd':sum(v['reported_cost_usd'] for v in consumer_groups.values()),
        'basis':'Current published price estimate, not invoice. Entire start-boundary overlapping sessions/jobs included conservatively. Missing records are not assumed zero. Window cost per publication is not lifetime dataset construction cost. Nous-route token usage valued at DeepSeek direct equivalent rates; Ollama route at Ollama rates. Timing range uses session intervals, not guessed call times. Consumer modelUsage and cost are last cumulative counters per unique session.'}
if not consumer_available:
    result['consumer'] = None
    result['consumer_total_reported_usd'] = None
write('factory-model-costs.json',rows);write('factory-worker-costs.json',workers);write('summary.json',result)
if not args.summary_only:
 (OUT/'REPORT.md').write_text(f'''# Interim operating costs — 15 November 2026

Factory cost at published token rates: **${low+worker_usd+hosting:.2f}–${high+worker_usd+hosting:.2f}**,
or **${(low+worker_usd+hosting)/summary['published_in_window_total']:.2f}–${(high+worker_usd+hosting)/summary['published_in_window_total']:.2f} per publication** across {summary['published_in_window_total']} new releases.
Charging all recorded inference at peak rates gives **${total:.2f}**, or **${total/summary['published_in_window_total']:.2f} per publication**.
These are reproducible operating-cost estimates, not invoices or lifetime costs of each dataset.

## Window and components

Observation: {start.isoformat()} through {end.isoformat()} ({(end-start).total_seconds()/3600:.2f} hours).

- DeepSeek inference: **${low:.2f}–${high:.2f}** with provider-specific peak/off-peak schedules; **${peak:.2f}** if every token is priced at the peak rate.
- Workers: **€{worker_eur:.2f} / ${worker_usd:.2f}**; {len(workers)} CPX32 job lifetimes, {sum(x['billed_hours'] for x in workers)} billed hours, {sum(x['observed_lifetime_hours'] for x in workers):.2f} elapsed server-hours. Each lifetime is rounded up separately. Recorded rate is €0.05868/hour including primary IPv4 and VAT. One worker was still running; include its accrued rounded hours through cutoff.
- Nous hosting: **${hosting:.2f}**, allocated from Eduardo's $20/month plan over November's 30 days.
- All recorded failed production attempts are included; successful builds are not the only costs counted.

Token counts across {len(rows)} sessions: {result['tokens']['input_tokens']:,} uncached input,
{result['tokens']['cache_read_tokens']:,} cached input, {result['tokens']['output_tokens']:,} output;
{result['tokens']['calls']:,} recorded API calls. Input and cache counts are disjoint, confirmed
by Scout against Hermes normalization code. Five additional attempts failed with HTTP 402
before generation; Scout confirmed zero-token session records. Their diagnostics remain in
the pinned attempt export. There are no cache-write tokens in this production selection.

## Independent consumer study, separate from factory production

- Research sessions: **${consumer_groups['research']['reported_cost_usd']:.2f}** in CLI-reported list-price equivalents, including failed runs.
- Prescoring reviews: **${consumer_groups['pre_review']['reported_cost_usd']:.2f}**.
- Combined reported model cost: **${result['consumer_total_reported_usd']:.2f}**.

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
''')
print(json.dumps(result,indent=2))
