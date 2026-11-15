"""Check manuscript aggregates against the three retained snapshots; no model fits."""
from pathlib import Path
import collections, datetime, hashlib, json, re, statistics, subprocess
P=Path(__file__).resolve().parents[1]
names=['draft-inputs.json','update-inputs-2026-11-15.json','evening-inputs-2026-11-15.json']
snapshots=[json.loads((P/'analysis'/n).read_text()) for n in names]
D={}; execution={}
for s in snapshots:D.update(s['data']);execution.update(s.get('analysis_selection',{}))
E=snapshots[-1]
cohort=D['evidence/costs/2026-11-15/inputs/cohort.json'];C=D['evidence/costs/2026-11-15/summary.json']
read=lambda ds,name:D[E.get('review_overrides',{}).get(ds,{}).get(name,f'evidence/reviews/{execution.get(ds,ds)}/post/{name}')]
outcomes=collections.Counter();point_above=[];positive={'ordinary':{},'random':{}};probes=[];training=[]
table=(P/'draft/generated/score-rows.tex').read_text().splitlines();expected_models=0
for i,r in enumerate(cohort):
 ds=r['dataset'];summary=D[f'evidence/consumer/{execution.get(ds,ds)}/results/summary.json']
 outcomes.update(x['status'] for x in summary['outcomes'])
 scores=summary['scores'];ordinary=next(x for x in scores if x['kind']=='ordinary')
 agents=[x for x in scores if x['kind']=='agent'];random=[x for x in scores if x['kind']=='random']
 span=lambda rows:f"{min(x['holdout_auc'] for x in rows):.3f}--{max(x['holdout_auc'] for x in rows):.3f}" if rows else '--'
 cells=[x.strip().rstrip('\\').strip() for x in table[i].split('&')]
 assert cells[1:5]==[f"{ordinary['holdout_rows']:,}",f"{ordinary['holdout_auc']:.3f}",span(agents),span(random)],ds
 if not agents:continue
 expected_models+=len(agents)
 if all(x['holdout_auc']>ordinary['holdout_auc'] for x in agents):point_above.append(ds)
 probes+=read(ds,'artifact-probes.json');training+=read(ds,'training-feature-probes.json')
 if cells[5]=='?':assert ds=='phmsa-pipeline-penalty-reduction';continue
 b=read(ds,'bootstrap.json');assert cells[5]==f"{b['clusters']:,}"
 for control in positive:
  comparisons=[x for x in b['comparisons'] if x['control'].endswith('--'+control)]
  assert {x['run'] for x in comparisons}=={x['id'] for x in summary['outcomes'] if x['status']=='frozen'}
  positive[control][ds]=sum(x['low']>0 for x in comparisons)
assert len(D['queue.json'])==12 and len(cohort)==11 and len(table)==12
assert expected_models==29 and outcomes=={'frozen':29,'failed':3,'blocked':1}
assert len(point_above)==9
assert len(probes)==29 and all(x['real_validation_rows_checked']==25 and x['batch_equals_single_rows'] and x['reverse_order_invariant'] for x in probes)
errors=[x['run'] for x in training if 'error' in x]
assert len(training)==29 and len(errors)==3
assert all(all(c['changed_own_feature_cells']==0 for c in x['checks']) for x in training if 'error' not in x)
assert sorted(positive['ordinary'].values())==[0,0,0,2,3,3,3,3,3]
assert sorted(positive['random'].values())==[0,0,0,1,1,2,3,3,3]
assert [round(x,2) for x in C['factory_total_time_priced_usd_range']]==[27.84,27.94]
assert [round(x/11,2) for x in C['factory_total_time_priced_usd_range']]==[2.53,2.54]
start=datetime.datetime.fromisoformat(C['window_start']);stop=datetime.datetime.fromisoformat(C['cutoff'])
assert round((stop-start).total_seconds()/3600,2)==64.93
A=sum([D[f'evidence/costs/2026-11-15/inputs/attempts_{s}.json'] for s in ['carry_in','new_admissions']],[])
A=[a for a in A if start<=datetime.datetime.fromisoformat(a['started'])<=stop]
assert len(A)==394
counts=collections.Counter((a['stage'],a['status']) for a in A)
assert [counts['discover','retry'],counts['build','retry'],counts['evaluate','repair']]==[76,184,14]
assert [len({a['candidate'] for a in A if a['stage']==s and a['status']=='done'}) for s in ['discover','build','evaluate','publish']]==[41,14,11,11]
assert len(re.findall(r'\\bibitem\{',(P/'output/main.bbl').read_text()))==20
# Evidence, accounting figure and table remain identical; workflow wording and Figure 3 row order changed.
unchanged=[P/'analysis'/n for n in names]+[P/'draft/figures'/n for n in ['operations.pdf']]+[P/'draft/generated/score-rows.tex']
for f in unchanged:
 old=subprocess.check_output(['git','show',f'15889e5:paper/{f.relative_to(P)}'],cwd=P.parent)
 assert old==f.read_bytes(),f
old_comparisons=json.loads(subprocess.check_output(['git','show','74d7cca:paper/analysis/comparator-summary.json'],cwd=P.parent))
comparisons=json.loads((P/'analysis/comparator-summary.json').read_text())
assert comparisons==old_comparisons
medians=[statistics.median(c['delta'] for c in ds['ordinary']['comparisons']) for ds in comparisons.values()]
assert medians==sorted(medians)
report={'snapshot_sha256':{n:hashlib.sha256((P/'analysis'/n).read_bytes()).hexdigest() for n in names},'unchanged_evidence_accounting_figure_table':True,'figure3_comparisons_unchanged':True,'figure3_order':'median untuned AUC gain, ascending top to bottom, shared by both panels','publications':12,'cost_denominator':11,'scored_models':29,'scored_datasets':10,'selected_outcomes':dict(outcomes),'tasks_with_all_point_estimates_above_untuned':point_above,'positive_intervals':positive,'artifact_probe_passes':len(probes),'own_label_probe_errors':errors,'table_cells_checked':True,'cost_and_attempt_aggregates_checked':True,'cited_references':20}
(P/'analysis/revision-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
