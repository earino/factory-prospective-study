"""Capture the final compact evidence after recoveries and the fixed production export.

Original execution records and earlier paper snapshots remain unchanged. The
Seattle composite is produced separately by combine_seattle_recovery.py.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DEST = ROOT / 'paper/analysis/final-inputs-2026-11-16.json'
COST = 'evidence/costs/2026-11-16'
data, hashes, reviews, consumers = {}, {}, {}, {}


def read(name):
    raw = (ROOT / name).read_bytes()
    hashes[name] = hashlib.sha256(raw).hexdigest()
    data[name] = json.loads(raw)
    return data[name]


queue = read('queue.json')
cohort = sorted([r for r in queue if r.get('selected')], key=lambda r: r['release']['verified_at'])
assert len(cohort) == 12
selected = {r['dataset']: r['dataset'] for r in cohort}
for ds in ['faa-wildlife-strike-substantial-damage', 'fra-form54-hazmat-release',
           'eia861-reliability-deterioration']:
    selected[ds] = ds + '-retry-1'
selected['seattle-building-permit-completion'] = 'seattle-building-permit-completion-retry-1'

for r in cohort:
    ds, ex = r['dataset'], selected[r['dataset']]
    read(f'evidence/consumer/{ds}/results/summary.json')  # Original failures stay visible.
    read(f'evidence/consumer/{ex}/results/summary.json')
    read(f'evidence/reviews/{ex}/pinned-release.json')
    for name in ['bootstrap.json', 'artifact-probes.json', 'training-feature-probes.json', 'control-features.json']:
        path = f'evidence/reviews/{ex}/post/{name}'
        if ds == 'seattle-building-permit-completion':
            path = f'paper/analysis/final-2026-11-16/seattle-composite/{name}'
            reviews.setdefault(ds, {})[name] = path
        if (ROOT / path).exists():
            read(path)
        else:
            assert ds == 'phmsa-pipeline-penalty-reduction' and name == 'bootstrap.json', path

seattle = 'seattle-building-permit-completion'
path = 'paper/analysis/final-2026-11-16/seattle-composite/summary.json'
consumers[seattle] = path
read(path)
read('paper/analysis/final-2026-11-16/seattle-composite/provenance.json')
read('paper/analysis/final-2026-11-16/seattle-composite/prediction-agreement.json')
read(f'evidence/consumer/{seattle}-retry-2/results/summary.json')

# Use the resolved row mappings without erasing the original checker errors.
fixed = read('paper/analysis/final-2026-11-16/row-mapped-training-probes.json')
for replacement in fixed:
    ds = replacement['run'].rsplit('--r', 1)[0]
    original = f'evidence/reviews/{selected[ds]}/post/training-feature-probes.json'
    rows = json.loads(json.dumps(data[original]))
    row = next(x for x in rows if x['run'] == replacement['run'])
    assert 'error' in row
    row['original_probe_error'] = row.pop('error')
    row.update(replacement)
    row['training_feature_rows'] = replacement['fitted_rows']
    path = f'paper/analysis/final-2026-11-16/resolved-probes/{ds}.json'
    target = ROOT / path
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(rows, indent=2) + '\n')
    read(path)
    reviews.setdefault(ds, {})['training-feature-probes.json'] = path

for name in ['summary.json', 'factory-model-costs.json', 'factory-worker-costs.json',
             'inputs/cohort.json', 'inputs/attempts_carry_in.json', 'inputs/attempts_new_admissions.json',
             'inputs/candidates_carry_in.json', 'inputs/candidates_new_admissions.json']:
    read(f'{COST}/{name}')
cost = data[f'{COST}/summary.json']
assert dt.datetime.fromisoformat(cost['cutoff']) == dt.datetime(2026, 11, 16, 7, tzinfo=dt.timezone.utc)
# The export's cohort.json is capped at twelve; production accounting is not.
start, stop = (dt.datetime.fromisoformat(cost[k]) for k in ['window_start', 'cutoff'])
candidates = sum([data[f'{COST}/inputs/candidates_{k}.json'] for k in ['carry_in', 'new_admissions']], [])
attempts = sum([data[f'{COST}/inputs/attempts_{k}.json'] for k in ['carry_in', 'new_admissions']], [])
first_publication = {}
for a in attempts:
    if a['stage'] == 'publish' and a['status'] == 'done' and a.get('finished'):
        when = dt.datetime.fromisoformat(a['finished'])
        first_publication[a['candidate']] = min(first_publication.get(a['candidate'], when), when)
production = []
for c in candidates:
    when = first_publication.get(c['id'])
    if c['stage'] == 'published' and when is not None and start <= when <= stop:
        production.append({'id': c['id'], 'dataset': c['dataset'], 'created': c['created'], 'published_at': when.isoformat()})
production.sort(key=lambda r: (r['published_at'], r['id']))
assert len(production) == cost['published_datasets']
assert [r['dataset'] for r in production[:12]] == [r['dataset'] for r in cohort]
read('paper/analysis/final-2026-11-16/qualification-coverage.json')
read('paper/analysis/final-2026-11-16/sbir-acceptance/checks.json')

snapshot = {
    'captured_at': dt.datetime.now(dt.timezone.utc).isoformat(),
    'repository_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'cost_base': COST,
    'production_cohort': production,
    'consumer_cohort': [{'dataset': r['dataset'], 'verified_at': r['release']['verified_at']} for r in cohort],
    'analysis_selection': selected,
    'consumer_overrides': consumers,
    'review_overrides': reviews,
    'sources': hashes,
    'data': data,
    'selection_basis': 'First twelve publications; declared failure recoveries, with original failures retained. Seattle r2/r3 are unchanged. No selection by holdout outcome.',
}
assert not DEST.exists(), 'Do not overwrite a captured final snapshot; inspect and version any correction explicitly'
DEST.write_text(json.dumps(snapshot, indent=2) + '\n')
print(DEST)
