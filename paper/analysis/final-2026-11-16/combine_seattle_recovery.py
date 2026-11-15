"""Combine the authorized r1 recovery with unchanged r2/r3, preserving raw evidence.

Run only after retry-2 is terminal and its postchecks are available. This does not
select models, rerun scoring, or overwrite either execution's evidence.
"""
from pathlib import Path
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'seattle-composite'
DS = 'seattle-building-permit-completion'
OLD, NEW = DS + '-retry-1', DS + '-retry-2'
sources = {}


def read(path):
    b = (ROOT / path).read_bytes()
    sources[path] = hashlib.sha256(b).hexdigest()
    return json.loads(b)


def write(name, value):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


outcome = read(f'evidence/outcomes/{NEW}.json')
assert outcome['status'] == 'complete', outcome
old = read(f'evidence/consumer/{OLD}/results/summary.json')
new = read(f'evidence/consumer/{NEW}/results/summary.json')
assert [r['id'] for r in new['outcomes']] == [DS + '--r1']
assert new['outcomes'][0]['status'] == 'frozen', 'Inspect a failed recovery before analysis'
assert all(r['status'] == 'frozen' for r in old['outcomes'] if r['id'].endswith(('--r2', '--r3')))
base_old = [r for r in old['scores'] if r['kind'] == 'ordinary']
base_new = [r for r in new['scores'] if r['kind'] == 'ordinary']
assert base_old == base_new, 'The fixed control must agree across executions'
pin_old = read(f'evidence/reviews/{OLD}/pinned-release.json')
pin_new = read(f'evidence/reviews/{NEW}/pinned-release.json')
assert pin_old == pin_new, 'Release pins changed'

summary = {
    'dataset': DS,
    'derived_analysis_record': True,
    'selection_rule': 'Fresh authorized retry-2 r1 plus original retry-1 r2/r3; no score-based choice. Raw blocked r1 remains in retry-1 evidence.',
    'execution_by_run': {DS + '--r1': NEW, DS + '--r2': OLD, DS + '--r3': OLD},
    'outcomes': new['outcomes'] + [r for r in old['outcomes'] if r['id'].endswith(('--r2', '--r3'))],
    'scores': base_old + [r for r in new['scores'] if r['kind'] != 'ordinary'] + [r for r in old['scores'] if r['kind'] != 'ordinary'],
}
assert len({r['id'] for r in summary['scores']}) == len(summary['scores']) == 7
write('summary.json', summary)

b_old = read(f'evidence/reviews/{OLD}/post/bootstrap.json')
b_new = read(f'evidence/reviews/{NEW}/post/bootstrap.json')
for key in ['dataset', 'cluster_columns', 'clusters', 'rows', 'positives', 'missing_cluster_rows',
            'largest_cluster', 'seed', 'valid_replicates', 'invalid_replicates', 'method']:
    assert b_old[key] == b_new[key], key
b = copy.deepcopy(b_old)
b['comparisons'] = b_new['comparisons'] + b_old['comparisons']
b['inputs'].update(b_new['inputs'])
b['derived_analysis_record'] = True
assert len(b['comparisons']) == 6
assert {r['run'] for r in b['comparisons']} == set(summary['execution_by_run'])
write('bootstrap.json', b)

for name in ['artifact-probes.json', 'training-feature-probes.json']:
    a = read(f'paper/analysis/evening-2026-11-15/seattle-probes/{name}')
    z = read(f'evidence/reviews/{NEW}/post/{name}')
    assert {r['run'] for r in a} == {DS + '--r2', DS + '--r3'}
    assert {r['run'] for r in z} == {DS + '--r1'}
    write(name, z + a)

old_features = read('paper/analysis/evening-2026-11-15/seattle-probes/control-features.json')
new_features = read(f'evidence/reviews/{NEW}/post/control-features.json')
assert old_features == new_features
write('control-features.json', old_features)
write('provenance.json', {'derived_analysis_record': True, 'source_sha256': sources,
                         'rule': summary['selection_rule'], 'execution_by_run': summary['execution_by_run']})
print('Preserved two original models and added the single authorized recovery with its own paired control.')
