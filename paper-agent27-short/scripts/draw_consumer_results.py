"""Plot the frozen consumer results without fitting or selecting new models."""
from pathlib import Path
import hashlib
import json
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'paper-agent27-short'
snapshot_path = ROOT/'paper/analysis/final-inputs-2026-11-16.json'
snapshot = json.loads(snapshot_path.read_text())
coverage_path = ROOT/'paper/analysis/final-2026-11-16/qualification-coverage.json'
coverage = json.loads(coverage_path.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
labels = ['Trial within 36 months', 'Reliability deterioration', 'Penalty reduction',
          'Five-year recall', 'Route survival', 'Phase I to II award',
          'Violation escalation', 'Wastewater exceedance', 'Strike damage',
          'Permit completion', 'Hazmat release', 'Next-period lead']
rows = []
for (dataset, selected), label in zip(snapshot['analysis_selection'].items(), labels, strict=True):
    path = snapshot.get('consumer_overrides', {}).get(
        dataset, f'evidence/consumer/{selected}/results/summary.json')
    assert sha(ROOT/path) == snapshot['sources'][path]
    summary = json.loads((ROOT/path).read_text())
    assert summary == snapshot['data'][path]
    ordinary = [r for r in summary['scores'] if r['kind'] == 'ordinary']
    agents = [r for r in summary['scores'] if r['kind'] == 'agent']
    tuned = [r for r in summary['scores'] if r['kind'] == 'random']
    assert len(ordinary) == 1 and len(agents) == len(tuned) == 3
    assert {r['id']+'--random' for r in agents} == {r['id'] for r in tuned}
    assert {r['id'] for r in agents} == {r['id'] for r in summary['outcomes'] if r['status'] == 'frozen'}
    assert len({r['holdout_rows'] for r in ordinary+agents+tuned}) == 1
    qualification = next(r for r in coverage['releases'] if r['dataset'] == dataset)
    assert sha(ROOT/qualification['receipt']) == qualification['receipt_sha256']
    receipt = json.loads((ROOT/qualification['receipt']).read_text())
    assert receipt['accept_exit_code'] == 0
    values = [r['holdout_auc'] for r in agents]
    tuned_values = [r['holdout_auc'] for r in tuned]
    baseline = ordinary[0]['holdout_auc']
    rows.append({'dataset': dataset, 'label': label, 'summary': path,
                 'summary_sha256': snapshot['sources'][path],
                 'qualification_receipt': qualification['receipt'],
                 'qualification_receipt_sha256': qualification['receipt_sha256'],
                 'holdout_rows': ordinary[0]['holdout_rows'], 'baseline_auc': baseline,
                 'consumer_scores': {r['id']: r['holdout_auc'] for r in agents},
                 'consumer_median': statistics.median(values),
                 'consumer_min': min(values), 'consumer_max': max(values),
                 'tuned_scores': {r['id']: r['holdout_auc'] for r in tuned},
                 'tuned_median': statistics.median(tuned_values),
                 'tuned_min': min(tuned_values), 'tuned_max': max(tuned_values),
                 'all_three_above_baseline': min(values) > baseline})
rows.sort(key=lambda r: r['consumer_median'])
report = {'snapshot': str(snapshot_path.relative_to(ROOT)), 'snapshot_sha256': sha(snapshot_path),
          'qualification_coverage': str(coverage_path.relative_to(ROOT)),
          'qualification_coverage_sha256': sha(coverage_path),
          'scope': 'Descriptive holdout AUC from fixed baseline, all three frozen consumer models, and their three paired random-search controls. Ranges are observed run ranges, not confidence intervals. Existing final-run selection and qualification receipts are reused; no new fits or holdout-based model selection.',
          'baseline': {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1},
          'records': rows,
          'all_three_above_baseline_tasks': sum(r['all_three_above_baseline'] for r in rows),
          'paired_comparisons': {r['dataset']: [r['consumer_scores'][k]-r['tuned_scores'][k+'--random'] for k in r['consumer_scores']] for r in rows},
          'overlapping_run_ranges': [r['dataset'] for r in rows if max(r['consumer_min'],r['tuned_min'])<=min(r['consumer_max'],r['tuned_max'])],
          'consumer_tuned_medians_within_001': sum(abs(r['consumer_median']-r['tuned_median'])<.01 for r in rows),
          'median_auc_range': [min(r['consumer_median'] for r in rows), max(r['consumer_median'] for r in rows)]}
assert report['all_three_above_baseline_tasks'] == 11
assert report['consumer_tuned_medians_within_001'] == 5
(OUT/'analysis/consumer-results.json').write_text(json.dumps(report, indent=2)+'\n')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42, 'font.size': 8.5})
fig, ax = plt.subplots(figsize=(3.48, 3.35))
fig.subplots_adjust(left=.445, right=.945, top=.84, bottom=.17)
for y, r in enumerate(rows):
    if y % 2 == 0: ax.axhspan(y-.5, y+.5, color='#f2f4f6', zorder=0)
    comparisons = [([v-r['baseline_auc'] for v in r['consumer_scores'].values()], -.23, '#8a939a'),
                   ([v-r['tuned_scores'][k+'--random'] for k,v in r['consumer_scores'].items()], .23, '#246d98')]
    for values, offset, color in comparisons:
        center = statistics.median(values)
        ax.plot([min(values), max(values)], [y+offset, y+offset], color=color, lw=1.4, zorder=2)
        ax.scatter(center, y+offset, marker='o', s=14, color=color, zorder=3)
ax.axvline(0, color='#38434b', lw=.9, zorder=1)
ax.set_yticks(range(len(rows)), [r['label'] for r in rows])
ax.set_ylim(len(rows)-.5, -.5)
ax.set_xlim(-.025, .08)
ax.set_xticks([-.02, 0, .02, .04, .06, .08], ['−.02','0','+.02','+.04','+.06','+.08'])
ax.tick_params(axis='y', length=0, pad=5)
ax.tick_params(axis='x', length=2, color='#aab6bd', labelsize=8)
for side in ['top', 'right', 'left']: ax.spines[side].set_visible(False)
ax.spines['bottom'].set_color('#aab6bd')
ax.set_axisbelow(True); ax.grid(axis='x', color='#e0e5e9', lw=.5)
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], marker='o', color='#8a939a', markersize=3.5, label='Consumer − untuned'),
                    Line2D([], [], marker='o', color='#246d98', markersize=3.5, label='Consumer − tuned search')],
           loc='upper left', bbox_to_anchor=(.03, 1.0), frameon=False, fontsize=8.5,
           handlelength=1.5, labelspacing=.4)
ax.set_xlabel('Difference in holdout AUC', fontsize=8.7, labelpad=5)
fig.savefig(OUT/'draft/figures/consumer-results.pdf', metadata={'CreationDate': None, 'ModDate': None})
plt.close(fig)
print(json.dumps({'datasets': len(rows), 'all_three_above_baseline': 11, 'median_auc_range': report['median_auc_range']}))
