"""Reconcile the fixed observation window without equating retries with defects."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'paper-agent27-short'
BASE = ROOT / 'evidence/costs/2026-11-16/inputs'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
cost_path = BASE.parent / 'summary.json'
cost = read(cost_path)
start, end = map(datetime.fromisoformat, [cost['window_start'], cost['cutoff']])
files = [BASE / f'{kind}_{group}.json' for kind in ['attempts', 'candidates']
         for group in ['carry_in', 'new_admissions']]
all_attempts = read(files[0]) + read(files[1])
attempts = [a for a in all_attempts if start <= datetime.fromisoformat(a['started']) < end]
assert len({a['id'] for a in attempts}) == len(attempts) == 540
assert all(not a['finished'] or datetime.fromisoformat(a['finished']) < end for a in attempts)
stages = ['discover', 'build', 'evaluate', 'publish']
statuses = ['done', 'retry', 'repair', 'defer', 'reject', 'running']
counts = Counter((a['stage'], a['status']) for a in attempts)
assert all(s in stages and t in statuses for s, t in counts)
stage_outcomes = {s: {t: counts[s, t] for t in statuses} for s in stages}
retry_records = []
for a in attempts:
    if a['status'] != 'retry':
        continue
    try:
        result = json.loads(a['result'])
        reason, scope = result.get('reason', ''), result.get('retry_scope')
        truncated = False
    except json.JSONDecodeError:
        # The bounded export truncates some reasons. Only use the preserved prefix.
        assert a['result'].startswith('{"reason":"') and '[truncated ' in a['result']
        reason, scope, truncated = a['result'].removeprefix('{"reason":"'), None, True
    if scope == 'worker':
        category = 'worker_outcome'
    elif reason.startswith('Model invocation failed:'):
        category = 'model_invocation'
    elif a['stage'] == 'publish':
        assert reason == 'Publication incomplete; retry reconciles destination files and tags'
        category = 'publication_reconciliation'
    else:
        category = 'proposal_or_controller_validation'
    retry_records.append({'attempt': a['id'], 'stage': a['stage'], 'category': category,
                          'truncated_reason': truncated, 'reason_prefix': reason[:160]})
jobs_path = BASE / 'jobs_ledger.json'
jobs = {j['attempt']: j for j in read(jobs_path)}
worker_retries = [r for r in retry_records if r['category'] == 'worker_outcome']
assert len(worker_retries) == 206
assert len({jobs[r['attempt']]['server_id'] for r in worker_retries}) == 206
assert all(jobs[r['attempt']]['status'] == 'deleted' for r in worker_retries)
discovered = {a['candidate'] for a in attempts if a['stage'] == 'discover' and a['status'] == 'done'}
candidates = [c for c in read(files[2]) + read(files[3]) if c['id'] in discovered]
assert len(candidates) == len(discovered) == 54
assert all(datetime.fromisoformat(c['updated']) < end for c in candidates)
built = {a['candidate'] for a in attempts if a['stage'] == 'build' and a['status'] == 'done'}
deferrals = []
for c in candidates:
    if c['stage'] != 'deferred':
        continue
    history = sorted((a for a in attempts if a['candidate'] == c['id']), key=lambda a: a['started'])
    last = history[-1]
    if c['reason'].startswith('Attempt limit reached:'):
        assert last['stage'] == 'build' and last['status'] == 'retry'
        scope = json.loads(last['result']).get('retry_scope', 'task')
        category = 'build_' + scope + '_failure_limit'
    elif c['reason'].startswith('Semantic repair limit reached:'):
        assert last['stage'] == 'evaluate' and last['status'] == 'repair'
        category = 'semantic_repair_limit'
    else:
        assert last['stage'] == 'build' and last['status'] == 'defer'
        category = 'explicit_build_deferral'
    deferrals.append({'candidate': c['id'], 'completed_build': c['id'] in built,
                      'category': category, 'last_attempt': last['id'], 'last_outcome': last['status']})
report = {
    'window_start': cost['window_start'], 'cutoff': cost['cutoff'],
    'sources': {str(p.relative_to(ROOT)): sha(p) for p in [cost_path, *files, jobs_path]},
    'attempt_unit': 'One durable stage attempt, potentially spanning multiple controller ticks. Waiting updates the same running attempt; intermediate wait counts are not recoverable from the final-state export.',
    'stage_outcomes': stage_outcomes,
    'outcome_totals': {t: sum(counts[s, t] for s in stages) for t in statuses},
    'stage_totals': {s: sum(stage_outcomes[s].values()) for s in stages},
    'retry_categories': dict(Counter(r['category'] for r in retry_records)),
    'retry_records': retry_records,
    'worker_retry_jobs': [{'attempt': r['attempt'], 'server_id': jobs[r['attempt']]['server_id']}
                          for r in worker_retries],
    'discovery_completed_cutoff_states': dict(Counter(c['stage'] for c in candidates)),
    'discovery_completed_candidates': candidates,
    'deferred_candidate_records': deferrals,
    'deferral_categories': dict(Counter(d['category'] for d in deferrals)),
    'deferred_without_completed_build': sum(not d['completed_build'] for d in deferrals),
    'limits': 'Retry categories describe recorded operation boundaries, not unique underlying bugs or causal diagnoses. A worker outcome can reflect construction, qualification or infrastructure failure. Deferred is the recorded cutoff state, not a prediction that a candidate can never resume.'
}
(OUT / 'analysis/attempt-accounting.json').write_text(json.dumps(report, indent=2) + '\n')
rows = []
for s, label in zip(stages, ['Discover', 'Build', 'Evaluate', 'Publish']):
    rows.append(label + ' & ' + ' & '.join(str(stage_outcomes[s][t]) for t in statuses)
                + ' & ' + str(report['stage_totals'][s]) + r'\\')
rows += [r'\midrule', 'Total & ' + ' & '.join(str(report['outcome_totals'][t]) for t in statuses) + r' & 540\\']
(OUT / 'draft/generated/attempt-rows.tex').write_text('\n'.join(rows) + '\n')
print(json.dumps({k: report[k] for k in ['stage_totals', 'outcome_totals', 'retry_categories', 'discovery_completed_cutoff_states']}))
