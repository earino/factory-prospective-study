"""Verify final tables and aggregates from retained evidence; no fitting or scoring."""
import collections
import datetime as dt
import hashlib
import json
import math
import re
import statistics

from evidence_inputs import (P, D, E, C, final, consumer_complete, cost_base, cohort, production_cohort,
                             consumer_path, review_path, snapshot_names)

assert consumer_complete, 'The completed consumer evidence has not been captured'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
historical = {
    'draft-inputs.json': '1799b8991cf9b73b4477e8741d71f1f08b15e4ef98e4d24829de3b6c05ee0170',
    'update-inputs-2026-11-15.json': '578e13f2058620d46b282414078059f9467eeedbc21f36b5331d6106676151b5',
    'evening-inputs-2026-11-15.json': '665c491cdedc20d7fc188fd2d13a36ed99dc9c52dc7f26effb15b06f1118bc96',
}
for name, digest in historical.items():
    assert sha(P / 'analysis' / name) == digest, name

table = (P / 'draft/generated/score-rows.tex').read_text().splitlines()
assert len(table) == len(cohort) == 12
assert len(production_cohort) == C['published_datasets']
counts = collections.Counter()
all_above, positive, probes, training, missing_intervals = [], {'ordinary': {}, 'random': {}}, [], [], []
models = 0
for i, item in enumerate(cohort):
    ds = item['dataset']
    s = D[consumer_path(ds)]
    counts.update(r['status'] for r in s['outcomes'])
    scores = s['scores']
    ordinary = next(r for r in scores if r['kind'] == 'ordinary')
    agents = [r for r in scores if r['kind'] == 'agent']
    random = [r for r in scores if r['kind'] == 'random']
    frozen = {r['id'] for r in s['outcomes'] if r['status'] == 'frozen'}
    assert {r['id'] for r in agents} == frozen
    assert {r['id'].removesuffix('--random') for r in random} == frozen
    assert all(r['holdout_rows'] == ordinary['holdout_rows'] for r in agents + random)
    span = lambda rows: f"{min(r['holdout_auc'] for r in rows):.3f}--{max(r['holdout_auc'] for r in rows):.3f}" if rows else '--'
    cells = [x.strip().rstrip('\\').strip() for x in table[i].split('&')]
    assert cells[1:5] == [f"{ordinary['holdout_rows']:,}", f"{ordinary['holdout_auc']:.3f}", span(agents), span(random)], ds
    assert len(agents) == 3, ds
    models += len(agents)
    if agents and all(r['holdout_auc'] > ordinary['holdout_auc'] for r in agents):
        all_above.append(ds)
    for name, dest in [('artifact-probes.json', probes), ('training-feature-probes.json', training)]:
        rows = D.get(review_path(ds, name), [])
        assert {r['run'] for r in rows} == frozen, (ds, name)
        dest.extend(rows)
    b = D.get(review_path(ds, 'bootstrap.json'))
    if not b or not b.get('comparisons'):
        assert cells[5] == ('?' if agents else '--')
        missing_intervals.append(ds)
        continue
    assert b['rows'] == ordinary['holdout_rows']
    assert b['valid_replicates'] == 2000 and b['invalid_replicates'] == 0
    assert cells[5] == f"{b['clusters']:,}"
    by_id = {r['id']: r for r in scores}
    for control in positive:
        comparisons = [r for r in b['comparisons'] if r['control'].endswith('--' + control)]
        assert {r['run'] for r in comparisons} == frozen
        for r in comparisons:
            assert math.isclose(r['delta'], by_id[r['run']]['holdout_auc'] - by_id[r['control']]['holdout_auc'], abs_tol=1e-12)
            assert r['low'] <= r['delta'] <= r['high']
        positive[control][ds] = sum(r['low'] > 0 for r in comparisons)

# Count physical research attempts, excluding the derived Seattle composite.
cohort_ids = {r['dataset'] for r in cohort}
physical = []
for path, value in D.items():
    if path.startswith('evidence/consumer/') and path.endswith('/results/summary.json'):
        physical.extend(r for r in value['outcomes'] if r.get('dataset') in cohort_ids)
physical_counts = collections.Counter(r['status'] for r in physical)
assert len(physical) == 49 and physical_counts == {'frozen': 36, 'failed': 12, 'blocked': 1}
review = D['paper/analysis/final-2026-11-16/code-conduct-review.json']
assert len(review['runs']) == models == 36
assert {r['run'] for r in review['runs']} == {r['run'] for r in probes}
assert len(all_above) == 11
assert sum(n == 3 for n in positive['ordinary'].values()) == 7
assert sum(n == 3 for n in positive['random'].values()) == 5
assert len(probes) == len(training) == models
assert all(r['batch_equals_single_rows'] and r['reverse_order_invariant'] for r in probes)
external_events = [(r['run'], e) for r in probes for e in r['prepare_external_events']]
# The probe records lazy imports as well as data access. Inspect and retain the
# two pandas dependency reads; do not misreport them as an empty event list.
assert all(e.get('dependency_read') and e['event'] == 'open' and e['path'].endswith('/pandas/core/methods/__pycache__/to_dict.cpython-311.pyc') for _, e in external_events)
assert not [r for r in training if 'error' in r], 'Resolve checker errors before making a passing-check claim'
assert all(c['changed_own_feature_cells'] == 0 for r in training for c in r['checks'])

start, stop = (dt.datetime.fromisoformat(C[k]) for k in ['window_start', 'cutoff'])
attempts = sum([D[f'{cost_base}/inputs/attempts_{k}.json'] for k in ['carry_in', 'new_admissions']], [])
attempts = [a for a in attempts if a.get('started') and start <= dt.datetime.fromisoformat(a['started']) <= stop]
stage = collections.Counter((a['stage'], a['status']) for a in attempts)
latencies = [(dt.datetime.fromisoformat(r['published_at']) - dt.datetime.fromisoformat(r['created'])).total_seconds() / 60 for r in production_cohort]
inference = D[f'{cost_base}/factory-model-costs.json']
workers = D[f'{cost_base}/factory-worker-costs.json']
assert len({r['session_id'] for r in inference}) == len(inference)
assert math.isclose(sum(r['cost_eur'] for r in workers), C['workers']['eur'])
for i, key in enumerate(['time_priced_low_usd', 'time_priced_high_usd']):
    amount = sum(r[key] for r in inference) + C['workers']['usd'] + C['hosting_usd']
    assert math.isclose(amount, C['factory_total_time_priced_usd_range'][i])
    assert math.isclose(amount / len(production_cohort), C['factory_time_priced_usd_per_release_range'][i])
assert math.isclose(C['hosting_usd'], 20 * (stop - start).total_seconds() / (30 * 86400))

comparisons = json.loads((P / 'analysis/comparator-summary.json').read_text())
medians = [statistics.median(r['delta'] for r in ds['ordinary']['comparisons']) for ds in comparisons.values()]
assert medians == sorted(medians)
for ds, controls in comparisons.items():
    b = D[review_path(ds, 'bootstrap.json')]
    for name, result in controls.items():
        assert result['comparisons'] == [r for r in b['comparisons'] if r['control'].endswith('--' + name)]
assert len(re.findall(r'\\bibitem\{', (P / 'output/main.bbl').read_text())) == 22

report = {
    'snapshot_sha256': {n: sha(P / 'analysis' / n) for n in snapshot_names},
    'historical_snapshots_unchanged': True,
    'production_final': final,
    'production_publications': len(production_cohort),
    'consumer_datasets': len(cohort), 'scored_models': models,
    'selected_outcomes': dict(counts),
    'all_research_attempts': len(physical),
    'all_research_outcomes': dict(physical_counts),
    'selected_code_reviews': len(review['runs']),
    'tasks_with_all_point_estimates_above_untuned': all_above,
    'positive_intervals': positive, 'datasets_without_intervals': missing_intervals,
    'artifact_probe_dependency_reads': external_events,
    'artifact_probe_passes': len(probes), 'own_label_probe_passes': len(training),
    'stage_attempts': len(attempts),
    'discovery_retries': stage['discover', 'retry'], 'build_retries': stage['build', 'retry'],
    'semantic_repair_outcomes': stage['evaluate', 'repair'],
    'unique_completed_candidates': {s: len({a['candidate'] for a in attempts if a['stage'] == s and a['status'] == 'done'}) for s in ['discover', 'build', 'evaluate', 'publish']},
    'publication_latency_minutes': {'min': min(latencies), 'median': statistics.median(latencies), 'max': max(latencies)},
    'cost_and_table_cells_checked': True, 'cited_references': 22,
    'missing_model_usage': C['missing_model_usage'],
}
(P / 'analysis/revision-checks.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
