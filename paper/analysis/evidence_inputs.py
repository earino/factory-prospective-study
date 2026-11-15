"""Load retained paper snapshots, including the final snapshot when present."""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1]
snapshot_names = ['draft-inputs.json', 'update-inputs-2026-11-15.json', 'evening-inputs-2026-11-15.json']
final_name = 'final-inputs-2026-11-16.json'
if (P / 'analysis' / final_name).exists():
    snapshot_names.append(final_name)
D, execution_ids, review_overrides, consumer_overrides = {}, {}, {}, {}
for name in snapshot_names:
    E = json.loads((P / 'analysis' / name).read_text())
    D.update(E['data'])
    execution_ids.update(E.get('analysis_selection', {}))
    consumer_overrides.update(E.get('consumer_overrides', {}))
    for ds, overrides in E.get('review_overrides', {}).items():
        review_overrides.setdefault(ds, {}).update(overrides)
final = snapshot_names[-1] == final_name
cost_base = E.get('cost_base', 'evidence/costs/2026-11-15')
C = D[f'{cost_base}/summary.json']
cohort = E.get('consumer_cohort', D[f'{cost_base}/inputs/cohort.json'])
production_cohort = E.get('production_cohort', D[f'{cost_base}/inputs/cohort.json'])
labels = ['Civil trials', 'Utility reliability', 'Pipeline penalties', 'Device recalls',
          'Airline routes', 'Research grants', 'Air enforcement', 'Wastewater',
          'Wildlife strikes', 'Building permits', 'Railway hazmat', 'Drinking-water lead']
ordered = sorted([r for r in D['queue.json'] if r.get('selected')], key=lambda r: r['release']['verified_at'])
assert len(ordered) == len(labels) == 12
names = {r['dataset']: label for r, label in zip(ordered, labels)}


def consumer_path(ds):
    return consumer_overrides.get(ds, f'evidence/consumer/{execution_ids.get(ds, ds)}/results/summary.json')


def review_path(ds, name):
    return review_overrides.get(ds, {}).get(name, f'evidence/reviews/{execution_ids.get(ds, ds)}/post/{name}')
